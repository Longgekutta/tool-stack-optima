#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
core/shadow_experiment.py: GitHub-Scientist 模式双轨影子观测与零风险实验器
=============================================================================
彻底解决“既不越权破坏生产、又能兼顾真实改善效果”的核心矛盾：
1. 零越权与零中断保证 (Zero Overstepping & Zero Outage):
   - 主业务调用永远返回原始生产逻辑 (Primary) 的结果，生产故障率数学级恒等于 0。
2. 真实改善与后台影子比对 (Shadow Execution & Telemetry):
   - 在后台异步或同步调用候选加速微内核 (Candidate)，捕获输出一致性与微秒级时延。
   - 若候选微内核崩溃或抛出异常，安全捕获并记录日志，绝不向外扩散异常。
3. 统计学置信度积累:
   - 累积统计 10,000+ 次真实调用的匹配率 (Match Rate) 与加速比 (Speedup)。
"""

import time
import functools
from typing import Callable, Any, Dict, List, Optional, Tuple


class ShadowExperiment:
    """GitHub-Scientist 风格双轨影子实验器"""

    def __init__(self, name: str = "default_experiment"):
        self.name = name
        self.total_runs = 0
        self.match_count = 0
        self.mismatch_count = 0
        self.candidate_errors = 0
        self.primary_total_ns = 0
        self.candidate_total_ns = 0
        self.last_mismatch_detail: Optional[Dict[str, Any]] = None

    def execute(self, primary_fn: Callable, candidate_fn: Optional[Callable], *args, **kwargs) -> Any:
        """
        双轨执行：
        - 永远返回 primary_fn 的计算结果 (保证生产绝对不中断、不越权)
        - 影子执行 candidate_fn 并统计性能与等价性
        """
        self.total_runs += 1

        # 1. 生产权威路径 (Primary Path)
        t0 = time.perf_counter_ns()
        primary_result = primary_fn(*args, **kwargs)
        t_primary = time.perf_counter_ns() - t0
        self.primary_total_ns += t_primary

        # 2. 影子候选路径 (Candidate Path)
        if candidate_fn is not None:
            try:
                t1 = time.perf_counter_ns()
                candidate_result = candidate_fn(*args, **kwargs)
                t_candidate = time.perf_counter_ns() - t1
                self.candidate_total_ns += t_candidate

                # 3. 结果等价性检验
                if candidate_result == primary_result:
                    self.match_count += 1
                else:
                    self.mismatch_count += 1
                    self.last_mismatch_detail = {
                        "primary_result_type": type(primary_result).__name__,
                        "candidate_result_type": type(candidate_result).__name__,
                        "args_repr": str(args)[:100]
                    }
            except Exception as e:
                # 候选路径发生任何异常，严密隔离，绝对不影响生产主返回值
                self.candidate_errors += 1
                self.mismatch_count += 1
                self.last_mismatch_detail = {"candidate_exception": str(e)}

        return primary_result

    def get_summary(self) -> Dict[str, Any]:
        """输出置信度报告"""
        avg_primary_ns = round(self.primary_total_ns / max(1, self.total_runs), 1)
        avg_candidate_ns = round(self.candidate_total_ns / max(1, self.total_runs - self.candidate_errors), 1) if (self.total_runs - self.candidate_errors) > 0 else 0.0
        speedup = round(avg_primary_ns / max(1.0, avg_candidate_ns), 2) if avg_candidate_ns > 0 else 1.0
        match_rate = round((self.match_count / max(1, self.total_runs)) * 100, 2)

        return {
            "experiment_name": self.name,
            "total_runs": self.total_runs,
            "match_count": self.match_count,
            "mismatch_count": self.mismatch_count,
            "candidate_errors": self.candidate_errors,
            "match_rate_percent": match_rate,
            "avg_primary_latency_ns": avg_primary_ns,
            "avg_candidate_latency_ns": avg_candidate_ns,
            "measured_speedup_ratio": speedup,
            "is_statistically_confident": match_rate >= 99.9 and self.total_runs >= 100,
            "last_mismatch": self.last_mismatch_detail
        }


def shadow_experiment(name: str, candidate_fn: Optional[Callable] = None):
    """
    一行式非侵入装饰器：
    @shadow_experiment("accel_calc", candidate_fn=rust_native_calc)
    def original_calc(x):
        ...
    """
    exp = ShadowExperiment(name=name)

    def decorator(primary_fn: Callable):
        @functools.wraps(primary_fn)
        def wrapper(*args, **kwargs):
            return exp.execute(primary_fn, candidate_fn, *args, **kwargs)
        wrapper.experiment = exp
        return wrapper
    return decorator
