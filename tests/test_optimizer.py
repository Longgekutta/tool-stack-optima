#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_optimizer.py: 架构多语言求解与帕累托前沿推演测试
"""

import unittest
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.optimizer import PolyglotArchitectureOptimizer


class TestOptimizer(unittest.TestCase):
    """测试多语言架构求解器"""

    def test_vector_search_solution_assigns_rust_core(self):
        prompt = "做一个高性能本地向量检索库与服务"
        res = PolyglotArchitectureOptimizer.optimize(prompt)
        layers = res["architecture_blueprint"]["layers"]
        self.assertEqual(len(layers), 4)
        t1 = layers[0]
        self.assertEqual(t1["lang_key"], "RUST", "高性能向量计算内核应当推选 Rust")
        self.assertGreaterEqual(res["optimality_score"], 80)

    def test_crawler_monitor_solution_assigns_go_network_and_ts_ui(self):
        prompt = "做一个高并发全网社交媒体抓取与可视化监控大盘"
        res = PolyglotArchitectureOptimizer.optimize(prompt)
        layers = res["architecture_blueprint"]["layers"]
        t2 = layers[1]
        t4 = layers[3]
        self.assertEqual(t2["lang_key"], "GO", "高并发抓取服务应当推选 Go")
        self.assertEqual(t4["lang_key"], "TYPESCRIPT", "可视化监控大盘应当推选 TypeScript")

    def test_hft_hardware_solution_assigns_cpp_or_rust(self):
        prompt = "做一个基于 CUDA 与低延迟高频套利撮合系统"
        res = PolyglotArchitectureOptimizer.optimize(prompt)
        layers = res["architecture_blueprint"]["layers"]
        t1 = layers[0]
        self.assertIn(t1["lang_key"], ("CPP", "RUST"))

    def test_resource_forecast_bounds(self):
        prompt = "轻量级系统运维工具"
        res = PolyglotArchitectureOptimizer.optimize(prompt)
        rf = res["architecture_blueprint"]["resource_forecast"]
        self.assertGreater(rf["peak_compile_ram_mb"], 0)
        self.assertGreater(rf["estimated_runtime_ram_mb"], 0)


if __name__ == "__main__":
    unittest.main()
