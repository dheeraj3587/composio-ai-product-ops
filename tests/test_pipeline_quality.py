from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import config
import docs_research
import handcheck
import normalize
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


class EvidenceTests(unittest.TestCase):
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

        self.assertEqual(len(evidence["queries"]), 2)
        self.assertFalse(evidence["degraded"])
        self.assertEqual(set(evidence["supported_topics"]), {"api", "auth", "access"})
        self.assertIn(auth_url, evidence["fetched_urls"])
        self.assertIn(access_url, evidence["fetched_urls"])

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
                "text": "REST API using OAuth. A new developer can create a production app.",
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
            config, "llm_json", side_effect=[(invalid, ""), (base, "")]
        ) as llm:
            record, _ = synthesis.synthesize(
                {"app": "Acme", "slug": "acme", "category": "CRM", "hint_url": ""},
                evidence,
                {"composio_toolkit": "No"},
                write_log=False,
            )
        self.assertEqual(llm.call_count, 2)
        self.assertEqual(record.api_type, "REST")

    def test_invalid_nonempty_enum_never_silently_defaults(self):
        with self.assertRaisesRegex(ValueError, "invalid api_type"):
            synthesis._pick("REST/gRPC", synthesis._API_TYPE, "api_type")


class VerificationTests(unittest.TestCase):
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


class FreshRunTests(unittest.TestCase):
    def test_archive_clears_generated_state_but_preserves_report(self):
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
            archives = list((out / "archive").iterdir())
            self.assertEqual(len(archives), 1)
            self.assertTrue((archives[0] / "results.json").exists())
            self.assertTrue((archives[0] / "reasoning" / "acme.md").exists())


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


if __name__ == "__main__":
    unittest.main()
