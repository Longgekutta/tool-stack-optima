param (
    [Parameter(Position = 0)]
    [string]$Verb = "help",
    
    [Parameter(Position = 1, ValueFromRemainingArguments = $true)]
    [string[]]$RemainingArgs
)

# 1. CWD Anchoring
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# 2. Auto-detect Python runtime without environment variable requirements
function Get-PythonInterpreter {
    if (Get-Command "python" -ErrorAction SilentlyContinue) {
        return "python"
    }
    if (Get-Command "py" -ErrorAction SilentlyContinue) {
        return "py"
    }
    if (Get-Command "python3" -ErrorAction SilentlyContinue) {
        return "python3"
    }
    $localApp = $env:LOCALAPPDATA
    $progFiles = $env:ProgramFiles
    $searchPatterns = @(
        "D:\DevTools\Python\Python*\python.exe",
        "$localApp\Programs\Python\Python*\python.exe",
        "$progFiles\Python*\python.exe",
        "C:\Python*\python.exe",
        "D:\Python*\python.exe"
    )
    foreach ($pattern in $searchPatterns) {
        $found = Get-Item $pattern -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($found -and (Test-Path $found.FullName)) {
            return $found.FullName
        }
    }
    throw "Python interpreter not found. Please install Python."
}

$PythonExe = Get-PythonInterpreter

# 3. Dynamic PYTHONPATH injection
$WorkspaceBase = Split-Path -Parent $ScriptDir
$env:PYTHONPATH = $ScriptDir + ";" + $WorkspaceBase + ";" + $env:PYTHONPATH

# 4. Forward execution to main.py
switch ($Verb.ToLower()) {
    "setup" {
        & $PythonExe main.py setup @RemainingArgs
    }
    "run" {
        & $PythonExe main.py run @RemainingArgs
    }
    "synthesize" {
        & $PythonExe main.py synthesize @RemainingArgs
    }
    "test" {
        & $PythonExe main.py test @RemainingArgs
    }
    "health" {
        & $PythonExe main.py health @RemainingArgs
    }
    "clean" {
        & $PythonExe main.py clean @RemainingArgs
    }
    "languages" {
        & $PythonExe main.py languages @RemainingArgs
    }
    Default {
        & $PythonExe main.py --help
    }
}
