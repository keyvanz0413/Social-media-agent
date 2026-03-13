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

echo Step 1/3: smoke tests
%PYTHON_BIN% -m pytest -q -m smoke tests\smoke_test.py
if %ERRORLEVEL% NEQ 0 exit /b 1

echo Step 2/3: unit tests
%PYTHON_BIN% -m pytest -q -m unit tests
if %ERRORLEVEL% NEQ 0 exit /b 1

echo Step 3/3: integration tests
%PYTHON_BIN% -m pytest -q -m integration tests\comprehensive_test.py tests\test_langgraph_workflow.py tests\test_api.py
if %ERRORLEVEL% NEQ 0 exit /b 1

echo All CI-like tests passed.

