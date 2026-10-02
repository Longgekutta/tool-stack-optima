#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_v2_evolutions.py: Tests for HotspotProfiler and DifferentialTester.
"""
import os
import sys
import unittest
import tempfile
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.code_profiler_flame import HotspotProfiler
from core.differential_tester import DifferentialTester


class TestV2Evolutions(unittest.TestCase):

    def test_hotspot_profiler_on_minimal_script(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            script = Path(tmpdir) / "work.py"
            script.write_text("""
def compute():
    total = 0
    for i in range(1000):
        total += i
    return total

if __name__ == '__main__':
    compute()
""", encoding="utf-8")

            res = HotspotProfiler.profile_target(
                tmpdir,
                custom_cmd=f'"{sys.executable}" work.py'
            )

            self.assertTrue(res["success"])
            self.assertGreater(res["total_calls"], 0)
            self.assertGreaterEqual(len(res["top_cumulative_hotspots"]), 1)
            markdown = HotspotProfiler.render_markdown(res)
            self.assertIn("高精热点剖析报告", markdown)

    def test_differential_tester_on_mock_bridge(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = Path(tmpdir) / "bridge_glue.py"
            bridge.write_text("""
def is_native_accelerated():
    return False

def execute_accelerated_task(payload: bytes) -> bytes:
    return payload
""", encoding="utf-8")

            res = DifferentialTester.run_differential_test(tmpdir, iterations=100)
            self.assertTrue(res["success"])
            self.assertEqual(res["iterations_tested"], 100)
            self.assertEqual(res["counterexamples_count"], 0)
            self.assertFalse(res["is_native_accelerated"])

            markdown = DifferentialTester.render_markdown(res)
            self.assertIn("通用双轨差分模糊测试与语义等价性报告", markdown)
            self.assertIn("PASS (完全一致)", markdown)

    def test_differential_tester_numeric_and_float_equivalence(self):
        # 验证数值计算与浮点精度等价性测试能力 (非单纯 bytes)
        def primary_math(x: float, n: int) -> float:
            return (x * 1.5) + (n * 2)

        def candidate_optimized_math(x: float, n: int) -> float:
            # 语义等价实现
            return 1.5 * x + 2.0 * n

        res = DifferentialTester.test_callable_equivalence(
            primary_math, candidate_optimized_math, iterations=100
        )
        self.assertTrue(res["success"])
        self.assertEqual(res["counterexamples_count"], 0)

    def test_differential_tester_dict_structured_equivalence(self):
        # 验证结构化 JSON/Dict 数据的自适应等价性测试
        def primary_transform(data: dict) -> dict:
            return {"k_count": len(data), "has_status": "status" in data}

        def candidate_transform(data: dict) -> dict:
            out = {}
            out["k_count"] = len(data)
            out["has_status"] = ("status" in data)
            return out

        res = DifferentialTester.test_callable_equivalence(
            primary_transform, candidate_transform, iterations=50
        )
        self.assertTrue(res["success"])
        self.assertEqual(res["counterexamples_count"], 0)

    def test_differential_tester_detects_mismatch_and_counterexample(self):
        # 验证当候选实现存在微小边界缺陷时，能精准抓出反例
        def primary_abs(x: int) -> int:
            return abs(x)

        def buggy_candidate_abs(x: int) -> int:
            # 存在偶发 bug 的实现: 当 x 为特定值时出错
            if x == 42:
                return -42
            return abs(x)

        res = DifferentialTester.test_callable_equivalence(
            primary_abs, buggy_candidate_abs, iterations=50
        )
        self.assertFalse(res["success"])
        self.assertGreater(res["counterexamples_count"], 0)
        self.assertEqual(res["counterexamples"][0]["actual"], "-42")


if __name__ == "__main__":
    unittest.main()
