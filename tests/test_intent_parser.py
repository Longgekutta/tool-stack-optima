#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_intent_parser.py: 模糊意图解析与需求张量提取测试
"""

import unittest
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.intent_parser import FuzzyIntentParser


class TestIntentParser(unittest.TestCase):
    """测试模糊意图提取"""

    def test_vector_db_intent(self):
        prompt = "我想做一个高性能的本地向量检索库与列存索引"
        res = FuzzyIntentParser.parse_intent(prompt)
        self.assertEqual(res["primary_domain"], "VECTOR_SEARCH_STORAGE")
        self.assertGreaterEqual(res["demand_tensor"]["latency_sensitivity"], 4)

    def test_quant_hft_intent(self):
        prompt = "做一个低延迟加密货币高频量化交易订单流撮合系统"
        res = FuzzyIntentParser.parse_intent(prompt)
        self.assertEqual(res["primary_domain"], "QUANT_HIGH_FREQUENCY")
        self.assertGreaterEqual(res["demand_tensor"]["latency_sensitivity"], 5)

    def test_web_crawler_and_dashboard_intent(self):
        prompt = "做一个知乎自动监控抓取和后台Web大盘管理页面"
        res = FuzzyIntentParser.parse_intent(prompt)
        self.assertIn(res["primary_domain"], ("WEB_CRAWLER_MONITOR", "FULLSTACK_WEB_APP"))
        self.assertGreaterEqual(res["demand_tensor"]["gui_web_demand"], 4)

    def test_system_cli_intent(self):
        prompt = "做一个类似bt面板的轻量单文件运维CLI控制台"
        res = FuzzyIntentParser.parse_intent(prompt)
        self.assertEqual(res["primary_domain"], "SYSTEM_TOOL_CLI")
        self.assertGreaterEqual(res["demand_tensor"]["cli_facade_demand"], 4)
        self.assertGreaterEqual(res["demand_tensor"]["deploy_simplicity_demand"], 4)


if __name__ == "__main__":
    unittest.main()
