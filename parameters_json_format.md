# 参数 JSON 文件格式说明

## 一、文件保存位置

JSON 文件保存在项目根目录下的 `parameters_output/` 目录中：

```
MatMaster/
  └── parameters_output/
      └── parameters_{session_id}_{timestamp}.json
```

## 二、文件命名规则

文件名格式：`parameters_{session_id}_{timestamp}.json`

- `session_id`: 会话 ID 的前 8 位字符
- `timestamp`: 时间戳，格式为 `YYYYMMDD_HHMMSS`

**示例**：
- `parameters_a1b2c3d4_20241215_143022.json`
- `parameters_unknown_20241215_143022.json` (如果 session_id 不存在)

## 三、JSON 文件结构

### 3.1 完整结构

```json
{
  "nodes": [
    {
      "id": "node-$id1",
      "node_uuid": "7fc4da3d-1a34-504c-98cd-40e33bff838d",
      "node_version": "1.2",
      "label": "apex_calculation",
      "position_x": 0.0,
      "position_y": 0.0,
      "system_values": {
        "machine_type": "c2_m8_cpu",
        "image": "registry.dp.tech/dptech/dp/native/prod-16664/apex-agent-all:0.2.1",
        "docker_image": ""
      },
      "input_parameters": [
        {
          "name": "structure_file",
          "type": "str",
          "value": "https://example.com/structure.xyz"
        },
        {
          "name": "calculation_type",
          "type": "str",
          "value": "scf"
        }
      ],
      "output_parameters": []
    },
    {
      "id": "node-$id2",
      "node_uuid": "32452345-1a34-504c-98cd-40e33bff838d",
      "node_version": "1.2",
      "label": "abacus_calculation",
      "position_x": 0.0,
      "position_y": 0.0,
      "system_values": {
        "machine_type": "c2_m4_cpu",
        "image": "registry.dp.tech/dptech/dp/native/prod-22618/abacusagenttools-matmaster-new-tool:v0.2.3",
        "docker_image": ""
      },
      "input_parameters": [
        {
          "name": "input_file",
          "type": "str",
          "value": "https://example.com/input.in"
        }
      ],
      "output_parameters": []
    }
  ],
  "edges": [
    {
      "id": "edge-$id1",
      "source_node_id": "node-$id1",
      "source_parameter_name": "out_apex_calculation",
      "target_node_id": "node-$id2",
      "target_parameter_name": "input_file"
    }
  ],
  "meta": {
    "template_uuid": "68a4ed99-9fff-4b1a-9b47-98a8624b5143"
  }
}
```

### 3.2 字段说明

#### 顶层字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `nodes` | array | 节点列表，每个节点代表一个异步任务 |
| `edges` | array | 边列表，表示任务之间的依赖关系 |
| `meta` | object | 元数据信息 |

#### Node 字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | string | 节点唯一标识符，格式为 `node-$id1`, `node-$id2` 等 |
| `node_uuid` | string | 节点 UUID |
| `node_version` | string | 节点版本号（当前为 "1.2"） |
| `label` | string | 工具名称（MCP Tool 的名称） |
| `position_x` | float | 节点 X 坐标（当前为空置 0.0） |
| `position_y` | float | 节点 Y 坐标（当前为空置 0.0） |
| `system_values` | object | 系统配置值 |
| `system_values.machine_type` | string | 机器类型（从 agent executor 获取，默认 "c2_m4_cpu"） |
| `system_values.image` | string | Docker 镜像地址（从 mapping.py 的 AGENT_IMAGE_ADDRESS 获取） |
| `system_values.docker_image` | string | Docker 镜像（当前为空） |
| `input_parameters` | array | 输入参数列表，每个参数包含 name, type, value |
| `output_parameters` | array | 输出参数列表（当前为空） |

#### Edge 字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | string | 边的唯一标识符，格式为 `edge-$id1`, `edge-$id2` 等 |
| `source_node_id` | string | 源节点的 id |
| `source_parameter_name` | string | 源节点的输出参数名 |
| `target_node_id` | string | 目标节点的 id |
| `target_parameter_name` | string | 目标节点的输入参数名 |

**依赖关系说明**：
- `source_node_id` → `target_node_id` 表示源任务必须在目标任务之前执行
- `source_parameter_name` 指定源节点的输出参数
- `target_parameter_name` 指定目标节点中 MCP tool 对应的某个参数
- 本质上是通过判断两个节点的输出输入文件对接来建立连接

## 四、实际示例

### 示例 1: 单个任务

```json
{
  "nodes": [
    {
      "id": "node-$id1",
      "node_uuid": "7fc4da3d-1a34-504c-98cd-40e33bff838d",
      "node_version": "1.2",
      "label": "apex_calculation",
      "position_x": 0.0,
      "position_y": 0.0,
      "system_values": {
        "machine_type": "c2_m8_cpu",
        "image": "registry.dp.tech/dptech/dp/native/prod-16664/apex-agent-all:0.2.1",
        "docker_image": ""
      },
      "input_parameters": [
        {
          "name": "structure_file",
          "type": "str",
          "value": "https://oss.example.com/water.xyz"
        },
        {
          "name": "calculation_type",
          "type": "str",
          "value": "scf"
        },
        {
          "name": "basis_set",
          "type": "str",
          "value": "6-31G(d)"
        },
        {
          "name": "functional",
          "type": "str",
          "value": "B3LYP"
        }
      ],
      "output_parameters": []
    }
  ],
  "edges": [],
  "meta": {
    "template_uuid": "68a4ed99-9fff-4b1a-9b47-98a8624b5143"
  }
}
```

### 示例 2: 多个任务（有依赖关系）

```json
{
  "nodes": [
    {
      "id": "node-$id1",
      "node_uuid": "7fc4da3d-1a34-504c-98cd-40e33bff838d",
      "node_version": "1.2",
      "label": "structure_generate",
      "position_x": 0.0,
      "position_y": 0.0,
      "system_values": {
        "machine_type": "c2_m4_cpu",
        "image": "registry.dp.tech/dptech/dpa-calculator:46bc2c88",
        "docker_image": ""
      },
      "input_parameters": [
        {
          "name": "formula",
          "type": "str",
          "value": "H2O"
        },
        {
          "name": "method",
          "type": "str",
          "value": "random"
        }
      ],
      "output_parameters": []
    },
    {
      "id": "node-$id2",
      "node_uuid": "32452345-1a34-504c-98cd-40e33bff838d",
      "node_version": "1.2",
      "label": "apex_optimization",
      "position_x": 0.0,
      "position_y": 0.0,
      "system_values": {
        "machine_type": "c2_m8_cpu",
        "image": "registry.dp.tech/dptech/dp/native/prod-16664/apex-agent-all:0.2.1",
        "docker_image": ""
      },
      "input_parameters": [
        {
          "name": "structure_file",
          "type": "str",
          "value": "https://oss.example.com/initial.xyz"
        },
        {
          "name": "optimization_type",
          "type": "str",
          "value": "geometry"
        }
      ],
      "output_parameters": []
    },
    {
      "id": "node-$id3",
      "node_uuid": "45678901-1a34-504c-98cd-40e33bff838d",
      "node_version": "1.2",
      "label": "apex_calculation",
      "position_x": 0.0,
      "position_y": 0.0,
      "system_values": {
        "machine_type": "c2_m8_cpu",
        "image": "registry.dp.tech/dptech/dp/native/prod-16664/apex-agent-all:0.2.1",
        "docker_image": ""
      },
      "input_parameters": [
        {
          "name": "structure_file",
          "type": "str",
          "value": "https://oss.example.com/optimized.xyz"
        },
        {
          "name": "calculation_type",
          "type": "str",
          "value": "scf"
        }
      ],
      "output_parameters": []
    }
  ],
  "edges": [
    {
      "id": "edge-$id1",
      "source_node_id": "node-$id1",
      "source_parameter_name": "out_structure_generate",
      "target_node_id": "node-$id2",
      "target_parameter_name": "structure_file"
    },
    {
      "id": "edge-$id2",
      "source_node_id": "node-$id2",
      "source_parameter_name": "out_apex_optimization",
      "target_node_id": "node-$id3",
      "target_parameter_name": "structure_file"
    }
  ],
  "meta": {
    "template_uuid": "68a4ed99-9fff-4b1a-9b47-98a8624b5143"
  }
}
```

## 五、使用场景

生成的 JSON 文件可用于：

1. **工作流编排**: 根据 `nodes` 和 `edges` 构建 DAG（有向无环图）工作流
2. **批量任务提交**: 读取 `tool_args` 批量提交计算任务
3. **参数审计**: 记录和追踪所有任务的参数配置
4. **任务依赖分析**: 根据 `edges` 分析任务执行顺序
5. **结果关联**: 通过 `session_id` 关联同一会话的所有任务

## 六、注意事项

1. **只包含异步任务**: JSON 文件只包含继承自 `BaseAsyncJobAgent` 的 Agent 的任务
2. **参数已补全**: `input_parameters` 中的 `value` 包含完整的参数值（用户提供 + 自动补全）
3. **依赖关系**: 通过判断两个节点的输出输入文件对接来建立 edges 连接
4. **machine_type**: 从 agent 的 executor 配置中获取，如果未设置则默认使用 `c2_m4_cpu`
5. **image**: 从 `mapping.py` 的 `AGENT_IMAGE_ADDRESS` 字典中获取，如果未配置则为空字符串
6. **output_parameters**: 当前为空数组，后续可由其他工具获取
7. **文件编码**: JSON 文件使用 UTF-8 编码，支持中文字符
8. **文件格式**: 使用 2 空格缩进，便于阅读

## 七、文件路径获取

JSON 文件路径保存在 `ctx.session.state['parameters_json_path']` 中，可以通过以下方式获取：

```python
json_path = ctx.session.state.get('parameters_json_path')
if json_path:
    # 读取 JSON 文件
    import json
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
```
