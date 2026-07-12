from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from composio import Composio

import composio_agent
import composio_lookup
import config
import verify


class NotFoundError(Exception):
    status_code = 404


def toolkit(
    slug: str,
    name: str,
    *,
    tools: int,
    triggers: int = 0,
) -> SimpleNamespace:
    return SimpleNamespace(
        slug=slug,
        name=name,
        auth_config_details=[SimpleNamespace(mode=SimpleNamespace(value="OAUTH2"))],
        composio_managed_auth_schemes=[SimpleNamespace(value="OAUTH2")],
        meta=SimpleNamespace(
            tools_count=tools,
            triggers_count=triggers,
            available_versions=["20260601", "20260701"],
            categories=[SimpleNamespace(name="CRM")],
            version="20260701",
        ),
    )


class FakeToolkits:
    def __init__(self, entries: dict[str, object]):
        self.entries = entries

    def get(self, slug: str):
        if slug not in self.entries:
            raise NotFoundError(slug)
        value = self.entries[slug]
        if isinstance(value, Exception):
            raise value
        return value


class FakeSdkClient:
    def __init__(self, entries: dict[str, object]):
        self.toolkits = FakeToolkits(entries)


class CoverageAuditTests(unittest.TestCase):
    def setUp(self):
        self.apps = [
            {"app": "Alpha", "slug": "alpha"},
            {"app": "Front", "slug": "front"},
            {"app": "Absent App", "slug": "absent-app"},
        ]

    def test_classifies_and_aggregates_sdk_depth(self):
        client = FakeSdkClient({
            "alpha": toolkit("alpha", "Alpha", tools=12, triggers=2),
            "front": toolkit("front", "Front", tools=0),
        })

        payload = composio_lookup.audit_catalog(self.apps, workers=2, client=client)

        self.assertEqual(payload["apps"]["alpha"]["status"], "Active")
        self.assertEqual(payload["apps"]["front"]["status"], "Catalog-only")
        self.assertEqual(payload["apps"]["absent-app"]["status"], "Missing")
        self.assertEqual(payload["apps"]["alpha"]["auth_schemes"], ["OAUTH2"])
        self.assertEqual(payload["apps"]["alpha"]["versions_count"], 2)
        self.assertEqual(payload["summary"], {
            "n_apps": 3,
            "active": 1,
            "catalog_only": 1,
            "missing": 1,
            "tools_total": 12,
            "tools_median": 6.0,
            "trigger_enabled": 1,
            "without_triggers": 1,
        })

    def test_rejects_unrelated_identity_match(self):
        client = FakeSdkClient({
            "alpha": toolkit("different", "Different Product", tools=3),
        })
        with self.assertRaisesRegex(RuntimeError, "unrelated toolkit"):
            composio_lookup.audit_catalog([self.apps[0]], client=client)

    def test_missing_trigger_count_is_an_incomplete_sdk_response(self):
        incomplete = toolkit("alpha", "Alpha", tools=3)
        del incomplete.meta.triggers_count
        client = FakeSdkClient({"alpha": incomplete})
        with self.assertRaisesRegex(RuntimeError, "missing triggers_count"):
            composio_lookup.audit_catalog([self.apps[0]], client=client)

    def test_non_404_sdk_error_fails_closed_and_preserves_prior_file(self):
        class ServiceError(Exception):
            status_code = 503

        client = FakeSdkClient({"alpha": ServiceError("service unavailable")})
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "composio_coverage.json"
            path.write_text('{"prior": true}\n', encoding="utf-8")
            before = path.read_bytes()
            with mock.patch.object(config, "COMPOSIO_COVERAGE_PATH", path):
                with self.assertRaisesRegex(RuntimeError, "prior snapshot was preserved"):
                    composio_lookup.write_catalog_audit([self.apps[0]], client=client)
            self.assertEqual(path.read_bytes(), before)

    def test_metrics_namespace_is_derived_from_coverage_sidecar(self):
        current_record = json.loads(config.RESULTS_PATH.read_text(encoding="utf-8"))[0]
        summary = {
            "n_apps": 1,
            "active": 1,
            "catalog_only": 0,
            "missing": 0,
            "tools_total": 4,
            "tools_median": 4.0,
            "trigger_enabled": 1,
            "without_triggers": 0,
        }
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            results = root / "results.json"
            metrics = root / "metrics.json"
            coverage = root / "composio_coverage.json"
            results.write_text(json.dumps([current_record]), encoding="utf-8")
            metrics.write_text("{}", encoding="utf-8")
            coverage.write_text(json.dumps({"summary": summary}), encoding="utf-8")
            with (
                mock.patch.object(config, "OUT_DIR", root),
                mock.patch.object(config, "RESULTS_PATH", results),
                mock.patch.object(config, "METRICS_PATH", metrics),
                mock.patch.object(config, "COMPOSIO_COVERAGE_PATH", coverage),
                mock.patch.object(config, "FAILURE_STATE_PATH", root / "failures.json"),
                mock.patch.object(config, "BATCH_STATE_PATH", root / "batch_state.json"),
                mock.patch.object(config, "BROWSER_EVIDENCE_PATH", root / "browser_evidence.json"),
            ):
                rebuilt = verify.rebuild_metrics()
            self.assertEqual(rebuilt["composio_sdk"], summary)


class FakeBrowserContext:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []

    def execute(self, slug, arguments):
        self.calls.append((slug, arguments))
        return next(self.responses)


class AgentToolTests(unittest.TestCase):
    @staticmethod
    def _tool(slug: str, *, poll_interval: float = 0, timeout: float = 5):
        composio = Composio(api_key="test")
        tools, state = composio_agent.build_custom_tools(
            composio,
            poll_interval=poll_interval,
            timeout=timeout,
        )
        return next(tool for tool in tools if tool.slug == slug), state

    def test_compare_canonicalizes_auth_and_reports_exact_agreement(self):
        result = composio_agent.compare_verdict({
            "slug": "otter-ai",
            "api_type": "REST",
            "auth_methods": ["API key", "OAuth 2.0"],
            "access_model": "Gated",
            "evidence_urls": [
                "https://help.otter.ai/hc/en-us/articles/36130822688279-Otter-ai-Public-API"
            ],
            "notes": "Official API documentation requires Enterprise enablement.",
        })
        self.assertEqual(result["disagreed_fields"], [])
        self.assertFalse(result["requires_human_adjudication"])
        self.assertEqual(result["browser"]["auth_methods"], ["API Key", "OAuth2"])

    def test_compare_rejects_third_party_evidence(self):
        with self.assertRaisesRegex(ValueError, "not first-party"):
            composio_agent.compare_verdict({
                "slug": "otter-ai",
                "api_type": "REST",
                "auth_methods": ["API Key"],
                "access_model": "Gated",
                "evidence_urls": ["https://example.com/otter-summary"],
                "notes": "Third-party summary.",
            })

    def test_six_line_browser_protocol_parses_without_json_escaping(self):
        verdict = composio_agent._extract_browser_verdict(
            "SLUG: otter-ai\n"
            "API_TYPE: REST\n"
            "AUTH_METHODS: API Key | OAuth2\n"
            "ACCESS_MODEL: Gated\n"
            "EVIDENCE_URLS: https://help.otter.ai/api | https://help.otter.ai/mcp\n"
            "NOTES: Enterprise access requires account-manager enablement."
        )
        self.assertEqual(verdict["auth_methods"], ["API Key", "OAuth2"])
        self.assertEqual(len(verdict["evidence_urls"]), 2)

    def test_native_google_provider_removes_nested_examples(self):
        provider = composio_agent._native_google_provider()
        wrapped = provider.wrap_tool(SimpleNamespace(
            slug="TEST_TOOL",
            description="Nested schema test",
            input_parameters={
                "type": "object",
                "properties": {
                    "tools": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "tool_slug": {"type": "string", "examples": ["ONE"]}
                            },
                        },
                    }
                },
            },
        ))
        schema = wrapped.parameters_json_schema
        self.assertNotIn("examples", json.dumps(schema))
        self.assertEqual(
            schema["properties"]["tools"]["items"]["properties"]["tool_slug"]["type"],
            "string",
        )

    def test_compare_tool_uses_cached_browser_verdict_directly(self):
        tool, state = self._tool("COMPARE_RESEARCH_VERDICT")
        verdict = {
            "slug": "otter-ai",
            "api_type": "REST",
            "auth_methods": ["API Key", "OAuth2"],
            "access_model": "Gated",
            "evidence_urls": [
                "https://help.otter.ai/hc/en-us/articles/36130822688279-Otter-ai-Public-API"
            ],
            "notes": "Official docs require Enterprise access.",
        }
        with self.assertRaisesRegex(RuntimeError, "research must run before comparison"):
            tool.execute(composio_agent.CompareResearchInput(slug="otter-ai"), None)

        state["browser_runs"]["otter-ai"] = {"verdict": verdict}
        comparison = tool.execute(
            composio_agent.CompareResearchInput(slug="otter-ai"), None
        )
        self.assertEqual(comparison["disagreed_fields"], [])

    def test_browser_tool_polls_to_finished_and_reuses_single_result(self):
        tool, state = self._tool("RESEARCH_OFFICIAL_DOCS")
        verdict = {
            "slug": "otter-ai",
            "api_type": "REST",
            "auth_methods": ["API Key", "OAuth2"],
            "access_model": "Gated",
            "evidence_urls": [
                "https://help.otter.ai/hc/en-us/articles/36130822688279-Otter-ai-Public-API"
            ],
            "notes": "Official docs require Enterprise access.",
        }
        ctx = FakeBrowserContext([
            SimpleNamespace(
                data={"watch_task_id": "task_1", "browser_session_id": "session_1"},
                error=None,
            ),
            SimpleNamespace(data={"status": "started", "current_step": 1}, error=None),
            SimpleNamespace(
                data={"status": "finished", "current_step": 2, "output": json.dumps(verdict)},
                error=None,
            ),
        ])

        first = tool.execute(composio_agent.BrowserResearchInput(slug="otter-ai"), ctx)
        second = tool.execute(composio_agent.BrowserResearchInput(slug="otter-ai"), ctx)

        self.assertEqual(first, second)
        self.assertEqual(first["verdict"], verdict)
        self.assertEqual(len(ctx.calls), 3)
        self.assertEqual(ctx.calls[0][0], composio_agent.BROWSER_CREATE)
        create_payload = json.dumps(ctx.calls[0][1])
        for secret in (config.COMPOSIO_API_KEY, config.GOOGLE_API_KEY):
            if secret:
                self.assertNotIn(secret, create_payload)
        self.assertIn("otter-ai", state["browser_runs"])

    def test_browser_tool_stops_on_failure(self):
        tool, _ = self._tool("RESEARCH_OFFICIAL_DOCS")
        ctx = FakeBrowserContext([
            SimpleNamespace(data={"watch_task_id": "task_1"}, error=None),
            SimpleNamespace(data={"status": "failed", "output": "navigation failed"}, error=None),
        ])
        with self.assertRaisesRegex(RuntimeError, "navigation failed"):
            tool.execute(composio_agent.BrowserResearchInput(slug="otter-ai"), ctx)

    def test_browser_tool_times_out(self):
        tool, _ = self._tool("RESEARCH_OFFICIAL_DOCS", timeout=1)
        ctx = FakeBrowserContext([
            SimpleNamespace(data={"watch_task_id": "task_1"}, error=None),
            SimpleNamespace(data={"status": "started"}, error=None),
        ])
        with mock.patch.object(composio_agent.time, "monotonic", side_effect=[0, 0, 2]):
            with self.assertRaisesRegex(TimeoutError, "exceeded 1 seconds"):
                tool.execute(composio_agent.BrowserResearchInput(slug="otter-ai"), ctx)

    def test_agent_round_limit_does_not_write_verified_results(self):
        before = hashlib.sha256(config.RESULTS_PATH.read_bytes()).hexdigest()

        class FakeResponse:
            function_calls = [SimpleNamespace(name="GET_RESEARCH_TARGET", args={})]
            text = ""

        class FakeChat:
            def send_message(self, message, config=None):
                del message, config
                return FakeResponse()

        class FakeGoogle:
            chats = SimpleNamespace(create=lambda **kwargs: FakeChat())

        class FakeSession:
            session_id = "session_test"

            @staticmethod
            def tools():
                return []

            @staticmethod
            def execute(slug, arguments=None):
                del slug, arguments
                return SimpleNamespace(data={}, error=None)

        class FakeComposio:
            experimental = Composio(api_key="test").experimental

            @staticmethod
            def create(**kwargs):
                del kwargs
                return FakeSession()

        with self.assertRaisesRegex(RuntimeError, "1-round tool-call limit"):
            composio_agent.run(
                "otter-ai",
                composio_client=FakeComposio(),
                google_client=FakeGoogle(),
                max_rounds=1,
            )
        after = hashlib.sha256(config.RESULTS_PATH.read_bytes()).hexdigest()
        self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
