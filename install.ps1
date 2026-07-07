$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$WheelDir = Join-Path $Root "wheels"
$Wheel = Get-ChildItem -LiteralPath $WheelDir -Filter "spira_trust-*.whl" | Sort-Object Name | Select-Object -Last 1
$Venv = Join-Path $Root ".venv"
$Python = Join-Path $Venv "Scripts\python.exe"
$Spira = Join-Path $Venv "Scripts\spira-trust.exe"
$Shortcut = Join-Path $Root "spira.bat"
$TrustShortcut = Join-Path $Root "spira-trust.bat"

if (!$Wheel) {
    throw "Wheel not found under: $WheelDir"
}

if (!(Test-Path -LiteralPath $Python)) {
    python -m venv $Venv
}

& $Python -m pip install --no-index --force-reinstall $Wheel.FullName | Out-Host

& $Python -c "import spira_core.trust_cli" | Out-Host

$GlobalSpira = Get-Command spira-trust -ErrorAction SilentlyContinue
if ($GlobalSpira -and ($GlobalSpira.Source -notlike "$Venv*")) {
    Write-Host ""
    Write-Host "Warning: another spira-trust command exists outside this bundle:" -ForegroundColor Yellow
    Write-Host "  $($GlobalSpira.Source)" -ForegroundColor Yellow
    Write-Host "Use .\spira-trust.bat from this folder to avoid running an older global install." -ForegroundColor Yellow
}

$ShortcutBody = @"
@echo off
"%~dp0.venv\Scripts\spira-trust.exe" %*
"@
Set-Content -Path $Shortcut -Value $ShortcutBody -Encoding ASCII
Set-Content -Path $TrustShortcut -Value $ShortcutBody -Encoding ASCII

Write-Host ""
Write-Host "SPIRA Trust installed in local .venv." -ForegroundColor Green
Write-Host "Local shortcuts created: .\spira-trust.bat and .\spira.bat" -ForegroundColor Green
Write-Host ""
Write-Host "Run it with:" -ForegroundColor Cyan
Write-Host "  .\spira-trust.bat trust C:\path\to\package.whl --output-dir spira_trust_out"
Write-Host "  .\spira-trust.bat graph C:\path\to\wheel-folder --output-dir spira_graph_out"
Write-Host ""
Write-Host "Help:" -ForegroundColor Cyan
Write-Host "  .\spira-trust.bat --help"
Write-Host "  .\spira-trust.bat graph --help"
Write-Host ""

if (Test-Path -LiteralPath $Spira) {
    & $Spira --help | Select-Object -First 3 | Out-Host
}
