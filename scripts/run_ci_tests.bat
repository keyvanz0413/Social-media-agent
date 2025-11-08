@echo off
REM 本地运行 CI/CD 测试流程 (Windows版本)
REM 模拟 GitHub Actions 的测试流程

setlocal enabledelayedexpansion

REM 获取项目根目录
cd /d "%~dp0.."
set PROJECT_ROOT=%CD%

echo ============================================
echo === 本地 CI/CD 测试流程 (Windows) ===
echo ============================================
echo 项目目录: %PROJECT_ROOT%
echo.

REM 设置环境变量
set MOCK_MODE=true
set PYTHONPATH=%PROJECT_ROOT%;%PYTHONPATH%

REM 初始化测试计数
set TOTAL_TESTS=0
set PASSED_TESTS=0
set FAILED_TESTS=0

REM ============================================================================
REM 步骤 1: 烟雾测试
REM ============================================================================
echo ============================================
echo 📦 步骤 1/4: 烟雾测试 (Smoke Tests)
echo ============================================
echo.

echo [TEST] 烟雾测试
python tests\smoke_test.py
if %ERRORLEVEL% EQU 0 (
    echo ✅ 烟雾测试 - 通过
    set /a PASSED_TESTS+=1
) else (
    echo ❌ 烟雾测试 - 失败
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1
echo.

REM ============================================================================
REM 步骤 2: 单元测试
REM ============================================================================
echo ============================================
echo 🧪 步骤 2/4: 单元测试 (Unit Tests)
echo ============================================
echo.

REM 检查pytest是否安装
where pytest >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [TEST] 配置模块测试
    pytest tests\test_config.py -v -m "not mcp" --tb=short
    if %ERRORLEVEL% EQU 0 (
        echo ✅ 配置模块测试 - 通过
        set /a PASSED_TESTS+=1
    ) else (
        echo ❌ 配置模块测试 - 失败
        set /a FAILED_TESTS+=1
    )
    set /a TOTAL_TESTS+=1
    echo.
    
    echo [TEST] 工具函数测试
    pytest tests\test_tools.py -v -m "not mcp" --tb=short
    if %ERRORLEVEL% EQU 0 (
        echo ✅ 工具函数测试 - 通过
        set /a PASSED_TESTS+=1
    ) else (
        echo ❌ 工具函数测试 - 失败
        set /a FAILED_TESTS+=1
    )
    set /a TOTAL_TESTS+=1
    echo.
    
    echo [TEST] 工具模块测试
    pytest tests\test_utils.py -v -m "not mcp and not slow" --tb=short
    if %ERRORLEVEL% EQU 0 (
        echo ✅ 工具模块测试 - 通过
        set /a PASSED_TESTS+=1
    ) else (
        echo ❌ 工具模块测试 - 失败
        set /a FAILED_TESTS+=1
    )
    set /a TOTAL_TESTS+=1
    echo.
) else (
    echo ⚠️  pytest 未安装，跳过pytest单元测试
    echo.
)

REM ============================================================================
REM 步骤 3: 集成测试
REM ============================================================================
echo ============================================
echo 🔄 步骤 3/4: 集成测试 (Integration Tests)
echo ============================================
echo.

echo [TEST] 综合测试套件
python tests\comprehensive_test.py
if %ERRORLEVEL% EQU 0 (
    echo ✅ 综合测试套件 - 通过
    set /a PASSED_TESTS+=1
) else (
    echo ❌ 综合测试套件 - 失败
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1
echo.

REM ============================================================================
REM 步骤 4: 代码质量检查
REM ============================================================================
echo ============================================
echo ✨ 步骤 4/4: 代码质量检查 (Code Quality)
echo ============================================
echo.

REM Flake8 检查
where flake8 >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [CHECK] Flake8语法检查
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=__pycache__,venv,env,.venv,.git,outputs,logs
    if %ERRORLEVEL% EQU 0 (
        echo ✅ Flake8语法检查 - 通过
        set /a PASSED_TESTS+=1
    ) else (
        echo ❌ Flake8语法检查 - 失败
        set /a FAILED_TESTS+=1
    )
    set /a TOTAL_TESTS+=1
    echo.
    
    echo [CHECK] Flake8代码风格检查（警告级别）
    flake8 . --count --exit-zero --max-complexity=10 --max-line-length=120 --statistics --exclude=__pycache__,venv,env,.venv,.git,outputs,logs
    echo.
) else (
    echo ⚠️  flake8 未安装，跳过代码检查
    echo.
)

REM Black 格式检查
where black >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [CHECK] Black代码格式检查（信息级别）
    black --check --diff --exclude="/(\.git|\.venv|venv|env|__pycache__|outputs|logs)/" . 2>nul
    echo.
) else (
    echo ⚠️  black 未安装，跳过格式检查
    echo.
)

REM ============================================================================
REM 测试结果汇总
REM ============================================================================
echo.
echo ============================================
echo 📊 测试结果汇总
echo ============================================
echo.
echo 总计: %TOTAL_TESTS% 个测试
echo 通过: %PASSED_TESTS%
echo 失败: %FAILED_TESTS%
echo ============================================
echo.

REM 最终结果
if %FAILED_TESTS% EQU 0 (
    echo 🎉 所有测试通过！Agent功能正常运行。
    echo 💡 注意: MCP相关测试已被排除（需要单独的MCP服务）
    exit /b 0
) else (
    echo ⚠️  有 %FAILED_TESTS% 个测试失败，请检查问题。
    exit /b 1
)

