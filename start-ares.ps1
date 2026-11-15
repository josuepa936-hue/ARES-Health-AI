<#
.SYNOPSIS
  Build and run the complete ARES demo on a single loopback address.
.DESCRIPTION
  Compiles React locally using Vite, then launches FastAPI at 127.0.0.1:8000.
  Both UI and /api live on the same server. No public network hosting.
.EXAMPLE
  .\start-ares.ps1
.EXAMPLE
  .\start-ares.ps1 -SkipBuild
#>
param([switch]$SkipBuild)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $root
try {
    $dist = Join-Path $root 'frontend\dist\index.html'
    if (-not $SkipBuild) {
        $npm = Get-Command 'npm.cmd' -ErrorAction SilentlyContinue
        if (-not $npm) {
            throw 'Node.js/npm.cmd not found. Install Node.js 22.12+ or use -SkipBuild with an existing compiled frontend.'
        }
        Push-Location (Join-Path $root 'frontend')
        try {
            if (-not (Test-Path 'node_modules')) {
                & npm.cmd ci
                if ($LASTEXITCODE -ne 0) { throw 'npm ci failed.' }
            }
            & npm.cmd run build
            if ($LASTEXITCODE -ne 0) { throw 'Frontend production build failed.' }
        } finally {
            Pop-Location
        }
    }
    if (-not (Test-Path $dist)) {
        throw 'Frontend build is missing. Run .\start-ares.ps1 without -SkipBuild.'
    }
    $pythonExe = Join-Path $root '.venv\Scripts\python.exe'
    if (-not (Test-Path $pythonExe)) {
        $pythonExe = 'python'
    }
    Write-Host 'ARES Mission Console: http://127.0.0.1:8000/' -ForegroundColor Cyan
    Write-Host 'API documentation:    http://127.0.0.1:8000/docs' -ForegroundColor Cyan
    Write-Host 'Synthetic data only. Never host this unauthenticated demo publicly.' -ForegroundColor Yellow
    & $pythonExe -m uvicorn src.ares_health.api:app --host 127.0.0.1 --port 8000
} finally {
    Pop-Location
}
