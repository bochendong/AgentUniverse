# Agent Database Manager

数据库操作管理器，提供简洁的 API 用于管理 agents。

## 数据库位置

数据库文件存储在 `backend/database/db/agent_data.db` 目录中。

## 使用方法

### 基本用法

```python
from backend.database import AgentDBManager
from backend.agent.BaseAgent import BaseAgent, AgentType

# 创建数据库管理器实例
db_manager = AgentDBManager()

# 或者指定自定义数据库路径
# db_manager = AgentDBManager(db_path="/path/to/custom/db/agent_data.db")
```

### 创建新 Agent

```python
# 创建一个新的 agent
agent = BaseAgent(
    name="My Agent",
    instructions="You are a helpful assistant.",
    agent_type=AgentType.BASE_AGENT
)

# 保存到数据库
success = db_manager.create_new(agent)
if success:
    print(f"Agent created with ID: {agent.id}")
```

### 根据 ID 加载 Agent

```python
# 加载 agent
agent = db_manager.load_agent_by_id("agent-id-here")
if agent:
    print(f"Loaded agent: {agent.name}")
else:
    print("Agent not found")
```

### 更新 Agent

```python
# 修改 agent 的属性
agent.name = "Updated Name"
agent.instructions = "Updated instructions"

# 更新到数据库
success = db_manager.update_agent(agent)
if success:
    print("Agent updated successfully")
```

### 删除 Agent

```python
# 删除 agent
success = db_manager.delete_agent("agent-id-here")
if success:
    print("Agent deleted successfully")
```

## API 参考

### AgentDBManager

#### `__init__(db_path: Optional[str] = None)`

初始化数据库管理器。

- `db_path`: 可选的数据库路径。如果不提供，使用默认路径 `backend/database/db/agent_data.db`

#### `create_new(agent: BaseAgent) -> bool`

创建新的 agent。

- `agent`: 要创建的 agent 对象
- 返回: 成功返回 `True`，失败返回 `False`
- 注意: 如果 agent ID 已存在，会返回 `False` 并提示使用 `update_agent()`

#### `load_agent_by_id(agent_id: str) -> Optional[BaseAgent]`

根据 ID 加载 agent。

- `agent_id`: Agent 的 ID
- 返回: 加载的 agent 对象，如果不存在返回 `None`

#### `update_agent(agent: BaseAgent) -> bool`

更新已存在的 agent。

- `agent`: 要更新的 agent 对象
- 返回: 成功返回 `True`，失败返回 `False`
- 注意: 如果 agent ID 不存在，会返回 `False` 并提示使用 `create_new()`

#### `delete_agent(agent_id: str) -> bool`

删除 agent。

- `agent_id`: 要删除的 agent ID
- 返回: 成功返回 `True`，失败返回 `False`

#### `get_db_path() -> str`

获取当前使用的数据库路径。

- 返回: 数据库文件路径
