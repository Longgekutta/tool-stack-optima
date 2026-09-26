#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# tool-stack-optima: 跨平台统一操作入口 (Linux / macOS / WSL / Git Bash)
# 零环境变量依赖与执行目录自愈 (UCFS v1.0)
# -----------------------------------------------------------------------------
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PYTHON=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON="python"
elif [ -x "/usr/bin/python3" ]; then
    PYTHON="/usr/bin/python3"
elif [ -x "/usr/local/bin/python3" ]; then
    PYTHON="/usr/local/bin/python3"
elif [ -x "/opt/homebrew/bin/python3" ]; then
    PYTHON="/opt/homebrew/bin/python3"
elif [ -x "$HOME/.pyenv/shims/python3" ]; then
    PYTHON="$HOME/.pyenv/shims/python3"
else
    echo "[ERROR] 未能在系统中检测到可用的 Python 解释器。" >&2
    exit 1
fi

WORKSPACE_BASE="$(cd "$SCRIPT_DIR/.." && pwd)"
export PYTHONPATH="$SCRIPT_DIR:$WORKSPACE_BASE:$PYTHONPATH"

exec "$PYTHON" main.py "$@"
