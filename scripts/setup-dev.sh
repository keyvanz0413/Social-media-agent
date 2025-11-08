#!/bin/bash
# 开发环境设置脚本

set -e

echo "=========================================="
echo "Social Media Agent - 开发环境设置"
echo "=========================================="

# 检查 Python 版本
echo "检查 Python 版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python 版本: $python_version"

if [[ ! "$python_version" =~ ^3\.(9|10|11|12) ]]; then
    echo "⚠️  警告: 推荐使用 Python 3.9-3.12"
fi

# 创建虚拟环境（如果不存在）
if [ ! -d ".venv" ]; then
    echo ""
    echo "创建虚拟环境..."
    python3 -m venv .venv
    echo "✅ 虚拟环境已创建"
fi

# 激活虚拟环境
echo ""
echo "激活虚拟环境..."
source .venv/bin/activate

# 升级 pip
echo ""
echo "升级 pip..."
pip install --upgrade pip

# 安装项目依赖
echo ""
echo "安装项目依赖..."
pip install -r requirements.txt

# 安装开发依赖
echo ""
echo "安装开发依赖..."
pip install pytest pytest-cov pytest-asyncio pytest-mock pytest-xdist
pip install black flake8 mypy isort pylint bandit safety
pip install pre-commit

# 安装 pre-commit hooks
echo ""
echo "安装 pre-commit hooks..."
pre-commit install

# 创建必要的目录
echo ""
echo "创建输出目录..."
mkdir -p outputs/drafts
mkdir -p outputs/images
mkdir -p outputs/logs
mkdir -p outputs/cache

# 创建 .env 文件（如果不存在）
if [ ! -f ".env" ]; then
    echo ""
    echo "创建 .env 文件..."
    cp env.example .env
    echo "⚠️  请编辑 .env 文件，添加你的 API 密钥"
fi

# 运行烟雾测试
echo ""
echo "运行烟雾测试验证环境..."
export MOCK_MODE=true
python tests/smoke_test.py

echo ""
echo "=========================================="
echo "✅ 开发环境设置完成!"
echo "=========================================="
echo ""
echo "下一步:"
echo "  1. 激活虚拟环境: source .venv/bin/activate"
echo "  2. 编辑 .env 文件: vim .env"
echo "  3. 运行测试: make test"
echo "  4. 启动应用: python main.py"
echo ""
echo "有用的命令:"
echo "  make help         - 查看所有可用命令"
echo "  make test         - 运行测试"
echo "  make coverage     - 生成覆盖率报告"
echo "  make format       - 格式化代码"
echo "  make lint         - 代码检查"
echo ""

