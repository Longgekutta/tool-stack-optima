#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tool-stack-optima: 全域编译语言选型与多语言架构搭配决策装具
Universal CLI Facade (UCFS v1.0) Standard Entrypoint
=====================================================
标准动词契约：
  setup       校验当前主机安装的编译器工具链与运行时环境
  run         根据输入的模糊想法生成全局最优多语言搭配方案
  test        执行全量自动化回归单元测试套件
  health      组件探活诊断与自愈能力体检
  clean       清理临时缓存与字节码产物
  languages   列出精选黄金编译器语言特征表与淘汰技术栈台账
"""

import os
import sys
import json
import shutil
import argparse
import unittest
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.taxonomy import GOLDEN_COMPILER_STACKS, DISCARDED_STACKS, get_golden_summary_table
from core.intent_parser import FuzzyIntentParser
from core.optimizer import PolyglotArchitectureOptimizer
from core.blueprint_gen import BlueprintGenerator


def cmd_setup(args) -> int:
    """标准动词: setup (探测系统编译器工具链)"""
    compilers_to_check = {
        "Python": ["python", "python3", "py"],
        "Go": ["go"],
        "Rust": ["cargo", "rustc"],
        "Node / TypeScript": ["node", "npm", "bun", "pnpm"],
        "C / C++": ["gcc", "g++", "clang", "cl"],
        ".NET / C#": ["dotnet"],
        "Zig": ["zig"]
    }
    
    status_report = {}
    for name, bins in compilers_to_check.items():
        found_bin = None
        for b in bins:
            p = shutil.which(b)
            if p:
                found_bin = p
                break
        status_report[name] = {
            "installed": found_bin is not None,
            "path": found_bin or "NOT_FOUND"
        }

    # Python 当前运行时绝对保底
    status_report["Python"]["installed"] = True
    status_report["Python"]["path"] = sys.executable

    res = {
        "status": "ready",
        "tool": "tool-stack-optima",
        "spec": "UCFS v1.0",
        "compiler_toolchains": status_report
    }

    if getattr(args, "json", False):
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print("\n🔧 [SETUP] 宿主机编译器与运行时工具链探查报告:")
        print("----------------------------------------------------------------")
        for k, v in status_report.items():
            icon = "✅ [就绪]" if v["installed"] else "⚠️ [未安装]"
            print(f" {icon} {k:<18} : {v['path']}")
        print("----------------------------------------------------------------")
        print("💡 提示: tool-stack-optima 自身 100% 原生自洽，无论宿主机安装何种编译器均可完美推演。\n")
    return 0


def cmd_test(args) -> int:
    """标准动词: test (执行单元测试套件)"""
    loader = unittest.TestLoader()
    suite = loader.discover(str(BASE_DIR / "tests"))
    runner = unittest.TextTestRunner(verbosity=2 if not getattr(args, "json", False) else 0)
    result = runner.run(suite)

    res = {
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "passed": result.wasSuccessful()
    }
    if getattr(args, "json", False):
        print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0 if result.wasSuccessful() else 1


def cmd_health(args) -> int:
    """标准动词: health (自诊断与快速推演验真)"""
    t0 = time.perf_counter()
    # 运行一次微型测试推演
    test_prompt = "快速验证一个微型系统服务"
    opt = PolyglotArchitectureOptimizer.optimize(test_prompt)
    healthy = (opt.get("optimality_score", 0) > 70 and len(opt["architecture_blueprint"]["layers"]) == 4)
    duration_ms = round((time.perf_counter() - t0) * 1000, 2)

    res = {
        "status": "HEALTHY" if healthy else "DEGRADED",
        "tool": "tool-stack-optima",
        "standard": "UCFS v1.0",
        "golden_stacks_count": len(GOLDEN_COMPILER_STACKS),
        "discarded_stacks_count": len(DISCARDED_STACKS),
        "inference_latency_ms": duration_ms
    }
    if getattr(args, "json", False):
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(f"[tool-stack-optima] Health: {res['status']} ({len(GOLDEN_COMPILER_STACKS)} 黄金语言纳管, 耗时 {duration_ms}ms)")
    return 0 if healthy else 1


def cmd_clean(args) -> int:
    """标准动词: clean (清理字节码与临时文件)"""
    cleaned = 0
    for root, dirs, files in os.walk(BASE_DIR):
        for d in dirs:
            if d in ("__pycache__", ".pytest_cache", ".ruff_cache"):
                try:
                    shutil.rmtree(os.path.join(root, d))
                    cleaned += 1
                except Exception:
                    pass
    res = {"status": "success", "cleaned_dirs": cleaned}
    if getattr(args, "json", False):
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(f"[tool-stack-optima] Cleaned {cleaned} cache directories.")
    return 0


def cmd_languages(args) -> int:
    """专项动词: languages (输出精选黄金编译器矩阵)"""
    if getattr(args, "json", False):
        data = {
            "golden_compiler_stacks": GOLDEN_COMPILER_STACKS,
            "discarded_low_roi_stacks": DISCARDED_STACKS
        }
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print("\n================================================================================")
        print("🏛️ [GOLDEN COMPILER STACKS] 全域精选高性价比与绝对必要编译器语言库")
        print("================================================================================")
        print(get_golden_summary_table())
        print("\n================================================================================")
        print("🚫 [DISCARDED STACKS] 坚决淘汰的低性价比 / 冗余技术栈")
        print("================================================================================")
        for k, v in DISCARDED_STACKS.items():
            print(f" • ❌ {k:<15} : 【{v['reason']}】 - {v['details']}")
        print("================================================================================\n")
    return 0


def cmd_run(args) -> int:
    """标准动词: run (根据模糊意图求解最优架构与搭配方案)"""
    prompt = args.prompt
    if isinstance(prompt, list):
        prompt = " ".join(prompt).strip()
    if not prompt:
        prompt = "做一个高并发分布式行情与订单流监控网关，带网页大盘展示"

    opt = PolyglotArchitectureOptimizer.optimize(prompt)

    if getattr(args, "json", False):
        print(json.dumps(opt, ensure_ascii=False, indent=2))
        return 0

    markdown_doc = BlueprintGenerator.generate_markdown_blueprint(opt)
    print("\n" + markdown_doc)
    return 0


def main():
    parser = argparse.ArgumentParser(description="tool-stack-optima: 全域编译语言选型与多语言架构搭配决策装具")
    subparsers = parser.add_subparsers(dest="verb")

    p_setup = subparsers.add_parser("setup", help="校验宿主机编译器工具链")
    p_setup.add_argument("--json", action="store_true")

    p_run = subparsers.add_parser("run", help="输入模糊想法推演全局最优语言搭配架构")
    p_run.add_argument("prompt", nargs="*", default=[], help="模糊想法或需求描述")
    p_run.add_argument("--json", action="store_true", help="以 JSON 格式输出")

    p_synthesize = subparsers.add_parser("synthesize", help="生成架构蓝图 (run 命令别名)")
    p_synthesize.add_argument("prompt", nargs="*", default=[], help="模糊想法或需求描述")
    p_synthesize.add_argument("--json", action="store_true", help="以 JSON 格式输出")

    p_test = subparsers.add_parser("test", help="执行自动化回归单元测试")
    p_test.add_argument("--json", action="store_true")

    p_health = subparsers.add_parser("health", help="组件健康探针诊断")
    p_health.add_argument("--json", action="store_true")

    p_clean = subparsers.add_parser("clean", help="清理缓存与字节码产物")
    p_clean.add_argument("--json", action="store_true")

    p_langs = subparsers.add_parser("languages", help="展示精选黄金语言矩阵与淘汰台账")
    p_langs.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if not args.verb:
        parser.print_help()
        sys.exit(0)

    handlers = {
        "setup": cmd_setup,
        "run": cmd_run,
        "synthesize": cmd_run,
        "test": cmd_test,
        "health": cmd_health,
        "clean": cmd_clean,
        "languages": cmd_languages
    }

    handler = handlers.get(args.verb)
    if handler:
        sys.exit(handler(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
