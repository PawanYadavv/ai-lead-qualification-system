@echo off
setlocal

set BASE_URL=%1
if "%BASE_URL%"=="" set BASE_URL=http://localhost:8001/api/v1

if exist ".venv\Scripts\python.exe" (
  set PYTHON_CMD=.venv\Scripts\python.exe
) else (
  set PYTHON_CMD=python
)

echo Running smoke test against %BASE_URL%
%PYTHON_CMD% scripts\easy_test.py --base-url %BASE_URL%

if errorlevel 1 (
  echo.
  echo Smoke test failed.
  pause
  exit /b 1
)

echo.
echo Smoke test passed.
pause
exit /b 0
