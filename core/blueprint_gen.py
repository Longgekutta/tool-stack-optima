#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
blueprint_gen.py: 规范工程拓扑与多语言协同交付蓝图生成器
======================================================
将求解出的多语言黄金搭档方案，无缝编译为符合全域规范 (UCFS v1.0, spec-omni-project, 5大动词) 的具体交付蓝图：
1. 架构拓扑分工全景图 (ASCII Architecture Diagram)
2. 规范目录树与职责映射表 (Directory Tree & Manifest)
3. 跨语言桥接与通信契约 (FFI / IPC / REST 交互标准)
4. 标准 5 大动词启动脚本骨架 (Triple-Stack Launchers)
"""

from typing import Dict, Any


class BlueprintGenerator:
    """多语言规范蓝图生成器"""

    @classmethod
    def generate_markdown_blueprint(cls, plan: Dict[str, Any]) -> str:
        prompt = plan["prompt"]
        domain = plan["domain"]
        score = plan["optimality_score"]
        bp = plan["architecture_blueprint"]
        layers = bp["layers"]
        rf = bp["resource_forecast"]

        lines = [
            f"# 🏗️ 架构最优解蓝图: {prompt}",
            "",
            f"> **领域判定**：`{domain}` | **帕累托综合最优分**：`{score} / 100`  ",
            f"> **资源预估**：编译期峰值 RAM `~{rf['peak_compile_ram_mb']}MB` | 运行时常驻 RAM `~{rf['estimated_runtime_ram_mb']}MB`  ",
            "> **规范遵从**：`UCFS v1.0` 终端门面 | `0% GPU` 损耗 | 零环境变量路径自愈 | 5 大通用操作动词",
            "",
            "---",
            "",
            "## 一、 四层多语言黄金搭档方案 (Polyglot Pairing Recipe)",
            "",
            "| 分层架构 | 选用语言 | 系统职责定位 | 选型第一性原理与取舍决策 |",
            "| :--- | :---: | :--- | :--- |"
        ]

        for l in layers:
            lines.append(
                f"| **{l['tier']}** | `{l['language_name']}` | {l['role']} | {l['rationale']} |"
            )

        lines.extend([
            "",
            "---",
            "",
            "## 二、 现代跨语言通信与边界契约 (Inter-Component Contract)",
            "",
            "```",
            "  ┌────────────────────────────────────────────────────────┐",
            f"  │ Layer 4 门面视窗 [{layers[3]['language_name']}] (CLI / Web 看板)         │",
            "  └───────────────────────────┬────────────────────────────┘",
            "                              │ 统一本地 HTTP / 标准输入输出 JSON",
            "                              ▼",
            f"  │ Layer 2 网络中枢 [{layers[1]['language_name']}] (高并发异步服务与路由调度) │",
            "  └─────────────┬───────────────────────────┬──────────────┘",
            "                │ 零拷贝内存映射 / gRPC     │ 进程内管道 / FFI",
            "                ▼                           ▼",
            f"  │ Layer 1 计算存储内核 [{layers[0]['language_name']}]    Layer 3 AI业务胶水 [{layers[2]['language_name']}] │",
            "  └────────────────────────────────────────────────────────┘",
            "```",
            "",
            "---",
            "",
            "## 三、 推荐工程目录骨架 (Recommended Directory Skeleton)",
            "",
            "```text",
            "my-optimized-project/",
            "├── core/                   # Tier 1: 高性能计算与存储微内核 (" + layers[0]['lang_key'] + ")",
            "├── server/                 # Tier 2: 网络调度与服务中枢 (" + layers[1]['lang_key'] + ")",
            "├── workflows/              # Tier 3: 业务编排与大模型胶水 (" + layers[2]['lang_key'] + ")",
            "├── ui/                     # Tier 4: 终端交互门面或 Web 大盘 (" + layers[3]['lang_key'] + ")",
            "├── tests/                  # 跨层集成与自动化测试套件",
            "├── main.py                 # UCFS v1.0 标准 Python 调度中枢入口",
            "├── run.bat                 # Windows CMD 零环境变量启动器",
            "├── run.ps1                 # PowerShell 跨平台启动器",
            "├── run.sh                  # Linux/macOS 跨平台启动器",
            "├── justfile                # 5 大通用操作动词映射",
            "└── README.md               # 完备工程门面文档",
            "```",
            "",
            "---",
            "",
            "## 四、 关键取舍决策说明 (Architectural Trade-offs)",
            ""
        ])

        if bp.get("discarded_tradeoffs"):
            for t in bp["discarded_tradeoffs"]:
                lines.append(f"- 💡 **{t}**")
        else:
            lines.append("- 💡 **全面淘汰低效冗余技术栈，整套架构保持亚 3 秒启动与零依赖轻量部署。**")

        lines.extend([
            "",
            "---",
            "",
            "## 五、 统一动词操作指令 (Unified Operations)",
            "",
            "```bash",
            "# 1. 验证运行环境",
            "run.bat setup",
            "",
            "# 2. 启动全流程业务服务",
            "run.bat run",
            "",
            "# 3. 运行全语言自动化测试",
            "run.bat test",
            "",
            "# 4. 探针健康诊断",
            "run.bat health",
            "",
            "# 5. 清理编译缓存",
            "run.bat clean",
            "```",
            ""
        ])

        return "\n".join(lines)
