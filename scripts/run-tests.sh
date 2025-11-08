#!/bin/bash
# 运行测试脚本

set -e

echo "=========================================="
echo "Social Media Agent - 测试脚本"
echo "=========================================="

# 设置环境变量
export MOCK_MODE=true

# 检查参数
case "$1" in
    "smoke")
        echo "运行烟雾测试..."
        python tests/smoke_test.py
        ;;
    "unit")
        echo "运行单元测试..."
        pytest tests/ -v -m unit
        ;;
    "integration")
        echo "运行集成测试..."
        pytest tests/ -v -m integration
        ;;
    "comprehensive")
        echo "运行综合测试..."
        python tests/comprehensive_test.py
        ;;
    "coverage")
        echo "运行测试并生成覆盖率报告..."
        pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing
        echo ""
        echo "覆盖率报告已生成: htmlcov/index.html"
        ;;
    "all")
        echo "运行所有测试..."
        pytest tests/ -v --cov=. --cov-report=term-missing
        ;;
    *)
        echo "使用方法: $0 {smoke|unit|integration|comprehensive|coverage|all}"
        echo ""
        echo "可选参数:"
        echo "  smoke         - 快速烟雾测试 (~10秒)"
        echo "  unit          - 单元测试"
        echo "  integration   - 集成测试"
        echo "  comprehensive - 综合测试套件"
        echo "  coverage      - 测试 + 覆盖率报告"
        echo "  all           - 运行所有测试（默认）"
        exit 1
        ;;
esac

echo ""
echo "✅ 测试完成!"

