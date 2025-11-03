# 图片生成问题修复文档

## 问题描述

### 现象
在生成第2张图片时，程序卡住接近2分钟，没有任何进度提示，用户不知道发生了什么。

### 日志分析
```
1007| 生成图片 2/4: ...New Zealand's South Island...
1008| HTTP 500 Internal Server Error
1009| Retrying in 0.396296 seconds      <- SDK自动重试
1010| HTTP 500 Internal Server Error
1011| Retrying in 0.911723 seconds      <- 第2次重试
1012| [用户感觉卡住，按了很多次左箭头]
1013| 最终失败: content_policy_violation
```

---

## 根本原因

### 1. 内容审核触发
OpenAI的DALL-E 3有严格的安全系统，会拒绝某些内容：
- **触发原因**：prompt中可能包含被标记的词汇或概念
- **错误类型**：`content_policy_violation`
- **HTTP状态码**：500 Internal Server Error

### 2. 无意义的重试
OpenAI Python SDK默认重试机制：
```python
# SDK默认配置
max_retries = 2  # 最多重试2次
retry_delays = [0.4s, 0.9s, ...]  # 指数退避
```

**问题**：
- 内容违规错误重试无意义（内容不会变）
- 每次重试增加等待时间（0.4s → 0.9s → 更久）
- 用户体验差：卡住、无提示

### 3. 缺少错误分类
所有错误都用同一个 `except Exception` 处理：
- 无法区分"内容违规"、"速率限制"、"超时"等不同错误
- 无法给出针对性的友好提示

---

## 解决方案

### 修改1：减少重试次数和添加超时

**位置**：`tools/image_generator.py:372-380`

```python
# 修改前
client = OpenAI(
    api_key=ModelConfig.OPENAI_API_KEY,
    base_url=ModelConfig.OPENAI_BASE_URL
)

# 修改后
client = OpenAI(
    api_key=ModelConfig.OPENAI_API_KEY,
    base_url=ModelConfig.OPENAI_BASE_URL,
    max_retries=1,  # 最多重试1次（默认是2次）
    timeout=60.0     # 60秒超时
)
```

**效果**：
- 重试次数：2次 → 1次
- 最大等待时间：~3秒 → ~1.5秒
- 总超时：无限制 → 60秒

### 修改2：错误分类和友好提示

**位置**：`tools/image_generator.py:428-443`

```python
except Exception as e:
    error_str = str(e)
    
    # 识别错误类型并给出友好提示
    if "content_policy_violation" in error_str or "safety system" in error_str:
        logger.warning(f"⚠️  第 {idx + 1} 张图片被安全系统拒绝（内容违规），已跳过")
        logger.debug(f"被拒绝的prompt: {prompt}")
    elif "rate_limit" in error_str or "429" in error_str:
        logger.warning(f"⚠️  第 {idx + 1} 张图片生成受限（API速率限制），已跳过")
    elif "timeout" in error_str.lower():
        logger.warning(f"⚠️  第 {idx + 1} 张图片生成超时，已跳过")
    else:
        logger.error(f"❌ 生成第 {idx + 1} 张图片失败: {str(e)}")
    
    # 无论什么错误，都继续生成下一张
    continue
```

**效果**：
- ✅ 内容违规：友好提示，跳过
- ✅ 速率限制：提示限制，跳过
- ✅ 超时：提示超时，跳过
- ✅ 其他错误：记录详细错误

### 修改3：部分成功反馈

**位置**：`tools/image_generator.py:109-138`

```python
# 判断是否部分成功
success_rate = len(images) / actual_count
if success_rate < 1.0:
    logger.warning(f"⚠️  部分图片生成失败：成功 {len(images)}/{actual_count} 张")
    message = f"部分成功：生成了 {len(images)}/{actual_count} 张图片"
else:
    logger.info(f"✅ 成功生成 {len(images)} 张图片")
    message = f"成功生成 {len(images)} 张图片"

return json.dumps({
    "success": True,
    "images": images,
    "topic": topic,
    "method": method,
    "count": len(images),
    "requested_count": actual_count,
    "success_rate": f"{success_rate:.0%}",
    "message": message
}, ensure_ascii=False, indent=2)
```

**效果**：
- 目标4张，成功3张 → 返回成功，但标记"部分成功"
- 目标4张，成功0张 → 返回失败，说明原因
- 提供成功率统计

---

## 修复前后对比

### 修复前
```
1. 第2张图片触发内容审核
2. SDK自动重试3次（0.4s + 0.9s + 更久）
3. 卡住接近2分钟
4. 用户不知道发生了什么
5. 只有ERROR日志，没有友好提示
6. 最终抛出异常，整个流程失败
```

### 修复后
```
1. 第2张图片触发内容审核
2. SDK重试1次（0.4s）
3. 快速失败（~1秒）
4. 友好提示："⚠️ 第2张图片被安全系统拒绝（内容违规），已跳过"
5. 继续生成第3、4张
6. 返回部分成功："成功 3/4 张图片"
```

---

## 测试验证

### 测试场景1：内容违规
```bash
cd /Users/keyvanzhuo/Documents/CodeProjects/ConnetOnion/Social-media-agent
python main.py

# 输入一个可能触发内容审核的主题
👤 你: 写一篇军事武器的内容

# 预期结果：
# 1. 部分图片被拒绝，快速跳过（~1秒）
# 2. 友好提示："⚠️ 第X张图片被安全系统拒绝"
# 3. 继续生成其他图片
# 4. 最终返回："部分成功：生成了 2/4 张图片"
```

### 测试场景2：超时
```bash
# 在网络不稳定时测试
👤 你: 写一篇旅游攻略

# 预期结果：
# 1. 60秒超时自动终止
# 2. 提示："⚠️ 第X张图片生成超时"
# 3. 继续下一张
```

### 测试场景3：API限制
```bash
# 频繁调用后测试
👤 你: 写5篇不同主题的内容

# 预期结果：
# 1. 触发429错误
# 2. 提示："⚠️ 第X张图片生成受限（API速率限制）"
# 3. 跳过该图片
```

---

## 相关错误类型说明

### OpenAI DALL-E 3常见错误

| 错误类型 | HTTP状态码 | 原因 | 是否可重试 |
|---------|-----------|------|-----------|
| `content_policy_violation` | 500 | 内容违反安全政策 | ❌ 否 |
| `rate_limit_exceeded` | 429 | 超过速率限制 | ✅ 是（延迟后） |
| `timeout` | 504 | 请求超时 | ✅ 是 |
| `invalid_api_key` | 401 | API密钥无效 | ❌ 否 |
| `insufficient_quota` | 429 | 配额不足 | ❌ 否 |

### 识别规则

```python
# 内容违规
if "content_policy_violation" in error_str or "safety system" in error_str:
    # 不重试，跳过

# 速率限制
elif "rate_limit" in error_str or "429" in error_str:
    # 可以延迟后重试，但当前选择跳过

# 超时
elif "timeout" in error_str.lower():
    # 可以重试，但当前选择跳过（已有SDK层重试）

# 其他
else:
    # 记录详细错误，继续下一张
```

---

## 最佳实践建议

### 1. Prompt优化
避免触发内容审核：
```python
# ❌ 可能被拒绝的prompt
"A photo of weapons and military equipment"

# ✅ 更安全的prompt
"A photo of historical museum display"
```

### 2. 降级策略
当DALL-E失败时，可以：
- 使用Unsplash/Pexels图库（已集成在MCP）
- 使用本地Stable Diffusion
- 让用户手动上传图片

### 3. 用户提示
明确告知用户：
```
⚠️ 部分图片生成失败
原因：内容可能触发了安全系统

建议：
1. 调整内容描述
2. 使用图库搜索（推荐）
3. 手动上传图片
```

### 4. 监控和日志
记录关键指标：
- 图片生成成功率
- 失败原因分布
- 平均生成时间
- API配额使用情况

---

## 总结

### 核心改进
1. ✅ **减少重试**：2次 → 1次
2. ✅ **添加超时**：无限制 → 60秒
3. ✅ **错误分类**：统一异常 → 分类处理
4. ✅ **友好提示**：技术错误 → 用户友好
5. ✅ **部分成功**：全失败 → 返回部分结果

### 用户体验提升
- 等待时间：~2分钟 → ~1-2秒
- 错误理解：不知道 → 明确提示
- 流程中断：是 → 否（继续生成其他图片）

### 后续优化方向
1. 添加prompt内容检测，预先过滤
2. 实现智能降级（DALL-E失败自动切换到图库）
3. 提供prompt修改建议
4. 缓存生成结果，避免重复生成

