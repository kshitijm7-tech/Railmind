@echo off
REM =====================================================================
REM  RailMind demo launcher (branch: demo/integration)
REM
REM  Starts everything the SIH demo needs:
REM    1. Backend  (FastAPI + in-process engine)  http://127.0.0.1:8000
REM    2. Frontend (Next.js dev server)            http://localhost:3000
REM
REM  Usage:
REM    run.bat           start anything that is not already running
REM    run.bat restart   stop RailMind servers first, then start fresh
REM
REM  The script is idempotent: if a server already answers, it is left
REM  alone. Each server runs in its own window titled "RailMind ...".
REM =====================================================================
setlocal
cd /d "%~dp0"

echo ============================================
echo  RailMind - demo startup
echo ============================================

if /i "%~1"=="restart" goto :restart
goto :branchcheck

:restart
echo [restart] Stopping existing RailMind servers ...
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='uvicorn.exe'\" | Where-Object { $_.CommandLine -like '*app.main:app*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }; Get-CimInstance Win32_Process -Filter \"Name='node.exe'\" | Where-Object { $_.CommandLine -like '*Railmind*next*' -or $_.CommandLine -like '*next*dev*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
timeout /t 3 /nobreak >nul
goto :branchcheck

:branchcheck
for /f "delims=" %%b in ('git branch --show-current 2^>nul') do set BRANCH=%%b
if /i not "%BRANCH%"=="demo/integration" (
  echo [warn] Current branch is '%BRANCH%', expected 'demo/integration'.
  echo [warn] Continuing anyway - press Ctrl+C to abort.
  timeout /t 5 /nobreak >nul
)

where python >nul 2>nul
if %errorlevel% neq 0 (
  echo [error] 'python' not found on PATH. Install Python 3.12+ and retry.
  exit /b 1
)
where node >nul 2>nul
if %errorlevel% neq 0 (
  echo [error] 'node' not found on PATH. Install Node.js 20+ and retry.
  exit /b 1
)
where npm >nul 2>nul
if %errorlevel% neq 0 (
  echo [error] 'npm' not found on PATH. Install Node.js 20+ and retry.
  exit /b 1
)

REM ============================ BACKEND ================================
powershell -NoProfile -Command "try { if ((Invoke-WebRequest -UseBasicParsing -TimeoutSec 3 'http://127.0.0.1:8000/health').StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>nul
if %errorlevel% equ 0 (
  echo [ok] Backend already running on http://127.0.0.1:8000
  goto :backend_ok
)
echo [start] Backend: uvicorn app.main:app --host 127.0.0.1 --port 8000
where uvicorn >nul 2>nul
if %errorlevel% equ 0 (
  start "RailMind Backend" /d "%~dp0backend" cmd /k uvicorn app.main:app --host 127.0.0.1 --port 8000
) else (
  start "RailMind Backend" /d "%~dp0backend" cmd /k python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
)
echo [wait] Waiting for backend health (up to 60s) ...
powershell -NoProfile -Command "$t=0; while ($t -lt 60) { try { if ((Invoke-WebRequest -UseBasicParsing -TimeoutSec 3 'http://127.0.0.1:8000/health').StatusCode -eq 200) { exit 0 } } catch {}; Start-Sleep -Seconds 2; $t+=2 }; exit 1" >nul 2>nul
if %errorlevel% equ 0 (
  echo [ok] Backend is healthy.
  goto :backend_ok
)
echo [error] Backend did not become healthy. Check the 'RailMind Backend' window.
exit /b 1

:backend_ok
REM ============================ FRONTEND ===============================
if exist "%~dp0frontend\node_modules" goto :frontend_check
echo [start] Frontend dependencies missing - running 'npm install' (one time, may take a few minutes) ...
pushd "%~dp0frontend"
call npm install
if %errorlevel% neq 0 (
  echo [error] 'npm install' failed. Fix the errors above and rerun run.bat.
  popd
  exit /b 1
)
popd
:frontend_check
powershell -NoProfile -Command "try { Invoke-WebRequest -UseBasicParsing -TimeoutSec 5 'http://localhost:3000/' | Out-Null; exit 0 } catch { if ($_.Exception.Response) { exit 0 } else { exit 1 } }" >nul 2>nul
if %errorlevel% equ 0 (
  echo [ok] Frontend already running on http://localhost:3000
  goto :summary
)
echo [start] Frontend: npm run dev
start "RailMind Frontend" /d "%~dp0frontend" cmd /k npm run dev
echo [wait] Waiting for frontend (up to 120s, first compile is slow) ...
powershell -NoProfile -Command "$t=0; while ($t -lt 120) { try { Invoke-WebRequest -UseBasicParsing -TimeoutSec 5 'http://localhost:3000/' | Out-Null; exit 0 } catch { if ($_.Exception.Response) { exit 0 } }; Start-Sleep -Seconds 3; $t+=3 }; exit 1" >nul 2>nul
if %errorlevel% equ 0 (
  echo [ok] Frontend is responding.
  goto :summary
)
echo [error] Frontend did not respond. Check the 'RailMind Frontend' window.
exit /b 1

:summary
REM ============================ SUMMARY ================================
echo.
echo ============================================
echo  RailMind is up:
echo    Frontend UI : http://localhost:3000
echo    Backend API : http://127.0.0.1:8000
echo    Swagger     : http://127.0.0.1:8000/docs
echo ============================================
powershell -NoProfile -Command "try { $s=(Invoke-WebRequest -UseBasicParsing -TimeoutSec 5 'http://127.0.0.1:8000/api/v1/stations?page_size=50' | ConvertFrom-Json); $t=(Invoke-WebRequest -UseBasicParsing -TimeoutSec 5 'http://127.0.0.1:8000/api/v1/trains?page_size=50' | ConvertFrom-Json); Write-Host (\"  Dataset     : {0} stations / {1} trains (canonical C-07)\" -f $s.pagination.totalItems, $t.pagination.totalItems) } catch { Write-Host '  Dataset     : could not verify counts' }" 2>nul
echo.
echo Tip: 'run.bat restart' bounces both servers (use after git pull).
endlocal
