# 综合测试套件使用指南

## 📋 概述

`comprehensive_test.py` 是一个整合了所有功能测试的综合测试文件，用于全面检查 Social Media Agent 系统的各项功能。

### 测试覆盖范围

该测试文件涵盖以下6大模块，共18项测试：

1. **核心功能测试** (3项)
   - 模块导入检查
   - 配置系统验证
   - 日志系统测试

2. **工具模块测试** (5项)
   - 缓存管理器
   - 错误处理
   - 性能监控
   - 草稿管理器
   - Mock 数据生成

3. **内容创作测试** (4项)
   - 内容分析 Agent
   - 内容创作 Agent
   - 发布工具
   - 图片生成工具

4. **评审系统测试** (4项)
   - 质量评审
   - 互动评审
   - 合规性评审
   - 评审工具集

5. **端到端测试** (1项)
   - 完整工作流测试（分析→创作→评审）

6. **批处理测试** (1项)
   - 批量任务处理

## 🚀 快速开始

### 基本运行

```bash
# 进入项目目录
cd Social-media-agent

# 运行综合测试
python tests/comprehensive_test.py
```

### 使用 pytest 运行

```bash
# 安装 pytest（如果未安装）
pip install pytest

# 使用 pytest 运行
pytest tests/comprehensive_test.py -v

# 显示详细输出
pytest tests/comprehensive_test.py -v -s
```

## 📊 测试结果解读

### 输出格式

测试运行后会显示：

```
======================================================================
🧪 Social Media Agent - 综合测试套件
======================================================================
项目路径: /path/to/project
Mock 模式: 启用
测试时间: 2025-11-03 13:18:56

======================================================================
🧪 测试套件：核心功能
======================================================================

======================================================================
⚙️  测试：配置系统
======================================================================
✅ 项目根目录: /path/to/project
✅ 输出目录已创建
✅ Mock 模式已启用
✅ 配置验证通过

...

======================================================================
📊 测试总结
======================================================================

📦 核心功能: 2/3 通过
   ✅ Config
   ❌ Imports
   ✅ Logging

...

======================================================================
总计: 10/18 通过 (55.6%)
耗时: 3.7 秒
```

### 状态标识

- ✅ : 测试通过
- ❌ : 测试失败
- ⚠️  : 警告（功能可用但有问题）

## 🔧 常见问题

### 1. 网络相关测试失败

**问题：** 某些测试因为网络问题失败

**解决方法：**
- 确保网络连接正常
- 对于不需要真实 API 的测试，使用 Mock 模式（默认已启用）

### 2. API 密钥缺失

**问题：** 评审系统测试失败，提示缺少 API key

**解决方法：**
```bash
# 设置 OpenAI API Key
export OPENAI_API_KEY="your-api-key"

# 设置 Anthropic API Key（用于 Claude）
export ANTHROPIC_API_KEY="your-api-key"
```

或者在项目根目录创建 `.env` 文件：
```
OPENAI_API_KEY=your-api-key
ANTHROPIC_API_KEY=your-api-key
```

### 3. 导入错误

**问题：** 模块导入失败

**解决方法：**
```bash
# 确保所有依赖已安装
pip install -r requirements.txt

# 如果使用 connectonion 框架
pip install connectonion
```

### 4. MCP 服务未运行

**问题：** 小红书 MCP 相关测试失败

**解决方法：**
- 在 Mock 模式下，MCP 会被模拟，不需要真实服务
- 如果需要测试真实 MCP，启动 xiaohongshu-mcp 服务

## 📝 测试模式

### Mock 模式（默认）

默认启用 Mock 模式，所有外部 API 调用都会被模拟：

```python
# Mock 模式已在测试文件中自动设置
os.environ['MOCK_MODE'] = 'true'
```

**优点：**
- 不需要真实 API 密钥
- 运行速度快
- 不消耗 API 配额
- 适合 CI/CD

### 真实模式

如果需要测试真实 API，修改测试文件：

```python
# 在 comprehensive_test.py 顶部修改
os.environ['MOCK_MODE'] = 'false'
```

**注意：** 真实模式需要：
- 有效的 API 密钥
- 网络连接
- 会消耗 API 配额

## 🎯 针对性测试

### 只运行特定套件

如果只想测试特定功能，可以修改 `main()` 函数：

```python
def main():
    runner = TestRunner()
    
    # 只运行核心功能和工具模块测试
    runner.run_test_suite("核心功能", CoreFunctionalityTests)
    runner.run_test_suite("工具模块", UtilityTests)
    # 注释掉其他测试...
    
    return runner.print_summary()
```

### 运行单个测试

```python
# 在 Python 交互式环境或脚本中
from tests.comprehensive_test import CoreFunctionalityTests

# 运行单个测试
result = CoreFunctionalityTests.test_config()
print(f"测试结果: {'通过' if result else '失败'}")
```

## 📦 与原有测试文件的关系

### 原测试文件保留

以下原测试文件仍然保留，可以单独运行：

- `smoke_test.py` - 快速烟雾测试
- `test_config_validation.py` - 配置验证
- `test_cache_functionality.py` - 缓存功能
- `test_image_generator.py` - 图片生成
- `test_error_handling.py` - 错误处理
- `test_performance_monitor.py` - 性能监控
- `test_batch_mode.py` - 批处理
- `test_end_to_end_with_review.py` - 端到端
- `test_quality_reviewer_agent.py` - 质量评审
- `test_review_tools.py` - 评审工具

### 综合测试 vs 单独测试

| 特性 | 综合测试 | 单独测试 |
|------|---------|----------|
| 覆盖范围 | 全面 | 针对性强 |
| 运行时间 | 较长 | 较短 |
| 适用场景 | CI/CD、全面检查 | 开发调试、局部测试 |
| 结果展示 | 统一汇总 | 详细输出 |

## 🔄 CI/CD 集成

### GitHub Actions 示例

```yaml
name: 综合测试

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: 设置 Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: 安装依赖
        run: |
          pip install -r requirements.txt
      
      - name: 运行综合测试
        run: |
          python tests/comprehensive_test.py
        env:
          MOCK_MODE: 'true'
```

### GitLab CI 示例

```yaml
test:
  stage: test
  script:
    - pip install -r requirements.txt
    - python tests/comprehensive_test.py
  variables:
    MOCK_MODE: 'true'
```

## 📈 测试报告

### 生成详细报告

```bash
# 使用 pytest 生成 HTML 报告
pip install pytest-html
pytest tests/comprehensive_test.py --html=report.html --self-contained-html
```

### 代码覆盖率

```bash
# 安装 coverage
pip install coverage

# 运行测试并生成覆盖率报告
coverage run -m pytest tests/comprehensive_test.py
coverage report
coverage html
```

## 🛠️ 自定义测试

### 添加新测试

1. 在相应的测试类中添加方法：

```python
class CoreFunctionalityTests:
    @staticmethod
    def test_your_new_feature() -> bool:
        """测试：你的新功能"""
        print("\n" + "=" * 70)
        print("🔧 测试：你的新功能")
        print("=" * 70)
        
        try:
            # 你的测试代码
            assert True
            print("✅ 测试通过")
            return True
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            return False
```

2. 测试会自动被包含在测试套件中

### 创建新的测试套件

```python
class YourNewTestSuite:
    """你的新测试套件"""
    
    @staticmethod
    def test_feature_1() -> bool:
        # 测试代码
        return True
    
    @staticmethod
    def test_feature_2() -> bool:
        # 测试代码
        return True

# 在 main() 中添加
runner.run_test_suite("你的测试套件", YourNewTestSuite)
```

## 📞 获取帮助

如果遇到问题：

1. 查看测试输出的详细错误信息
2. 检查日志文件：`outputs/logs/`
3. 参考原有的单独测试文件
4. 查看项目文档：`docs/`

## 🎓 最佳实践

1. **定期运行** - 在每次代码改动后运行测试
2. **CI/CD 集成** - 将测试集成到 CI/CD 流程
3. **Mock 优先** - 开发时使用 Mock 模式
4. **真实验证** - 发布前用真实模式验证
5. **关注失败** - 重点关注新增的失败项
6. **更新测试** - 新功能开发后及时添加测试

## 📄 总结

`comprehensive_test.py` 提供了一个全面、易用的测试解决方案，帮助你：

- ✅ 快速验证系统整体健康状况
- ✅ 在开发过程中及时发现问题
- ✅ 确保代码质量和稳定性
- ✅ 支持 CI/CD 自动化测试
- ✅ 提供清晰的测试报告

建议将此测试作为项目的标准测试流程的一部分！

