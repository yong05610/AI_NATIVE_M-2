$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
$backendPath = Join-Path $projectRoot "backend"

if (-not (Test-Path -LiteralPath $venvPython)) {
    throw ".venv was not found. Run .\scripts\setup_venv.ps1 first."
}

$pythonVersion = (& $venvPython -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')").Trim()
$versionParts = $pythonVersion.Split(".")
$majorVersion = [int]$versionParts[0]
$minorVersion = [int]$versionParts[1]
if ($majorVersion -ne 3 -or $minorVersion -lt 11 -or $minorVersion -eq 14) {
    throw ".venv uses unsupported Python $pythonVersion. Python 3.12 is recommended and Python 3.14 is excluded."
}

Push-Location -LiteralPath $backendPath
try {
    & $venvPython -m uvicorn main:app --reload
}
finally {
    Pop-Location
}
