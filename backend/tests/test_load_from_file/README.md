# Test Load From File - 使用测试数据库

这个目录包含了用于测试文件上传和 notebook 创建的测试脚本。

## 测试文件

### `test_top_level_agent.py`
原始测试脚本，使用默认数据库。适用于手动运行和开发测试。

### `test_with_test_db.py`
使用 pytest 框架的测试脚本，使用独立的测试数据库。适用于自动化测试和 CI/CD。

## 运行测试

### 运行 pytest 测试（推荐）

```bash
# 安装 pytest（如果还没有）
pip install pytest pytest-asyncio

# 运行所有测试
pytest backend/tests/test_load_from_file/test_with_test_db.py -v -s

# 运行特定测试
pytest backend/tests/test_load_from_file/test_with_test_db.py::test_create_top_level_agent -v -s
```

### 运行原始测试脚本

```bash
python backend/tests/test_load_from_file/test_top_level_agent.py
```

## 测试数据库

`test_with_test_db.py` 使用临时测试数据库，具有以下特点：

- **隔离性**：每个测试使用独立的临时数据库
- **自动清理**：测试结束后自动删除临时数据库
- **不影响生产数据**：不会修改或访问生产数据库

测试数据库存储在临时目录中，格式为：
```
/tmp/agent_test_db_XXXXXX/test_agent_data.db
```

## 测试文件要求

测试需要以下文件存在：

- `Python.md` - Python 相关的笔记文件
- `Group.md` - Group 理论相关的笔记文件

这些文件应该位于 `backend/tests/test_load_from_file/` 目录下。

## 测试内容

测试包括以下场景：

1. **创建 TopLevelAgent** - 验证可以创建 TopLevelAgent 实例
2. **MasterAgent 存在** - 验证 TopLevelAgent 包含 MasterAgent
3. **文件上传** - 测试上传 Python.md 和 Group.md 文件
4. **Notebook 创建** - 验证文件上传后创建了 NotebookAgent
5. **问题查询** - 测试对 Python 和 Group 主题的问题查询
6. **Agent Card** - 验证 agent card 内容正确生成

## 注意事项

- 测试是异步的，需要等待 notebook 创建完成
- 文件上传测试可能需要较长时间（约 15 秒）
- 确保测试文件存在且格式正确
