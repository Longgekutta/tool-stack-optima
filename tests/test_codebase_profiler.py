#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_codebase_profiler.py: Tests for RepoResolver and CodebaseProfiler.
"""
import unittest
import os
import sys
import tempfile
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.repo_resolver import RepoResolver
from core.codebase_profiler import CodebaseProfiler
from core.optimizer import PolyglotArchitectureOptimizer


class TestCodebaseProfiler(unittest.TestCase):

    def test_local_repo_resolution_and_profiling(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a mock repo structure
            p_core = Path(tmpdir) / "core"
            p_core.mkdir(parents=True)

            py_file = p_core / "worker.py"
            py_file.write_text("""
import asyncio
import subprocess

async def process_task(task_id):
    # Simulate high frequency subprocess and async
    res = subprocess.run(["echo", task_id], capture_output=True)
    return res.stdout
""", encoding="utf-8")

            # 1. Test RepoResolver
            resolved_path, meta = RepoResolver.resolve(tmpdir)
            self.assertEqual(meta["type"], "LOCAL_DIR")
            self.assertEqual(resolved_path, str(Path(tmpdir).resolve()))

            # 2. Test CodebaseProfiler
            profile = CodebaseProfiler.profile_repository(resolved_path)
            self.assertEqual(profile["dominant_language"], "Python")
            self.assertEqual(profile["total_code_files"], 1)
            self.assertGreater(profile["total_loc"], 5)
            self.assertGreater(profile["detected_signals_count"]["subprocess_calls"], 0)
            self.assertGreater(profile["detected_signals_count"]["concurrency_models"], 0)

            # 3. Test Optimizer optimize_repo
            opt = PolyglotArchitectureOptimizer.optimize_repo(tmpdir)
            self.assertIn("architecture_blueprint", opt)
            self.assertIn("diagnosed_bottlenecks", opt)
            self.assertEqual(opt["target_input"], tmpdir)


if __name__ == "__main__":
    unittest.main()
