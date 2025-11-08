#!/bin/bash
# 本地运行 CI/CD 测试流程
# 模拟 GitHub Actions 的测试流程

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本所在目录的父目录（项目根目录）
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_ROOT"

echo -e "${BLUE}=== 本地 CI/CD 测试流程 ===${NC}"
echo -e "${BLUE}项目目录: $PROJECT_ROOT${NC}"
echo ""

# 设置环境变量
export MOCK_MODE=true
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# 初始化测试计数
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 测试结果记录
declare -a TEST_RESULTS

# 运行测试函数
run_test() {
    local test_name=$1
    local test_command=$2
    
    echo -e "${YELLOW}▶ $test_name${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if eval "$test_command"; then
        echo -e "${GREEN}✅ $test_name - 通过${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        TEST_RESULTS+=("✅ $test_name")
        echo ""
        return 0
    else
        echo -e "${RED}❌ $test_name - 失败${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        TEST_RESULTS+=("❌ $test_name")
        echo ""
        return 1
    fi
}

# ============================================================================
# 步骤 1: 烟雾测试
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📦 步骤 1/4: 烟雾测试 (Smoke Tests)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

run_test "烟雾测试" "python tests/smoke_test.py" || true

# ============================================================================
# 步骤 2: 单元测试
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🧪 步骤 2/4: 单元测试 (Unit Tests)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 检查pytest是否安装
if ! command -v pytest &> /dev/null; then
    echo -e "${YELLOW}⚠️  pytest 未安装，跳过pytest单元测试${NC}"
else
    run_test "配置模块测试" "pytest tests/test_config.py -v -m 'not mcp' --tb=short" || true
    run_test "工具函数测试" "pytest tests/test_tools.py -v -m 'not mcp' --tb=short" || true
    run_test "工具模块测试" "pytest tests/test_utils.py -v -m 'not mcp and not slow' --tb=short" || true
fi

# ============================================================================
# 步骤 3: 集成测试
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🔄 步骤 3/4: 集成测试 (Integration Tests)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

run_test "综合测试套件" "python tests/comprehensive_test.py" || true

# ============================================================================
# 步骤 4: 代码质量检查
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}✨ 步骤 4/4: 代码质量检查 (Code Quality)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Flake8 检查
if command -v flake8 &> /dev/null; then
    run_test "Flake8语法检查" \
        "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=__pycache__,venv,env,.venv,.git,outputs,logs" \
        || true
    
    echo -e "${YELLOW}▶ Flake8代码风格检查（警告级别）${NC}"
    flake8 . --count --exit-zero --max-complexity=10 --max-line-length=120 --statistics \
        --exclude=__pycache__,venv,env,.venv,.git,outputs,logs || true
    echo ""
else
    echo -e "${YELLOW}⚠️  flake8 未安装，跳过代码检查${NC}"
    echo ""
fi

# Black 格式检查
if command -v black &> /dev/null; then
    echo -e "${YELLOW}▶ Black代码格式检查（信息级别）${NC}"
    black --check --diff --exclude="/(\.git|\.venv|venv|env|__pycache__|outputs|logs)/" . || true
    echo ""
else
    echo -e "${YELLOW}⚠️  black 未安装，跳过格式检查${NC}"
    echo ""
fi

# ============================================================================
# 测试结果汇总
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📊 测试结果汇总${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 打印所有测试结果
for result in "${TEST_RESULTS[@]}"; do
    echo "$result"
done

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "总计: $TOTAL_TESTS 个测试"
echo -e "${GREEN}通过: $PASSED_TESTS${NC}"

if [ $FAILED_TESTS -gt 0 ]; then
    echo -e "${RED}失败: $FAILED_TESTS${NC}"
else
    echo -e "失败: $FAILED_TESTS"
fi

SUCCESS_RATE=$(awk "BEGIN {printf \"%.1f\", ($PASSED_TESTS/$TOTAL_TESTS)*100}")
echo -e "成功率: ${SUCCESS_RATE}%"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 最终结果
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 所有测试通过！Agent功能正常运行。${NC}"
    echo -e "${BLUE}💡 注意: MCP相关测试已被排除（需要单独的MCP服务）${NC}"
    exit 0
else
    echo -e "${RED}⚠️  有 $FAILED_TESTS 个测试失败，请检查问题。${NC}"
    exit 1
fi

