$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "Installing gateway dependencies..."
py -m pip install -r gateway\requirements.txt

Write-Host "Starting API Gateway on http://0.0.0.0:8000"
py -m uvicorn main:app --host 0.0.0.0 --port 8000
