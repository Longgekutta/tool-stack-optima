#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_scaffold.py: Tests for ScaffoldGenerator automated microkernel synthesis.
"""
import unittest
import os
import sys
import tempfile
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.scaffold_generator import ScaffoldGenerator


class TestScaffoldGenerator(unittest.TestCase):

    def test_scaffold_generation_end_to_end(self):
        with tempfile.TemporaryDirectory() as src_repo, tempfile.TemporaryDirectory() as out_dir:
            # Create a mock repo with ctypes FFI bottleneck (>3 lowlevel_system_apis signals)
            src_file = Path(src_repo) / "driver.py"
            src_file.write_text("""
import ctypes

def call_native():
    lib = ctypes.windll.kernel32
    pid = lib.GetCurrentProcessId()
    handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, pid)
    buf = ctypes.c_void_p()
    ctypes.windll.kernel32.CloseHandle(handle)
    return pid
""", encoding="utf-8")

            res = ScaffoldGenerator.generate_scaffold(src_repo, output_dir=out_dir)

            self.assertEqual(res["status"], "success")
            self.assertEqual(res["generated_files_count"], 7)
            self.assertIn("FFI_MARSHALLING_OVERHEAD", res["targeted_bottlenecks"])

            # Verify files exist on disk
            cargo_toml = Path(out_dir) / "native_core" / "Cargo.toml"
            lib_rs = Path(out_dir) / "native_core" / "src" / "lib.rs"
            bridge_glue = Path(out_dir) / "bridge_glue.py"
            build_ps1 = Path(out_dir) / "build_native.ps1"
            readme = Path(out_dir) / "README_SCAFFOLD.md"
            patch_file = Path(out_dir) / "integration.patch"
            runbook_file = Path(out_dir) / "ROLLBACK_RUNBOOK.md"

            self.assertTrue(cargo_toml.exists())
            self.assertTrue(lib_rs.exists())
            self.assertTrue(bridge_glue.exists())
            self.assertTrue(build_ps1.exists())
            self.assertTrue(readme.exists())
            self.assertTrue(patch_file.exists())
            self.assertTrue(runbook_file.exists())

            # Verify content of Cargo.toml and bridge_glue
            self.assertIn("crate-type = [\"cdylib\", \"rlib\"]", cargo_toml.read_text(encoding="utf-8"))
            self.assertIn("def is_native_accelerated", bridge_glue.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
