#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
core/repo_resolver.py: 通用仓库解析与定位适配器 (Universal Repository Resolver)
=============================================================================
支持对以下三种目标形态的统一无感解析：
1. 本地目录绝对/相对路径：如 "D:\\github\\my-repo", "./my-repo"
2. 远程 Git/GitHub URL：如 "https://github.com/psf/requests.git" (浅克隆至独立缓存)
3. 仓库短名/Slug：如 "psf/requests" 或本地工作空间已有的仓库名 "infra-windows-pc-sandbox"
"""

import os
import re
import sys
import shutil
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, Tuple


class RepoResolver:
    """
    通用工业母机仓库定位解析器。
    将任何本地路径、远程 Git 地址或仓库短名解析为本地有效且可进行物理静态分析的绝对路径。
    """

    CACHE_DIR = Path.home() / ".cache" / "industrial_meta_tools" / "repos"

    @classmethod
    def resolve(cls, target_input: str, search_roots: Optional[list] = None) -> Tuple[str, Dict[str, Any]]:
        """
        解析目标，返回 (本地绝对路径, 元数据字典)
        """
        raw = target_input.strip()
        metadata = {
            "input": raw,
            "type": "UNKNOWN",
            "is_temporary": False,
            "resolved_path": ""
        }

        if not raw:
            raise ValueError("Repository target input cannot be empty.")

        # 1. 尝试直接作为本地路径
        local_p = Path(raw).expanduser().resolve()
        if local_p.exists() and local_p.is_dir():
            metadata["type"] = "LOCAL_DIR"
            metadata["resolved_path"] = str(local_p)
            return str(local_p), metadata

        # 2. 尝试在候选搜索根目录下匹配 (如 D:\github)
        candidate_roots = search_roots or [
            Path(r"D:\github"),
            Path.cwd(),
            Path.cwd().parent
        ]
        for root in candidate_roots:
            p = (Path(root) / raw).resolve()
            if p.exists() and p.is_dir():
                metadata["type"] = "LOCAL_NAMED_DIR"
                metadata["resolved_path"] = str(p)
                return str(p), metadata

        # 3. 检查是否为远程 Git/GitHub URL
        if raw.startswith("http://") or raw.startswith("https://") or raw.startswith("git@") or raw.endswith(".git"):
            metadata["type"] = "REMOTE_GIT_URL"
            cached_path = cls._clone_or_update_git_repo(raw)
            metadata["resolved_path"] = str(cached_path)
            return str(cached_path), metadata

        # 4. 检查是否为 GitHub Slug (owner/repo)
        if re.match(r"^[\w\-\.]+/[\w\-\.]+$", raw):
            github_url = f"https://github.com/{raw}.git"
            metadata["type"] = "GITHUB_SLUG"
            cached_path = cls._clone_or_update_git_repo(github_url)
            metadata["resolved_path"] = str(cached_path)
            return str(cached_path), metadata

        # 无法解析
        raise FileNotFoundError(f"Cannot resolve target repository: '{target_input}' (Neither local directory nor valid Git URL/Slug)")

    @classmethod
    def _clone_or_update_git_repo(cls, git_url: str) -> Path:
        """浅克隆远程仓库到专用缓存区"""
        cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        # 生成安全缓存目录名
        safe_name = re.sub(r"[^\w\-]", "_", git_url.replace("https://", "").replace("http://", "").replace("git@", "").replace(".git", ""))
        target_dir = cls.CACHE_DIR / safe_name

        if target_dir.exists() and (target_dir / ".git").exists():
            # 尝试拉取最新提交
            try:
                subprocess.run(["git", "pull", "--depth", "1"], cwd=target_dir, capture_output=True, timeout=15)
            except Exception:
                pass
            return target_dir

        if target_dir.exists():
            shutil.rmtree(target_dir, ignore_errors=True)

        # 浅克隆加速
        cmd = ["git", "clone", "--depth", "1", git_url, str(target_dir)]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if res.returncode != 0:
            raise RuntimeError(f"Failed to clone remote repository {git_url}: {res.stderr}")

        return target_dir
