@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

set "PYTHONUNBUFFERED=1"
set "PYTHONIOENCODING=utf-8"

set "PYTHON="

python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON=python"
    goto :found_python
)

py -3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON=py -3"
    goto :found_python
)

for /d %%D in ("D:\DevTools\Python\Python*") do (
    if exist "%%~D\python.exe" (
        set "PYTHON=%%~D\python.exe"
        goto :found_python
    )
)
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
    if exist "%%~D\python.exe" (
        set "PYTHON=%%~D\python.exe"
        goto :found_python
    )
)
for /d %%D in ("%ProgramFiles%\Python*") do (
    if exist "%%~D\python.exe" (
        set "PYTHON=%%~D\python.exe"
        goto :found_python
    )
)
for /d %%D in ("C:\Python*") do (
    if exist "%%~D\python.exe" (
        set "PYTHON=%%~D\python.exe"
        goto :found_python
    )
)

echo [ERROR] Python interpreter not found. Please install Python.
exit /b 1

:found_python
for %%I in ("%~dp0..") do set "WORKSPACE_BASE=%%~fI"
set "PYTHONPATH=%~dp0;%WORKSPACE_BASE%;%PYTHONPATH%"

%PYTHON% main.py %*
exit /b %errorlevel%
