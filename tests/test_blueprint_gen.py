#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_blueprint_gen.py: 架构蓝图与目录树生成测试
"""

import unittest
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.optimizer import PolyglotArchitectureOptimizer
from core.blueprint_gen import BlueprintGenerator


class TestBlueprintGen(unittest.TestCase):
    """测试蓝图文本与交付骨架生成"""

    def test_markdown_blueprint_contains_all_sections(self):
        prompt = "做一个高并发分布式事件总线与流处理网关"
        plan = PolyglotArchitectureOptimizer.optimize(prompt)
        doc = BlueprintGenerator.generate_markdown_blueprint(plan)

        self.assertIn("# 🏗️ 架构最优解蓝图", doc)
        self.assertIn("## 一、 四层多语言黄金搭档方案", doc)
        self.assertIn("## 二、 现代跨语言通信与边界契约", doc)
        self.assertIn("## 三、 推荐工程目录骨架", doc)
        self.assertIn("## 四、 关键取舍决策说明", doc)
        self.assertIn("## 五、 统一动词操作指令", doc)
        self.assertIn("run.bat", doc)
        self.assertIn("run.ps1", doc)


if __name__ == "__main__":
    unittest.main()
