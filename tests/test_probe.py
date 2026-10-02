#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_probe.py: Tests for ProbeRunner adaptive codebase physical probe.
"""
import unittest
import os
import sys
import tempfile
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.probe_runner import ProbeRunner


class TestProbeRunner(unittest.TestCase):

    def test_detect_probe_command_for_tests(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "tests"
            test_dir.mkdir()
            (test_dir / "test_sample.py").write_text("import unittest\n", encoding="utf-8")

            info = ProbeRunner.detect_probe_command(tmpdir)
            self.assertEqual(info["type"], "UNITTEST_DISCOVERY")
            self.assertIn("discover tests", info["command"])

    def test_detect_probe_command_for_cli(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "cli.py").write_text("print('hello')\n", encoding="utf-8")

            info = ProbeRunner.detect_probe_command(tmpdir)
            self.assertEqual(info["type"], "CLI_FACADE")
            self.assertIn("cli.py --help", info["command"])

    def test_live_probe_execution(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cli_path = Path(tmpdir) / "cli.py"
            cli_path.write_text("""
import sys
if '--help' in sys.argv:
    print('Usage: cli.py [options]')
    sys.exit(0)
""", encoding="utf-8")

            res = ProbeRunner.probe(tmpdir)
            self.assertEqual(res["status"], "success")
            self.assertIn("telemetry", res)
            self.assertGreater(res["telemetry"]["peak_ram_mb"], 1.0)
            self.assertGreater(res["telemetry"]["latency_ms"], 0.0)
            self.assertIn("ratings", res)

            markdown = ProbeRunner.render_markdown(res)
            self.assertIn("目标工程实机物理基线探针报告", markdown)


if __name__ == "__main__":
    unittest.main()
