@echo off
REM 快速测试脚本 (Windows版本)
REM 用于日常开发中的快速验证

setlocal

REM 获取项目根目录
cd /d "%~dp0.."
set PROJECT_ROOT=%CD%

echo ============================================
echo === 快速测试 (Quick Test) ===
echo ============================================
echo.

REM 设置环境变量
set MOCK_MODE=true
set PYTHONPATH=%PROJECT_ROOT%;%PYTHONPATH%

REM 运行烟雾测试
echo 📦 运行烟雾测试...
echo.
python tests\smoke_test.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ 快速测试完成！
    echo 💡 提示: 运行 'scripts\run_ci_tests.bat' 进行完整测试
    exit /b 0
) else (
    echo.
    echo ❌ 测试失败，请检查错误信息
    exit /b 1
)

