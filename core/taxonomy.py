#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
taxonomy.py: 黄金编译器语言帕累托矩阵与淘汰技术栈台账
=====================================================
第一性原理筛选法则：
1. 性价比高 (High ROI): 编译快、占用小、语法正交、分发简单、AI生成通过率高 (ROI >= 8/10)
2. 很有必要 (High Necessity): 领域不可替代、内存安全底线、生态事实垄断 (Necessity >= 9/10)
二者必占其一，否则坚决剔除淘汰！
"""

from typing import Dict, Any, List

# =============================================================================
# 一、 黄金高性价比与绝对必要编译器语言库 (The Golden Essential Stacks)
# =============================================================================
GOLDEN_COMPILER_STACKS: Dict[str, Dict[str, Any]] = {
    "GO": {
        "name": "Go (Golang)",
        "tier": "GOLDEN_CORE",
        "roi_score": 9.8,
        "necessity_score": 9.5,
        "summary": "云原生与高并发微服务的性价比之王。秒级极速编译，单一静态二进制无依赖分发，极低运行内存。",
        "build_speed": "ULTRA_FAST",       # 1-3秒编译
        "toolchain_size_mb": 650,          # 工具链仅 ~650MB
        "compile_ram_mb": 200,             # 编译时仅耗 150-300MB RAM
        "runtime_ram_mb": 15,              # 运行时仅占 10-25MB RAM
        "ai_synthesis_pass_rate": 0.94,    # AI 一次性编译成功率极高 (语法正交且无复杂泛型宏陷阱)
        "deploy_form": "SINGLE_STATIC_BINARY",
        "irreplaceable_domains": [
            "云原生基础设施 (K8s/Docker/Caddy)",
            "高并发网络服务与代理网关 (Proxy/Tunnel/Mesh)",
            "跨平台极速命令行工具 (CLI/TUI/Daemon)",
            "分布式存储中间件与轻量后端"
        ],
        "strengths": [
            "单静态二进制文件，跨平台编译极其丝滑 (GOOS=linux GOARCH=amd64)",
            "原生 Goroutine / Channel 协程并发模型，百万连接轻松承载",
            "标准库自带完整 HTTP/TLS/JSON/RPC，零外部第三方包也能做生产级服务",
            "内存占用比 Python/Java 低 80% 以上"
        ],
        "weaknesses": [
            "不适合写极严苛的无 GC 低延迟内核 (如高频金融交易纳秒级撮合)",
            "不适合写复杂的深度学习与 AI 算法算子"
        ],
        "sweet_spots": ["网络中枢", "分布式网关", "监控服务", "系统探针", "API中继"]
    },
    "RUST": {
        "name": "Rust",
        "tier": "GOLDEN_CORE",
        "roi_score": 8.5,
        "necessity_score": 10.0,
        "summary": "系统级极致性能与内存安全终极防线。0 运行时开销，0 GC 垃圾回收，精准编译器错误自愈指导。",
        "build_speed": "SLOW_BUT_SOUND",   # 宏与单态化导致编译偏慢，但静态保障坚不可摧
        "toolchain_size_mb": 1800,         # ~1.8GB
        "compile_ram_mb": 2500,            # 编译时吃 2-4GB RAM (需预留内存)
        "runtime_ram_mb": 5,               # 运行时仅耗 5-15MB RAM
        "ai_synthesis_pass_rate": 0.88,    # 编译器报错精确到字符，AI 极易根据借用检查器错误闭环自愈
        "deploy_form": "NATIVE_MACHINE_CODE",
        "irreplaceable_domains": [
            "高性能计算密集型存储与检索内核 (如向量库/列存引擎)",
            "高频量化交易纳秒级撮合与风控 (Ultra-Low Latency Trading)",
            "操作系统内核、驱动、WebAssembly 与密码学核心",
            "替代 C/C++ 消除所有内存越界与并发数据竞争"
        ],
        "strengths": [
            "所有权与生命周期静态检查，运行期 0 GC 暂停",
            "性能与 C/C++ 相当，但彻底杜绝空指针异常与内存泄漏",
            "极其强大的 Cargo 包管理器与生态 (Tokio, Serde, Polars, PyO3)",
            "PyO3 能够极速将 Rust 内核包装为原生 Python 扩展包"
        ],
        "weaknesses": [
            "编译较慢，多核编译需要 2GB 以上空闲 RAM",
            "快速原型迭代不如 Python/Go 迅速"
        ],
        "sweet_spots": ["计算内核", "向量检索", "高性能存储", "算法加速", "高频交易"]
    },
    "TYPESCRIPT": {
        "name": "TypeScript / Node.js (or Bun)",
        "tier": "GOLDEN_CORE",
        "roi_score": 9.5,
        "necessity_score": 10.0,
        "summary": "现代全栈、前端 UI、开放插件与人类交互视窗的绝对霸主。生态最繁荣，AI 训练语料最丰富。",
        "build_speed": "FAST_JIT",
        "toolchain_size_mb": 250,
        "compile_ram_mb": 300,
        "runtime_ram_mb": 40,
        "ai_synthesis_pass_rate": 0.95,
        "deploy_form": "V8_RUNTIME_OR_BUN_BUNDLE",
        "irreplaceable_domains": [
            "现代响应式 Web 前端 (React/Next.js/Vue/Svelte)",
            "富交互桌面控制台与大盘 (Electron/Tauri)",
            "编辑器与智能体插件生态 (VSCode/Cursor/OpenClaw Plugins)",
            "全栈 BFF 胶水层与 Serverless 云函数"
        ],
        "strengths": [
            "全球最大开源生态 (npm)，UI 框架与可视化组件库应有尽有",
            "强类型系统 (TypeScript Generics)，大幅削减前后端类型漂移",
            "全网 AI 拥有最大规模的代码语料库，代码补全与重构准确率极高",
            "配合 Bun 或 Node.js JIT 执行，吞吐性能优于纯 Python"
        ],
        "weaknesses": [
            "不适合密集数学计算与裸机硬件交互",
            "node_modules 历史包袱容易产生深层目录黑洞"
        ],
        "sweet_spots": ["可视化前端", "管理大盘", "交互门面", "插件系统", "BFF中间层"]
    },
    "PYTHON": {
        "name": "Python",
        "tier": "GOLDEN_CORE",
        "roi_score": 9.2,
        "necessity_score": 10.0,
        "summary": "AI 大模型、多智能体协同、数据科学与量化回测的统领者。开发生产力无可匹敌，天下胶水第一。",
        "build_speed": "INSTANT_NO_COMPILE",
        "toolchain_size_mb": 300,
        "compile_ram_mb": 50,
        "runtime_ram_mb": 35,
        "ai_synthesis_pass_rate": 0.96,
        "deploy_form": "INTERPRETED_BYTECODE",
        "irreplaceable_domains": [
            "大模型智能体编排 (LangChain/Prism/OpenClaw/MCP)",
            "量化金融策略研究与回测 (Backtrader/VnPy/Qlib)",
            "深度学习算法训练与推理适配 (PyTorch/Transformers)",
            "快速原型研发与端到端敏捷流水线"
        ],
        "strengths": [
            "开发周期最短，表达能力极强，3行代码顶编译语言20行",
            "在 AI 与科学计算领域具有不可逾越的生态垄断地位",
            "动态性强，作为主架构中的'编排胶水'与'策略外层'体验最佳"
        ],
        "weaknesses": [
            "纯计算性能与并发较低 (GIL 限制)",
            "单静态二进制打包沉重 (PyInstaller 容易体积臃肿)"
        ],
        "sweet_spots": ["AI编排", "策略研究", "数据胶水", "自动化脚本", "原型实验"]
    },
    "CPP": {
        "name": "C / C++ (C++20)",
        "tier": "GOLDEN_CORE",
        "roi_score": 6.8,
        "necessity_score": 9.2,
        "summary": "裸机硬件驱动、GPU 自定义算子与游戏引擎底层基石。不可替代但无需全量使用，宜作为微内核存在。",
        "build_speed": "MODERATE",
        "toolchain_size_mb": 1200,
        "compile_ram_mb": 1500,
        "runtime_ram_mb": 5,
        "ai_synthesis_pass_rate": 0.85,
        "deploy_form": "NATIVE_SHARED_LIB_OR_EXE",
        "irreplaceable_domains": [
            "GPU 深度学习加速算子 (CUDA / Cutlass / TensorRT)",
            "操作系统内核交互与硬件设备直通驱动",
            "工业级 3D 渲染与物理引擎 (Unreal / Vulkan)",
            "极低延时网络驱动与音视频硬件编解码 (FFmpeg/WebRTC)"
        ],
        "strengths": [
            "对底层硬件内存与 CPU 寄存器拥有绝对控制力",
            "全球存量顶尖高性能系统与 CUDA 库的最原生绑定",
            "无与伦比的极端硬件优化上限"
        ],
        "weaknesses": [
            "手动内存管理极易产生段错误与越界 (除非极严谨的现代 C++20)",
            "依赖与构建体系分散 (CMake 复杂度较高)"
        ],
        "sweet_spots": ["CUDA加速算子", "音视频底层", "硬件设备接入", "性能极值微内核"]
    },
    "ZIG": {
        "name": "Zig",
        "tier": "SPECIAL_LIGHTWEIGHT",
        "roi_score": 9.6,
        "necessity_score": 8.2,
        "summary": "极轻量、无隐式控制流的新一代 C 替代黑马。自带跨平台 C/C++ 编译器，工具链仅数十兆。",
        "build_speed": "FAST",
        "toolchain_size_mb": 150,          # 工具链仅仅 ~150MB，极度紧凑
        "compile_ram_mb": 200,
        "runtime_ram_mb": 3,
        "ai_synthesis_pass_rate": 0.86,
        "deploy_form": "SINGLE_STATIC_BINARY",
        "irreplaceable_domains": [
            "极轻量嵌入式与系统工具开发",
            "极简跨平台构建（自带 `zig cc` / `zig c++` 可直接编译 C/C++）",
            "零内存黑盒隐藏分配的确定性嵌入式核心"
        ],
        "strengths": [
            "极其轻量，一个解压文件夹搞定所有，不向系统注册任何杂质",
            "无任何隐式内存分配，显式传递 Allocator，程序行为 100% 确定",
            "自带天下最强的跨平台交叉编译器，甚至能帮 C/C++ 项目做轻量交叉编译"
        ],
        "weaknesses": [
            "生态尚在成长期，第三方库数量不及 Go/Rust"
        ],
        "sweet_spots": ["极轻量CLI", "跨平台交叉构建", "确定性嵌入式内核", "极速小型系统组件"]
    }
}

# =============================================================================
# 二、 坚决淘汰/降级的低性价比技术栈台账 (Discarded / Deprecated Stacks)
# =============================================================================
DISCARDED_STACKS: Dict[str, Dict[str, Any]] = {
    "JAVA": {
        "reason": "臃肿笨重，内存性价比极低",
        "details": "JVM 启动即吃 500MB+ 堆内存；在微服务和轻量云原生场景下，完全被 Go 和 Rust 降维替代。现代 AI 集群与装具工程严禁引入 Java。"
    },
    "SCALA": {
        "reason": "语法复杂度失控，生态快速衰退",
        "details": "编译极其缓慢，隐式转换与类型系统极其晦涩，AI 容易产生幻觉代码，长期维护成本属于灾难级。"
    },
    "PHP": {
        "reason": "领域退化，与现代系统工程脱节",
        "details": "生态局限于传统建站与内容管理；在系统底座、高并发网络中枢与 AI 智能体体系中无任何技术优势。"
    },
    "RUBY": {
        "reason": "执行缓慢，高并发性能落后",
        "details": "除特定 Rails 单体建站外，现代微服务和工具链已无竞争力，并发模型落后于 Go/Rust/Node。"
    },
    "HASKELL": {
        "reason": "心智负担极重，工程落地性价比极低",
        "details": "纯函数式 Monad 数学模型学习曲线陡峭，招聘与智能体维护成本高，仅适合学术论文与形式化验证。"
    },
    "DART_FLUTTER": {
        "reason": "领域单一，非移动端场景冗余过重",
        "details": "除非明确要开发一套跨双端原生手机 App，否则在后端、系统工具与 Web 面板中属于严重的冗余负担。"
    },
    "JULIA": {
        "reason": "JIT 预热延迟严重 (Time-to-First-Plot)",
        "details": "首次执行存在明显的 JIT 编译停顿，包管理器体积庞大，完全不适合高响应微服务与极速命令行工具。"
    }
}


def get_golden_summary_table() -> str:
    """输出黄金矩阵对齐摘要表格"""
    lines = [
        "| 语言 | 梯队评级 | 性价比(ROI) | 必要性 | 编译耗时 | 编译内存 | 运行时内存 | AI通过率 | 核心定位与搭配槽位 |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |"
    ]
    for k, v in GOLDEN_COMPILER_STACKS.items():
        lines.append(
            f"| **{v['name']}** | `{v['tier']}` | **{v['roi_score']}/10** | **{v['necessity_score']}/10** | "
            f"{v['build_speed']} | ~{v['compile_ram_mb']}MB | ~{v['runtime_ram_mb']}MB | "
            f"{int(v['ai_synthesis_pass_rate']*100)}% | {v['summary'][:26]}... |"
        )
    return "\n".join(lines)
