# Notebook Wake-up Test

这个测试套件验证了 notebook agent 的唤醒功能，使用 `AgentManager` 来管理 agent 的加载和 tools 恢复。

## 功能

测试包括以下场景：

1. **基本唤醒测试** (`test_notebook_wakeup`)
   - 从数据库加载 notebook agent
   - 验证 tools 被正确恢复
   - 验证 agent 的基本功能（receive_messgae, agent_card）

2. **多次唤醒测试** (`test_multiple_wakeups`)
   - 测试 AgentManager 的缓存功能
   - 验证多次唤醒使用同一个实例
   - 验证 tools 在多次唤醒后仍然存在

3. **通过 send_message 唤醒** (`test_wakeup_via_send_message`)
   - 测试通过 send_message 工具唤醒 notebook agent
   - 验证 MasterAgent 可以正确唤醒子 agent
   - 验证唤醒的 agent 有完整的 tools

## 使用方法

### 运行测试

```bash
# 从项目根目录运行
python backend/tests/test_notebook_wakeup/test_notebook_wakeup.py
```

### 测试数据库选项

测试脚本提供两种方式创建测试数据库：

1. **复制生产数据库**（推荐用于真实场景测试）
   - 如果检测到生产数据库，会询问是否复制
   - 从复制的数据库中查找现有的 NoteBookAgent
   - 如果没有找到，会创建新的测试数据库

2. **创建新的测试数据库**
   - 自动创建 TopLevelAgent、MasterAgent 和 NoteBookAgent
   - 适合测试基本功能

### 测试数据库位置

测试数据库保存在：
```
backend/tests/test_notebook_wakeup/test_db/test_notebook_wakeup.db
```

## 测试输出

测试会输出详细的执行信息：
- ✓ 表示成功
- ✗ 表示失败
- ⚠ 表示警告

最后会显示测试摘要，包括每个测试的通过/失败状态。

## 依赖

- `backend.utils.agent_manager` - AgentManager 用于统一管理 agent 唤醒
- `backend.database.agent_db` - 数据库操作
- `backend.agent.NoteBookAgent` - NoteBookAgent 类

## 注意事项

- 测试会创建独立的测试数据库，不会影响生产数据
- 如果复制生产数据库，请确保生产数据库中有 NoteBookAgent
- 测试数据库会在每次运行时被清理（如果选择创建新数据库）
