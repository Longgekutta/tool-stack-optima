#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_tournament_engine.py: Tests for empirical benchmark harness and Pareto optimization.
"""
import unittest
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.tournament_engine import (
    EmpiricalBenchmarkHarness,
    BenchmarkSpec,
    CandidateSolution,
    TelemetryMetrics
)


class TestBenchmarkEngine(unittest.TestCase):

    def test_multi_objective_evaluation(self):
        spec = BenchmarkSpec(
            spec_id="SPEC-WORKER-01",
            title="High-Concurrency Worker Benchmark",
            problem_domain="State relay and worker task scheduling",
            slas={"min_pass_rate": 1.0, "max_latency_ms": 200.0, "max_ram_mb": 50.0}
        )

        c1 = CandidateSolution(
            solution_id="go_worker",
            name="Go Single Binary Worker",
            language_stack=["Go"],
            model_source="Claude-3.7-Sonnet",
            archetype="tool",
            technical_description="Lightweight Goroutine multiplexing",
            metrics=TelemetryMetrics(test_pass_rate=1.0, latency_p99_ms=4.2, peak_ram_mb=12.5, token_cost=3200)
        )

        c2 = CandidateSolution(
            solution_id="java_spring",
            name="Java Spring Microservice",
            language_stack=["Java"],
            model_source="GPT-4o",
            archetype="svc",
            technical_description="Heavy JVM runtime with microservice scaffold",
            metrics=TelemetryMetrics(test_pass_rate=1.0, latency_p99_ms=120.0, peak_ram_mb=280.0, token_cost=8500)
        )

        c3 = CandidateSolution(
            solution_id="rust_py_core",
            name="Rust Core with Python Glue",
            language_stack=["Rust", "Python"],
            model_source="DeepSeek-V3",
            archetype="tool",
            technical_description="Native PyO3 binding",
            metrics=TelemetryMetrics(test_pass_rate=1.0, latency_p99_ms=1.8, peak_ram_mb=28.0, token_cost=5800)
        )

        spec.candidates = [c1, c2, c3]
        report = EmpiricalBenchmarkHarness.evaluate(spec, execute_live=False)

        # Java exceeds RAM SLA (280MB > 50MB) -> Disqualified
        java_cand = next(c for c in report.ranked_solutions if c.solution_id == "java_spring")
        self.assertTrue(java_cand.is_disqualified)

        # Go and Rust are qualified
        self.assertEqual(report.qualified_count, 2)
        self.assertIsNotNone(report.optimal_solution)
        self.assertFalse(report.optimal_solution.is_disqualified)

        # Markdown report rendering
        md = EmpiricalBenchmarkHarness.render_markdown_report(report)
        self.assertIn("实证基准评估报告", md)
        self.assertIn("最优推荐", md)
        self.assertIn("TOPSIS", md)

    def test_strict_pareto_dominance(self):
        spec = BenchmarkSpec(
            spec_id="SPEC-PARETO",
            title="Pareto Dominance Invariance",
            problem_domain="Mathematical check",
            slas={"min_pass_rate": 0.9, "max_latency_ms": 1000.0, "max_ram_mb": 1000.0}
        )

        cand_a = CandidateSolution(
            solution_id="cand_a",
            name="Solution A",
            language_stack=["Go"],
            model_source="ModelA",
            archetype="tool",
            technical_description="",
            metrics=TelemetryMetrics(test_pass_rate=1.0, latency_p99_ms=10.0, peak_ram_mb=20.0, token_cost=1000)
        )
        cand_b = CandidateSolution(
            solution_id="cand_b",
            name="Solution B",
            language_stack=["Python"],
            model_source="ModelB",
            archetype="tool",
            technical_description="",
            metrics=TelemetryMetrics(test_pass_rate=1.0, latency_p99_ms=50.0, peak_ram_mb=60.0, token_cost=3000)
        )

        spec.candidates = [cand_a, cand_b]
        report = EmpiricalBenchmarkHarness.evaluate(spec)

        self.assertEqual(report.optimal_solution.solution_id, "cand_a")
        self.assertIn(cand_a, report.pareto_frontier)
        self.assertNotIn(cand_b, report.pareto_frontier)

    def test_create_spec_from_repo_and_live_telemetry(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a real python repo with an actual python file
            p_core = Path(tmpdir) / "core"
            p_core.mkdir(parents=True)
            (p_core / "app.py").write_text("import os\nprint('live test ok')\n", encoding="utf-8")

            # 1. Derive benchmark spec from physical repo
            spec = EmpiricalBenchmarkHarness.create_spec_from_repo(tmpdir)
            self.assertEqual(len(spec.candidates), 3)
            self.assertIn("Python", spec.candidates[0].language_stack)

            # 2. Attach a real command and test live telemetry
            spec.candidates[0].benchmark_command = f'{sys.executable} -c "import time; time.sleep(0.01); print(\'done\')"'
            report = EmpiricalBenchmarkHarness.evaluate(spec, execute_live=True)
            
            # Live telemetry must record actual elapsed time > 0, real peak RAM > 1.0 MB, and pass rate 1.0
            self.assertGreater(spec.candidates[0].metrics.latency_p99_ms, 0.0)
            self.assertGreater(spec.candidates[0].metrics.peak_ram_mb, 1.0)
            self.assertEqual(spec.candidates[0].metrics.test_pass_rate, 1.0)
            self.assertIsNotNone(report.optimal_solution)


if __name__ == "__main__":
    unittest.main()
