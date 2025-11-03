"""
测试批处理模式
"""

import pytest
import json
from pathlib import Path
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import _load_tasks_from_file, _save_batch_report


def test_load_tasks_from_json(tmp_path):
    """测试从JSON文件加载任务"""
    # 创建测试文件
    task_file = tmp_path / "tasks.json"
    tasks_data = [
        {"task": "任务1", "priority": 1},
        {"task": "任务2", "priority": 2}
    ]
    
    with open(task_file, 'w', encoding='utf-8') as f:
        json.dump(tasks_data, f)
    
    # 加载任务
    tasks = _load_tasks_from_file(str(task_file))
    
    assert len(tasks) == 2
    assert tasks[0]["task"] == "任务1"
    assert tasks[1]["priority"] == 2


def test_load_tasks_from_txt(tmp_path):
    """测试从文本文件加载任务"""
    # 创建测试文件
    task_file = tmp_path / "tasks.txt"
    content = """# 这是注释
任务1
任务2

# 另一个注释
任务3
"""
    
    with open(task_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 加载任务
    tasks = _load_tasks_from_file(str(task_file))
    
    assert len(tasks) == 3
    assert tasks[0] == "任务1"
    assert tasks[1] == "任务2"
    assert tasks[2] == "任务3"


def test_load_tasks_file_not_found():
    """测试文件不存在的情况"""
    with pytest.raises(FileNotFoundError):
        _load_tasks_from_file("nonexistent_file.json")


def test_load_tasks_invalid_format(tmp_path):
    """测试不支持的文件格式"""
    task_file = tmp_path / "tasks.xml"
    task_file.write_text("<tasks></tasks>")
    
    with pytest.raises(ValueError, match="不支持的文件格式"):
        _load_tasks_from_file(str(task_file))


def test_load_tasks_invalid_json(tmp_path):
    """测试无效的JSON格式"""
    task_file = tmp_path / "tasks.json"
    task_file.write_text("not valid json")
    
    with pytest.raises(json.JSONDecodeError):
        _load_tasks_from_file(str(task_file))


def test_save_batch_report(tmp_path):
    """测试保存批处理报告"""
    results = [
        {
            "index": 1,
            "task": "任务1",
            "status": "success",
            "result": "成功",
            "timestamp": "2025-01-01T00:00:00"
        },
        {
            "index": 2,
            "task": "任务2",
            "status": "failed",
            "error": "失败原因",
            "timestamp": "2025-01-01T00:01:00"
        }
    ]
    
    task_file = str(tmp_path / "tasks.json")
    
    # 保存报告
    report_path = _save_batch_report(results, task_file)
    
    # 验证文件已创建
    assert os.path.exists(report_path)
    
    # 验证内容
    with open(report_path, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    assert report["summary"]["total"] == 2
    assert report["summary"]["success"] == 1
    assert report["summary"]["failed"] == 1
    assert len(report["results"]) == 2


def test_batch_tasks_example_files():
    """测试示例任务文件是否存在且格式正确"""
    from pathlib import Path
    
    project_root = Path(__file__).parent.parent
    examples_dir = project_root / "examples"
    
    # 检查示例文件
    txt_file = examples_dir / "batch_tasks_example.txt"
    json_file = examples_dir / "batch_tasks_example.json"
    
    if txt_file.exists():
        tasks = _load_tasks_from_file(str(txt_file))
        assert len(tasks) > 0
        print(f"✅ TXT示例文件包含 {len(tasks)} 个任务")
    
    if json_file.exists():
        tasks = _load_tasks_from_file(str(json_file))
        assert len(tasks) > 0
        print(f"✅ JSON示例文件包含 {len(tasks)} 个任务")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

