@echo off
setlocal

set DASHBOARD_URL=%1
if "%DASHBOARD_URL%"=="" set DASHBOARD_URL=http://localhost:8001/test-dashboard

start "" "%DASHBOARD_URL%"
exit /b 0







