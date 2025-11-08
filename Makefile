# Makefile for Social Media Agent
# 提供便捷的开发命令

.PHONY: help install test test-unit test-integration test-smoke coverage lint format security clean run docs

# 默认目标
.DEFAULT_GOAL := help

# ==================== 帮助信息 ====================
help:  ## 显示帮助信息
	@echo "Social Media Agent - 开发命令"
	@echo ""
	@echo "使用方法: make [target]"
	@echo ""
	@echo "可用命令:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ==================== 安装和设置 ====================
install:  ## 安装项目依赖
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install pytest pytest-cov pytest-asyncio pytest-mock pytest-xdist
	@echo "✅ 依赖安装完成"

install-dev:  ## 安装开发依赖
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install pytest pytest-cov pytest-asyncio pytest-mock pytest-xdist
	pip install black flake8 mypy isort pylint bandit safety
	pip install pre-commit
	@echo "✅ 开发依赖安装完成"

setup:  ## 初始化开发环境
	@make install-dev
	pre-commit install
	@echo "✅ 开发环境初始化完成"

# ==================== 测试 ====================
test:  ## 运行所有测试
	export MOCK_MODE=true && pytest tests/ -v --cov=. --cov-report=term-missing

test-unit:  ## 运行单元测试
	export MOCK_MODE=true && pytest tests/ -v -m unit

test-integration:  ## 运行集成测试
	export MOCK_MODE=true && pytest tests/ -v -m integration

test-smoke:  ## 运行烟雾测试（快速验证）
	export MOCK_MODE=true && python tests/smoke_test.py

test-comprehensive:  ## 运行综合测试
	export MOCK_MODE=true && python tests/comprehensive_test.py

test-parallel:  ## 并行运行测试（更快）
	export MOCK_MODE=true && pytest tests/ -v -n auto

test-fast:  ## 快速测试（跳过慢速测试）
	export MOCK_MODE=true && pytest tests/ -v -m "not slow"

# ==================== 代码覆盖率 ====================
coverage:  ## 生成代码覆盖率报告
	export MOCK_MODE=true && pytest tests/ --cov=. --cov-report=html --cov-report=term-missing
	@echo "✅ 覆盖率报告生成完成，打开 htmlcov/index.html 查看"

coverage-open:  ## 生成并打开覆盖率报告
	@make coverage
	open htmlcov/index.html || xdg-open htmlcov/index.html

# ==================== 代码质量 ====================
lint:  ## 运行所有代码检查
	@echo "运行 Flake8..."
	flake8 . --max-line-length=100 --exclude=venv,env,.venv,outputs,logs || true
	@echo "运行 MyPy..."
	mypy . --ignore-missing-imports --no-strict-optional || true
	@echo "运行 Pylint..."
	pylint **/*.py --disable=C0111,C0103,R0913 || true
	@echo "✅ 代码检查完成"

format:  ## 格式化代码
	@echo "运行 Black..."
	black . --line-length=100
	@echo "运行 isort..."
	isort . --profile black --line-length=100
	@echo "✅ 代码格式化完成"

format-check:  ## 检查代码格式（不修改）
	@echo "检查 Black..."
	black . --check --diff --line-length=100
	@echo "检查 isort..."
	isort . --check-only --diff --profile black --line-length=100

# ==================== 安全检查 ====================
security:  ## 运行安全扫描
	@echo "运行 Bandit（安全扫描）..."
	bandit -r . -f screen || true
	@echo "运行 Safety（依赖安全检查）..."
	pip install -r requirements.txt
	safety check || true
	@echo "✅ 安全检查完成"

# ==================== 清理 ====================
clean:  ## 清理临时文件
	@echo "清理 Python 缓存..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "清理测试缓存..."
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov
	@echo "清理构建产物..."
	rm -rf build dist
	@echo "✅ 清理完成"

clean-outputs:  ## 清理输出文件
	@echo "清理草稿..."
	rm -rf outputs/drafts/*.json
	@echo "清理图片..."
	rm -rf outputs/images/*.jpg outputs/images/*.png
	@echo "清理日志..."
	rm -rf outputs/logs/*.log
	@echo "✅ 输出文件清理完成"

# ==================== 运行 ====================
run:  ## 运行交互式模式
	python main.py

run-single:  ## 运行单任务模式（需要设置 TASK 变量）
	python main.py --mode single --task "$(TASK)"

run-skip-mcp:  ## 运行（跳过 MCP 检查）
	python main.py --skip-mcp-check

# ==================== Pre-commit ====================
pre-commit:  ## 运行 pre-commit 检查
	pre-commit run --all-files

pre-commit-install:  ## 安装 pre-commit hooks
	pre-commit install
	@echo "✅ Pre-commit hooks 已安装"

# ==================== CI/CD ====================
ci-local:  ## 本地模拟 CI 流程
	@echo "==================== 本地 CI 检查 ===================="
	@echo "1. 代码格式检查..."
	@make format-check
	@echo ""
	@echo "2. 代码质量检查..."
	@make lint
	@echo ""
	@echo "3. 安全扫描..."
	@make security
	@echo ""
	@echo "4. 运行测试..."
	@make test
	@echo ""
	@echo "5. 生成覆盖率报告..."
	@make coverage
	@echo ""
	@echo "==================== CI 检查完成 ===================="

# ==================== 文档 ====================
docs:  ## 查看文档
	@echo "可用文档："
	@echo "  - README.md - 项目说明"
	@echo "  - docs/Architecture.md - 架构设计"
	@echo "  - docs/CI-CD-Guide.md - CI/CD 指南"
	@echo "  - docs/API-Agents.md - Agent API 文档"

# ==================== 信息 ====================
info:  ## 显示项目信息
	@echo "项目信息"
	@echo "========================================"
	@echo "项目名称: Social Media Agent"
	@echo "版本: 1.0.0"
	@echo "Python 版本: $(shell python --version)"
	@echo "项目路径: $(shell pwd)"
	@echo ""
	@echo "依赖包数量: $(shell pip list | wc -l)"
	@echo "测试文件数量: $(shell find tests -name 'test_*.py' -o -name '*_test.py' | wc -l)"
	@echo "代码行数: $(shell find . -name '*.py' -not -path './venv/*' -not -path './.venv/*' -not -path './env/*' -not -path './outputs/*' | xargs wc -l | tail -1)"
	@echo "========================================"

# ==================== 快捷命令 ====================
quick-test: test-smoke test-fast  ## 快速测试（烟雾测试 + 快速测试）

full-check: format lint security test coverage  ## 完整检查（格式化、检查、测试、覆盖率）

release-check: clean full-check  ## 发布前检查

dev-setup: clean install-dev setup  ## 开发环境完整设置

