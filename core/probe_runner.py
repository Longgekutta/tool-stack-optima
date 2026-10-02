#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
core/probe_runner.py: 仓库物理冷启动与基线性能自适应探针 (Adaptive Codebase Probe Runner)
=============================================================================
纯标准库实现：
针对任何输入的目标仓库，自动嗅探最合适的非破坏性探针命令 (测试套件、CLI 门面或编译器检查)，
通过 ProcessTelemetry 采集物理指标（真实物理内存常驻集 MB、冷启动时延 ms、退出状态），
为架构决策和横向对比提供 100% 真实的物理基线证据。
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

from .repo_resolver import RepoResolver
from .process_telemetry import ProcessTelemetry


class ProbeRunner:
    """自适应代码库物理探针执行器"""

    @classmethod
    def detect_probe_command(cls, repo_path: str) -> Dict[str, str]:
        """
        自动嗅探最适合用于非破坏性冷启动性能采样的探针命令
        """
        p = Path(repo_path).resolve()
        
        # 1. 优先检测 Python 项目
        if (p / "tests").is_dir() or list(p.glob("test_*.py")):
            return {
                "command": f'"{sys.executable}" -m unittest discover tests',
                "type": "UNITTEST_DISCOVERY",
                "rationale": "检测到自动化单元测试目录，执行非破坏性测试套件探针"
            }
        elif (p / "main.py").exists():
            return {
                "command": f'"{sys.executable}" main.py --help',
                "type": "MAIN_CLI_FACADE",
                "rationale": "检测到 main.py 门面，执行 CLI 帮助菜单冷启动探针"
            }
        elif (p / "cli.py").exists():
            return {
                "command": f'"{sys.executable}" cli.py --help',
                "type": "CLI_FACADE",
                "rationale": "检测到 cli.py 入口，执行 CLI 帮助菜单冷启动探针"
            }
        elif (p / "Cargo.toml").exists():
            return {
                "command": "cargo check",
                "type": "RUST_CARGO_CHECK",
                "rationale": "检测到 Rust Cargo 工程，执行 cargo check 语法与依赖树冷启动"
            }
        elif (p / "go.mod").exists():
            return {
                "command": "go test -run=^$ ./...",
                "type": "GO_DRY_TEST",
                "rationale": "检测到 Go Module，执行 dry-run 空测试集探针"
            }
        elif (p / "package.json").exists():
            return {
                "command": "npm test --if-present",
                "type": "NODE_NPM_TEST",
                "rationale": "检测到 Node.js package.json，执行 npm test 探针"
            }
        else:
            # 普适兜底：Python 语法编译检查
            return {
                "command": f'"{sys.executable}" -m compileall -q .',
                "type": "COMPILEALL_VERIFY",
                "rationale": "通用字节码与语法扫描探针"
            }

    @classmethod
    def probe(cls, target_input: str, custom_cmd: Optional[str] = None, timeout: float = 30.0) -> Dict[str, Any]:
        """
        针对指定仓库执行自适应物理采样
        """
        resolved_path, meta = RepoResolver.resolve(target_input)
        repo_name = Path(resolved_path).name

        probe_info = cls.detect_probe_command(resolved_path) if not custom_cmd else {
            "command": custom_cmd,
            "type": "CUSTOM_COMMAND",
            "rationale": "用户指定的显式探针命令"
        }

        cmd_to_run = probe_info["command"]
        telemetry = ProcessTelemetry.execute(cmd_to_run, cwd=resolved_path, timeout=timeout)

        # 评估物理指标基线等级
        ram = telemetry["peak_ram_mb"]
        lat = telemetry["latency_ms"]

        if ram < 25.0:
            ram_rating = "EXCELLENT (轻量级常驻)"
        elif ram < 64.0:
            ram_rating = "ACCEPTABLE (标准进程开销)"
        elif ram < 200.0:
            ram_rating = "HEAVY (偏重，具备微内核下沉优化空间)"
        else:
            ram_rating = "CRITICAL (极高内存常驻，需重点排查内存泄漏/大模型上下文)"

        if lat < 100.0:
            lat_rating = "INSTANT (<100ms 极速响应)"
        elif lat < 500.0:
            lat_rating = "FAST (百毫秒级快速就绪)"
        elif lat < 2000.0:
            lat_rating = "MODERATE (存在一定解释器初始化延迟)"
        else:
            lat_rating = "SLOW (秒级冷启动，建议下沉为原生编译二进制)"

        return {
            "status": "success" if telemetry["success"] else "failed",
            "repo_name": repo_name,
            "resolved_path": resolved_path,
            "repo_metadata": meta,
            "probe_type": probe_info["type"],
            "probe_command": cmd_to_run,
            "probe_rationale": probe_info["rationale"],
            "telemetry": telemetry,
            "ratings": {
                "peak_ram": ram_rating,
                "latency": lat_rating
            }
        }

    @classmethod
    def render_markdown(cls, report: Dict[str, Any]) -> str:
        """格式化渲染物理基线探针报告"""
        t = report["telemetry"]
        r = report["ratings"]
        status_icon = "🟢" if report["status"] == "success" else "🔴"

        lines = [
            f"# {status_icon} 目标工程实机物理基线探针报告: `{report['repo_name']}`",
            "",
            "> 采用操作系统底层物理采样 (`ctypes.windll` / `psapi` / `resource`)，杜绝虚假打分与臆测数据。",
            "",
            "## 📌 探针探测上下文",
            f"- **目标工程物理路径**: `{report['resolved_path']}`",
            f"- **探针推演类型**: `{report['probe_type']}`",
            f"- **执行采样命令**: `{report['probe_command']}`",
            f"- **探针推选依据**: {report['probe_rationale']}",
            "",
            "## 📊 操作系统级实测物理度量",
            "| 物理度量维度 | 实测数值 | 评级判定 |",
            "| :--- | :--- | :--- |",
            f"| **峰值物理内存 (Peak Working Set)** | **{t['peak_ram_mb']} MB** | `{r['peak_ram']}` |",
            f"| **冷启动时延 (Wall Latency)** | **{t['latency_ms']} ms** | `{r['latency']}` |",
            f"| **进程退出状态码** | `{t['exit_code']}` | {'✅ 正常退出' if t['success'] else '❌ 异常退出'} |",
            "",
            "## 📝 标准输出与错误截流 (Stdout/Stderr)",
            "```text",
            t["stdout_snippet"] or "(无标准输出)",
            "```",
        ]
        if t["stderr_snippet"] and not t["success"]:
            lines.extend([
                "### 错误详情:",
                "```text",
                t["stderr_snippet"],
                "```"
            ])
        lines.append("")
        return "\n".join(lines)
