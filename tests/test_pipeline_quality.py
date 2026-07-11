from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import config
import batch_pipeline
import docs_research
import handcheck
import normalize
import pipeline
import research
import synthesis
import verify


def valid_record(slug: str = "dealcloud") -> dict:
    return {
        "app": "DealCloud",
        "category": "CRM",
        "one_liner": "A documented CRM API.",
        "auth_methods": ["API Key", "OAuth2"],
        "access_model": {"kind": "Gated", "note": "Existing customer account required."},
        "api_type": "REST",
        "api_breadth": "Broad",
        "existing_mcp": "None",
        "composio_toolkit": "No",
        "buildability": "Hard",
        "main_blocker": "Existing customer access is required.",
        "recommended_next_action": "Partner-Gated",
        "evidence_urls": ["https://docs.example.com/api"],
        "confidence": 0.8,
        "verification_status": "Auto",
        "slug": slug,
        "primary_docs_url": "https://docs.example.com/api",
        "rate_limit_note": "Not documented.",
        "last_verified": "2026-07-10",
    }


class NormalizeTests(unittest.TestCase):
    def test_strict_mode_rejects_unknown_model_label(self):
        with self.assertRaisesRegex(ValueError, "unknown auth label"):
            normalize.normalize_auth_list(["magic workspace credential"], strict=True)

    def test_auth_accuracy_uses_exact_canonical_sets(self):
        self.assertTrue(normalize.auth_sets_equal(["OAuth 2.0"], ["OAuth2"]))
        self.assertFalse(
            normalize.auth_sets_equal(["OAuth2", "API Key"], ["OAuth2"])
        )
        self.assertTrue(
            normalize.auth_sets_overlap(["OAuth2", "API Key"], ["OAuth2"])
        )


class ProviderTests(unittest.TestCase):
    def test_google_cancellation_is_retryable(self):
        error = RuntimeError("cancelled")
        error.code = 499
        self.assertEqual(config._classify_error(error), "retry")

    def test_daily_google_quota_is_a_batch_stop(self):
        error = RuntimeError(
            "Quota exceeded: generate_requests_per_model_per_day; retry tomorrow"
        )
        error.code = 429
        self.assertEqual(config._classify_error(error), "quota")

    def test_batch_stops_after_hard_quota_without_starting_more_apps(self):
        apps = [
            {"app": "One", "slug": "one", "category": "Test"},
            {"app": "Two", "slug": "two", "category": "Test"},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            with (
                mock.patch.object(pipeline, "load_apps", return_value=apps),
                mock.patch.object(config, "RESULTS_PATH", Path(tmp) / "results.json"),
                mock.patch.object(
                    pipeline,
                    "research_app",
                    side_effect=config.ProviderQuotaExhausted("daily quota"),
                ) as research_app,
                mock.patch.object(docs_research, "_log_failure"),
            ):
                with self.assertRaises(config.ProviderQuotaExhausted):
                    pipeline.run_batch(workers=1, resume=False)
        self.assertEqual(research_app.call_count, 1)

    def test_batch_request_preserves_system_and_repair_turns(self):
        request = batch_pipeline._batch_request([
            {"role": "system", "content": "strict system"},
            {"role": "user", "content": "initial evidence"},
            {"role": "assistant", "content": "bad json"},
            {"role": "user", "content": "repair it"},
        ])
        self.assertEqual(
            request["config"]["system_instruction"]["parts"][0]["text"],
            "strict system",
        )
        self.assertEqual(
            [content["role"] for content in request["contents"]],
            ["user", "model", "user"],
        )
        self.assertIs(
            request["config"]["response_schema"], synthesis.SynthesisOutput
        )

    def test_repair_prompt_identifies_first_party_claim_sources(self):
        entry = {
            "app_meta": {
                "app": "Pinterest",
                "slug": "pinterest",
                "category": "Social",
                "hint_url": "https://developers.pinterest.com",
            },
            "evidence": {
                "fetched": [{
                    "url": "https://github.com/pinterest/api-quickstart/blob/main/nodejs/README.md",
                    "ok": True,
                    "support_tags": ["api", "auth", "access"],
                }],
                "mcp": {"fetched": []},
            },
            "composio_signal": {},
            "preseed": None,
        }
        sources = batch_pipeline._first_party_tagged_sources(entry)
        self.assertEqual(len(sources), 1)
        self.assertIn("supports: api, auth, access", sources[0])

    def test_paid_preflight_rejects_missing_key_before_a_run(self):
        with (
            mock.patch.object(config, "PERPLEXITY_API_KEY", ""),
            mock.patch.object(config, "GOOGLE_API_KEY", "present"),
            self.assertRaisesRegex(SystemExit, "PERPLEXITY_API_KEY"),
        ):
            research._preflight_paid_runtime(workers=1)

    def test_batch_rejects_unsafe_google_concurrency(self):
        with self.assertRaisesRegex(ValueError, "workers must be between"):
            research.pipeline.run_batch(workers=config.GOOGLE_MAX_WORKERS + 1)


class EvidenceTests(unittest.TestCase):
    def test_fetch_uses_advertised_markdown_variant_for_complete_docs(self):
        html_response = mock.Mock(
            status_code=200,
            text="<html><body>Add .md for the markdown version of any page.</body></html>",
        )
        markdown_response = mock.Mock(
            status_code=200,
            text=(
                "# Authentication\nAPI keys use HTTP Basic authentication. "
                "The API key is the username and the password is empty.\n" * 4
            ),
        )
        with mock.patch.object(
            docs_research.requests, "get", side_effect=[html_response, markdown_response]
        ) as get:
            fetched = docs_research.fetch("https://docs.acme.test/api/auth")

        self.assertTrue(fetched["ok"])
        self.assertEqual(fetched["content_url"], "https://docs.acme.test/api/auth.md")
        self.assertIn("HTTP Basic authentication", fetched["text"])
        self.assertEqual(get.call_count, 2)

    def test_auth_signals_preserve_specific_plural_credentials(self):
        signals = set(docs_research.auth_evidence_signals(
            "The API supports API keys, bearer API tokens, user PATs, and "
            "service-account key-pair authentication."
        ))
        self.assertTrue({
            "API Key", "Bearer Token", "Personal Access Token", "Service Account"
        } <= signals)

    def test_negated_api_key_is_not_treated_as_supported_auth(self):
        cases = [
            "OAuth client IDs are not an independent API-key method.",
            "A client API key is not accepted as the API credential.",
        ]
        for text in cases:
            with self.subTest(text=text):
                self.assertNotIn("API Key", docs_research.auth_evidence_signals(text))

    def test_access_tags_cover_real_credential_enablement_language(self):
        samples = [
            "Open your dashboard and activate API access for this scraper.",
            "Book a call or contact sales to receive production credentials.",
            "Enable API access through user group permissions or contact your admin.",
            "Generate an API key from Settings in your workspace.",
        ]
        for sample in samples:
            with self.subTest(sample=sample):
                self.assertIn("access", docs_research.support_tags(sample))

    def test_access_seed_is_reserved_before_guessed_doc_roots(self):
        urls = docs_research._candidate_urls(
            "https://dealcloud.com", [], app="DealCloud", slug="dealcloud"
        )
        self.assertIn("https://api.docs.dealcloud.com/docs/apikeys", urls)

    def test_known_paid_platform_reserves_official_pricing_evidence(self):
        urls = docs_research._candidate_urls(
            "https://docs.snowflake.com", [], app="Snowflake", slug="snowflake"
        )
        self.assertIn("https://www.snowflake.com/en/pricing-options/", urls)

    def test_cross_domain_official_docs_are_recognized(self):
        cases = [
            (
                "https://github.com/pinterest/api-quickstart/blob/main/nodejs/README.md",
                "https://developers.pinterest.com",
                "pinterest",
            ),
            ("https://apidocs.fan/", "https://fanbasis.com", "fanbasis"),
            (
                "https://docs.cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/set-up-notebooklm",
                "https://cloud.google.com/gemini",
                "notebooklm",
            ),
        ]
        for url, hint_url, slug in cases:
            with self.subTest(slug=slug):
                self.assertTrue(docs_research.is_first_party(url, hint_url, slug))

    def test_search_results_keep_reserved_fetch_slots(self):
        results = [
            {
                "title": "Acme API authentication",
                "url": f"https://docs.acme.test/api/authentication/{index}",
                "snippet": "OAuth production credentials",
            }
            for index in range(5)
        ]
        candidates = docs_research._candidate_urls(
            "https://acme.test", results, app="Acme", slug="acme"
        )
        search_urls = {result["url"] for result in results}
        self.assertLessEqual(len(candidates), docs_research.MAX_FETCH)
        self.assertGreaterEqual(len(search_urls & set(candidates)), 3)
        self.assertIn(results[0]["url"], candidates)

    def test_pricing_result_gets_a_reserved_fetch_slot(self):
        auth_results = [
            {
                "title": f"Acme API Authentication {index}",
                "url": f"https://docs.acme.test/auth/{index}",
                "snippet": "OAuth credentials and API keys",
            }
            for index in range(5)
        ]
        pricing = {
            "title": "Acme pricing and production API plans",
            "url": "https://acme.test/pricing",
            "snippet": "The API trial expires before paid production access.",
        }
        candidates = docs_research._candidate_urls(
            "https://acme.test", [*auth_results, pricing], app="Acme", slug="acme"
        )
        self.assertIn(pricing["url"], candidates)

    def test_key_generation_alone_is_not_production_access_evidence(self):
        item = {
            "url": "https://docs.acme.test/auth",
            "ok": True,
            "text": "Generate an API key from account settings.",
        }
        self.assertIn(
            "credential_enablement",
            docs_research.access_evidence_signals(item["text"], item["url"]),
        )
        self.assertFalse(docs_research.access_decision_ready([item]))

    def test_without_manual_approval_is_not_misread_as_a_gate(self):
        signals = docs_research.access_evidence_signals(
            "Generate production API credentials without manual approval."
        )
        self.assertIn("self_serve_production", signals)
        self.assertNotIn("manual_gate", signals)

    def test_free_developer_environment_is_not_assumed_to_be_production(self):
        signals = docs_research.access_evidence_signals(
            "The free Developer Edition includes API access for development and testing. "
            "Production requires a paid plan."
        )
        self.assertIn("nonproduction_only", signals)
        self.assertIn("commercial_gate", signals)
        self.assertNotIn("self_serve_production", signals)

    def test_zero_api_free_plan_is_not_misread_as_free_production(self):
        signals = docs_research.access_evidence_signals(
            "The free plan has zero API calls; production API access requires a paid plan."
        )
        self.assertIn("commercial_gate", signals)
        self.assertNotIn("free_api_account", signals)
        self.assertNotIn("self_serve_production", signals)

    def test_temporary_trial_plus_paid_monthly_pricing_is_gated(self):
        signals = docs_research.access_evidence_signals(
            "Start a 7-day free trial. Starter is $35 /month."
        )
        self.assertIn("nonproduction_only", signals)
        self.assertIn("commercial_gate", signals)

    def test_free_api_plan_plus_key_creation_is_decision_grade(self):
        items = [
            {
                "url": "https://acme.test/pricing",
                "ok": True,
                "text": "The free plan includes API access with 1,000 requests per month.",
            },
            {
                "url": "https://docs.acme.test/auth",
                "ok": True,
                "text": "Generate an API key from account settings.",
            },
        ]
        self.assertTrue(docs_research.access_decision_ready(items))

    def test_support_tags_require_claim_bearing_text(self):
        self.assertEqual(docs_research.support_tags("Welcome to our company"), [])
        tags = docs_research.support_tags(
            "Use OAuth credentials for the REST API. Production access needs app review."
        )
        self.assertEqual(set(tags), {"api", "auth", "access"})

    def test_gather_evidence_combines_auth_and_production_queries(self):
        auth_url = "https://docs.acme.test/api/authentication"
        access_url = "https://docs.acme.test/api/production-access"
        groups = [
            [{"title": "Authentication", "url": auth_url, "snippet": "OAuth API"}],
            [{"title": "Production access", "url": access_url, "snippet": "app review"}],
        ]

        def fake_fetch(url):
            text = {
                auth_url: "The REST API uses OAuth2 credentials.",
                access_url: "Production access requires business verification and app review.",
            }.get(url, "Acme product homepage")
            return {"url": url, "ok": True, "status": 200, "text": text, "error": ""}

        with (
            mock.patch.object(
                docs_research, "search_many", return_value=groups[0] + groups[1]
            ),
            mock.patch.object(docs_research, "fetch", side_effect=fake_fetch),
            mock.patch.object(docs_research, "gather_mcp_evidence", return_value={
                "query": "mcp", "search_results": [], "fetched": [], "fetched_urls": [],
            }),
            mock.patch.object(docs_research.time, "sleep"),
        ):
            evidence = docs_research.gather_evidence(
                "Acme", "acme", hint_url="https://acme.test", log=False
            )

        self.assertEqual(len(evidence["queries"]), 3)
        self.assertFalse(evidence["degraded"])
        self.assertEqual(set(evidence["supported_topics"]), {"api", "auth", "access"})
        self.assertIn("manual_gate", evidence["supported_access_signals"])
        self.assertIn(auth_url, evidence["fetched_urls"])
        self.assertIn(access_url, evidence["fetched_urls"])

    def test_gather_evidence_degrades_without_a_production_entitlement_source(self):
        auth_url = "https://docs.acme.test/api/authentication"

        def fake_fetch(url):
            text = (
                "The REST API uses OAuth2. Generate an API key from account settings."
                if url == auth_url
                else "Acme product homepage"
            )
            return {"url": url, "ok": True, "status": 200, "text": text, "error": ""}

        with (
            mock.patch.object(docs_research, "search_many", return_value=[{
                "title": "Authentication",
                "url": auth_url,
                "snippet": "OAuth API key",
            }]),
            mock.patch.object(docs_research, "fetch", side_effect=fake_fetch),
            mock.patch.object(docs_research, "gather_mcp_evidence", return_value={
                "query": "mcp", "search_results": [], "fetched": [], "fetched_urls": [],
            }),
            mock.patch.object(docs_research.time, "sleep"),
        ):
            evidence = docs_research.gather_evidence(
                "Acme", "acme", hint_url="https://acme.test", log=False
            )

        self.assertTrue(evidence["degraded"])
        self.assertFalse(evidence["access_decision_ready"])

    def test_recovered_failure_leaves_history_but_not_unresolved_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            out = root / "out"
            reasoning = out / "reasoning"
            cache = out / "cache"
            handcheck_dir = root / "handcheck"
            patches = [
                mock.patch.object(config, "OUT_DIR", out),
                mock.patch.object(config, "REASONING_DIR", reasoning),
                mock.patch.object(config, "CACHE_DIR", cache),
                mock.patch.object(config, "HANDCHECK_DIR", handcheck_dir),
                mock.patch.object(config, "FAILURES_PATH", out / "failures.log"),
                mock.patch.object(config, "FAILURE_STATE_PATH", out / "failures.json"),
            ]
            for patcher in patches:
                patcher.start()
            try:
                docs_research._log_failure("acme", "timeout", phase="pipeline")
                docs_research.resolve_failure("acme", "pipeline")
                state = config.load_json(config.FAILURE_STATE_PATH)
                history = config.FAILURES_PATH.read_text(encoding="utf-8")
            finally:
                for patcher in reversed(patches):
                    patcher.stop()
        self.assertEqual(state, {})
        self.assertIn("FAILED\tpipeline\tacme\ttimeout", history)
        self.assertIn("RESOLVED\tpipeline\tacme", history)


class SynthesisTests(unittest.TestCase):
    @staticmethod
    def _evidence(text: str, url: str = "https://docs.acme.com/api") -> dict:
        return {
            "fetched": [{
                "url": url,
                "ok": True,
                "text": text,
                "support_tags": docs_research.support_tags(text, url),
            }],
            "mcp": {"fetched": []},
        }

    def test_preseed_hypothesis_is_withheld_from_model_prompt(self):
        evidence = {
            "app": "Acme",
            "category": "CRM",
            "query": "q",
            "queries": ["q"],
            "fetched_urls": [],
            "fetched": [],
            "search_results": [],
            "mcp": {"search_results": [], "fetched": []},
        }
        messages = synthesis.build_messages(
            evidence,
            {"composio_toolkit": "No"},
            preseed={"hypothesis": {"secret_stale_guess": "Self-Serve"}},
        )
        self.assertNotIn("secret_stale_guess", messages[1]["content"])
        self.assertIn("withheld", messages[1]["content"])

    def test_third_party_only_evidence_caps_confidence(self):
        record = {
            "evidence_urls": ["https://catalog.example/acme-api"],
            "confidence": 0.9,
            "existing_mcp": "None",
        }
        evidence = {
            "fetched": [{
                "url": "https://catalog.example/acme-api",
                "ok": True,
                "text": "Acme API authentication and production access",
                "support_tags": ["api", "auth", "access"],
            }],
            "mcp": {"fetched": []},
        }
        app = {
            "app": "Acme",
            "slug": "acme",
            "hint_url": "https://acme.com",
        }
        with self.assertRaisesRegex(ValueError, "third-party-only"):
            synthesis._validate_source_quality(record, evidence, app)

    def test_official_mcp_requires_first_party_mcp_page(self):
        record = {
            "evidence_urls": [
                "https://docs.acme.com/api",
                "https://catalog.example/acme-mcp",
            ],
            "confidence": 0.5,
            "existing_mcp": "Official",
        }
        evidence = {
            "fetched": [{
                "url": "https://docs.acme.com/api",
                "ok": True,
                "text": "Acme API authentication and production access",
                "support_tags": ["api", "auth", "access"],
            }],
            "mcp": {"fetched": [{
                "url": "https://catalog.example/acme-mcp",
                "ok": True,
                "text": "Acme MCP server",
                "support_tags": ["mcp"],
            }]},
        }
        app = {
            "app": "Acme",
            "slug": "acme",
            "hint_url": "https://acme.com",
        }
        with self.assertRaisesRegex(ValueError, "first-party MCP"):
            synthesis._validate_source_quality(record, evidence, app)

    def test_first_party_homepage_cannot_launder_third_party_api_claims(self):
        record = {
            "evidence_urls": [
                "https://acme.com",
                "https://catalog.example/acme-api",
            ],
            "confidence": 0.9,
            "existing_mcp": "None",
            "api_type": "REST",
        }
        evidence = {
            "fetched": [
                {
                    "url": "https://acme.com",
                    "ok": True,
                    "text": "Create an Acme account.",
                    "support_tags": ["access"],
                },
                {
                    "url": "https://catalog.example/acme-api",
                    "ok": True,
                    "text": "Acme REST API uses OAuth.",
                    "support_tags": ["api", "auth"],
                },
            ],
            "mcp": {"fetched": []},
        }
        app = {
            "app": "Acme",
            "slug": "acme",
            "hint_url": "https://acme.com",
        }
        with self.assertRaisesRegex(ValueError, "first-party coverage"):
            synthesis._validate_source_quality(record, evidence, app)

    def test_specific_token_is_not_duplicated_as_bearer(self):
        record = valid_record()
        record["auth_methods"] = ["Personal Access Token", "Bearer Token"]
        with self.assertRaisesRegex(ValueError, "must not also be labeled Bearer"):
            synthesis._validate_semantics(record)

    def test_oauth_client_id_does_not_ground_an_api_key_label(self):
        record = valid_record()
        record["evidence_urls"] = ["https://docs.acme.com/api"]
        evidence = self._evidence(
            "The REST API uses OAuth 2.0. Register a client ID and client secret."
        )
        with self.assertRaisesRegex(ValueError, "API Key"):
            synthesis._validate_auth_grounding(record, evidence)

    def test_personal_access_token_must_not_be_generic_bearer(self):
        record = valid_record()
        record["auth_methods"] = ["Bearer Token"]
        record["evidence_urls"] = ["https://docs.acme.com/api"]
        evidence = self._evidence(
            "Authenticate API requests with a personal access token."
        )
        with self.assertRaisesRegex(ValueError, "specific canonical label"):
            synthesis._validate_auth_grounding(record, evidence)

    def test_key_pair_must_not_be_other_token(self):
        record = valid_record()
        record["auth_methods"] = ["OAuth2", "Other Token"]
        record["evidence_urls"] = ["https://docs.acme.com/api"]
        evidence = self._evidence(
            "The REST API supports OAuth 2.0 and key-pair authentication."
        )
        with self.assertRaisesRegex(ValueError, "Service Account"):
            synthesis._validate_auth_grounding(record, evidence)

    def test_oauth1_requires_other_token_alongside_oauth2(self):
        record = valid_record()
        record["auth_methods"] = ["OAuth2"]
        record["evidence_urls"] = ["https://docs.acme.com/api"]
        evidence = self._evidence(
            "The API supports OAuth 1.0a for legacy integrations and OAuth 2.0 for cloud apps."
        )
        with self.assertRaisesRegex(ValueError, "represent it as Other Token"):
            synthesis._validate_auth_grounding(record, evidence)

    def test_explicit_api_key_basic_flow_requires_basic_auth(self):
        record = valid_record()
        record["auth_methods"] = ["API Key", "OAuth2"]
        record["evidence_urls"] = ["https://docs.acme.com/api-key-authentication"]
        evidence = self._evidence(
            "Use your API key as the username with HTTP Basic authentication. "
            "OAuth 2.0 is also supported.",
            url="https://docs.acme.com/api-key-authentication",
        )
        with self.assertRaisesRegex(ValueError, "include Basic Auth"):
            synthesis._validate_auth_grounding(record, evidence)

    def test_basic_transport_explicitly_marked_non_independent_is_not_required(self):
        item = {
            "url": "https://docs.acme.com/auth",
            "text": (
                "The API token is sent through Basic transport. Basic transport is not "
                "an independent credential."
            ),
        }
        self.assertFalse(synthesis._explicit_basic_for_api_requests(item))

    def test_self_serve_rejects_trial_only_production_access(self):
        record = valid_record()
        record["access_model"] = {
            "kind": "Self-Serve",
            "note": "Generate credentials during a free trial; a paid plan is required after the trial.",
        }
        record["recommended_next_action"] = "Build Now"
        record["buildability"] = "Moderate"
        with self.assertRaisesRegex(ValueError, "contradicts"):
            synthesis._validate_semantics(record)

    def test_free_production_plan_can_ground_self_serve_access(self):
        record = valid_record()
        record["access_model"] = {
            "kind": "Self-Serve",
            "note": "The free plan includes production API access and keys are generated in settings.",
        }
        record["evidence_urls"] = ["https://docs.acme.com/plans"]
        evidence = self._evidence(
            "The free plan includes production API access. Generate an API key in settings.",
            url="https://docs.acme.com/plans",
        )
        synthesis._validate_access_grounding(record, evidence)

    def test_long_one_liner_never_exceeds_schema_limit(self):
        clipped = synthesis._clip120("word " * 40)
        self.assertLessEqual(len(clipped), 120)
        self.assertTrue(clipped.endswith("..."))

    def test_marketing_homepage_cannot_support_api_auth_and_access_claims(self):
        record = valid_record()
        evidence = {
            "fetched": [{
                "url": record["evidence_urls"][0],
                "ok": True,
                "support_tags": [],
            }],
            "mcp": {"fetched": []},
        }
        with self.assertRaisesRegex(ValueError, "missing topics"):
            synthesis._validate_citations(record, evidence)

    def test_invalid_enum_gets_one_repair_instead_of_defaulting(self):
        evidence_url = "https://docs.acme.test/api/authentication"
        evidence = {
            "app": "Acme",
            "slug": "acme",
            "category": "CRM",
            "query": "Acme API auth",
            "queries": ["Acme API auth", "Acme production access"],
            "search_results": [],
            "fetched": [{
                "url": evidence_url,
                "ok": True,
                "status": 200,
                "text": "REST API using OAuth. A new developer can generate production OAuth credentials from the dashboard without approval.",
                "support_tags": ["api", "auth", "access"],
                "source_kind": "search_result",
                "relevance_score": 40,
            }],
            "fetched_urls": [evidence_url],
            "degraded": False,
            "evidence_quality": "adequate",
            "mcp": {"search_results": [], "fetched": []},
        }
        base = {
            "one_liner": "Acme exposes a documented API for CRM records.",
            "auth_methods": ["OAuth2"],
            "access_model": {
                "kind": "Self-Serve",
                "note": "A new developer can register a production app without approval.",
            },
            "api_type": "REST",
            "api_breadth": "Broad",
            "existing_mcp": "None",
            "buildability": "Moderate",
            "main_blocker": "",
            "recommended_next_action": "Build Now",
            "rate_limit_note": "Not documented.",
            "evidence_urls": [evidence_url],
            "confidence": 0.82,
            "reasoning": "The fetched authentication page supports the decision.",
        }
        invalid = {**base, "api_type": "REST/gRPC"}
        with mock.patch.object(
            config,
            "llm_json",
            side_effect=[
                config.StructuredOutputError("truncated"),
                (invalid, ""),
                (base, ""),
            ],
        ) as llm:
            record, _ = synthesis.synthesize(
                {
                    "app": "Acme",
                    "slug": "acme",
                    "category": "CRM",
                    "hint_url": "https://acme.test",
                },
                evidence,
                {"composio_toolkit": "No"},
                write_log=False,
            )
        self.assertEqual(llm.call_count, 3)
        self.assertEqual(llm.call_args_list[1].kwargs["thinking_level"], "low")
        self.assertEqual(record.api_type, "REST")

    def test_invalid_nonempty_enum_never_silently_defaults(self):
        with self.assertRaisesRegex(ValueError, "invalid api_type"):
            synthesis._pick("REST/gRPC", synthesis._API_TYPE, "api_type")


class VerificationTests(unittest.TestCase):
    def test_blind_verification_searches_pricing_and_production_access(self):
        queries = verify._blind_queries("Acme")
        self.assertEqual(len(queries), 3)
        self.assertTrue(any("pricing" in query for query in queries))

    def test_url_identity_blocks_fragment_and_trailing_slash_reuse(self):
        stored = "https://Docs.Example.com/auth/?utm_source=test#oauth"
        rediscovered = "https://docs.example.com/auth"
        self.assertEqual(verify._url_identity(stored), verify._url_identity(rediscovered))

    def test_blind_verification_does_not_mutate_results(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            results_path = root / "results.json"
            metrics_path = root / "metrics.json"
            record = valid_record()
            results_path.write_text(json.dumps([record], indent=2), encoding="utf-8")
            before = results_path.read_bytes()
            derived = {
                "verdict": {
                    "auth_methods": ["OAuth2"],
                    "access_model": {"kind": "Gated", "note": "Approval is required."},
                },
                "queries": ["q1", "q2"],
                "used_urls": ["https://official.example/auth"],
                "model": "provider:capable-model",
                "source_independence": {
                    "no_exact_url_reused": True,
                    "same_host_as_pass_1": False,
                    "excluded_url_count": 1,
                },
            }
            with (
                mock.patch.object(config, "RESULTS_PATH", results_path),
                mock.patch.object(config, "METRICS_PATH", metrics_path),
                mock.patch.object(config, "OUT_DIR", root),
                mock.patch.object(verify.pipeline, "load_preseed_map", return_value={}),
                mock.patch.object(verify, "_rederive", return_value=derived),
                mock.patch.object(verify, "rebuild_metrics", return_value={}),
                mock.patch("builtins.print"),
            ):
                output = verify.run_verification(sample_size=1)

            self.assertEqual(results_path.read_bytes(), before)
            self.assertEqual(output["auth_methods_exact_agreement_rate"], 0.0)
            self.assertEqual(output["auth_methods_overlap_rate"], 1.0)
            self.assertEqual(output["checks"][0]["used_urls"], derived["used_urls"])
            self.assertIn("does not mutate", output["confidence_policy"])

    def test_browser_auth_only_difference_is_a_disagreement_not_correction(self):
        rows = [{
            "slug": "acme",
            "first_pass": {
                "api_type": "REST",
                "auth_methods": ["OAuth2", "API Key"],
                "access_model": "Self-Serve",
            },
            "browser": {
                "api_type": "REST",
                "auth_methods": ["OAuth2"],
                "access_model": "Self-Serve",
            },
        }]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "browser_verification.json").write_text(json.dumps(rows), encoding="utf-8")
            with mock.patch.object(config, "OUT_DIR", root):
                summary = verify._browser_use_summary()
        self.assertEqual(summary["n_disagreements"], 1)
        self.assertEqual(summary["field_disagreements"], {"auth_methods": 1})
        self.assertEqual(summary["n_corrections_found"], 0)

    def test_browser_sdk_task_view_output_is_unwrapped(self):
        import browser_verify

        class TaskView:
            output = '{"verdicts":[{"slug":"acme"}]}'

            def model_dump(self):
                return {"output": self.output, "status": "finished"}

        self.assertEqual(
            browser_verify._to_dict(TaskView()),
            {"verdicts": [{"slug": "acme"}]},
        )

    def test_metrics_rebuild_preserves_completed_audit_without_ignored_batch_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            results_path = root / "results.json"
            metrics_path = root / "metrics.json"
            results_path.write_text(json.dumps([valid_record()]), encoding="utf-8")
            metrics_path.write_text(json.dumps({
                "quality": {"source_audit_complete": True, "source_audited_rows": 1}
            }), encoding="utf-8")
            with (
                mock.patch.object(config, "RESULTS_PATH", results_path),
                mock.patch.object(config, "METRICS_PATH", metrics_path),
                mock.patch.object(config, "OUT_DIR", root),
                mock.patch.object(config, "BATCH_STATE_PATH", root / "batch_state.json"),
                mock.patch.object(config, "FAILURE_STATE_PATH", root / "failure_state.json"),
                mock.patch.object(config, "BROWSER_EVIDENCE_PATH", root / "browser_evidence.json"),
                mock.patch.object(verify.pipeline, "load_preseed_map", return_value={}),
            ):
                rebuilt = verify.rebuild_metrics()
        self.assertTrue(rebuilt["quality"]["source_audit_complete"])
        self.assertEqual(rebuilt["quality"]["source_audited_rows"], 1)


class FreshRunTests(unittest.TestCase):
    def test_build_report_bundles_reasoning_for_static_review(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            out = root / "out"
            report = root / "report"
            reasoning_dir = out / "reasoning"
            reasoning_dir.mkdir(parents=True)
            results_path = out / "results.json"
            metrics_path = out / "metrics.json"
            results_path.write_text(json.dumps([valid_record()]), encoding="utf-8")
            metrics_path.write_text(json.dumps({"generated": "2026-07-11"}), encoding="utf-8")
            (reasoning_dir / "dealcloud.md").write_text(
                "# DealCloud reasoning\n\n## Model reasoning\nOfficial docs support the decision.\n",
                encoding="utf-8",
            )

            with (
                mock.patch.object(config, "REPORT_DIR", report),
                mock.patch.object(config, "REASONING_DIR", reasoning_dir),
                mock.patch.object(config, "RESULTS_PATH", results_path),
                mock.patch.object(config, "METRICS_PATH", metrics_path),
                mock.patch("builtins.print"),
            ):
                research.cmd_build_report()

            bundled = json.loads((report / "data" / "reasoning.json").read_text(encoding="utf-8"))
            self.assertIn("Official docs support the decision.", bundled["dealcloud"])
            data_js = (report / "data.js").read_text(encoding="utf-8")
            self.assertIn("window.REASONING", data_js)
            self.assertIn("DealCloud reasoning", data_js)

    def test_archive_clears_generated_state_but_preserves_report_and_handcheck(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            out = root / "out"
            reasoning = out / "reasoning"
            cache = out / "cache"
            report = root / "report"
            handcheck_dir = root / "handcheck"
            for path in (reasoning, cache, report, handcheck_dir):
                path.mkdir(parents=True)
            paths = {
                "RESULTS_PATH": out / "results.json",
                "METRICS_PATH": out / "metrics.json",
                "FAILURES_PATH": out / "failures.log",
                "FAILURE_STATE_PATH": out / "failures.json",
                "USAGE_PATH": out / "usage.json",
                "BATCH_STATE_PATH": out / "batch_state.json",
                "HANDCHECK_PATH": handcheck_dir / "handcheck.json",
            }
            for path in paths.values():
                path.write_text("{}", encoding="utf-8")
            (out / "results_firstpass.json").write_text("[]", encoding="utf-8")
            (reasoning / "acme.md").write_text("trace", encoding="utf-8")
            report_file = report / "index.html"
            report_file.write_text("published", encoding="utf-8")

            patches = [
                mock.patch.object(config, "OUT_DIR", out),
                mock.patch.object(config, "REASONING_DIR", reasoning),
                mock.patch.object(config, "CACHE_DIR", cache),
                mock.patch.object(config, "HANDCHECK_DIR", handcheck_dir),
                *(mock.patch.object(config, name, path) for name, path in paths.items()),
            ]
            for patcher in patches:
                patcher.start()
            try:
                with mock.patch("builtins.print"):
                    research._archive_current_run()
            finally:
                for patcher in reversed(patches):
                    patcher.stop()

            self.assertEqual(report_file.read_text(encoding="utf-8"), "published")
            self.assertFalse(paths["RESULTS_PATH"].exists())
            self.assertTrue(paths["HANDCHECK_PATH"].exists())
            archives = list((out / "archive").iterdir())
            self.assertEqual(len(archives), 1)
            self.assertTrue((archives[0] / "results.json").exists())
            self.assertTrue((archives[0] / "batch_state.json").exists())
            self.assertTrue((archives[0] / "reasoning" / "acme.md").exists())
            self.assertTrue((archives[0] / "handcheck.json").exists())


class HandcheckTests(unittest.TestCase):
    def test_legacy_access_rubric_cannot_be_scored_as_current(self):
        with self.assertRaises(SystemExit):
            handcheck._require_current_rubric({"rows": []})

    def test_fold_scores_current_row_without_historical_substitution(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            results_path = root / "results.json"
            metrics_path = root / "metrics.json"
            handcheck_path = root / "handcheck.json"
            results_path.write_text(json.dumps([valid_record()]), encoding="utf-8")
            metrics_path.write_text(
                json.dumps({"handcheck": {"accuracy": 0.951, "n": 27}}), encoding="utf-8"
            )
            handcheck_path.write_text(json.dumps({
                "access_rubric": handcheck.ACCESS_RUBRIC,
                "rows": [{
                    "slug": "dealcloud",
                    "app": "DealCloud",
                    "filled": True,
                    "truth": {
                        "api_type": "REST",
                        "auth_methods": ["API Key", "Other Token"],
                        "access_model": "Gated",
                        "evidence_urls": ["https://docs.example.com/api"],
                        "notes": "Test truth intentionally differs from current auth.",
                    },
                }],
            }), encoding="utf-8")
            with (
                mock.patch.object(config, "RESULTS_PATH", results_path),
                mock.patch.object(config, "METRICS_PATH", metrics_path),
                mock.patch.object(config, "HANDCHECK_PATH", handcheck_path),
                mock.patch.object(handcheck.pipeline, "load_apps", return_value=[{"slug": "dealcloud"}]),
                mock.patch.object(handcheck.verify, "rebuild_metrics", return_value={}),
                mock.patch.object(handcheck.synthesis, "append_final_state"),
                mock.patch("builtins.print"),
            ):
                output = handcheck.fold()

            self.assertEqual(output["auth_accuracy"], 0.0)
            self.assertEqual(output["accuracy"], 0.667)
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            self.assertEqual(metrics["handcheck_historical"]["snapshot"]["accuracy"], 0.951)

    def test_apply_handcheck_revalidates_dependent_decision(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            results_path = root / "results.json"
            metrics_path = root / "metrics.json"
            handcheck_path = root / "handcheck.json"
            record = valid_record()
            record["access_model"] = {"kind": "Self-Serve", "note": "Test keys only."}
            record["buildability"] = "Easy"
            record["recommended_next_action"] = "Build Now"
            record["main_blocker"] = ""
            results_path.write_text(json.dumps([record]), encoding="utf-8")
            metrics_path.write_text("{}", encoding="utf-8")
            handcheck_path.write_text(json.dumps({
                "access_rubric": handcheck.ACCESS_RUBRIC,
                "rows": [{
                    "slug": "dealcloud",
                    "app": "DealCloud",
                    "filled": True,
                    "truth": {
                        "api_type": "REST",
                        "auth_methods": ["OAuth2"],
                        "access_model": "Gated",
                        "existing_mcp": "Official",
                        "evidence_urls": ["https://docs.example.com/api"],
                        "notes": "Production requires customer approval.",
                    },
                    "correction": {
                        "access_note": "Production requires an existing customer account.",
                        "buildability": "Hard",
                        "recommended_next_action": "Partner-Gated",
                        "main_blocker": "Existing customer account required.",
                    },
                }],
            }), encoding="utf-8")
            with (
                mock.patch.object(config, "RESULTS_PATH", results_path),
                mock.patch.object(config, "METRICS_PATH", metrics_path),
                mock.patch.object(config, "HANDCHECK_PATH", handcheck_path),
                mock.patch.object(
                    handcheck.pipeline, "load_apps", return_value=[{"slug": "dealcloud"}]
                ),
                mock.patch.object(handcheck.verify, "rebuild_metrics", return_value={}),
                mock.patch.object(handcheck.synthesis, "append_final_state"),
                mock.patch("builtins.print"),
            ):
                count = handcheck.apply_corrections()

            corrected = json.loads(results_path.read_text(encoding="utf-8"))[0]
            self.assertEqual(count, 1)
            self.assertEqual(corrected["auth_methods"], ["OAuth2"])
            self.assertEqual(corrected["access_model"]["kind"], "Gated")
            self.assertEqual(corrected["existing_mcp"], "Official")
            self.assertEqual(corrected["recommended_next_action"], "Partner-Gated")


if __name__ == "__main__":
    unittest.main()
