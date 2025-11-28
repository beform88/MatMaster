# MatMaster 整体运行逻辑详细说明

## 一、整体架构

MatMaster 采用分层 Agent 架构：
- **顶层**: `MatMasterFlowAgent` - 主流程控制
- **中层**: `MatMasterSupervisorAgent` (execution_agent) - 计划执行协调
- **底层**: 各种专业 Agent（如 apex_agent, abacus_agent, structure_generate_agent 等）

## 二、完整执行流程

### 阶段1: 意图识别与问题分析

```
用户输入
  ↓
intent_agent (识别意图: CHAT 或 RESEARCH)
  ↓
如果是 RESEARCH 模式:
  ├─ expand_agent (扩写用户问题)
  ├─ scene_agent (划分问题场景)
  └─ 更新 state['scenes']
```

**关键点**:
- 一旦进入 RESEARCH 模式，暂时无法退出
- 如果用户上传文件，强制切换为 RESEARCH 模式

### 阶段2: 计划制定

```
检查计划状态
  ↓
plan_confirm_agent (判断用户是否确认计划)
  ↓
如果需要制定新计划:
  ├─ plan_make_agent (根据场景和可用工具制定计划)
  │   └─ 动态创建 PlanSchema（基于 available_tools）
  ├─ plan_info_agent (总结计划内容)
  └─ 询问用户确认计划
      └─ 如果用户确认 (plan_confirm.flag = True)，进入执行阶段
```

**计划结构**:
```json
{
  "steps": [
    {
      "tool_name": "工具名称",
      "description": "步骤描述",
      "status": "plan" | "process" | "submitted" | "success" | "failed"
    }
  ],
  "feasibility": "full" | "part" | "null"
}
```

### 阶段3: 参数提取 (parameters_agent)

```
计划确认后，进入参数提取阶段:
  ↓
parameters_agent (收集所有异步工具的参数)
  ├─ 1. get_async_tool_steps() (获取所有异步工具步骤)
  ├─ 2. collect_tool_params_parallel() (并行收集所有工具参数)
  │   └─ 对每个工具:
  │       ├─ 调用对应 agent 的 tool_call_info_agent
  │       ├─ 如有缺失参数，调用 recommend_params_agent
  │       ├─ 调用 recommend_params_schema_agent 补全参数
  │       └─ 返回完整的 tool_args
  ├─ 3. 展示参数汇总信息（不生成 JSON，等待用户确认）
  └─ 4. 保存参数到 state['parameters_collection']
```

**关键点**:
- 只收集异步工具的参数（继承自 `BaseAsyncJobAgent` 的 agent）
- 参数收集是并行进行的，提高效率
- 收集完成后展示参数，但不立即生成 JSON 文件

### 阶段4: 参数确认 (parameters_confirm_agent)

```
参数提取完成后，进入参数确认阶段:
  ↓
parameters_confirm_agent (判断用户是否确认参数)
  ├─ 1. 显示参数确认卡片
  ├─ 2. 分析用户回复，判断是否确认
  └─ 3. 如果确认 (parameters_confirm.flag = True)，进入 JSON 生成阶段
```

**关键点**:
- 用户必须明确确认参数后才会生成 JSON
- 如果用户未确认，流程会暂停等待

### 阶段5: 生成参数 JSON (parameters_agent)

```
参数确认后，生成 JSON 文件:
  ↓
parameters_agent (生成 JSON)
  ├─ 1. analyze_async_task_dependencies() (分析依赖关系)
  ├─ 2. save_parameters_to_json() (保存为 JSON 文件)
  └─ 3. 保存 JSON 路径到 state['parameters_json_path']
  ↓
流程结束
```

**注意**: `execution_agent` 的执行逻辑已被停用，不会执行计划中的任务。

## 三、工具参数获取流程

### 3.1 参数获取的核心流程 (BaseAgentWithParamsRecommendation)

所有支持参数推荐的 Agent 都继承自 `BaseAgentWithParamsRecommendation`，包含以下子 Agent：

```
tool_call_info_agent (SchemaAgent)
  ↓
  调用 LLM，返回 ToolCallInfoSchema:
  {
    "tool_name": "工具名",
    "tool_args": {"参数名": "参数值"},
    "missing_tool_args": ["缺失的参数列表"]
  }
  ↓
update_tool_call_info_with_function_declarations
  ↓
  检查必需参数，补充到 missing_tool_args
  ↓
如果有 missing_tool_args:
  ├─ recommend_params_agent (LLM Agent)
  │   └─ 生成参数推荐的自然语言描述
  ├─ recommend_params_schema_agent (SchemaAgent)
  │   └─ 动态创建 Schema，LLM 填充缺失参数
  └─ update_tool_call_info_with_recommend_params
      └─ 合并补全的参数到 tool_args
```

**关键点**:
- `tool_call_info_agent` 使用 `ToolCallInfoSchema` 作为输出 Schema
- 如果 LLM 只返回 `missing_tool_args` 而没有 `tool_args`，Schema 会使用默认值 `{}`
- 参数补全后，完整的 `tool_args` 存储在 `state['tool_call_info']['tool_args']` 中

### 3.2 参数更新机制 (update_tool_args callback)

在工具调用前，通过 `update_tool_args` callback 确保使用补全后的参数：

```python
# 在 before_tool_callback 中
if tool_call_info['tool_args']:
    # 使用补全后的 tool_args 更新 function_call.args
    part.function_call.args = tool_call_info['tool_args']
```

## 四、异步任务执行流程

### 4.1 异步 Agent 架构 (BaseAsyncJobAgent)

异步 Agent（如 `apex_agent`, `abacus_agent`）继承自 `BaseAsyncJobAgent`：

```
BaseAsyncJobAgent
  ├─ submit_agent (SequentialAgent)
  │   ├─ submit_core_agent (SubmitCoreMCPAgent)
  │   ├─ submit_render_agent (SubmitRenderAgent)
  │   └─ submit_validator_agent (ValidatorAgent)
  ├─ result_agent (SequentialAgent)
  │   └─ result_core_agent (ResultMCPAgent)
  ├─ tool_call_info_agent
  ├─ recommend_params_agent
  └─ recommend_params_schema_agent
```

### 4.2 异步任务执行流程

```
BaseAsyncJobAgent._run_events():
  ├─ 1. 设置 state['dflow'] 和 state['sync_tools']
  ├─ 2. result_agent.run_async() (查询已有任务状态)
  └─ 3. 如果当前步骤状态不是 SUBMITTED/SUCCESS/FAILED:
      └─ super()._run_events() (执行参数获取和任务提交)
          ↓
          BaseAgentWithParamsRecommendation._run_events():
          ├─ tool_call_info_agent (获取参数)
          ├─ recommend_params_agent (如有缺失参数)
          ├─ recommend_params_schema_agent (补全参数)
          └─ submit_agent.run_async() (提交任务)
              ↓
              submit_core_agent:
              ├─ 调用 MCP Tool (async_mode=True, wait=False)
              ├─ 返回 job_id 和状态信息
              └─ 更新 step.status = SUBMITTED
              ↓
              submit_render_agent:
              └─ 渲染任务提交结果给前端
              ↓
              submit_validator_agent:
              └─ 验证任务是否成功提交
```

**关键点**:
- 异步任务使用 `async_mode=True, wait=False` 的 MCP Tool
- 任务提交后，`step.status` 更新为 `SUBMITTED`
- 后续轮询通过 `result_agent` 查询任务状态

### 4.3 异步任务状态管理

```
任务状态流转:
PLAN → PROCESS → SUBMITTED → SUCCESS/FAILED

每次 execution_agent 执行时:
1. 先调用 result_agent 查询所有已提交任务的状态
2. 如果任务已完成，更新 step.status = SUCCESS/FAILED
3. 如果任务未完成，跳过提交流程，只查询状态
```

## 五、同步任务执行流程

### 5.1 同步 Agent 架构 (BaseSyncAgentWithToolValidator)

同步 Agent（如 `structure_generate_agent`, `nmr_agent`）继承自 `BaseSyncAgentWithToolValidator`：

```
BaseSyncAgentWithToolValidator
  ├─ tool_call_info_agent
  ├─ recommend_params_agent
  ├─ recommend_params_schema_agent
  └─ submit_agent (SequentialAgent)
      ├─ sync_mcp_agent (SyncMCPAgent)
      └─ tool_validator_agent (ValidatorAgent)
```

### 5.2 同步任务执行流程

```
BaseSyncAgentWithToolValidator._run_events():
  ├─ tool_call_info_agent (获取参数)
  ├─ recommend_params_agent (如有缺失参数)
  ├─ recommend_params_schema_agent (补全参数)
  └─ submit_agent.run_async()
      ↓
      sync_mcp_agent:
      ├─ 调用 MCP Tool (async_mode=False, wait=True)
      ├─ 同步等待任务完成
      └─ 直接返回结果
      ↓
      tool_validator_agent:
      └─ 验证工具是否被调用
```

**关键点**:
- 同步任务使用 `async_mode=False, wait=True` 的 MCP Tool
- 任务执行完成后，`step.status` 直接更新为 `SUCCESS` 或 `FAILED`
- 不需要额外的状态查询流程

### 5.3 同步工具的特殊处理

在 `before_tool_callback` 中，如果工具在 `sync_tools` 列表中：

```python
if tool.name in sync_tools:
    tool.async_mode = False
    tool.wait = True
    tool.executor = LOCAL_EXECUTOR  # 使用本地执行器
```

**注意**: Storage 配置在 toolset 初始化时设置，不会被修改。

## 六、Parameters Agent 的作用

### 6.1 Parameters Agent 的触发时机

`ParametersAgent` **已集成到主流程中**，在计划确认后自动触发：

1. **在计划确认后收集所有异步任务的参数**
2. **等待用户确认参数**
3. **参数确认后生成包含 nodes 和 edges 的 JSON 文件**
4. **用于后续的批量任务提交或工作流编排**

### 6.2 Parameters Agent 的工作流程

```
ParametersAgent._run_async_impl():
  ├─ 阶段1: 参数收集（如果未收集过）
  │   ├─ 1. get_async_tool_steps() (获取所有异步工具步骤)
  │   ├─ 2. collect_tool_params_parallel() (并行收集所有工具参数)
  │   │   └─ 对每个工具:
  │   │       ├─ 调用对应 agent 的 tool_call_info_agent
  │   │       ├─ 如有缺失参数，调用 recommend_params_agent
  │   │       ├─ 调用 recommend_params_schema_agent 补全参数
  │   │       └─ 返回完整的 tool_args
  │   ├─ 3. 展示参数汇总信息（不生成 JSON，等待用户确认）
  │   └─ 4. 保存参数到 state['parameters_collection']
  │
  └─ 阶段2: JSON 生成（仅在参数确认后）
      ├─ 1. analyze_async_task_dependencies() (分析依赖关系)
      ├─ 2. save_parameters_to_json() (保存为 JSON 文件)
      └─ 3. 保存 JSON 路径到 state['parameters_json_path']
```

**关键点**:
- 参数收集和 JSON 生成是分离的两个阶段
- 只有在用户确认参数后才会生成 JSON 文件
- JSON 文件保存在 `parameters_output/` 目录下

### 6.3 生成的 JSON 格式

```json
{
  "session_id": "会话ID",
  "timestamp": "时间戳",
  "total_nodes": 节点数量,
  "nodes": [
    {
      "id": "node_0",
      "step_index": 0,
      "tool_name": "工具名",
      "description": "描述",
      "agent_name": "agent名",
      "tool_args": {"完整参数"},
      "missing_tool_args": []
    }
  ],
  "edges": [
    {"source": "node_0", "target": "node_1"}
  ]
}
```

## 七、关键状态管理

### 7.1 计划状态 (PlanStepStatusEnum)

- `PLAN`: 计划阶段，尚未执行
- `PROCESS`: 正在处理中
- `SUBMITTED`: 已提交（异步任务）
- `SUCCESS`: 执行成功
- `FAILED`: 执行失败

### 7.2 流程状态 (FlowStatusEnum)

- `NO_PLAN`: 无计划
- `NEW_PLAN`: 新计划
- `PROCESS`: 执行中
- `COMPLETE`: 完成

### 7.3 关键 State 字段

```python
state = {
    'plan': {...},                    # 计划信息
    'plan_index': 0,                  # 当前执行的步骤索引
    'plan_confirm': {'flag': False},  # 计划确认状态
    'parameters_collection': {...},   # 收集到的参数集合（DflowParamsCollectionSchema）
    'parameters_confirm': {           # 参数确认状态
        'flag': False,
        'reason': '...'
    },
    'parameters_json_path': '...',    # 生成的 JSON 文件路径
    'tool_call_info': {               # 工具调用信息
        'tool_name': '...',
        'tool_args': {...},
        'missing_tool_args': [...]
    },
    'recommend_params': {...},        # 推荐的参数
    'sync_tools': [...],              # 同步工具列表
    'dflow': False,                   # 是否使用 dflow
    'long_running_jobs': {...},       # 长运行任务
    'scenes': [...],                  # 场景列表
    'intent': {'type': 'research'},   # 用户意图
}
```

## 八、执行流程图

```
用户输入
  ↓
意图识别 (intent_agent)
  ↓
RESEARCH 模式?
  ├─ 是 → 扩写问题 (expand_agent)
  │      → 场景划分 (scene_agent)
  │      → 计划制定 (plan_make_agent)
  │      → 计划总结 (plan_info_agent)
  │      → 计划确认 (plan_confirm_agent)
  │         ↓
  │         如果计划已确认:
  │         ├─ 参数提取 (parameters_agent)
  │         │   ├─ 并行收集所有异步工具的参数
  │         │   ├─ 展示参数汇总
  │         │   └─ 等待用户确认
  │         │
  │         ├─ 参数确认 (parameters_confirm_agent)
  │         │   └─ 判断用户是否确认参数
  │         │
  │         └─ 生成 JSON (parameters_agent)
  │             ├─ 分析任务依赖关系
  │             ├─ 生成包含 nodes 和 edges 的 JSON
  │             └─ 流程结束
  │
  └─ 否 → 聊天模式 (chat_agent)
```

**注意**: `execution_agent` 的执行逻辑已被停用，不会执行计划中的任务。当前流程在生成 JSON 文件后结束。

## 九、关键设计点

### 9.1 参数补全机制
- **自动补全**: 当用户未提供完整参数时，系统自动调用 LLM 补全
- **参数验证**: 通过 Schema 验证确保参数格式正确
- **参数合并**: 使用 `deepmerge` 合并用户参数和补全参数

### 9.2 异步 vs 同步任务
- **异步任务**: 提交到 Bohrium 云端执行，需要轮询状态
- **同步任务**: 在服务器上同步执行，立即返回结果
- **混合模式**: 同一 Agent 可以同时支持异步和同步工具（通过 `sync_tools` 配置）

### 9.3 错误处理
- **参数错误**: 通过 Schema 验证捕获
- **执行错误**: 通过 `error_agent` 处理
- **任务失败**: 更新 `step.status = FAILED`，停止后续步骤执行

### 9.4 状态持久化
- 所有状态存储在 `ctx.session.state` 中
- 通过 `update_state_event` 更新状态
- 状态会持久化到数据库（通过 DatabaseSessionService）

## 十、总结

MatMaster 的整体运行逻辑是一个**分层、模块化、状态驱动**的架构：

1. **计划制定阶段**: 通过多个 Agent 协作，理解用户意图，制定可执行计划
2. **计划确认阶段**: 用户确认计划后，进入参数收集流程
3. **参数提取阶段**: 并行收集所有异步工具的参数，智能补全缺失参数
4. **参数确认阶段**: 用户确认参数后，生成包含任务依赖关系的 JSON 文件
5. **流程结束**: 生成 JSON 文件后流程结束（当前版本不执行任务）

**当前版本特点**:
- `execution_agent` 的执行逻辑已被停用
- 流程专注于参数收集和 JSON 生成
- 生成的 JSON 文件可用于后续的批量任务提交或工作流编排

整个流程通过状态管理实现协调，每个 Agent 专注于自己的职责，通过事件机制进行通信。
