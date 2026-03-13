@echo off
setlocal

cd /d "%~dp0.."
set PROJECT_ROOT=%CD%

set MOCK_MODE=true
set PYTHONPATH=%PROJECT_ROOT%;%PYTHONPATH%

if exist ".venv\Scripts\python.exe" (
  set PYTHON_BIN=.venv\Scripts\python.exe
) else (
  set PYTHON_BIN=python
)

echo Running smoke tests...
%PYTHON_BIN% -m pytest -q -m smoke tests\smoke_test.py
if %ERRORLEVEL% NEQ 0 exit /b 1
echo Smoke tests passed.

