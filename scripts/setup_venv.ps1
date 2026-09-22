$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPath = Join-Path $projectRoot ".venv"
$venvPython = Join-Path $venvPath "Scripts\python.exe"
$requirementsPath = Join-Path $projectRoot "backend\requirements.txt"

Write-Host "Project root: $projectRoot"
Set-Location -LiteralPath $projectRoot

if (-not (Test-Path -LiteralPath $venvPython)) {
    Write-Host "Creating .venv with Python 3.12..."
    py -3.12 -m venv .venv
}

if (-not (Test-Path -LiteralPath $venvPython)) {
    throw "Failed to create .venv. Install Python 3.12 and retry."
}

$pythonVersion = (& $venvPython -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')").Trim()
$versionParts = $pythonVersion.Split(".")
$majorVersion = [int]$versionParts[0]
$minorVersion = [int]$versionParts[1]
if ($majorVersion -ne 3 -or $minorVersion -lt 11 -or $minorVersion -eq 14) {
    throw ".venv uses unsupported Python $pythonVersion. Use Python 3.11+ except 3.14; Python 3.12 is recommended."
}

& $venvPython --version
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r $requirementsPath

Write-Host "Setup complete. Activate with: .\.venv\Scripts\Activate.ps1"
Write-Host "Create .env manually from .env.example; this script does not create secrets."
