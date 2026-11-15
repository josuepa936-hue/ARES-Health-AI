@echo off
setlocal
cd /d "%~dp0"
echo ===============================================
echo  ARES Health AI - Integrated Mission Console
echo ===============================================
echo.
if /I "%~1"=="--skip-build" goto run_server
where npm.cmd >nul 2>nul
if errorlevel 1 (
  echo ERROR: Node.js/npm.cmd is missing. Install Node.js 22.12 or later.
  echo To use an existing compiled frontend: start-ares.cmd --skip-build
  exit /b 1
)
pushd frontend
if not exist node_modules\package.json if not exist node_modules (
  call npm.cmd ci
  if errorlevel 1 (
    popd
    echo ERROR: Could not install frontend packages.
    exit /b 1
  )
)
call npm.cmd run build
if errorlevel 1 (
  popd
  echo ERROR: Frontend build failed.
  exit /b 1
)
popd
:run_server
if not exist frontend\dist\index.html (
  echo ERROR: Compiled React frontend is missing.
  echo Run start-ares.cmd to build it, then retry.
  exit /b 1
)
echo ARES UI:           http://127.0.0.1:8000/
echo API documentation: http://127.0.0.1:8000/docs
echo Synthetic demonstration only. No real medical data.
echo Keep this window open; Ctrl+C stops ARES.
echo.
if exist .venv\Scripts\python.exe (
  ".venv\Scripts\python.exe" -m uvicorn src.ares_health.api:app --host 127.0.0.1 --port 8000
) else (
  python -m uvicorn src.ares_health.api:app --host 127.0.0.1 --port 8000
)
endlocal
