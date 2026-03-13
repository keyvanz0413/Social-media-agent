"""
Unit tests for LangChain StructuredTool registry.
"""

import pytest


@pytest.mark.unit
def test_structured_tool_registry_contains_core_tools():
    from social_media_agent.tools.langchain_tools import get_structured_tools

    names = {t.name for t in get_structured_tools()}
    assert "analyze_xiaohongshu" in names
    assert "create_content" in names
    assert "save_memory" in names
    assert "create_schedule" in names


@pytest.mark.unit
def test_create_content_tool_accepts_dict_analysis(monkeypatch):
    import social_media_agent.tools.langchain_tools as lt

    def _fake_create_content(analysis_result, topic, style="casual", quality_level="balanced"):
        assert isinstance(analysis_result, dict)
        parsed = analysis_result
        assert parsed.get("keyword") == "悉尼旅行"
        return {"success": True, "data": {"title": f"{topic}-标题"}}

    monkeypatch.setattr(lt, "create_content_native", _fake_create_content)

    tool = next(t for t in lt.get_structured_tools() if t.name == "create_content")
    result = tool.invoke(
        {
            "analysis_result": {"keyword": "悉尼旅行"},
            "topic": "悉尼旅行",
            "style": "casual",
            "quality_level": "balanced",
        }
    )
    assert result["success"] is True
    assert result["data"]["title"] == "悉尼旅行-标题"


@pytest.mark.unit
def test_save_memory_tool_accepts_dict_metadata(monkeypatch):
    import social_media_agent.tools.langchain_tools as lt

    def _fake_save_memory(item_type, content, metadata=None, source="agent"):
        assert isinstance(metadata, dict)
        parsed_metadata = metadata
        assert parsed_metadata["lang"] == "zh"
        return {"success": True, "data": {"item_type": item_type, "content": content}}

    monkeypatch.setattr(lt, "save_memory_native", _fake_save_memory)

    tool = next(t for t in lt.get_structured_tools() if t.name == "save_memory")
    result = tool.invoke(
        {
            "item_type": "user_preference",
            "content": "偏好短标题",
            "metadata": {"lang": "zh"},
            "source": "test",
        }
    )
    assert result["success"] is True
    assert result["data"]["item_type"] == "user_preference"
