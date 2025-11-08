#!/bin/bash
# 快速测试脚本 - 用于日常开发中的快速验证
# 只运行最基本的测试，适合频繁执行

set -e

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 获取项目根目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_ROOT"

echo -e "${BLUE}=== 快速测试 (Quick Test) ===${NC}"
echo ""

# 设置环境变量
export MOCK_MODE=true
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# 运行烟雾测试
echo -e "${YELLOW}📦 运行烟雾测试...${NC}"
python tests/smoke_test.py

echo ""
echo -e "${GREEN}✅ 快速测试完成！${NC}"
echo -e "${BLUE}💡 提示: 运行 './scripts/run_ci_tests.sh' 进行完整测试${NC}"

