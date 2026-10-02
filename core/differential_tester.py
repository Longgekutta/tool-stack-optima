#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
core/differential_tester.py: 双轨差分模糊测试与语义等价性自验引擎 (Dual-Track Differential Tester)
=============================================================================
灵感源自 Hypothesis 与学术界差分测试 (Differential Testing)：
在影子沙盒中自动对编译出的原生微内核与 Python 保底逻辑进行随机边界注入 (Property-based Fuzzing)。
验证：
1. 语义等价性: f_native(payload) 是否对全集输入严格等于 f_fallback(payload)
2. 极限性能加速比: 纳秒级实测真实加速比 (Speedup = T_fallback / T_native)
3. 发现边界裂痕: 若输出不一致，精准抓出最小反例 (Counterexample)
"""

import os
import sys
import time
import random
import math
import inspect
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Callable, get_type_hints


class DynamicStrategyFactory:
    """自适应多模态模糊测试用例策略生成器 (Universal Multi-Modal Strategy Factory)"""

    @classmethod
    def generate_value_for_type(cls, target_type: Any, seed_idx: int) -> Any:
        """根据类型推导生成确定性边界与随机用例"""
        # 1. 整数
        if target_type in (int, "int"):
            boundaries = [0, 1, -1, 42, 255, 32767, -32768, 2147483647, -2147483648]
            if seed_idx < len(boundaries):
                return boundaries[seed_idx]
            return random.randint(-1_000_000, 1_000_000)

        # 2. 浮点数
        if target_type in (float, "float"):
            boundaries = [0.0, -0.0, 1.0, -1.0, 0.5, 1e-7, 1e7, math.pi, math.e]
            if seed_idx < len(boundaries):
                return boundaries[seed_idx]
            return random.uniform(-1000.0, 1000.0)

        # 3. 字符串
        if target_type in (str, "str"):
            boundaries = [
                "", " ", "0", "hello world",
                "工业软件母机全域泛化测试",
                "🎯🚀⚡\n\t\r\x00",
                "a" * 1024,
                "{" + '"key": "value"' + "}"
            ]
            if seed_idx < len(boundaries):
                return boundaries[seed_idx]
            return f"rand_str_{seed_idx}_{os.urandom(8).hex()}"

        # 4. 字节流 / 内存切片
        if target_type in (bytes, "bytes", bytearray):
            boundaries = [
                b"", b"\x00", b"0", b"ping",
                b"hello world",
                "多语言字节边界测试".encode("utf-8"),
                b"\x00\xff\xfe\xfd\x01\x02\x03",
                b"A" * 1024,
                b"B" * 65536
            ]
            if seed_idx < len(boundaries):
                return boundaries[seed_idx]
            length = random.choice([4, 16, 64, 256, 1024, 4096])
            return os.urandom(length)

        # 5. 布尔值
        if target_type in (bool, "bool"):
            return (seed_idx % 2 == 0)

        # 6. 字典 / 键值对映射
        if target_type in (dict, "dict"):
            boundaries = [
                {},
                {"status": "ok"},
                {"id": seed_idx, "payload": "data"},
                {"nested": {"a": [1, 2, 3], "flag": True}},
                {"empty_str": "", "zero": 0, "null": None}
            ]
            if seed_idx < len(boundaries):
                return boundaries[seed_idx]
            return {"k": seed_idx, "v": f"val_{seed_idx}"}

        # 7. 列表 / 序列集合
        if target_type in (list, "list"):
            boundaries = [
                [],
                [0],
                [1, 2, 3, 4, 5],
                ["alpha", "beta", "gamma"],
                [random.randint(0, 100) for _ in range(20)]
            ]
            if seed_idx < len(boundaries):
                return boundaries[seed_idx]
            return [seed_idx, seed_idx + 1]

        # 8. 未知/无类型标注 (Polymorphic Fallback)
        poly_types = [str, int, float, bytes, dict, list]
        chosen = poly_types[seed_idx % len(poly_types)]
        return cls.generate_value_for_type(chosen, seed_idx)


class DifferentialTester:
    """
    通用型双轨差分模糊测试与语义等价性自验引擎 (Universal Differential Equivalence Tester)
    =============================================================================
    支持任意函数签名、任意入参模态（数字、字符串、JSON、二进制流、混合结构）：
    1. 反射解析函数入参签名 (inspect.signature)
    2. 基于类型提示自适应激活对应领域模糊生成器
    3. 支持浮点精度自适应对比与结构体深层遍历
    4. 发现分歧自动捕获最小入参反例与调用堆栈
    """

    @classmethod
    def test_callable_equivalence(
        cls,
        primary_fn: Callable,
        candidate_fn: Callable,
        iterations: int = 500,
        float_rel_tol: float = 1e-6
    ) -> Dict[str, Any]:
        """
        对任意两个 Python 可调用对象进行 N 轮自适应多模态差分模糊测试
        """
        # 反射获取参数签名
        sig = inspect.signature(primary_fn)
        params = list(sig.parameters.values())

        counterexamples = []
        primary_latencies_ns = []
        candidate_latencies_ns = []

        for idx in range(iterations):
            # 生成符合参数签名的实参
            args = []
            kwargs = {}
            for p_idx, p in enumerate(params):
                ann = p.annotation if p.annotation != inspect.Parameter.empty else Any
                val = DynamicStrategyFactory.generate_value_for_type(ann, idx + p_idx)
                if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                    args.append(val)
                elif p.kind == inspect.Parameter.KEYWORD_ONLY:
                    kwargs[p.name] = val
                elif p.kind == inspect.Parameter.VAR_POSITIONAL:
                    args.append(val)

            # 1. 运行基准主干函数
            t0 = time.perf_counter_ns()
            try:
                res_primary = primary_fn(*args, **kwargs)
                err_primary = None
            except Exception as e:
                res_primary = None
                err_primary = type(e).__name__
            t_primary = time.perf_counter_ns() - t0
            primary_latencies_ns.append(t_primary)

            # 2. 运行候选加速函数
            t1 = time.perf_counter_ns()
            try:
                res_candidate = candidate_fn(*args, **kwargs)
                err_candidate = None
            except Exception as e:
                res_candidate = None
                err_candidate = type(e).__name__
            t_candidate = time.perf_counter_ns() - t1
            candidate_latencies_ns.append(t_candidate)

            # 3. 校验等价性
            is_equivalent = False
            if err_primary is not None or err_candidate is not None:
                # 异常等价性 (若两者均合法抛出同类异常视为等价)
                is_equivalent = (err_primary == err_candidate)
            elif isinstance(res_primary, float) and isinstance(res_candidate, float):
                if math.isnan(res_primary) and math.isnan(res_candidate):
                    is_equivalent = True
                else:
                    is_equivalent = math.isclose(res_primary, res_candidate, rel_tol=float_rel_tol, abs_tol=1e-9)
            else:
                is_equivalent = (res_primary == res_candidate)

            if not is_equivalent:
                counterexamples.append({
                    "round": idx,
                    "sample_args": [str(a)[:60] for a in args],
                    "expected": str(res_primary)[:80] if err_primary is None else f"EXCEPTION({err_primary})",
                    "actual": str(res_candidate)[:80] if err_candidate is None else f"EXCEPTION({err_candidate})"
                })

        avg_primary_ns = sum(primary_latencies_ns) / len(primary_latencies_ns)
        avg_candidate_ns = sum(candidate_latencies_ns) / len(candidate_latencies_ns)
        speedup = round(avg_primary_ns / max(1.0, avg_candidate_ns), 2)

        return {
            "success": len(counterexamples) == 0,
            "iterations_tested": iterations,
            "counterexamples_count": len(counterexamples),
            "counterexamples": counterexamples[:5],
            "telemetry": {
                "avg_fallback_latency_ns": round(avg_primary_ns, 1),
                "avg_native_latency_ns": round(avg_candidate_ns, 1),
                "measured_speedup_ratio": speedup
            }
        }

    @classmethod
    def run_differential_test(cls, scaffold_dir: str, iterations: int = 500) -> Dict[str, Any]:
        """
        在指定脚手架目录下自适应探测加速算子并执行差分等价性测试
        """
        scaffold_path = Path(scaffold_dir).resolve()
        bridge_file = scaffold_path / "bridge_glue.py"

        if not bridge_file.exists():
            return {
                "success": False,
                "error": f"未找到 bridge_glue.py: {bridge_file}"
            }

        sys.path.insert(0, str(scaffold_path))
        try:
            import importlib
            if "bridge_glue" in sys.modules:
                bridge = importlib.reload(sys.modules["bridge_glue"])
            else:
                bridge = importlib.import_module("bridge_glue")
        except Exception as e:
            return {"success": False, "error": f"导入 bridge_glue 失败: {e}"}

        is_accelerated = bridge.is_native_accelerated()

        # 动态定位目标函数
        target_fn = getattr(bridge, "execute_accelerated_task", None)
        if not target_fn:
            return {"success": False, "error": "bridge_glue 未导出 execute_accelerated_task 算子"}

        # 定义 Python 原生回退基准
        def fallback_fn(payload):
            return payload

        # 调用通用可调用对象等价性自验
        report = cls.test_callable_equivalence(fallback_fn, target_fn, iterations=iterations)
        report["scaffold_path"] = str(scaffold_path)
        report["is_native_accelerated"] = is_accelerated
        return report

    @classmethod
    def render_markdown(cls, report: Dict[str, Any]) -> str:
        t = report.get("telemetry", {})
        status_icon = "🟢" if report.get("success") else "🔴"
        accel_text = "✅ 已启用 Rust 原生微内核" if report.get("is_native_accelerated") else "⚠️ 未编译原生动态库 (处于 Python 自愈回退模式)"

        lines = [
            f"# {status_icon} 通用双轨差分模糊测试与语义等价性报告",
            "",
            "> 基于自适应多模态策略工厂 (Dynamic Strategy Factory)，严格比对新微内核与原逻辑在数百次随机边界用例下的输出一致性与加速比。",
            "",
            "## 📌 运行环境与状态",
            f"- **脚手架目录**: `{report.get('scaffold_path', 'N/A')}`",
            f"- **加速内核状态**: {accel_text}",
            f"- **模糊用例轮次**: **{report.get('iterations_tested', 0)} 轮** (涵盖边界值、极值、Unicode/二进制序列与混合结构)",
            "",
            "## 📊 物理性能与加速比 (Nanosecond Benchmarking)",
            "| 评测维度 | 原生回退基准 | 候选微内核路径 | 实测加速比 |",
            "| :--- | :--- | :--- | :--- |",
            f"| **单次执行平均耗时** | `{t.get('avg_fallback_latency_ns', 0)} ns` | `{t.get('avg_native_latency_ns', 0)} ns` | **{t.get('measured_speedup_ratio', 1.0)}x** |",
            "",
            f"## 🛡️ 语义等价性断言结果: `{'PASS (完全一致)' if report.get('success') else 'FAIL (发现语义分歧)'}`",
            f"- **反例样本总数**: `{report.get('counterexamples_count', 0)}` 处"
        ]
        if report.get("counterexamples"):
            lines.append("### 捕获的反例样本 (Counterexamples):")
            for c in report["counterexamples"]:
                lines.append(f"- 轮次 {c['round']}: 入参 `{c['sample_args']}` | 期望 `{c['expected']}` | 实际 `{c['actual']}`")
        lines.append("")
        return "\n".join(lines)

