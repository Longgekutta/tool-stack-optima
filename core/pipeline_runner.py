#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
core/pipeline_runner.py: 工业软件母机通用跨工具协同流水线 (Universal Meta-Toolchain Pipeline)
=============================================================================
遵循高内聚、低耦合原则：
1. 三大母机皆可单兵作战 (Standalone CLI)。
2. 通过 UCFS v1.0 与标准 JSON 接口实现无缝流水线协作：
   - Phase 1: tool-taxonomy-arbiter (架构形态仲裁与物理不变量约束)
   - Phase 2: tool-stack-optima (代码指纹张量、实证瓶颈推导与帕累托选型)
   - Phase 3: tool-code-optima (体积断层剖析、未用依赖提纯与控制流复杂度)
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

from .repo_resolver import RepoResolver
from .codebase_profiler import CodebaseProfiler
from .optimizer import PolyglotArchitectureOptimizer
from .tournament_engine import EmpiricalBenchmarkHarness


class MetaToolchainPipeline:
    """
    通用跨工具协同调度器。
    协同工作时整合全维信息，解耦时各自独立可用。
    """

    @classmethod
    def run_pipeline(cls, target_input: str) -> Dict[str, Any]:
        resolved_path, meta = RepoResolver.resolve(target_input)
        repo_name = os.path.basename(resolved_path)

        result: Dict[str, Any] = {
            "target_input": target_input,
            "resolved_path": resolved_path,
            "repo_name": repo_name,
            "metadata": meta,
            "phase_taxonomy": None,
            "phase_stack_optima": None,
            "phase_code_optima": None
        }

        # -------------------------------------------------------------
        # Phase 1: tool-taxonomy-arbiter (形态裁定与物理验真)
        # -------------------------------------------------------------
        arbiter_dir = Path(r"D:\github\tool-taxonomy-arbiter")
        if arbiter_dir.exists() and (arbiter_dir / "main.py").exists():
            try:
                import subprocess
                proc = subprocess.run(
                    [sys.executable, str(arbiter_dir / "main.py"), "verify", resolved_path, "--json"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                raw_out = proc.stdout.strip()
                if raw_out:
                    ver_data = json.loads(raw_out)
                    result["phase_taxonomy"] = {
                        "archetype": ver_data.get("deduced_archetype", "unknown"),
                        "suggested_name": ver_data.get("repo_name", repo_name),
                        "physical_verification_status": ver_data.get("status", "UNKNOWN"),
                        "purity_score": ver_data.get("purity_score", 100),
                        "violations": ver_data.get("violations", []),
                        "checks_performed": ver_data.get("checks_performed", [])
                    }
            except Exception as e:
                result["phase_taxonomy"] = {"error": str(e)}

        # -------------------------------------------------------------
        # Phase 2: tool-stack-optima (代码指纹、瓶颈推导与帕累托选拔)
        # -------------------------------------------------------------
        try:
            profile = CodebaseProfiler.profile_repository(resolved_path)
            opt_plan = PolyglotArchitectureOptimizer.optimize_repo(resolved_path)
            bench_spec = EmpiricalBenchmarkHarness.create_spec_from_repo(resolved_path)
            eval_report = EmpiricalBenchmarkHarness.evaluate(bench_spec, execute_live=False)

            result["phase_stack_optima"] = {
                "profile": profile,
                "diagnosed_bottlenecks": opt_plan.get("diagnosed_bottlenecks", []),
                "architecture_blueprint": opt_plan.get("architecture_blueprint", {}),
                "evaluation_report": eval_report.to_dict()
            }
        except Exception as e:
            result["phase_stack_optima"] = {"error": str(e)}

        # -------------------------------------------------------------
        # Phase 3: tool-code-optima (代码级体积、依赖与AST认知复杂度)
        # -------------------------------------------------------------
        code_optima_dir = Path(r"D:\github\tool-code-optima")
        if code_optima_dir.exists() and (code_optima_dir / "main.py").exists():
            try:
                import subprocess
                proc = subprocess.run(
                    [sys.executable, str(code_optima_dir / "main.py"), "audit", resolved_path, "--json"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                raw_out = proc.stdout.strip()
                if raw_out:
                    audit_res = json.loads(raw_out)
                    result["phase_code_optima"] = {
                        "score": audit_res.get("score"),
                        "rating": audit_res.get("rating"),
                        "archetype_profile": audit_res.get("profile", {}),
                        "bloat_summary": audit_res.get("bloat_summary", {}),
                        "imports_summary": audit_res.get("imports_summary", {}),
                        "complexity_summary": audit_res.get("complexity_summary", {}),
                        "architecture_summary": audit_res.get("architecture_summary", {})
                    }
            except Exception as e:
                result["phase_code_optima"] = {"error": str(e)}

        return result

    @classmethod
    def render_markdown(cls, pipeline_data: Dict[str, Any]) -> str:
        lines = []
        name = pipeline_data.get("repo_name", "Unknown")
        inp = pipeline_data.get("target_input", "")
        resolved = pipeline_data.get("resolved_path", "")

        lines.append(f"# ⚙️ 工业软件母机全域协同审计报告: {name}")
        lines.append(f"> **目标输入**：`{inp}` ｜ **物理定位路径**：`{resolved}`  ")
        lines.append(f"> **协作模式**：`tool-taxonomy-arbiter` ➔ `tool-stack-optima` ➔ `tool-code-optima` 三位一体正交流水线\n")

        # Phase 1
        lines.append("## 一、 架构形态与物理合规验真 (tool-taxonomy-arbiter)")
        tax = pipeline_data.get("phase_taxonomy")
        if tax and "error" not in tax:
            status_icon = "🟢 PASS" if tax.get("physical_verification_status") == "PASS" else "🔴 FAIL"
            lines.append(f"- **确定性最小必要形态**：【 `{str(tax.get('archetype', 'UNKNOWN')).upper()}` 】 (建议命名: `{tax.get('suggested_name', name)}`)")
            if tax.get("confidence") is not None:
                lines.append(f"- **裁决置信度**：`{tax['confidence']:.1%}`")
            if tax.get("minimal_viable_rationale"):
                lines.append(f"- **最小必要理由**：{tax['minimal_viable_rationale']}")
            lines.append(f"- **物理运行期合规**：{status_icon} (架构纯度分: `{tax.get('purity_score', 100)}/100`)")
            if tax.get("violations"):
                lines.append(f"  - ⚠️ 违规项清单: {', '.join(tax['violations'])}")
        else:
            lines.append("⚠️ 形态仲裁母机未激活或未检出。\n")

        # Phase 2
        lines.append("\n## 二、 代码库事实指纹与帕累托选型 (tool-stack-optima)")
        stk = pipeline_data.get("phase_stack_optima")
        if stk and "error" not in stk:
            prof = stk["profile"]
            lines.append(f"- **物理事实**：主导语言 `{prof['dominant_language']}` ｜ 代码行数 `{prof['total_loc']}` 行 ｜ 源文件 `{prof['total_code_files']}` 个")
            b_list = stk.get("diagnosed_bottlenecks", [])
            if b_list:
                lines.append(f"- **检出物理瓶颈 ({len(b_list)} 处)**：")
                for b in b_list:
                    lines.append(f"  - ⚠️ `[{b['category']}]` ({b['severity']}): {b['impact']}")
            else:
                lines.append("- **检出物理瓶颈**：✅ 未检出明显的物理架构级瓶颈")

            eval_rep = stk.get("evaluation_report", {})
            opt_sol = eval_rep.get("optimal_solution")
            if opt_sol:
                lines.append(f"- **帕累托最优推荐方案**：**{opt_sol['name']}** (TOPSIS 贴近度: `{opt_sol['topsis_score']}/100`)")
                lines.append(f"  - 推荐技术栈: `{'+'.join(opt_sol['language_stack'])}` ｜ 架构机制: {opt_sol['technical_description']}")
        else:
            lines.append("⚠️ 架构求解母机未激活或处理异常。\n")

        # Phase 3
        lines.append("\n## 三、 代码体积断层与复杂度治理 (tool-code-optima)")
        cod = pipeline_data.get("phase_code_optima")
        if cod and "error" not in cod:
            lines.append(f"- **综合健康评分**：`{cod.get('score')}/100` (工程评级: `{cod.get('rating')}`)")
            bloat = cod.get("bloat_summary", {})
            lines.append(f"- **体积与产物**：总物理大小 `{bloat.get('total_mb')} MB` ｜ 非代码膨胀率 `{bloat.get('bloat_ratio_pct')}%`")
            imp = cod.get("imports_summary", {})
            lines.append(f"- **依赖纯度**：未用引用 `{imp.get('total_unused')} 个` ｜ 重型依赖 `{imp.get('total_heavy')} 个`")
            comp = cod.get("complexity_summary", {})
            lines.append(f"- **认知复杂度**：控制流嵌套深度超限 `{comp.get('deep_nestings')} 处` ｜ 巨型长函数 `{comp.get('bloated_functions')} 个`")
            dag = cod.get("architecture_summary", {})
            dag_str = "✓ 纯净有向无环图 (Acyclic DAG)" if dag.get("is_acyclic_dag") else f"✗ 存在 {dag.get('circular_cycles_count')} 处循环依赖"
            lines.append(f"- **架构拓扑状态**：{dag_str}")
        else:
            lines.append("⚠️ 代码卡尺母机未激活或未包含相应模块。\n")

        lines.append("\n---\n*本报告由全域工业软件母机流水线全自动实测推导生成，杜绝任何人工虚假数据。*")
        return "\n".join(lines)
