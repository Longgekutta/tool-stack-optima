#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
core/code_profiler_flame.py: 行级与函数级高精热点剖析引擎 (Line-Level Hotspot & Function Profiler)
=============================================================================
纯标准库实现 (基于 cProfile + pstats)，零外部依赖：
不满足于整进程级黑盒遥测，向下穿透至函数体与代码行号：
1. 捕获真实函数调用栈与总调用频次 (Call Count)
2. 排查 CPU 耗时黑洞 (Top Self Time vs Cumulative Time)
3. 准确输出瓶颈发生的代码行号 (File:Line) 与单次调用开销
4. 输出可视化热点分布表
"""

import os
import sys
import cProfile
import pstats
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

from .repo_resolver import RepoResolver
from .probe_runner import ProbeRunner


class HotspotProfiler:
    """行级与函数级热点剖析器"""

    @classmethod
    def profile_target(cls, target_input: str, custom_cmd: Optional[str] = None, top_n: int = 10) -> Dict[str, Any]:
        """
        对目标仓库进行无侵入式函数调用栈与热点分析
        """
        resolved_path, meta = RepoResolver.resolve(target_input)
        repo_name = Path(resolved_path).name

        probe_info = ProbeRunner.detect_probe_command(resolved_path) if not custom_cmd else {
            "command": custom_cmd,
            "type": "CUSTOM_COMMAND",
            "rationale": "自定义分析入口"
        }

        # 通过标准库 cProfile 执行目标命令并捕获二进制性能剖析数据
        with tempfile.NamedTemporaryFile(suffix=".pstats", delete=False) as tf:
            pstats_path = tf.name

        try:
            # 构造带 cProfile 的探针命令
            import shlex
            raw_cmd = probe_info["command"]
            parts = shlex.split(raw_cmd, posix=False)
            clean_parts = [p.strip('\"\'') for p in parts]

            if clean_parts and (clean_parts[0].lower().endswith("python.exe") or clean_parts[0].lower().endswith("python")):
                exec_args = [sys.executable, "-m", "cProfile", "-o", pstats_path] + clean_parts[1:]
            else:
                exec_args = [sys.executable, "-m", "cProfile", "-o", pstats_path] + clean_parts

            proc = subprocess.run(
                exec_args,
                cwd=resolved_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            if not os.path.exists(pstats_path) or os.path.getsize(pstats_path) == 0:
                return {
                    "success": False,
                    "repo_name": repo_name,
                    "error": f"未能生成有效的 pstats 性能数据 (退出码 {proc.returncode}): {proc.stderr[:300]}"
                }

            # 解析 pstats 性能账本
            stats = pstats.Stats(pstats_path)
            stats.strip_dirs()

            total_calls = stats.total_calls
            total_tt = stats.total_tt

            # 抓取耗时最长的函数 (按照累积时间 cumulative 与自身时间 tottime)
            stats.sort_stats("cumulative")
            hotspots_cum = []
            for func_key, (cc, nc, tt, ct, callers) in list(stats.stats.items())[:top_n]:
                filename, line_no, func_name = func_key
                pct = round((ct / max(0.0001, total_tt)) * 100, 1)
                hotspots_cum.append({
                    "function": func_name,
                    "location": f"{filename}:{line_no}",
                    "call_count": nc,
                    "cumulative_time_s": round(ct, 4),
                    "self_time_s": round(tt, 4),
                    "time_percentage": min(100.0, pct)
                })

            stats.sort_stats("tottime")
            hotspots_self = []
            for func_key, (cc, nc, tt, ct, callers) in list(stats.stats.items())[:top_n]:
                filename, line_no, func_name = func_key
                pct = round((tt / max(0.0001, total_tt)) * 100, 1)
                hotspots_self.append({
                    "function": func_name,
                    "location": f"{filename}:{line_no}",
                    "call_count": nc,
                    "self_time_s": round(tt, 4),
                    "cumulative_time_s": round(ct, 4),
                    "self_percentage": min(100.0, pct)
                })

            return {
                "success": True,
                "repo_name": repo_name,
                "resolved_path": resolved_path,
                "command_executed": raw_cmd,
                "total_calls": total_calls,
                "total_cpu_time_s": round(total_tt, 4),
                "top_cumulative_hotspots": hotspots_cum,
                "top_self_cpu_hotspots": hotspots_self
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "repo_name": repo_name, "error": "性能剖析超时 (30秒)"}
        except Exception as e:
            return {"success": False, "repo_name": repo_name, "error": str(e)}
        finally:
            if os.path.exists(pstats_path):
                try:
                    os.remove(pstats_path)
                except Exception:
                    pass

    @classmethod
    def render_markdown(cls, report: Dict[str, Any]) -> str:
        if not report.get("success"):
            return f"❌ 性能剖析失败: {report.get('error', '未知错误')}"

        lines = [
            f"# 🔥 目标工程行级与函数级高精热点剖析报告: `{report['repo_name']}`",
            "",
            "> 穿透至函数体与代码行号，揭示 CPU 耗时与调用频次真实分布。",
            "",
            "## 📌 剖析概览",
            f"- **目标物理工程**: `{report['resolved_path']}`",
            f"- **执行采样指令**: `{report['command_executed']}`",
            f"- **总调用函数次数**: **{report['total_calls']:,} 次**",
            f"- **总采样 CPU 运行耗时**: **{report['total_cpu_time_s']} 秒**",
            "",
            "## 📊 累积耗时最深 Top 10 函数调用链 (Cumulative Time Hotspots)",
            "| 耗时占比 | 累积耗时 | 函数名称 | 源码物理位置 | 调用频次 |",
            "| :---: | :---: | :--- | :--- | :---: |"
        ]

        for h in report["top_cumulative_hotspots"]:
            lines.append(f"| **{h['time_percentage']}%** | `{h['cumulative_time_s']}s` | `{h['function']}` | `{h['location']}` | {h['call_count']} |")

        lines.extend([
            "",
            "## ⚡ 自身计算密集度 Top 10 函数 (Self CPU Time Hotspots)",
            "| 自身占比 | 纯计算耗时 | 函数名称 | 源码物理位置 | 调用频次 |",
            "| :---: | :---: | :--- | :--- | :---: |"
        ])
        for h in report["top_self_cpu_hotspots"]:
            lines.append(f"| **{h['self_percentage']}%** | `{h['self_time_s']}s` | `{h['function']}` | `{h['location']}` | {h['call_count']} |")

        lines.append("")
        return "\n".join(lines)
