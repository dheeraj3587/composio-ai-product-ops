"""Read-only, one-app Composio Session research agent.

The agent deliberately cannot write any project artifact. It gives Gemini three
preloaded local tools: load one verified record, run one first-party Browser
Tool investigation, and deterministically compare the returned verdict.
"""
from __future__ import annotations

import json
import re
import time
from typing import Literal
from urllib.parse import urlparse

from pydantic import BaseModel, Field

import config
import docs_research
import handcheck
import normalize
import pipeline

USER_ID = "takehome-composio-agent"
BROWSER_CREATE = "BROWSER_TOOL_CREATE_TASK"
BROWSER_WATCH = "BROWSER_TOOL_WATCH_TASK"
POLL_INTERVAL_SECONDS = 3.0
BROWSER_TIMEOUT_SECONDS = 180.0
MAX_TOOL_ROUNDS = 8


class TargetInput(BaseModel):
    slug: str = Field(description="Exact app slug from the assignment catalog")


class BrowserResearchInput(BaseModel):
    slug: str = Field(description="Exact app slug to investigate in official documentation")


class CompareResearchInput(BaseModel):
    slug: str = Field(description="Exact app slug whose cached browser verdict should be compared")


class CompareVerdictInput(BaseModel):
    slug: str
    api_type: Literal["REST", "GraphQL", "SDK", "SOAP", "MCP-only", "None"]
    auth_methods: list[str]
    access_model: Literal["Self-Serve", "Gated"]
    evidence_urls: list[str]
    notes: str


def _current_record(slug: str) -> tuple[dict, dict]:
    try:
        app_meta = pipeline.get_app(slug)
    except KeyError as exc:
        raise ValueError(str(exc)) from exc
    records = config.load_json(config.RESULTS_PATH, default=[]) or []
    record = next((row for row in records if row.get("slug") == slug), None)
    if not record:
        raise ValueError(f"{slug}: no current verified record in results.json")
    return record, app_meta


def _as_dict(value) -> dict:
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    data = getattr(value, "data", None)
    error = getattr(value, "error", None)
    if data is not None or error is not None:
        return {"data": data or {}, "error": error}
    raise ValueError(f"unexpected tool response type: {type(value).__name__}")


def _unwrap_session_response(response, action: str) -> dict:
    payload = _as_dict(response)
    if payload.get("error"):
        raise RuntimeError(f"{action} failed: {payload['error']}")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise RuntimeError(f"{action} returned malformed data")
    return data


def _extract_browser_verdict(value) -> dict:
    if isinstance(value, dict):
        return value
    if not isinstance(value, str) or not value.strip():
        raise ValueError("browser task returned no structured verdict")
    text = value.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.I | re.S)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as json_error:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            try:
                parsed = json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                raise ValueError(f"browser task returned malformed JSON: {json_error}") from json_error
        else:
            protocol_keys = [
                "SLUG",
                "API_TYPE",
                "AUTH_METHODS",
                "ACCESS_MODEL",
                "EVIDENCE_URLS",
                "NOTES",
            ]
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            if len(lines) != len(protocol_keys):
                raise ValueError("browser task output does not match the six-line protocol")
            values = {}
            for expected, line in zip(protocol_keys, lines, strict=True):
                key, separator, raw = line.partition(":")
                if not separator or key.strip() != expected or not raw.strip():
                    raise ValueError("browser task output has a malformed protocol line")
                values[expected] = raw.strip()
            parsed = {
                "slug": values["SLUG"],
                "api_type": values["API_TYPE"],
                "auth_methods": [
                    item.strip()
                    for item in values["AUTH_METHODS"].split("|")
                    if item.strip()
                ],
                "access_model": values["ACCESS_MODEL"],
                "evidence_urls": [
                    item.strip()
                    for item in values["EVIDENCE_URLS"].split("|")
                    if item.strip()
                ],
                "notes": values["NOTES"],
            }
    if not isinstance(parsed, dict):
        raise ValueError("browser task verdict must be a JSON object")
    return parsed


def _browser_task_prompt(record: dict, app_meta: dict) -> str:
    return f"""Investigate {record['app']} ({record['slug']}) using ONLY first-party vendor
documentation. Do not use search snippets, integration directories, blogs, social posts,
or third-party summaries as evidence. Do not log in, create an account, submit forms, or
enter credentials.

Determine these exact fields under the current assignment rubric:
- api_type: one of REST, GraphQL, SDK, SOAP, MCP-only, None. Use the primary public
  integration surface, not an incidental internal endpoint.
- auth_methods: one or more canonical labels from {json.dumps(normalize.CANONICAL)}.
- access_model: {handcheck.ACCESS_RUBRIC}

Prefer claim-bearing API, authentication, plan/access, and MCP pages. Start with
{record.get('primary_docs_url') or app_meta.get('hint_url') or 'the vendor documentation'}.
Return exactly these six plain-text lines, in this order, with no bullets, Markdown, JSON,
blank lines, backslashes, or surrounding prose:
SLUG: {record['slug']}
API_TYPE: one allowed api_type value
AUTH_METHODS: canonical label | canonical label
ACCESS_MODEL: Self-Serve or Gated
EVIDENCE_URLS: exact first-party URL | exact first-party URL
NOTES: one plain-text sentence connecting the documentation to every verdict
"""


def compare_verdict(verdict: dict) -> dict:
    """Validate and compare a browser verdict without changing the dataset."""
    validated = CompareVerdictInput.model_validate(verdict)
    record, app_meta = _current_record(validated.slug)
    auth_methods = normalize.normalize_auth_list(validated.auth_methods, strict=True)
    if not auth_methods:
        raise ValueError("browser verdict must contain at least one auth method")
    if not validated.evidence_urls:
        raise ValueError("browser verdict must contain at least one evidence URL")
    for url in validated.evidence_urls:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError(f"invalid browser evidence URL: {url!r}")
        if not docs_research.is_first_party(
            url,
            hint_url=app_meta.get("hint_url") or record.get("primary_docs_url", ""),
            slug=validated.slug,
        ):
            raise ValueError(f"browser evidence is not first-party: {url}")
    if not validated.notes.strip():
        raise ValueError("browser verdict notes must explain the decision")

    current_access = (record.get("access_model") or {}).get("kind")
    browser = {
        "api_type": validated.api_type,
        "auth_methods": auth_methods,
        "access_model": validated.access_model,
    }
    current = {
        "api_type": record.get("api_type"),
        "auth_methods": normalize.normalize_auth_list(
            record.get("auth_methods", []), strict=True
        ),
        "access_model": current_access,
    }
    matches = {
        "api_type": current["api_type"] == browser["api_type"],
        "auth_methods": normalize.auth_sets_equal(
            current["auth_methods"], browser["auth_methods"], strict=True
        ),
        "access_model": current["access_model"] == browser["access_model"],
    }
    disagreed_fields = [field for field, agreed in matches.items() if not agreed]
    return {
        "slug": validated.slug,
        "app": record["app"],
        "current": current,
        "browser": browser,
        "matches": matches,
        "disagreed_fields": disagreed_fields,
        "evidence_urls": validated.evidence_urls,
        "notes": validated.notes.strip(),
        "requires_human_adjudication": bool(disagreed_fields),
    }


def build_custom_tools(
    composio,
    *,
    poll_interval: float = POLL_INTERVAL_SECONDS,
    timeout: float = BROWSER_TIMEOUT_SECONDS,
) -> tuple[list, dict]:
    """Build the three preloaded local tools and their in-memory trace state."""
    if poll_interval < 0 or timeout <= 0:
        raise ValueError("poll_interval must be non-negative and timeout must be positive")
    state: dict = {"browser_runs": {}, "comparison": None}

    @composio.experimental.tool(slug="GET_RESEARCH_TARGET", preload=True)
    def get_research_target(input: TargetInput, ctx) -> dict:
        """Load assignment metadata and the current verified record for one app."""
        del ctx
        record, app_meta = _current_record(input.slug)
        return {
            "assignment": {
                "auth_vocabulary": normalize.CANONICAL,
                "access_rubric": handcheck.ACCESS_RUBRIC,
                "allowed_api_types": ["REST", "GraphQL", "SDK", "SOAP", "MCP-only", "None"],
            },
            "app_metadata": app_meta,
            "current_record": {
                key: record.get(key)
                for key in (
                    "slug",
                    "app",
                    "category",
                    "api_type",
                    "auth_methods",
                    "access_model",
                    "existing_mcp",
                    "primary_docs_url",
                    "evidence_urls",
                    "confidence",
                    "verification_status",
                )
            },
        }

    @composio.experimental.tool(slug="RESEARCH_OFFICIAL_DOCS", preload=True)
    def research_official_docs(input: BrowserResearchInput, ctx) -> dict:
        """Run one bounded Browser Tool investigation using first-party documentation."""
        if input.slug in state["browser_runs"]:
            return state["browser_runs"][input.slug]
        if state["browser_runs"]:
            raise RuntimeError("this scoped agent permits only one Browser Tool task")
        record, app_meta = _current_record(input.slug)
        start_url = record.get("primary_docs_url") or app_meta.get("hint_url") or None
        arguments = {"task": _browser_task_prompt(record, app_meta)}
        if start_url:
            arguments["startUrl"] = start_url
        created = _unwrap_session_response(
            ctx.execute(BROWSER_CREATE, arguments), "Browser Tool create task"
        )
        task_id = created.get("watch_task_id") or created.get("task_id")
        if not isinstance(task_id, str) or not task_id:
            raise RuntimeError("Browser Tool create task returned no watch task id")

        deadline = time.monotonic() + timeout
        last_step = 0
        while time.monotonic() < deadline:
            watched = _unwrap_session_response(
                ctx.execute(
                    BROWSER_WATCH,
                    {"taskId": task_id, "lastStepSeen": last_step},
                ),
                "Browser Tool watch task",
            )
            status = str(watched.get("status") or "").lower()
            if not status:
                raise RuntimeError("Browser Tool watch task returned no status")
            steps = watched.get("steps") or []
            if isinstance(steps, list):
                last_step = max(
                    [last_step]
                    + [
                        int(step.get("step", step.get("step_number", 0)) or 0)
                        for step in steps
                        if isinstance(step, dict)
                    ]
                )
            current_step = watched.get("current_step")
            if isinstance(current_step, int):
                last_step = max(last_step, current_step)
            if status == "finished":
                verdict = _extract_browser_verdict(watched.get("output"))
                if verdict.get("slug") != input.slug:
                    raise ValueError("browser verdict slug does not match the requested app")
                result = {
                    "task_id": task_id,
                    "browser_session_id": created.get("browser_session_id"),
                    "status": status,
                    "steps_observed": last_step,
                    "verdict": verdict,
                }
                state["browser_runs"][input.slug] = result
                return result
            if status in {"failed", "stopped"}:
                detail = watched.get("output") or watched.get("message") or "no detail"
                raise RuntimeError(f"Browser Tool task {status}: {detail}")
            if status not in {"started", "running", "queued"}:
                raise RuntimeError(f"Browser Tool returned unknown status {status!r}")
            if poll_interval:
                time.sleep(poll_interval)
        raise TimeoutError(f"Browser Tool task exceeded {timeout:g} seconds")

    @composio.experimental.tool(slug="COMPARE_RESEARCH_VERDICT", preload=True)
    def compare_research_verdict(input: CompareResearchInput, ctx) -> dict:
        """Canonicalize and compare a browser verdict with the verified record."""
        del ctx
        browser_run = state["browser_runs"].get(input.slug)
        if not browser_run:
            raise RuntimeError("official-doc research must run before comparison")
        cached = CompareVerdictInput.model_validate(browser_run["verdict"]).model_dump(
            mode="json"
        )
        comparison = compare_verdict(cached)
        state["comparison"] = comparison
        return comparison

    return [get_research_target, research_official_docs, compare_research_verdict], state


def _tool_payload(result) -> dict:
    payload = _as_dict(result)
    if payload.get("error"):
        return {"successful": False, "error": payload["error"], "data": payload.get("data")}
    return {
        "successful": bool(payload.get("successful", True)),
        "data": payload.get("data", payload),
    }


def _function_arguments(function_call) -> dict:
    value = getattr(function_call, "args", None) or {}
    if isinstance(value, str):
        value = json.loads(value)
    if hasattr(value, "items"):
        value = {
            str(key): _function_argument_value(item)
            for key, item in value.items()
        }
    if not isinstance(value, dict):
        raise ValueError("Gemini tool arguments must be an object")
    return value


def _function_argument_value(value):
    if hasattr(value, "items"):
        return {
            str(key): _function_argument_value(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_function_argument_value(item) for item in value]
    return value


def _without_schema_examples(value):
    """Remove examples recursively; Gemini's function schema rejects that keyword."""
    if isinstance(value, dict):
        return {
            key: _without_schema_examples(item)
            for key, item in value.items()
            if key != "examples"
        }
    if isinstance(value, list):
        return [_without_schema_examples(item) for item in value]
    return value


def _native_google_provider():
    """Adapt Composio's executor to native google-genai function declarations."""
    from composio_google import GoogleProvider
    from google.genai import types

    class NativeGoogleProvider(GoogleProvider, name="google-native"):
        def wrap_tool(self, tool):
            schema = _without_schema_examples(tool.input_parameters)
            return types.FunctionDeclaration(
                name=tool.slug,
                description=tool.description,
                parameters_json_schema=schema,
            )

    return NativeGoogleProvider()


def run(
    slug: str,
    *,
    model: str | None = None,
    composio_client=None,
    google_client=None,
    max_rounds: int = MAX_TOOL_ROUNDS,
    poll_interval: float = POLL_INTERVAL_SECONDS,
    timeout: float = BROWSER_TIMEOUT_SECONDS,
) -> dict:
    """Run a bounded Session agent and return diagnostic evidence only."""
    if max_rounds < 1:
        raise ValueError("max_rounds must be at least 1")
    _current_record(slug)
    if composio_client is None and not config.COMPOSIO_API_KEY:
        raise RuntimeError("COMPOSIO_API_KEY is not set")

    from composio import Composio
    from google.genai import types

    provider = _native_google_provider()
    composio = composio_client or Composio(
        api_key=config.COMPOSIO_API_KEY,
        provider=provider,
    )
    custom_tools, state = build_custom_tools(
        composio,
        poll_interval=poll_interval,
        timeout=timeout,
    )
    session = composio.create(
        user_id=USER_ID,
        toolkits=["browser_tool"],
        sandbox={"enable": False},
        experimental={"custom_tools": custom_tools},
    )
    selected_model = model or config.PRIMARY_MODEL
    client = google_client or config.get_client()
    wrapped_tools = session.tools()
    system_instruction = (
        "You are a read-only product-operations audit agent. Use the required tool "
        "with the exact requested app slug, never invent evidence, and never suggest "
        "that a diagnostic disagreement has already corrected the dataset."
    )

    def generation_config(required_tool: str | None):
        mode = (
            types.FunctionCallingConfigMode.ANY
            if required_tool
            else types.FunctionCallingConfigMode.NONE
        )
        function_config = types.FunctionCallingConfig(mode=mode)
        if required_tool:
            function_config.allowed_function_names = [required_tool]
        return types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0,
            max_output_tokens=4096,
            tools=[types.Tool(function_declarations=wrapped_tools)],
            tool_config=types.ToolConfig(function_calling_config=function_config),
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            thinking_config=types.ThinkingConfig(
                thinking_level=config.GOOGLE_THINKING_LEVEL
            ),
        )

    chat = client.chats.create(
        model=selected_model,
        config=generation_config(None),
    )
    prompt = (
        f"Audit {slug}. First call GET_RESEARCH_TARGET. Then call "
        "RESEARCH_OFFICIAL_DOCS exactly once. Then call COMPARE_RESEARCH_VERDICT for the "
        "same slug; that tool reads the cached browser verdict directly. End with a short "
        "factual summary of agreement or fields requiring human adjudication."
    )
    logical_sequence = [
        "GET_RESEARCH_TARGET",
        "RESEARCH_OFFICIAL_DOCS",
        "COMPARE_RESEARCH_VERDICT",
    ]
    registered_tools = session.custom_tools() if hasattr(session, "custom_tools") else []
    registered_by_logical = {
        str(tool.slug).removeprefix("LOCAL_"): str(tool.slug)
        for tool in registered_tools
    }
    sequence = [registered_by_logical.get(name, name) for name in logical_sequence]
    response = chat.send_message(prompt, config=generation_config(sequence[0]))
    trace: list[str] = []
    rounds = 0
    for index, expected_tool in enumerate(sequence):
        rounds += 1
        if rounds > max_rounds:
            raise RuntimeError(f"Gemini exceeded the {max_rounds}-round tool-call limit")
        function_calls = list(response.function_calls or [])
        if len(function_calls) != 1:
            raise RuntimeError(
                f"Gemini returned {len(function_calls)} calls; expected exactly one "
                f"{expected_tool} call"
            )
        function_call = function_calls[0]
        name = str(function_call.name or "")
        if name != expected_tool:
            raise RuntimeError(f"Gemini called {name or '<unnamed>'}; expected {expected_tool}")
        trace.append(name)
        print(f"[composio-agent] session={session.session_id} tool={name}")
        executed = session.execute(
            name,
            arguments=_function_arguments(function_call),
        )
        payload = _tool_payload(executed)
        if not payload.get("successful"):
            raise RuntimeError(f"{name} failed: {payload.get('error') or 'unknown error'}")
        part = types.Part.from_function_response(
            name=name,
            response=payload,
        )
        next_tool = sequence[index + 1] if index + 1 < len(sequence) else None
        response = chat.send_message([part], config=generation_config(next_tool))

    if state.get("comparison") is None:
        raise RuntimeError("agent stopped before producing the deterministic comparison")
    return {
        "slug": slug,
        "model": selected_model,
        "session_id": session.session_id,
        "tool_trace": trace,
        "comparison": state["comparison"],
        "agent_summary": (response.text or "").strip(),
        "read_only": True,
    }
