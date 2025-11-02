# AI 图片生成指南

## 📖 概述

本系统使用 **AI 生成图片**，而非搜索图库。这样可以确保：
- ✅ 完全原创的内容
- ✅ 精确匹配描述要求
- ✅ 高度可定制化
- ✅ 无版权问题

> **注意**：Unsplash 和 Pexels 图库搜索已经集成在 MCP 服务器中，如需使用请通过 MCP 调用。

---

## 🎨 支持的 AI 生成方式

### 1. DALL-E 3（推荐）⭐

**OpenAI 最新的图像生成模型**

**优势**：
- ✅ 最高质量的 AI 生成
- ✅ 完美理解复杂描述
- ✅ 支持多种风格和场景
- ✅ 自动优化提示词
- ✅ 生成速度快（10-15秒/张）

**费用**：
- Standard (1024×1024): $0.040/张
- HD (1024×1792): $0.080/张

**使用场景**：
- 所有类型的内容创作
- 需要特定场景的图片
- 创意概念图
- 不存在的场景

**配置**：
```bash
# .env 文件
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1  # 可选
```

### 2. Stable Diffusion（本地）

**开源的本地 AI 图像生成**

**优势**：
- ✅ 完全免费
- ✅ 无限制使用
- ✅ 完全可控（模型、参数）
- ✅ 隐私保护（本地运行）

**要求**：
- 需要 GPU（推荐 8GB+ VRAM）
- 本地部署 SD WebUI
- 一定的技术能力

**费用**：
- 免费（仅电费）

**使用场景**：
- 高频使用
- 预算有限
- 需要完全控制
- 特定风格需求

**配置**：
```bash
# .env 文件
SD_API_URL=http://localhost:7860

# 启动 SD WebUI 时需要加 --api 参数
python launch.py --api
```

---

## 🚀 使用方法

### 方法 1: 自动生成（推荐）

使用 Coordinator Agent 自动完成整个流程：

```python
from agent import create_coordinator_agent

coordinator = create_coordinator_agent()
result = coordinator.input("我想发表一篇关于悉尼旅游的帖子")
```

Coordinator 会自动：
1. 分析内容
2. 创作文案
3. **使用 DALL-E 3 生成图片** ⭐
4. 发布到小红书

### 方法 2: 从草稿生成

```python
from tools.content_creator import agent_c_create_content
from tools.image_generator import generate_images_from_draft

# 1. 创作内容（生成草稿）
creation_result = agent_c_create_content(
    analysis_result=analysis_json,
    topic="悉尼旅游"
)

creation_data = json.loads(creation_result)
draft_id = creation_data["metadata"]["draft_id"]

# 2. 从草稿使用 AI 生成图片
image_result = generate_images_from_draft(
    draft_id=draft_id,
    method="dalle",  # 使用 DALL-E 3
    count=4
)

# 3. 提取图片路径
image_data = json.loads(image_result)
image_paths = [img["path"] for img in image_data["images"]]
```

### 方法 3: 直接生成

```python
from tools.image_generator import generate_images_for_content
import json

# 准备详细的图片描述
image_suggestions = [
    {
        "description": "悉尼歌剧院在金色日落时的壮观景象，港口倒影，温暖的色调，专业摄影",
        "purpose": "展示标志性地标",
        "position": 1
    }
]

# 使用 DALL-E 3 生成
result = generate_images_for_content(
    image_suggestions=json.dumps(image_suggestions, ensure_ascii=False),
    topic="悉尼旅游",
    count=1,
    method="dalle",
    save_to_disk=True
)
```

---

## 📝 提示词优化技巧

### DALL-E 3 提示词建议

好的提示词能显著提升生成质量：

**✅ 好的描述：**
```python
"悉尼歌剧院在金色日落时的壮观景象，港口倒影，温暖的色调，专业摄影风格"
"邦迪海滩的蓝色海浪和冲浪者，明亮的天空，充满活力，俯视角度"
"悉尼海港大桥的夜景，璀璨的灯光，现代都市氛围，长曝光效果"
```

**❌ 不好的描述：**
```python
"悉尼"  # 太笼统
"一张好看的照片"  # 没有具体内容
"图片1"  # 完全没有描述
```

**提示词要素：**
1. **主体**：明确的拍摄对象
2. **环境**：时间、天气、氛围
3. **风格**：摄影风格、视角
4. **细节**：色调、光线、构图

**示例模板：**
```
[主体] + [环境/时间] + [风格/视角] + [细节/氛围]

例如：
悉尼歌剧院 + 在金色日落时 + 专业摄影风格 + 温暖色调，港口倒影
```

### Stable Diffusion 提示词建议

SD 使用标签式提示词：

**格式：**
```
masterpiece, best quality, [主体], [环境], [风格], [细节]
```

**示例：**
```
masterpiece, best quality, high resolution, Sydney Opera House, sunset, golden hour, harbor reflection, professional photography, cinematic lighting, warm tones
```

---

## 💰 成本分析

### DALL-E 3

| 质量 | 尺寸 | 价格/张 | 推荐场景 |
|------|------|---------|----------|
| Standard | 1024×1024 | $0.040 | 一般内容 |
| Standard | 1024×1792 | $0.040 | 小红书（竖屏）|
| HD | 1024×1024 | $0.080 | 高质量需求 |
| HD | 1024×1792 | $0.080 | 专业内容 |

**每篇帖子成本估算：**
- 4 张图片（Standard）: $0.16
- 4 张图片（HD）: $0.32
- 9 张图片（Standard）: $0.36

**月度成本估算：**
- 每天 1 篇（4张图）: $4.8/月
- 每天 3 篇（4张图）: $14.4/月
- 每天 10 篇（4张图）: $48/月

### Stable Diffusion

**完全免费**（仅电费）

**硬件成本：**
- GPU 租用：$0.5-2/小时
- 或一次性购买 GPU

**适合场景：**
- 高频使用（>100张/天）
- 长期使用
- 预算有限

---

## ⚙️ 配置说明

### 环境变量

在 `.env` 文件中配置：

```bash
# DALL-E 3（推荐）
OPENAI_API_KEY=sk-...  # 必需
OPENAI_BASE_URL=https://api.openai.com/v1  # 可选

# Stable Diffusion（可选）
SD_API_URL=http://localhost:7860  # SD WebUI 地址
```

### 业务配置

在 `config.py` 中调整：

```python
IMAGE_GENERATION = {
    "count": 4,              # 默认生成数量
    "min_count": 1,
    "max_count": 9,
    "aspect_ratio": "9:16",  # 小红书推荐比例
    "quality": "hd",         # standard 或 hd
}
```

---

## 🎯 最佳实践

### 1. 选择合适的方法

| 需求 | 推荐方法 | 原因 |
|------|----------|------|
| 一般内容创作 | DALL-E 3 | 质量最佳，速度快 |
| 高频使用 | Stable Diffusion | 完全免费 |
| 预算有限 | Stable Diffusion | 无使用限制 |
| 特殊风格 | Stable Diffusion | 可更换模型 |

### 2. 优化图片描述

```python
# 系统会自动优化，但你也可以提供更好的描述

# 基础描述（系统会优化）
"悉尼歌剧院"

# 优化后的描述（更好的效果）
"悉尼歌剧院在金色日落时的壮观景象，港口倒影，温暖的色调，专业摄影"
```

### 3. 控制生成数量

```python
# 小红书推荐 4-9 张图片
count=4  # 平衡质量和成本
count=6  # 更丰富的内容
count=9  # 最大化展示
```

### 4. 处理生成失败

```python
result = generate_images_from_draft(draft_id, method="dalle")
result_data = json.loads(result)

if not result_data.get("success"):
    # 方案1: 降级到本地 SD
    result = generate_images_from_draft(draft_id, method="local")
    
    # 方案2: 使用 MCP 搜索图库
    # 调用 MCP 的 Unsplash 工具
    
    # 方案3: 提示用户
    print("AI 生成失败，请检查配置")
```

---

## 🐛 故障排除

### 问题 1: DALL-E 3 调用失败

**现象：**
```
❌ DALL-E API 调用失败: ...
```

**解决方案：**
1. 检查 `OPENAI_API_KEY` 是否正确
2. 检查账户余额是否充足
3. 检查网络连接
4. 验证 API Key 权限

### 问题 2: 本地 SD 连接失败

**现象：**
```
❌ SD API 调用失败: Connection refused
```

**解决方案：**
1. 确认 SD WebUI 正在运行
2. 启动时加 `--api` 参数
3. 检查端口配置（默认 7860）
4. 检查防火墙设置

### 问题 3: 生成的图片不符合预期

**现象：**
图片与描述差异较大

**解决方案：**
1. 优化提示词（更详细、更具体）
2. 调整生成参数（quality、size）
3. 多次生成选择最佳结果
4. 考虑使用 HD 质量

### 问题 4: 内存不足

**现象：**
```
❌ MemoryError: 无法保存图片
```

**解决方案：**
1. 减少生成数量
2. 使用较小尺寸
3. 增加系统内存
4. 清理旧图片文件

---

## 📊 性能对比

| 指标 | DALL-E 3 | Stable Diffusion |
|------|----------|------------------|
| 质量 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 速度 | 10-15秒/张 | 5-30秒/张（取决于硬件）|
| 成本 | $0.04-0.08/张 | 免费 |
| 易用性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 可控性 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 部署 | 无需部署 | 需要本地部署 |

---

## 🎓 示例代码

### 完整工作流程

```python
# 运行完整示例
python examples/ai_image_generation.py
```

### 单独测试

```python
# 测试 DALL-E 3
python -c "
from tools.image_generator import generate_images_for_content
import json

suggestions = [{
    'description': '悉尼歌剧院在日落时的美景',
    'purpose': '测试',
    'position': 1
}]

result = generate_images_for_content(
    json.dumps(suggestions),
    '测试',
    count=1,
    method='dalle'
)

print(json.loads(result)['success'])
"
```

---

## 🔗 相关资源

- [DALL-E 3 官方文档](https://platform.openai.com/docs/guides/images)
- [Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
- [提示词工程指南](https://platform.openai.com/docs/guides/images/prompting)

---

## 💡 推荐配置

**标准配置（推荐）：**
```python
method="dalle"       # DALL-E 3
count=4             # 4 张图片
quality="standard"  # 标准质量
size="1024x1792"   # 竖屏（小红书推荐）
```

**成本优化：**
```python
method="local"      # 本地 SD（需要部署）
count=4
# 完全免费
```

**高质量内容：**
```python
method="dalle"
count=6
quality="hd"       # HD 质量
size="1024x1792"
```

---

**现在开始使用 AI 生成图片，创作独一无二的内容！** 🎨

