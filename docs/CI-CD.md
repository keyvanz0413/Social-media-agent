# CI/CD 配置说明

## 概述

本项目使用 GitHub Actions 进行持续集成/持续部署（CI/CD），专注于测试 Agent 功能，不包含需要独立服务的 MCP 功能测试。

## 工作流结构

### 1. 烟雾测试 (Smoke Tests)
- **目的**: 快速验证系统核心功能是否正常
- **运行时间**: ~3-5分钟
- **测试内容**:
  - 模块导入检查
  - 配置系统验证
  - 日志系统测试
  - Mock数据生成
  - 草稿管理器
  - 子Agent功能
  - 统一响应格式

### 2. 单元测试 (Unit Tests)
- **目的**: 测试各个模块的独立功能
- **运行时间**: ~10-15分钟
- **测试内容**:
  - 配置模块 (`test_config.py`)
  - 工具函数 (`test_tools.py`)
  - 工具模块 (`test_utils.py`)
- **排除内容**: 
  - 带有 `@pytest.mark.mcp` 标记的测试
  - 带有 `@pytest.mark.slow` 标记的测试

### 3. 集成测试 (Integration Tests)
- **目的**: 测试完整的Agent工作流
- **运行时间**: ~15-20分钟
- **测试内容**:
  - 核心功能测试
  - 工具模块测试
  - 内容创作测试
  - 评审系统测试
  - 端到端工作流
  - 批处理测试

### 4. 代码质量检查 (Code Quality)
- **目的**: 确保代码质量和一致性
- **工具**:
  - **Flake8**: Python代码静态检查
  - **Black**: 代码格式检查
  - **Pylint**: 代码质量分析（可选）

## 触发条件

CI/CD 工作流在以下情况下自动触发：

1. **推送到主分支**: 
   ```bash
   git push origin main
   git push origin develop
   ```

2. **Pull Request**:
   - 针对 `main` 分支的 PR
   - 针对 `develop` 分支的 PR

3. **手动触发**:
   - 在 GitHub Actions 页面手动运行

## 环境配置

### 必需环境变量
```bash
MOCK_MODE=true          # 启用Mock模式，避免真实API调用
PYTHON_VERSION=3.10     # Python版本
```

### 可选环境变量（生产环境）
```bash
OPENAI_API_KEY=xxx      # OpenAI API密钥（生产环境）
OPENAI_BASE_URL=xxx     # OpenAI API地址（可选）
```

> ⚠️ **注意**: CI环境中默认使用Mock模式，不需要真实的API密钥

## MCP 测试排除策略

### 为什么排除 MCP 测试？

MCP（Model Context Protocol）功能需要单独运行的服务器：
```bash
# MCP服务需要单独启动
npx @modelcontextprotocol/server-xiaohongshu
```

在 CI/CD 环境中，我们：
1. ❌ **不测试 MCP 连接** - 避免服务依赖
2. ✅ **测试 Agent 逻辑** - 使用 Mock 数据
3. ✅ **测试业务流程** - 验证工作流正确性

### 如何标记 MCP 测试？

在测试函数上添加 `@pytest.mark.mcp` 标记：

```python
@pytest.mark.mcp
def test_mcp_connection():
    """需要真实MCP服务的测试"""
    client = XiaohongshuMCPClient()
    result = client.search("测试")
    assert result is not None
```

### CI/CD 中的排除方式

```bash
# pytest 命令自动排除 mcp 标记的测试
pytest -q -m unit tests
```

## 本地测试

### 快速测试（推荐）

```bash
# 运行烟雾测试
pytest -q -m smoke tests/smoke_test.py

# 运行所有Agent测试（排除MCP）
pytest -q -m unit tests
```

### 完整测试

```bash
# 运行综合测试套件
pytest -q -m integration tests/comprehensive_test.py

# 使用pytest运行所有测试（排除MCP和慢速测试）
pytest -q -m unit tests
```

### 测试特定模块

```bash
# 测试配置模块
pytest tests/test_config.py -v

# 测试工具模块
pytest tests/test_tools.py -v

# 测试工具函数
pytest tests/test_utils.py -v
```

### 代码质量检查

```bash
# Flake8 检查
flake8 . --exclude=__pycache__,venv,outputs,logs

# Black 格式检查
black --check .

# Black 自动格式化
black .
```

## 测试覆盖率

启用测试覆盖率报告：

```bash
# 运行测试并生成覆盖率报告
pytest --cov=. --cov-report=html --cov-report=term -m "not mcp"

# 查看HTML报告
open htmlcov/index.html
```

## 测试最佳实践

### 1. 使用 Mock 模式
```python
import os
os.environ['MOCK_MODE'] = 'true'
```

### 2. 标记测试类型
```python
@pytest.mark.unit          # 单元测试
@pytest.mark.integration   # 集成测试
@pytest.mark.slow          # 慢速测试
@pytest.mark.mcp           # 需要MCP服务的测试
```

### 3. 测试隔离
```python
@pytest.fixture(autouse=True)
def setup_test_env():
    """为每个测试设置环境"""
    os.environ['MOCK_MODE'] = 'true'
    yield
    # 清理
```

### 4. 异常处理
```python
def test_error_handling():
    """测试错误处理"""
    with pytest.raises(AgentError):
        raise AgentError("测试错误")
```

## CI/CD 工作流文件

主配置文件位置：
```
.github/workflows/agent-tests.yml
```

## 故障排查

### 测试失败

1. **检查日志输出**
   ```bash
   # 查看详细日志
   pytest -v -s
   ```

2. **本地重现**
   ```bash
   # 设置相同的环境变量
   export MOCK_MODE=true
   pytest -q -m smoke tests/smoke_test.py
   ```

3. **检查依赖**
   ```bash
   pip install -r requirements.txt
   ```

### 常见问题

#### 问题1: 模块导入失败
```bash
# 解决方案：添加项目路径到 PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### 问题2: Mock模式未启用
```bash
# 确认环境变量
echo $MOCK_MODE  # 应该输出 "true"
```

#### 问题3: 测试超时
```bash
# 增加超时时间或跳过慢速测试
pytest -q -m unit tests
```

## 本地 CI/CD 脚本

创建 `scripts/run_ci_tests.sh` 脚本：

```bash
#!/bin/bash
# 本地运行 CI/CD 测试流程

set -e  # 遇到错误立即退出

echo "=== 开始本地CI/CD测试 ==="
echo ""

# 设置环境变量
export MOCK_MODE=true

# 1. 烟雾测试
echo "📦 步骤 1/4: 烟雾测试"
pytest -q -m smoke tests/smoke_test.py
echo ""

# 2. 单元测试
echo "🧪 步骤 2/4: 单元测试"
pytest tests/test_config.py tests/test_tools.py tests/test_utils.py \
  -v -m "not mcp and not slow"
echo ""

# 3. 集成测试
echo "🔄 步骤 3/4: 集成测试"
pytest -q -m integration tests/comprehensive_test.py
echo ""

# 4. 代码质量
echo "✨ 步骤 4/4: 代码质量检查"
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics \
  --exclude=__pycache__,venv,env,.venv,.git,outputs,logs
echo ""

echo "🎉 所有测试通过！"
```

## 持续改进

### 后续优化方向

1. **测试覆盖率目标**: 80%+
2. **性能测试**: 添加性能基准测试
3. **安全扫描**: 集成安全漏洞扫描
4. **文档生成**: 自动生成API文档
5. **发布自动化**: 自动化版本发布流程

### 监控指标

- ✅ 测试通过率
- ⏱️ 测试执行时间
- 📊 代码覆盖率
- 🐛 Bug检出率
- 📈 代码质量分数

## 参考资源

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Pytest 文档](https://docs.pytest.org/)
- [Flake8 文档](https://flake8.pycqa.org/)
- [Black 文档](https://black.readthedocs.io/)

## 联系方式

如有问题或建议，请：
1. 提交 GitHub Issue
2. 联系项目维护者
3. 查看项目文档

