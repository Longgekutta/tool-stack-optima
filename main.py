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


def cmd_analyze(args) -> int:
    """工业母机动词: analyze (输入任何本地目录、远程Git URL或仓库名，剖析物理代码并求解最优多语言架构)"""
    target = args.target
    if isinstance(target, list):
        target = " ".join(target).strip()
    if not target:
        target = "."

    opt = PolyglotArchitectureOptimizer.optimize_repo(target)

    if getattr(args, "json", False):
        print(json.dumps(opt, ensure_ascii=False, indent=2))
        return 0

    markdown_doc = BlueprintGenerator.generate_markdown_blueprint(opt)
    print("\n" + markdown_doc)
    return 0


def cmd_pipeline(args) -> int:
    """母机协同动词: pipeline (触发母机流水线: arbiter -> stack-optima -> code-optima)"""
    from core.pipeline_runner import MetaToolchainPipeline
    target = getattr(args, "target", ".")
    if isinstance(target, list):
        target = " ".join(target).strip()
    if not target:
        target = "."

    data = MetaToolchainPipeline.run_pipeline(target)

    if getattr(args, "json", False):
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0

    doc = MetaToolchainPipeline.render_markdown(data)
    print("\n" + doc)
    return 0


def cmd_scaffold(args) -> int:
    """母机动手术动词: scaffold (针对检出的瓶颈自动生成原生零拷贝微内核与胶水脚手架)"""
    from core.scaffold_generator import ScaffoldGenerator
    target = getattr(args, "target", ".")
    if isinstance(target, list):
        target = " ".join(target).strip()
    if not target:
        target = "."

    out_dir = getattr(args, "out", None)
    res = ScaffoldGenerator.generate_scaffold(target, output_dir=out_dir)

    if getattr(args, "json", False):
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0

    print("=" * 80)
    print(f" 🛠️  原生零拷贝重构手术脚手架已生成: {res['repo_name']}")
    print("=" * 80)
    print(f" • 针对病灶:   {', '.join(res['targeted_bottlenecks']) if res['targeted_bottlenecks'] else '常规性能优化'}")
    print(f" • 产物根目录: {res['scaffold_root']}")
    print(f" • 生成物料:   {res['generated_files_count']} 个文件")
    for f in res["files"]:
        print(f"    ✓ {f}")
    print("-" * 80)
    print(" 🚀 下一步操作：运行 build_native 脚本编译高性能动态库，并在 Python 中引入 bridge_glue。")
    print("=" * 80)
    return 0


def cmd_probe(args) -> int:
    """实机基线动词: probe (自适应探测仓库冷启动时延与峰值物理常驻内存)"""
    from core.probe_runner import ProbeRunner
    target = getattr(args, "target", ".")
    if isinstance(target, list):
        target = " ".join(target).strip()
    if not target:
        target = "."

    custom_cmd = getattr(args, "cmd", None)
    res = ProbeRunner.probe(target, custom_cmd=custom_cmd)

    if getattr(args, "json", False):
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0 if res["status"] == "success" else 1

    doc = ProbeRunner.render_markdown(res)
    print("\n" + doc)
    return 0 if res["status"] == "success" else 1


def cmd_run(args) -> int:
    """标准动词: run (支持输入模糊意图文本，或直接输入仓库路径/URL进行物理分析)"""
    prompt = args.prompt
    if isinstance(prompt, list):
        prompt = " ".join(prompt).strip()
    if not prompt:
        prompt = "."

    is_repo = False
    try:
        from core.repo_resolver import RepoResolver
        resolved, _ = RepoResolver.resolve(prompt)
        is_repo = True
    except Exception:
        is_repo = False

    if is_repo:
        opt = PolyglotArchitectureOptimizer.optimize_repo(prompt)
    else:
        opt = PolyglotArchitectureOptimizer.optimize(prompt)

    if getattr(args, "json", False):
        print(json.dumps(opt, ensure_ascii=False, indent=2))
        return 0

    markdown_doc = BlueprintGenerator.generate_markdown_blueprint(opt)
    print("\n" + markdown_doc)
    return 0


def cmd_tournament(args) -> int:
    """专项动词: benchmark / tournament (组织多模型与多技术栈实证基准测试与帕累托选拔)"""
    from core.tournament_engine import EmpiricalBenchmarkHarness, BenchmarkSpec, CandidateSolution, TelemetryMetrics
    
    spec_path = getattr(args, "spec", None)
    target_repo = getattr(args, "target", None)
    if not target_repo and getattr(args, "extra_args", None):
        target_repo = args.extra_args[0]

    if spec_path and os.path.exists(spec_path):
        with open(spec_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        candidates = []
        for c in data.get("candidates", []):
            m_data = c.get("metrics", {})
            m = TelemetryMetrics(**m_data)
            c_copy = {k: v for k, v in c.items() if k != "metrics"}
            candidates.append(CandidateSolution(**c_copy, metrics=m))
        spec = BenchmarkSpec(
            spec_id=data.get("spec_id", "CUSTOM-BENCHMARK"),
            title=data.get("title", "自定义实证基准评估"),
            problem_domain=data.get("problem_domain", ""),
            slas=data.get("slas", {}),
            candidates=candidates
        )
    elif target_repo:
        try:
            spec = EmpiricalBenchmarkHarness.create_spec_from_repo(target_repo)
        except Exception as e:
            print(f"[ERROR] Failed to generate benchmark from target '{target_repo}': {e}", file=sys.stderr)
            return 1
    else:
        spec = BenchmarkSpec(
            spec_id="EMPIRICAL-BENCH-01",
            title="多技术栈与多模型实证效能基准测试",
            problem_domain="无头任务分发与状态调度",
            slas={"min_pass_rate": 1.0, "max_latency_ms": 200.0, "max_ram_mb": 64.0},
            candidates=[
                CandidateSolution(
                    solution_id="go_native_worker",
                    name="Go 单静态二进制异步协程中枢",
                    language_stack=["Go"],
                    model_source="Claude-3.7-Sonnet",
                    archetype="tool",
                    technical_description="单静态二进制，Goroutine 原生承载高并发网络调度，极低物理内存",
                    metrics=TelemetryMetrics(test_pass_rate=1.0, latency_p99_ms=4.2, peak_ram_mb=12.5, token_cost=3200)
                ),
                CandidateSolution(
                    solution_id="rust_core_py_glue",
                    name="Rust 硬件与免杀内核 (PyO3) + Python 胶水调度",
                    language_stack=["Rust", "Python"],
                    model_source="DeepSeek-V3",
                    archetype="tool",
                    technical_description="底层硬件控制与内存安全采用 Rust 动态库，上层编排采用 Python",
                    metrics=TelemetryMetrics(test_pass_rate=1.0, latency_p99_ms=1.8, peak_ram_mb=28.0, token_cost=5800)
                ),
                CandidateSolution(
                    solution_id="python_std_standalone",
                    name="全量纯 Python (All-in-Python) 原生标准库方案",
                    language_stack=["Python"],
                    model_source="Gemini-2.5-Pro",
                    archetype="tool",
                    technical_description="完全使用 Python 标准库，开发周期短，但高并发存在 GIL 争用与较高内存开销",
                    metrics=TelemetryMetrics(test_pass_rate=1.0, latency_p99_ms=48.5, peak_ram_mb=42.0, token_cost=2100)
                )
            ]
        )

    execute_live = getattr(args, "live", False)
    report = EmpiricalBenchmarkHarness.evaluate(spec, execute_live=execute_live)

    if getattr(args, "json", False):
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
        return 0

    markdown_doc = EmpiricalBenchmarkHarness.render_markdown_report(report)
    print("\n" + markdown_doc)
    return 0


def main():
    parser = argparse.ArgumentParser(description="tool-stack-optima: 全域编译语言选型与多语言架构搭配决策装具")
    subparsers = parser.add_subparsers(dest="verb")

    p_setup = subparsers.add_parser("setup", help="校验宿主机编译器工具链")
    p_setup.add_argument("--json", action="store_true")

    p_analyze = subparsers.add_parser("analyze", help="输入任何本地目录或远程Git URL，物理剖析代码并求解最优多语言架构")
    p_analyze.add_argument("target", nargs="*", default=".", help="目标仓库路径、Git URL或短名")
    p_analyze.add_argument("--json", action="store_true", help="以 JSON 格式输出")

    p_run = subparsers.add_parser("run", help="输入仓库路径/URL或模糊想法推演全局最优架构")
    p_run.add_argument("prompt", nargs="*", default=[], help="仓库路径、URL或需求描述")
    p_run.add_argument("--json", action="store_true", help="以 JSON 格式输出")

    p_synthesize = subparsers.add_parser("synthesize", help="生成架构蓝图 (run 命令别名)")
    p_synthesize.add_argument("prompt", nargs="*", default=[], help="模糊想法或需求描述")
    p_synthesize.add_argument("--json", action="store_true", help="以 JSON 格式输出")

    p_pipe = subparsers.add_parser("pipeline", help="全域跨母机协同流水线 (arbiter -> stack-optima -> code-optima)")
    p_pipe.add_argument("target", nargs="*", default=".", help="目标仓库路径、Git URL 或仓库短名")
    p_pipe.add_argument("--json", action="store_true", help="以 JSON 格式输出协同数据")

    p_scaffold = subparsers.add_parser("scaffold", help="针对架构病灶自动生成原生零拷贝微内核与重构脚手架 (动手术)")
    p_scaffold.add_argument("target", nargs="*", default=".", help="目标仓库路径、Git URL 或短名")
    p_scaffold.add_argument("--out", type=str, default=None, help="脚手架输出目录 (默认在仓库内 scaffold_refactor)")
    p_scaffold.add_argument("--json", action="store_true", help="以 JSON 格式输出")

    p_tour = subparsers.add_parser("tournament", help="组织多模型与跨语言实证竞技评测 (结果导向选拔)")
    p_tour.add_argument("target", nargs="?", default=None, help="目标仓库路径、Git URL 或仓库短名")
    p_tour.add_argument("--spec", type=str, default=None, help="基准规范与候选人矩阵 JSON 路径")
    p_tour.add_argument("--live", action="store_true", help="启用实机命令沙盒执行与实时测速")
    p_tour.add_argument("--json", action="store_true", help="以 JSON 格式输出评估数据")

    p_bench = subparsers.add_parser("benchmark", help="实证基准测试 (tournament 别名)")
    p_bench.add_argument("target", nargs="?", default=None, help="目标仓库路径、Git URL 或仓库短名")
    p_bench.add_argument("--spec", type=str, default=None, help="基准规范与候选人矩阵 JSON 路径")
    p_bench.add_argument("--live", action="store_true", help="启用实机命令沙盒执行与实时测速")
    p_bench.add_argument("--json", action="store_true", help="以 JSON 格式输出评估数据")

    p_probe = subparsers.add_parser("probe", help="实机自适应物理采样探针 (冷启动时延/操作系统真实峰值物理内存)")
    p_probe.add_argument("target", nargs="*", default=".", help="目标仓库路径、Git URL 或短名")
    p_probe.add_argument("--cmd", type=str, default=None, help="自定义执行探针命令")
    p_probe.add_argument("--json", action="store_true", help="以 JSON 格式输出")

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
        "analyze": cmd_analyze,
        "pipeline": cmd_pipeline,
        "pipe": cmd_pipeline,
        "scaffold": cmd_scaffold,
        "surgery": cmd_scaffold,
        "probe": cmd_probe,
        "run": cmd_run,
        "synthesize": cmd_run,
        "tournament": cmd_tournament,
        "benchmark": cmd_tournament,
        "exam": cmd_tournament,
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
