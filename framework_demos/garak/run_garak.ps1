# Run both Garak scans against the local PX Service Assistant, then apply the PX rules.
# Usage (PowerShell):  $env:PX_KEY = "<your TRAINING_API_KEY>"; .\run_garak.ps1
# Needs the app running on localhost:8000 and Garak installed (see ..\README.md).
if (-not $env:PX_KEY) { throw "Set `$env:PX_KEY to your TRAINING_API_KEY first" }
$env:REST_API_KEY = $env:PX_KEY
Set-Location $PSScriptRoot
$failed = $false
foreach ($run in "px_direct", "px_indirect") {
    Write-Host "=== garak: $run ==="
    garak --config "$run.yaml"
    if ($LASTEXITCODE -ne 0) { $failed = $true }
    python check_garak_report.py $run
    if ($LASTEXITCODE -ne 0) { $failed = $true }
}
if ($failed) { exit 1 }
