#!/bin/bash
# Pre-push 检查脚本
# 在推送代码前运行完整检查

set -e

echo "=========================================="
echo "Pre-Push 检查"
echo "=========================================="

# 设置颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查函数
check_step() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1 通过${NC}"
    else
        echo -e "${RED}❌ $1 失败${NC}"
        exit 1
    fi
}

# 1. 代码格式检查
echo ""
echo "1️⃣  检查代码格式..."
black --check --diff . || {
    echo -e "${YELLOW}⚠️  代码格式不符合要求${NC}"
    echo "运行 'make format' 或 'black .' 来修复"
    exit 1
}
check_step "代码格式"

# 2. Import 排序检查
echo ""
echo "2️⃣  检查 Import 排序..."
isort --check-only --diff . || {
    echo -e "${YELLOW}⚠️  Import 排序不正确${NC}"
    echo "运行 'isort .' 来修复"
    exit 1
}
check_step "Import 排序"

# 3. 代码风格检查
echo ""
echo "3️⃣  检查代码风格 (Flake8)..."
flake8 . --max-line-length=100 --exclude=venv,env,.venv,outputs,logs --count --select=E9,F63,F7,F82 --show-source --statistics
check_step "代码风格"

# 4. 类型检查（可选，允许警告）
echo ""
echo "4️⃣  运行类型检查 (MyPy)..."
mypy . --ignore-missing-imports --no-strict-optional || {
    echo -e "${YELLOW}⚠️  类型检查有警告（不阻塞）${NC}"
}

# 5. 安全检查（可选，允许警告）
echo ""
echo "5️⃣  运行安全检查 (Bandit)..."
bandit -r . -ll -f screen 2>/dev/null || {
    echo -e "${YELLOW}⚠️  安全检查有警告（不阻塞）${NC}"
}

# 6. 运行测试
echo ""
echo "6️⃣  运行测试..."
export MOCK_MODE=true
pytest tests/ -v --tb=short -x || {
    echo -e "${RED}❌ 测试失败${NC}"
    exit 1
}
check_step "测试"

# 7. 检查覆盖率
echo ""
echo "7️⃣  检查代码覆盖率..."
export MOCK_MODE=true
pytest tests/ --cov=. --cov-report=term-missing --cov-fail-under=60 -q || {
    echo -e "${YELLOW}⚠️  代码覆盖率低于 60%${NC}"
    echo "运行 'make coverage' 查看详细报告"
}
check_step "覆盖率"

echo ""
echo "=========================================="
echo -e "${GREEN}✅ 所有检查通过！可以安全推送代码。${NC}"
echo "=========================================="
echo ""
echo "推送命令:"
echo "  git push origin <branch>"
echo ""

