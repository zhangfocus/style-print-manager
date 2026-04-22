# PRD: 限定规则查询API实现

## Problem Statement

当前系统已经实现了限定规则的管理功能（款式全禁、位置限定、款式位置限定），但缺少完整的查询接口来验证和测试这些规则。开发者和测试人员需要能够：

1. 验证某个具体的款式+位置+印花组合是否被允许
2. 查询某个款式在所有位置上可用的印花列表（带位置对应关系）
3. 在其他程序中复用这些限定检查逻辑

目前只有两个查询接口（款式+位置→印花、款式+印花→位置），无法满足完整的测试和集成需求。

## Solution

实现两个新的后端查询接口，补全限定规则查询能力：

1. **校验接口** (`POST /api/restrictions/check`)：输入款式+位置+印花，返回是否允许及详细原因
2. **款式查询接口** (`GET /api/restrictions/available-by-style`)：输入款式，返回所有可用位置及每个位置对应的可用印花列表

这两个接口与现有的两个接口（`available-prints`、`available-positions`）共同构成完整的限定规则查询体系，支持所有可能的查询场景。

## User Stories

1. 作为测试人员，我想输入款式+位置+印花组合，查看是否被允许，以便验证限定规则配置是否正确
2. 作为测试人员，我想看到拒绝的具体原因和触发的规则ID，以便快速定位问题规则
3. 作为测试人员，我想输入一个款式，查看该款式在所有位置上可用的印花，以便全面了解该款式的限定情况
4. 作为测试人员，我想看到每个位置是否受限定规则约束，以便区分"默认允许"和"规则允许"
5. 作为开发者，我想在下单系统中调用校验接口，以便在用户提交订单前验证组合是否合法
6. 作为开发者，我想在选品界面调用款式查询接口，以便动态展示可选的位置和印花
7. 作为系统管理员，我想查询结果只包含启用的位置和印花，以便避免用户选择已禁用的数据
8. 作为测试人员，我想看到款式全禁的情况，以便确认该款式完全不可用
9. 作为开发者，我想接口返回结构化的JSON数据，以便在不同系统中复用
10. 作为测试人员，我想看到位置限定规则的优先级高于款式位置限定，以便验证黑名单策略的正确性
11. 作为开发者，我想接口性能足够好，以便支持实时查询场景
12. 作为测试人员，我想看到每个位置的完整信息（ID、名称、编码），以便清晰识别位置
13. 作为测试人员，我想看到每个印花的完整信息（ID、编码），以便清晰识别印花
14. 作为开发者，我想接口遵循RESTful规范，以便与现有API风格保持一致
15. 作为测试人员，我想在款式查询接口中看到位置按ID排序，以便结果稳定可预测

## Implementation Decisions

### 模块设计

1. **限定规则查询服务模块**（新增）
   - 实现 `check_restriction()` 函数：校验款式+位置+印花组合
   - 实现 `get_available_by_style()` 函数：查询款式的所有可用位置和印花
   - 复用现有的 `get_available_prints()` 逻辑
   - 位置：`backend/app/routers/restrictions.py`（直接在路由文件中实现，与现有接口保持一致）

2. **API路由层**（修改 `backend/app/routers/restrictions.py`）
   - 新增 `POST /api/restrictions/check` 端点
   - 新增 `GET /api/restrictions/available-by-style?style_id=X` 端点

3. **Schema定义**（修改 `backend/app/schemas.py`）
   - 新增 `RestrictionCheckRequest`：包含 style_id, position_id, print_id
   - 新增 `RestrictionCheckResponse`：包含 allowed, reason, rule_type, rule_id
   - 新增 `AvailablePositionWithPrints`：包含位置信息和可用印花列表
   - 新增 `AvailableByStyleResponse`：包含 style_id, is_banned, available_positions

### 技术决策

1. **校验接口使用POST方法**
   - 虽然是查询操作，但参数较多且语义上是"检查"操作
   - 请求体使用JSON格式，便于扩展

2. **款式查询接口使用GET方法**
   - 符合RESTful规范（查询操作）
   - 参数简单（只有style_id），使用query参数

3. **黑名单策略实现**
   - 类型1（款式全禁）优先级最高
   - 类型2（位置限定）优先级高于类型3
   - 款式有类型3规则时，只能在规则指定的位置使用（黑名单）
   - 类型2可以扩展类型3的白名单

4. **数据过滤**
   - 只返回 `is_active=True` 的位置和印花
   - 只检查 `is_active=True` 的限定规则

5. **性能优化**
   - 款式查询接口：批量查询所有位置，然后对每个位置调用现有的 `available-prints` 逻辑
   - 使用数据库索引：`idx_rule_type_position`（已存在）
   - 避免N+1查询：批量加载位置和印花信息

### API契约

#### 1. POST /api/restrictions/check

**请求体**：
```json
{
  "style_id": 1,
  "position_id": 2,
  "print_id": 3
}
```

**响应**：
```json
{
  "allowed": false,
  "reason": "印花 3 不在位置 2 的允许印花列表中",
  "rule_type": "position_restriction",
  "rule_id": 123
}
```

**字段说明**：
- `allowed`: 是否允许（boolean）
- `reason`: 拒绝原因或允许原因（string）
- `rule_type`: 触发的规则类型（"style_ban" | "position_restriction" | "style_position" | null）
- `rule_id`: 触发的规则ID（number | null）

#### 2. GET /api/restrictions/available-by-style?style_id=X

**查询参数**：
- `style_id`: 款式ID（必填）

**响应**：
```json
{
  "style_id": 1,
  "is_banned": false,
  "available_positions": [
    {
      "position_id": 2,
      "position_name": "前胸",
      "position_code": "FRONT",
      "print_ids": [1, 2, 3],
      "print_codes": ["P001", "P002", "P003"],
      "is_restricted": true,
      "reason": "款式位置限定了允许的印花列表"
    },
    {
      "position_id": 5,
      "position_name": "袖口",
      "position_code": "SLEEVE",
      "print_ids": [7, 8, 9],
      "print_codes": ["P007", "P008", "P009"],
      "is_restricted": true,
      "reason": "位置限定了允许的印花列表"
    }
  ]
}
```

**字段说明**：
- `style_id`: 款式ID
- `is_banned`: 款式是否被全禁（boolean）
- `available_positions`: 可用位置列表（如果款式被全禁则为空数组）
  - `position_id`: 位置ID
  - `position_name`: 位置名称
  - `position_code`: 位置编码
  - `print_ids`: 该位置可用的印花ID列表（已排序）
  - `print_codes`: 该位置可用的印花编码列表（与print_ids对应）
  - `is_restricted`: 该位置是否受限定规则约束（boolean）
  - `reason`: 限定原因说明

### 校验逻辑实现

**check_restriction() 逻辑**：
1. 检查款式全禁（类型1）→ 如果全禁则拒绝
2. 检查位置限定（类型2）→ 如果有规则则按规则判断，通过则允许（不再检查类型3）
3. 检查款式位置限定（类型3）→ 如果款式有类型3规则，检查位置是否在白名单及印花是否允许
4. 默认允许

**get_available_by_style() 逻辑**：
1. 检查款式全禁（类型1）→ 如果全禁则返回 `is_banned=true, available_positions=[]`
2. 查询所有启用的位置
3. 对每个位置调用现有的 `get_available_prints(style_id, position_id)` 逻辑
4. 过滤掉返回空印花列表的位置（不可用）
5. 批量查询印花编码，构造完整响应

## Testing Decisions

### 测试原则

- 只测试外部行为（API响应），不测试内部实现细节
- 测试应覆盖三种规则类型的优先级和交互
- 测试应覆盖边界情况（NULL值、空列表、款式全禁）

### 测试模块

1. **校验接口测试** (`test_check_restriction`)
   - 测试款式全禁场景
   - 测试位置限定优先级（类型2优先于类型3）
   - 测试款式位置限定的黑名单策略
   - 测试默认允许场景
   - 测试NULL值处理（不限款式、不限印花）

2. **款式查询接口测试** (`test_available_by_style`)
   - 测试款式全禁返回空列表
   - 测试款式有类型3规则的黑名单策略
   - 测试类型2扩展白名单
   - 测试款式无规则返回所有位置
   - 测试只返回启用的位置和印花

### 测试先例

参考现有的 `test_restrictions.py`（如果存在）或 `test_routers.py` 中的测试风格：
- 使用 FastAPI TestClient
- 使用测试数据库fixture
- 每个测试独立准备数据和清理

## Out of Scope

以下内容不在本PRD范围内：

1. **前端查询页面**：只实现后端API，前端页面后续单独实现
2. **批量查询接口**：不支持一次查询多个款式或组合
3. **缓存优化**：不实现Redis缓存，后续根据性能需求添加
4. **权限控制**：查询接口不需要权限验证（与现有接口保持一致）
5. **日志记录**：不添加特殊的查询日志，使用框架默认日志
6. **性能监控**：不添加性能指标收集
7. **API版本控制**：使用当前的API路径，不引入版本号
8. **国际化**：错误消息和原因说明使用中文（与现有接口保持一致）

## Further Notes

### 与现有接口的关系

四个查询接口形成完整的查询矩阵：

| 输入 | 输出 | 接口 | 状态 |
|------|------|------|------|
| 款式 + 位置 | 可用印花 | `/available-prints` | ✅ 已实现 |
| 款式 + 印花 | 可用位置 | `/available-positions` | ✅ 已实现 |
| 款式 + 位置 + 印花 | 是否允许 | `/check` | ❌ 本PRD实现 |
| 款式 | 位置→印花映射 | `/available-by-style` | ❌ 本PRD实现 |

### 复用性考虑

- `check` 接口可以被下单系统、订单校验等场景复用
- `available-by-style` 接口可以被选品界面、产品配置等场景复用
- 所有接口遵循相同的黑名单策略和优先级规则，保证一致性

### 后续扩展

如果需要前端测试页面，可以实现：
- Tab切换四种查询场景
- 搜索式下拉选择款式/位置/印花
- 结果展示区域（表格或卡片）
- 错误提示和原因说明
