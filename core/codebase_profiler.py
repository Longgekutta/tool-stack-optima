#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
core/codebase_profiler.py: 物理代码库真实特征与架构瓶颈静态探针
=============================================================================
不依赖任何主观臆想或硬编码场景，直接静态遍历目标仓库的所有源文件与 AST，
提取语言分布、I/O 模式、底层系统调用、并发模型与计算热点，
生成客观物理事实驱动的需求张量 (Empirical Demand Tensor) 与潜在瓶颈诊断清单。
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, List, Set, Tuple


LANGUAGE_EXTENSIONS = {
    ".py": "Python",
    ".go": "Go",
    ".rs": "Rust",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".c": "C",
    ".h": "C/C++ Header",
    ".hpp": "C++ Header",
    ".ts": "TypeScript",
    ".tsx": "TypeScript (React)",
    ".js": "JavaScript",
    ".jsx": "JavaScript (React)",
    ".zig": "Zig",
    ".cs": "C#",
    ".java": "Java",
    ".kt": "Kotlin",
    ".sh": "Shell",
    ".ps1": "PowerShell"
}

# 忽略扫描的通用依赖与编译目录
IGNORE_DIRS = {
    ".git", "__pycache__", "node_modules", "target", "build", "dist",
    "venv", ".venv", "env", "bin", "obj", ".idea", ".vscode"
}


class CodebaseProfiler:
    """
    代码库物理特征探针：完全从物理源码提取事实，作为语言引擎选型与架构重构的客观输入。
    """

    @classmethod
    def profile_repository(cls, repo_dir: str) -> Dict[str, Any]:
        root_path = Path(repo_dir).resolve()
        if not root_path.exists() or not root_path.is_dir():
            raise FileNotFoundError(f"Directory does not exist: {repo_dir}")

        language_stats: Dict[str, Dict[str, int]] = {}
        total_files = 0
        total_loc = 0
        total_complexity = 0

        # 特征信号计数器
        signals = {
            "network_listeners": [],       # 网络端口监听/服务特征
            "high_freq_io": [],            # WebSocket / 原始 Socket / 轮询
            "concurrency_models": [],      # 协程 / 线程 / 异步事件循环
            "subprocess_calls": [],        # 子进程启停 (如调用外部CLI工具)
            "lowlevel_system_apis": [],    # CFFI / ctypes / Win32 / Syscall / Unsafe
            "heavy_compute_crypto": [],    # 加密 / 哈希 / 图像 / 数学计算
            "ai_agent_calls": [],          # LLM API / Prompt 模板 / 智能体工具调用
            "ui_web_interfaces": [],       # React / HTML / Vue / 前端视图
            "cli_interfaces": []           # argparse / click / cobra / UCFS
        }

        # 1. 遍历代码文件
        for root, dirs, files in os.walk(root_path):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            for f in files:
                f_path = Path(root) / f
                ext = f_path.suffix.lower()
                if ext in LANGUAGE_EXTENSIONS:
                    lang = LANGUAGE_EXTENSIONS[ext]
                    total_files += 1
                    try:
                        content = f_path.read_text(encoding="utf-8", errors="ignore")
                        loc = len(content.splitlines())
                        total_loc += loc

                        if lang not in language_stats:
                            language_stats[lang] = {"files": 0, "loc": 0, "bytes": 0}
                        language_stats[lang]["files"] += 1
                        language_stats[lang]["loc"] += loc
                        language_stats[lang]["bytes"] += f_path.stat().st_size

                        # 探测物理特征信号与圈复杂度
                        cls._probe_code_signals(f_path.relative_to(root_path), content, ext, signals)
                        total_complexity += cls._calculate_file_cyclomatic_complexity(content, ext)
                    except Exception:
                        pass

        # 2. 计算主导语言
        dominant_language = "Unknown"
        if language_stats:
            dominant_language = max(language_stats.items(), key=lambda x: x[1]["loc"])[0]

        # 3. 基于物理信号推导客观需求张量 (1~5 分制)
        demand_tensor = cls._derive_demand_tensor(signals, language_stats, total_loc)

        # 4. 定位具体物理瓶颈
        bottlenecks = cls._diagnose_bottlenecks(dominant_language, signals, language_stats)

        return {
            "repo_name": root_path.name,
            "root_path": str(root_path),
            "dominant_language": dominant_language,
            "total_code_files": total_files,
            "total_loc": total_loc,
            "ast_cyclomatic_complexity": max(1, total_complexity),
            "language_distribution": language_stats,
            "detected_signals_count": {k: len(v) for k, v in signals.items()},
            "signal_samples": {k: v[:5] for k, v in signals.items() if v},
            "empirical_demand_tensor": demand_tensor,
            "diagnosed_bottlenecks": bottlenecks
        }

    @classmethod
    def _calculate_file_cyclomatic_complexity(cls, content: str, ext: str) -> int:
        """从 Python AST 或多语言分支关键字统计文件级圈复杂度"""
        if ext == ".py":
            try:
                import ast
                tree = ast.parse(content)
                comp = 1
                for node in ast.walk(tree):
                    if isinstance(node, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler, ast.With, ast.AsyncWith)):
                        comp += 1
                    elif isinstance(node, ast.BoolOp):
                        comp += len(node.values) - 1
                return comp
            except Exception:
                pass

        branch_matches = re.findall(r'\b(if|else\s+if|for|while|switch|case|catch|match)\b|&&|\|\||\?', content)
        func_matches = re.findall(r'\b(fn|func|function|def|void|int|bool|pub fn)\s+([a-zA-Z_]\w*)\s*\(', content)
        return max(1, len(func_matches) + len(branch_matches))

    @classmethod
    def _probe_code_signals(cls, rel_path: Path, content: str, ext: str, signals: Dict[str, List[str]]):
        rel_str = str(rel_path)

        # A. 网络监听
        for m in re.finditer(r"(\.listen\(|uvicorn\.run|app\.run\(|http\.ListenAndServe|TcpListener::bind|socket\.bind)", content):
            signals["network_listeners"].append(f"{rel_str} ({m.group(0)})")

        # B. 高频 I/O 与 WebSocket
        for m in re.finditer(r"\b(websocket|websockets|WebSocketClient|\.connect\(ws|recv_loop)\b", content, re.IGNORECASE):
            signals["high_freq_io"].append(f"{rel_str} ({m.group(0)})")

        # C. 并发模型
        for m in re.finditer(r"\b(async def|asyncio\.|threading\.Thread|multiprocessing|go\s+\w+\(|tokio::spawn)\b", content):
            signals["concurrency_models"].append(f"{rel_str} ({m.group(0)})")

        # D. 子进程调用 (高频外部命令)
        for m in re.finditer(r"\b(subprocess\.run|subprocess\.Popen|os\.system|exec\.Command|Command::new)\b", content):
            signals["subprocess_calls"].append(f"{rel_str} ({m.group(0)})")

        # E. 底层硬件与原生系统调用
        for m in re.finditer(r"\b(ctypes|cffi|win32api|win32gui|win32con|syscall|unsafe\.Pointer|ioctl|DirectX|ANGLE)\b", content):
            signals["lowlevel_system_apis"].append(f"{rel_str} ({m.group(0)})")

        # F. 计算密集与哈希加密
        for m in re.finditer(r"\b(hashlib|CryptUnprotectData|AES|RSA|HMAC|TOTP|pyotp|numpy|polars|matrix|bezier)\b", content):
            signals["heavy_compute_crypto"].append(f"{rel_str} ({m.group(0)})")

        # G. 大模型与智能体调用
        for m in re.finditer(r"\b(openai|anthropic|chat_completion|system_prompt|tool_call|mcp|langchain)\b", content, re.IGNORECASE):
            signals["ai_agent_calls"].append(f"{rel_str} ({m.group(0)})")

        # H. UI 交互
        for m in re.finditer(r"\b(react|vue|electron|tauri|next\.js|render\(|document\.getElementById)\b", content, re.IGNORECASE):
            signals["ui_web_interfaces"].append(f"{rel_str} ({m.group(0)})")
        if ext in (".tsx", ".jsx"):
            signals["ui_web_interfaces"].append(f"{rel_str} (React/TSX)")

        # I. CLI 命令行门面
        for m in re.finditer(r"\b(argparse|click|typer|cobra|clap|sys\.argv|run\.ps1|run\.bat)\b", content):
            signals["cli_interfaces"].append(f"{rel_str} ({m.group(0)})")
        if rel_str in ("cli.py", "main.py"):
            signals["cli_interfaces"].append(f"{rel_str} (标准入口)")

    @classmethod
    def _derive_demand_tensor(cls, signals: Dict[str, List[str]], lang_stats: Dict[str, Dict[str, int]], total_loc: int) -> Dict[str, int]:
        """从真实代码信号统计推导 1~5 分客观需求张量"""
        # 时延敏感度: 底层API + 算法计算
        lat_score = 1
        if len(signals["lowlevel_system_apis"]) > 0: lat_score += 2
        if len(signals["heavy_compute_crypto"]) > 0: lat_score += 1
        if len(signals["subprocess_calls"]) > 5: lat_score += 1 # 子进程抖动对时延高度敏感

        # 并发需求: 网络监听 + 异步模型 + WebSocket
        concurrency_score = 1
        if len(signals["network_listeners"]) > 0: concurrency_score += 2
        if len(signals["high_freq_io"]) > 0: concurrency_score += 1
        if len(signals["concurrency_models"]) > 2: concurrency_score += 1

        # 底层系统访问
        system_score = 1
        if len(signals["lowlevel_system_apis"]) > 0: system_score += 2
        if len(signals["lowlevel_system_apis"]) > 3: system_score += 2

        # AI 亲和度
        ai_score = 1
        if len(signals["ai_agent_calls"]) > 0: ai_score += 3

        # 部署便携性: CLI 为主且无外部重型前端时便携性要求高
        deploy_score = 3
        if len(signals["cli_interfaces"]) > 0 and len(signals["ui_web_interfaces"]) == 0:
            deploy_score = 5

        # Web/GUI 交互需求
        gui_score = 1
        if len(signals["ui_web_interfaces"]) > 0: gui_score += 4

        # 门面 CLI 需求
        cli_score = 1
        if len(signals["cli_interfaces"]) > 0: cli_score += 4

        return {
            "latency_sensitivity": min(5, max(1, lat_score)),
            "concurrency_demand": min(5, max(1, concurrency_score)),
            "lowlevel_system_demand": min(5, max(1, system_score)),
            "ai_data_affinity": min(5, max(1, ai_score)),
            "deploy_simplicity_demand": min(5, max(1, deploy_score)),
            "gui_web_demand": min(5, max(1, gui_score)),
            "cli_facade_demand": min(5, max(1, cli_score))
        }

    @classmethod
    def _diagnose_bottlenecks(cls, dominant_lang: str, signals: Dict[str, List[str]], lang_stats: Dict[str, Dict[str, int]]) -> List[Dict[str, str]]:
        """基于语言固有物理约束与代码实际行为，指出不可调和的工程瓶颈 (支持多语言多架构泛化推导)"""
        issues = []
        d_lang = dominant_lang.capitalize()

        # 1. 高频子进程调用瓶颈 (Subprocess Latency Bottleneck)
        if len(signals["subprocess_calls"]) > 2:
            if d_lang == "Python":
                issues.append({
                    "severity": "HIGH",
                    "category": "SUBPROCESS_LATENCY_BOTTLENECK",
                    "evidence": f"代码中发现 {len(signals['subprocess_calls'])} 处子进程外部调用 (如 {signals['subprocess_calls'][0]})",
                    "impact": "Python 频繁通过 subprocess 启停外部二进制存在 50ms~200ms 的固定开销与进程创建风暴",
                    "recommendation": "将该外部交互下沉为原生直连 (如 C-ABI/PyO3 动态链接库直接嵌入、长连接守护进程或共享内存 IPC)"
                })
            elif d_lang in ("Typescript", "Javascript"):
                issues.append({
                    "severity": "HIGH",
                    "category": "EVENT_LOOP_SUBPROCESS_STALL",
                    "evidence": f"Node/TS 代码中发现 {len(signals['subprocess_calls'])} 处子进程调用",
                    "impact": "Node.js 频繁衍生 child_process 或使用 execSync 将导致 V8 单线程事件循环发生物理停顿",
                    "recommendation": "改写为基于 Worker Threads 异步池或通过 N-API 原生插件嵌入"
                })
            else:
                issues.append({
                    "severity": "MEDIUM",
                    "category": "UNNECESSARY_SUBPROCESS_SPAWN",
                    "evidence": f"系统编程语言中频繁调用外部命令 ({len(signals['subprocess_calls'])}处)",
                    "impact": "在系统语言中频繁 spawn 外部命令违背了单二进制自包含原则，产生额外上下文切换损耗",
                    "recommendation": "采用对应语言的原生库生态直接集成，消除对宿主环境外部 CLI 的隐式依赖"
                })

        # 2. 高并发网络/WebSocket 与并发模型阻塞
        if len(signals["high_freq_io"]) > 0 and len(signals["concurrency_models"]) > 0:
            if d_lang == "Python":
                issues.append({
                    "severity": "HIGH",
                    "category": "GIL_CONCURRENCY_LIMITATION",
                    "evidence": f"在 Python 代码中检测到高频流式通信/WebSocket ({len(signals['high_freq_io'])}处) 并发调度",
                    "impact": "由于 Python GIL (全局解释器锁) 存在，大量密集序列化与网络多路复用会导致单核打满、P99 抖动剧烈",
                    "recommendation": "将中枢网络网关/反向代理/WebSocket 复用层剥离为 Go/Rust 独立中枢 (单静态二进制，亚毫秒级无锁事件分发)"
                })
            elif d_lang in ("Typescript", "Javascript"):
                issues.append({
                    "severity": "MEDIUM",
                    "category": "EVENT_LOOP_CPU_SATURATION",
                    "evidence": f"在 JS/TS 中检测到并发高频网络流 ({len(signals['high_freq_io'])}处)",
                    "impact": "密集的网络流协议解析容易抢占 Node 事件循环微任务队列，导致其他异步请求延迟激增",
                    "recommendation": "采用 Cluster 多进程模型分流，或将协议编解码卸载至 Rust NAPI 扩展"
                })

        # 3. 频繁跨语言边界调用与 FFI 封送开销
        if len(signals["lowlevel_system_apis"]) > 3:
            if d_lang == "Python":
                issues.append({
                    "severity": "MEDIUM",
                    "category": "FFI_MARSHALLING_OVERHEAD",
                    "evidence": f"大量分散的 ctypes/win32/系统级调用 ({len(signals['lowlevel_system_apis'])}处)",
                    "impact": "通过 ctypes 反复进行数据封送 (marshalling) 与内存指针转换易引发潜在访问违规 (Memory Access Violation) 且性能损耗高",
                    "recommendation": "将硬件访问与底层系统安全核心收拢为独立 Rust/C++ 微内核库，向上统一暴露精简 C ABI 或 PyO3 绑定"
                })
            elif d_lang == "Go":
                issues.append({
                    "severity": "MEDIUM",
                    "category": "CGO_CALL_OVERHEAD",
                    "evidence": f"Go 代码中检测到底层系统/C 交互 ({len(signals['lowlevel_system_apis'])}处)",
                    "impact": "CGo 调用存在跨栈切换 (Goroutine 栈与 OS 线程栈)、GC 同步开销 (~100ns/call)，高频调用会严重破坏调度效率",
                    "recommendation": "尽量使用纯 Go 重写系统接口，或通过批量汇聚调用减少 cgo 穿越频次"
                })

        # 4. 解释型语言纯 CPU 密集运算瓶颈 (Compute / Crypto Loop)
        if d_lang in ("Python", "Typescript", "Javascript") and len(signals["heavy_compute_crypto"]) > 2:
            issues.append({
                "severity": "HIGH",
                "category": "INTERPRETER_CPU_COMPUTE_BOTTLENECK",
                "evidence": f"在解释型语言中检测到密集数学运算/加密/哈希算法 ({len(signals['heavy_compute_crypto'])}处)",
                "impact": "解释器字节码逐条解释与动态类型装箱导致吞吐量比编译型语言低 10x~50x",
                "recommendation": "将核心计算循环下沉至 Rust/C++ 原生库，利用 SIMD 向量化指令提升吞吐"
            })

        return issues

