#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
intent_parser.py: 模糊意图语义解构与系统需求张量提取器
======================================================
将人类自然语言的模糊想法（例如：“做一个高并发的股票回测和行情抓取服务”、“做一个类似bt面板的跨平台小工具”）
拆解为包含 7 大核心物理指标的需求张量，为后续多目标最优架构求解提供确定性输入。
"""

import re
from typing import Dict, Any, List


class FuzzyIntentParser:
    """模糊意图特征提取与张量化解析器"""

    # 领域特征词典
    DOMAIN_PATTERNS = {
        "VECTOR_SEARCH_STORAGE": [
            "向量", "vector", "embedding", "hnsw", "检索", "列存", "storage", "数据库", "db", "索引", "index"
        ],
        "QUANT_HIGH_FREQUENCY": [
            "量化", "quant", "交易", "trade", "高频", "hft", "orderflow", "订单流", "撮合", "行情", "tick", "回测", "策略"
        ],
        "WEB_CRAWLER_MONITOR": [
            "爬虫", "抓取", "crawl", "spider", "监控", "monitor", "知乎", "推特", "微博", "小红书", "邮件", "email", "通知", "hook"
        ],
        "NETWORK_GATEWAY_MESH": [
            "网关", "gateway", "反代", "proxy", "隧道", "tunnel", "路由", "router", "mesh", "负载均衡", "微服务", "rpc", "grpc"
        ],
        "SYSTEM_TOOL_CLI": [
            "系统工具", "cli", "终端", "命令行", "面板", "panel", "bt", "宝塔", "探针", "probe", "单文件", "静态二进制", "运维"
        ],
        "FULLSTACK_WEB_APP": [
            "网站", "web", "前端", "ui", "后台管理", "dashboard", "看板", "页面", "react", "vue", "next"
        ],
        "AI_AGENT_WORKFLOW": [
            "智能体", "agent", "llm", "大模型", "工作流", "workflow", "prompt", "多模型", "集群", "mcp"
        ],
        "HARDWARE_EMBEDDED": [
            "硬件", "单片机", "嵌入式", "iot", "cuda", "gpu", "驱动", "driver", "音视频", "编解码", "ffmpeg"
        ]
    }

    @classmethod
    def parse_intent(cls, prompt: str) -> Dict[str, Any]:
        """
        核心解析函数：输入自然语言 prompt，输出结构化工程需求规格
        """
        p_lower = prompt.lower()
        
        # 1. 领域匹配与打分
        domain_scores = {}
        for domain, keywords in cls.DOMAIN_PATTERNS.items():
            score = 0
            for kw in keywords:
                if kw in p_lower:
                    score += 1
            if score > 0:
                domain_scores[domain] = score
        
        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
        primary_domain = sorted_domains[0][0] if sorted_domains else "SYSTEM_TOOL_CLI"
        secondary_domains = [d[0] for d in sorted_domains[1:3]]

        # 2. 7 维需求张量评估 (1 - 5 分)
        # (1) 延迟敏感度 (Latency Sensitivity)
        latency_score = 1
        if any(w in p_lower for w in ["极速", "低延迟", "微秒", "纳秒", "高性能", "实时", "高频", "fast", "low latency"]):
            latency_score = 5
        elif any(w in p_lower for w in ["并发", "检索", "网络", "抓取"]):
            latency_score = 3

        # (2) 并发与吞吐要求 (Concurrency Demand)
        concurrency_score = 1
        if any(w in p_lower for w in ["高并发", "海量", "分布式", "多线程", "异步", "大规模", "吞吐", "cluster"]):
            concurrency_score = 5
        elif any(w in p_lower for w in ["网络", "服务", "服务器", "server", "gateway"]):
            concurrency_score = 4
        elif any(w in p_lower for w in ["爬虫", "批处理"]):
            concurrency_score = 3

        # (3) AI / 数据处理亲和度 (AI & Data Affinity)
        ai_score = 1
        if any(w in p_lower for w in ["ai", "大模型", "llm", "agent", "智能体", "模型", "自然语言", "embedding", "向量"]):
            ai_score = 5
        elif any(w in p_lower for w in ["分析", "数据", "清洗", "回测", "统计"]):
            ai_score = 4

        # (4) GUI / Web 前端交互需求 (GUI / Web Interaction)
        gui_score = 1
        if any(w in p_lower for w in ["前端", "web", "界面", "ui", "看板", "页面", "图表", "大盘", "可视化"]):
            gui_score = 5
        elif any(w in p_lower for w in ["面板", "panel", "展示"]):
            gui_score = 3

        # (5) 终端门面与 CLI 需求 (CLI & Facade)
        cli_score = 3  # 默认遵循 UCFS 标准，具备基础 CLI
        if any(w in p_lower for w in ["cli", "命令行", "终端", "宝塔", "bt", "快捷键", "控制台"]):
            cli_score = 5

        # (6) 硬件与底层系统访问 (Hardware & Low-level System)
        sys_score = 1
        if any(w in p_lower for w in ["硬件", "驱动", "cuda", "gpu", "内核", "kernel", "寄存器", "裸机", "嵌入式"]):
            sys_score = 5
        elif any(w in p_lower for w in ["内存安全", "无gc", "c++", "rust", "进程", "pid"]):
            sys_score = 4

        # (7) 交付轻量与单文件免安装要求 (Deploy Simplicity & Portability)
        portability_score = 3
        if any(w in p_lower for w in ["免安装", "单文件", "便携", "轻量", "单二进制", "无依赖", "开箱即用", "portable"]):
            portability_score = 5

        # 3. 汇总需求张量
        tensor = {
            "latency_sensitivity": latency_score,
            "concurrency_demand": concurrency_score,
            "ai_data_affinity": ai_score,
            "gui_web_demand": gui_score,
            "cli_facade_demand": cli_score,
            "lowlevel_system_demand": sys_score,
            "deploy_simplicity_demand": portability_score
        }

        return {
            "raw_prompt": prompt,
            "primary_domain": primary_domain,
            "secondary_domains": secondary_domains,
            "demand_tensor": tensor,
            "spec_invariants": {
                "ucfs_compliant": True,
                "zero_gpu_overhead": True,
                "zero_envvar_self_healing": True,
                "five_universal_verbs": True
            }
        }
