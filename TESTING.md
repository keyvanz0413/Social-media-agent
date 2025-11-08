# 测试指南

## 📋 快速开始

### 一键运行测试

```bash
# 使用 Makefile（推荐）
make test

# 使用脚本
./scripts/run-tests.sh all

# 直接使用 pytest
export MOCK_MODE=true && pytest tests/ -v
```

---

## 🧪 测试类型

### 1. 烟雾测试（Smoke Test）

**目的**: 快速验证核心功能是否正常

**运行时间**: ~10 秒

**运行方法**:

```bash
# 方式 1: 直接运行
python tests/smoke_test.py

# 方式 2: 使用 Makefile
make test-smoke

# 方式 3: 使用脚本
./scripts/run-tests.sh smoke
```

**测试内容**:
- ✅ 模块导入
- ✅ 配置加载
- ✅ 日志系统
- ✅ Mock 数据生成
- ✅ 草稿管理
- ✅ 子 Agent 功能
- ✅ 响应格式

---

### 2. 单元测试（Unit Test）

**目的**: 测试独立模块和函数

**运行时间**: ~30 秒

**运行方法**:

```bash
# 运行所有单元测试
pytest tests/ -v -m unit

# 使用 Makefile
make test-unit

# 运行特定测试文件
pytest tests/test_config.py -v
pytest tests/test_utils.py -v
pytest tests/test_tools.py -v
```

**测试文件**:

| 文件 | 描述 | 测试数量 |
|------|------|---------|
| `test_config.py` | 配置模块测试 | 12 |
| `test_utils.py` | 工具模块测试 | 15 |
| `test_tools.py` | 工具函数测试 | 10 |

**测试覆盖**:
- ✅ 配置加载和验证
- ✅ 草稿管理（保存、加载、删除）
- ✅ 响应格式化
- ✅ Mock 数据生成
- ✅ 日志系统
- ✅ 错误处理
- ✅ 性能监控

---

### 3. 集成测试（Integration Test）

**目的**: 测试模块间的协作

**运行时间**: ~1 分钟

**运行方法**:

```bash
# 运行集成测试
pytest tests/ -v -m integration

# 使用 Makefile
make test-integration
```

**测试场景**:
- ✅ 完整内容创作流程（分析→创作→评审→发布）
- ✅ Agent 间通信
- ✅ 批量任务处理

---

### 4. 综合测试（Comprehensive Test）

**目的**: 全面测试所有功能模块

**运行时间**: ~2 分钟

**运行方法**:

```bash
# 运行综合测试
python tests/comprehensive_test.py

# 使用 Makefile
make test-comprehensive

# 使用脚本
./scripts/run-tests.sh comprehensive
```

**测试套件**:
1. 核心功能测试
2. 工具模块测试
3. 内容创作测试
4. 评审系统测试
5. 端到端测试
6. 批处理测试

---

## 📊 代码覆盖率

### 生成覆盖率报告

```bash
# 方式 1: 使用 Makefile（推荐）
make coverage

# 方式 2: 使用脚本
./scripts/run-tests.sh coverage

# 方式 3: 直接使用 pytest
export MOCK_MODE=true
pytest tests/ --cov=. --cov-report=html --cov-report=term-missing
```

### 查看覆盖率报告

```bash
# macOS
make coverage-open

# 手动打开
open htmlcov/index.html
```

### 覆盖率目标

- **最低要求**: 60%
- **推荐目标**: 80%
- **理想目标**: 90%+

---

## 🎯 测试标记（Markers）

使用 pytest markers 来组织和筛选测试：

```bash
# 只运行单元测试
pytest -m unit

# 只运行集成测试
pytest -m integration

# 跳过慢速测试
pytest -m "not slow"

# 运行烟雾测试
pytest -m smoke

# 运行需要 Mock 的测试
pytest -m mock

# 运行需要 API 的测试（实际环境）
pytest -m api

# 运行需要 MCP 服务的测试
pytest -m mcp
```

**可用标记**:
- `unit` - 单元测试
- `integration` - 集成测试
- `slow` - 慢速测试
- `smoke` - 烟雾测试
- `mock` - 使用 Mock 的测试
- `api` - 需要 API 访问的测试
- `mcp` - 需要 MCP 服务的测试

---

## 🛠️ 测试配置

### pytest 配置

配置文件：`pytest.ini` 和 `pyproject.toml`

**关键配置**:
```ini
[pytest]
testpaths = tests
addopts = -v --cov=. --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
```

### Mock 模式

所有测试默认在 Mock 模式下运行，避免真实 API 调用：

```python
import os
os.environ['MOCK_MODE'] = 'true'
```

---

## 📝 编写测试

### 测试文件结构

```python
"""
单元测试：模块名称
简短描述
"""

import os
import pytest

# 设置 Mock 模式
os.environ['MOCK_MODE'] = 'true'


class TestModuleName:
    """模块测试类"""
    
    @pytest.fixture
    def sample_data(self):
        """测试数据 fixture"""
        return {'key': 'value'}
    
    def test_function_name(self, sample_data):
        """测试函数名称"""
        # 安排（Arrange）
        expected = 'value'
        
        # 执行（Act）
        result = sample_data['key']
        
        # 断言（Assert）
        assert result == expected
```

### 测试命名规范

```python
# ✅ 好的命名
def test_config_loads_from_environment():
    pass

def test_draft_manager_saves_correctly():
    pass

def test_content_creation_returns_valid_format():
    pass

# ❌ 不好的命名
def test1():
    pass

def test_something():
    pass
```

### 使用 Fixtures

```python
import pytest

@pytest.fixture
def draft_manager():
    """创建草稿管理器实例"""
    from utils.draft_manager import DraftManager
    return DraftManager()

@pytest.fixture
def sample_content():
    """示例内容数据"""
    return {
        'title': '测试标题',
        'content': '测试内容'
    }

def test_save_draft(draft_manager, sample_content):
    """使用 fixtures 的测试"""
    draft_id = draft_manager.save(sample_content)
    assert draft_id is not None
```

---

## 🔍 调试测试

### 详细输出

```bash
# 显示 print 输出
pytest tests/test_config.py -v -s

# 显示详细的失败信息
pytest tests/test_config.py -v --tb=long

# 显示最详细的信息
pytest tests/test_config.py -vv --tb=long
```

### 只运行失败的测试

```bash
# 只重新运行上次失败的测试
pytest --lf

# 先运行失败的，再运行其他的
pytest --ff
```

### 在第一个失败时停止

```bash
pytest -x
```

### 进入调试模式

```bash
# 在失败时自动进入 pdb
pytest --pdb

# 在测试开始时进入 pdb
pytest --trace
```

---

## ⚡ 性能优化

### 并行运行测试

```bash
# 自动选择进程数
pytest -n auto

# 指定进程数
pytest -n 4

# 使用 Makefile
make test-parallel
```

### 只运行快速测试

```bash
# 跳过标记为 slow 的测试
pytest -m "not slow"

# 使用 Makefile
make test-fast
```

---

## 📈 持续集成

### GitHub Actions

CI 工作流在以下情况触发：
- Push 到 `main` 或 `develop` 分支
- 创建 Pull Request
- 手动触发

**CI 流程**:
1. 代码质量检查（Black, Flake8, MyPy）
2. 多版本 Python 测试（3.9-3.12）
3. 集成测试
4. 安全扫描
5. 文档检查
6. 构建验证

### 本地模拟 CI

```bash
# 运行完整的 CI 检查
make ci-local

# 或使用脚本
./scripts/pre-push-check.sh
```

---

## 🚀 最佳实践

### 1. 提交前检查

```bash
# 快速检查
make test-smoke

# 完整检查
make full-check

# 或使用 pre-push 脚本
./scripts/pre-push-check.sh
```

### 2. 代码覆盖率

- 新功能必须包含测试
- PR 不应降低整体覆盖率
- 关键路径需要 100% 覆盖

### 3. 测试独立性

- 测试之间不应有依赖
- 使用 fixtures 管理共享状态
- 清理测试产生的数据

### 4. Mock 外部依赖

- API 调用使用 Mock
- 文件操作使用临时目录
- 时间相关使用 freezegun

---

## 📚 参考资源

### 文档
- [pytest 官方文档](https://docs.pytest.org/)
- [Coverage.py 文档](https://coverage.readthedocs.io/)
- [CI/CD 指南](./docs/CI-CD-Guide.md)

### 项目测试文件
- `tests/smoke_test.py` - 烟雾测试示例
- `tests/test_config.py` - 单元测试示例
- `tests/test_utils.py` - 工具测试示例
- `tests/comprehensive_test.py` - 综合测试示例

---

## ❓ 常见问题

### Q: 测试运行很慢怎么办？

**A**: 
```bash
# 1. 并行运行
make test-parallel

# 2. 只运行快速测试
make test-fast

# 3. 只运行特定测试
pytest tests/test_config.py -v
```

### Q: 如何查看测试覆盖率？

**A**:
```bash
make coverage-open
```

### Q: 测试失败如何调试？

**A**:
```bash
# 详细输出
pytest tests/test_config.py -vv --tb=long

# 进入调试器
pytest tests/test_config.py --pdb
```

### Q: 如何跳过某些测试？

**A**:
```python
import pytest

@pytest.mark.skip(reason="暂时跳过")
def test_something():
    pass

@pytest.mark.skipif(condition, reason="条件跳过")
def test_something_else():
    pass
```

---

## 🎓 学习资源

### 视频教程
- [pytest 入门教程](https://www.youtube.com/watch?v=bbp_849-RZ4)
- [Python 测试最佳实践](https://www.youtube.com/watch?v=DhUpxWjOhME)

### 推荐阅读
- 《Python Testing with pytest》
- 《Test-Driven Development with Python》

---

**祝测试愉快！** 🎉

如有问题，请查阅 [CI/CD 指南](./docs/CI-CD-Guide.md) 或提交 Issue。

