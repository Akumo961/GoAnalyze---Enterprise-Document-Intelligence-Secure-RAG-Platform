$ErrorActionPreference = "Stop"

Write-Host "GoAnalyze Government — Phase 14 synthetic demonstration" -ForegroundColor Cyan
Write-Host "Synthetic/non-authoritative data only. No government decision is automated." -ForegroundColor Yellow

python .\demo\run_demo.py
if ($LASTEXITCODE -ne 0) {
    throw "Phase 14 demo failed with exit code $LASTEXITCODE"
}

Write-Host "Demo completed. Review demo\last_run.json for machine-readable evidence." -ForegroundColor Green
