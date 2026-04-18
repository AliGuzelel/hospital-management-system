@echo off
setlocal
cd /d "%~dp0"
echo Installing gateway dependencies...
py -m pip install -r gateway\requirements.txt
if errorlevel 1 exit /b 1
echo Starting API Gateway on http://0.0.0.0:8000
py -m uvicorn main:app --host 0.0.0.0 --port 8000
