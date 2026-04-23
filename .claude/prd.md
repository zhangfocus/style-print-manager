# PRD: 限定规则查询接口改造 - 从ID到名称

## Problem Statement

当前四个限定规则查询接口（check、available-by-style、available-prints、available-positions）使用ID作为入参和返回值，这导致：

1. **手动测试困难**：测试时需要先查询name→id，然后才能调用接口，流程繁琐
2. **外部脚本集成不便**：其他脚本调用这些接口时，通常只有名称（款式编码、位置名称、印花编码），需要额外的转换步骤
3. **可读性差**：接口返回的reason字段包含ID（如"款式 123 被全禁"），不直观

用户需要这些接口直接支持名称输入和输出，简化测试和集成流程。

## Solution

将四个限定规则查询接口的入参和返回值从ID改为名称：

1. **入参改造**：
   - 款式：使用 `style_code`（款式编码）
   - 位置：使用 `position_name`（位置名称）
   - 印花：使用 `print_code`（印花编码）

2. **返回值改造**：
   - 所有返回的ID字段改为对应的名称字段
   - reason字段中的ID替换为名称（如"款式 ABC001 被全禁"）

3. **性能优化**：
   - 实现内存缓存机制，缓存name↔id映射关系
   - 应用启动时加载缓存，每小时自动刷新

4. **错误处理**：
   - 任何一个名称找不到，返回404并明确指出哪个字段不存在

## User Stories

1. 作为测试人员，我想直接用款式编码、位置名称、印花编码调用查询接口，这样我不需要先查询ID就能测试
2. 作为外部脚本开发者，我想用名称调用限定规则查询接口，这样我的脚本不需要维护name→id的转换逻辑
3. 作为系统用户，我想看到可读的错误信息（如"款式 ABC001 被全禁"），而不是"款式 123 被全禁"，这样我能快速理解限定原因
4. 作为API调用者，我想在传入不存在的款式编码时得到明确的404错误（如"款式编码 'XYZ999' 不存在"），这样我能快速定位问题
5. 作为API调用者，我想在传入不存在的位置名称时得到明确的404错误（如"位置名称 '不存在的位置' 不存在"），这样我能快速定位问题
6. 作为API调用者，我想在传入不存在的印花编码时得到明确的404错误（如"印花编码 'P999' 不存在"），这样我能快速定位问题
7. 作为系统管理员，我想系统自动缓存name↔id映射，这样查询接口的性能不会因为名称转换而显著下降
8. 作为系统管理员，我想缓存每小时自动刷新，这样新增的款式/位置/印花能在合理时间内被查询接口识别
9. 作为前端开发者，我想available-by-style接口返回位置名称和印花编码，而不是ID，这样我能直接展示给用户
10. 作为前端开发者，我想available-prints接口返回印花编码列表，而不是ID列表，这样我能直接展示给用户
11. 作为前端开发者，我想available-positions接口返回位置名称列表，而不是ID列表，这样我能直接展示给用户
12. 作为测试脚本维护者，我想test_restriction_api.py不再需要name→id转换逻辑，这样测试代码更简洁
13. 作为API调用者，我想check接口的reason字段使用名称而不是ID，这样日志和错误信息更易读
14. 作为API调用者，我想available-prints接口的reason字段使用名称而不是ID，这样我能理解为什么某些印花不可用
15. 作为API调用者，我想available-positions接口的reason字段使用名称而不是ID，这样我能理解为什么某些位置不可用
16. 作为系统开发者，我想名称解析逻辑集中在一个模块中，这样未来维护和扩展更容易
17. 作为系统开发者，我想缓存机制是可测试的，这样我能验证缓存的正确性和刷新逻辑
18. 作为API调用者，我想接口在找不到名称时立即返回404，而不是继续执行并返回错误的结果
19. 作为系统用户，我想reason字段中的多个ID都被替换为名称（如"款式 ABC001 在位置 左胸 不可用"），这样信息完整且可读
20. 作为性能监控人员，我想缓存命中率高，这样name→id转换不会成为性能瓶颈

## Implementation Decisions

### 模块设计

#### 1. 名称解析缓存模块（新增）
- **职责**：维护name↔id的双向映射缓存，提供快速查询
- **接口**：
  - `init_cache(db)`: 应用启动时初始化缓存
  - `refresh_cache(db)`: 刷新缓存（每小时调用）
  - `get_style_id_by_code(code) -> int | None`: 根据款式编码获取ID
  - `get_position_id_by_name(name) -> int | None`: 根据位置名称获取ID
  - `get_print_id_by_code(code) -> int | None`: 根据印花编码获取ID
  - `get_style_code_by_id(id) -> str | None`: 根据款式ID获取编码
  - `get_position_name_by_id(id) -> str | None`: 根据位置ID获取名称
  - `get_print_code_by_id(id) -> str | None`: 根据印花ID获取编码
- **实现细节**：
  - 使用Python字典存储映射关系
  - 线程安全（使用锁保护缓存更新）
  - 缓存结构：`{style_code_to_id: dict, style_id_to_code: dict, position_name_to_id: dict, ...}`

#### 2. 名称解析辅助函数（新增）
- **职责**：提供统一的名称→ID转换和404错误处理
- **接口**：
  - `resolve_style_code(code: str) -> int`: 转换款式编码，找不到抛出HTTPException(404)
  - `resolve_position_name(name: str) -> int`: 转换位置名称，找不到抛出HTTPException(404)
  - `resolve_print_code(code: str) -> int`: 转换印花编码，找不到抛出HTTPException(404)
  - `resolve_names_to_ids(style_code: str, position_name: str, print_code: str) -> tuple[int, int, int]`: 批量转换，任何一个找不到都抛出404
- **错误信息格式**：`{"detail": "款式编码 'ABC999' 不存在"}`

#### 3. Reason字段生成器（新增）
- **职责**：生成包含名称而非ID的reason字符串
- **接口**：
  - `format_reason_with_names(reason_template: str, style_id: int | None, position_id: int | None, print_id: int | None) -> str`
- **实现细节**：
  - 接收原始reason模板（如"款式 {style_id} 被全禁"）
  - 使用缓存查询ID对应的名称
  - 替换模板中的占位符为实际名称

#### 4. 查询接口改造（修改）

**POST /api/restrictions/check**
- 入参：`RestrictionCheckRequest(style_code: str, position_name: str, print_code: str)`
- 返回：`RestrictionCheckResponse(allowed: bool, reason: str, rule_type: str | None, rule_id: int | None)`
- 逻辑变化：
  1. 调用 `resolve_names_to_ids()` 转换入参
  2. 执行原有的限定规则检查逻辑（使用ID）
  3. 生成reason时使用名称而非ID

**GET /api/restrictions/available-by-style**
- 入参：`style_code: str`
- 返回：`AvailableByStyleResponse(style_code: str, is_banned: bool, available_positions: list[AvailablePositionWithPrints])`
- `AvailablePositionWithPrints` 结构：
  - `position_name: str`
  - `position_code: str`
  - `print_codes: list[str]`（移除 `print_ids`）
  - `is_restricted: bool`
  - `reason: str`（使用名称）
- 逻辑变化：
  1. 调用 `resolve_style_code()` 转换入参
  2. 执行原有查询逻辑（使用ID）
  3. 将返回结果中的ID转换为名称

**GET /api/restrictions/available-prints**
- 入参：`style_code: str, position_name: str`
- 返回：`AvailablePrintsResponse(available: bool, print_codes: list[str], is_restricted: bool, reason: str)`
- 逻辑变化：
  1. 调用 `resolve_names_to_ids()` 转换入参
  2. 执行原有查询逻辑（使用ID）
  3. 将 `print_ids` 转换为 `print_codes`
  4. reason使用名称

**GET /api/restrictions/available-positions**
- 入参：`style_code: str, print_code: str`
- 返回：`AvailablePositionsResponse(available: bool, position_names: list[str], is_restricted: bool, reason: str)`
- 逻辑变化：
  1. 调用 `resolve_names_to_ids()` 转换入参
  2. 执行原有查询逻辑（使用ID）
  3. 将 `position_ids` 转换为 `position_names`
  4. reason使用名称

#### 5. Schemas改造（修改）

**新增/修改的Schema**：
- `RestrictionCheckRequest`: 字段改为 `style_code, position_name, print_code`
- `AvailableByStyleResponse`: 移除 `style_id`，添加 `style_code`
- `AvailablePositionWithPrints`: 移除 `position_id, print_ids`，保留 `position_name, position_code, print_codes`
- `AvailablePrintsResponse`（新增）: `available, print_codes, is_restricted, reason`
- `AvailablePositionsResponse`（新增）: `available, position_names, is_restricted, reason`

#### 6. 应用启动和定时任务（修改）
- 在FastAPI应用启动事件中调用 `init_cache()`
- 使用APScheduler或类似库实现每小时调用 `refresh_cache()`
- 确保缓存刷新失败不会导致应用崩溃（记录错误日志但继续使用旧缓存）

#### 7. 测试脚本改造（修改）
- `test_restriction_api.py`: 移除所有 `get_*_id_by_*` 函数
- 直接使用名称调用接口
- 简化测试流程

### 技术决策

1. **缓存实现**：使用内存字典而非Redis，因为数据量小（款式/位置/印花总数通常<10000），且不需要跨进程共享
2. **缓存刷新**：使用后台定时任务而非TTL，确保所有缓存同步刷新，避免部分数据过期
3. **线程安全**：使用 `threading.Lock` 保护缓存更新操作
4. **错误处理**：name找不到时立即返回404，不继续执行业务逻辑
5. **向后兼容**：不保留ID字段，完全移除，因为前端尚未实现这四个接口
6. **reason生成**：在业务逻辑层直接使用名称生成reason，而不是先生成ID版本再替换

### 数据库查询优化

- 缓存初始化时一次性查询所有启用的款式/位置/印花（`is_active=True`）
- 避免在请求处理中执行name→id的数据库查询
- 缓存刷新时使用批量查询而非逐条查询

## Testing Decisions

### 测试原则
- **测试外部行为，不测试实现细节**：测试接口的输入输出，不测试内部的缓存数据结构
- **隔离测试**：每个模块独立测试，使用mock隔离依赖
- **集成测试**：端到端测试完整的请求流程

### 测试模块

#### 1. 名称解析缓存模块测试（单元测试）
- **测试文件**：`backend/tests/test_name_cache.py`
- **测试用例**：
  - 测试缓存初始化：验证启动时正确加载所有映射
  - 测试正向查询：`get_style_id_by_code()` 返回正确ID
  - 测试反向查询：`get_style_code_by_id()` 返回正确编码
  - 测试不存在的名称：返回None
  - 测试缓存刷新：新增数据后刷新缓存能查到
  - 测试线程安全：并发读写缓存不会出错
- **Prior Art**：参考现有的 `backend/tests/` 中的单元测试结构

#### 2. 名称解析辅助函数测试（单元测试）
- **测试文件**：`backend/tests/test_name_resolver.py`
- **测试用例**：
  - 测试成功解析：传入存在的名称返回ID
  - 测试404错误：传入不存在的名称抛出HTTPException(404)
  - 测试错误信息格式：验证404错误信息包含具体的字段和值
  - 测试批量解析：`resolve_names_to_ids()` 正确转换三个参数
  - 测试批量解析失败：任何一个名称不存在都抛出404
- **Mock策略**：Mock缓存模块的查询函数

#### 3. 查询接口测试（集成测试）
- **测试文件**：`backend/tests/test_restrictions_api.py`
- **测试用例**：

**POST /api/restrictions/check**
- 测试成功场景：传入有效的名称，返回正确的allowed和reason
- 测试款式全禁：reason包含款式编码而非ID
- 测试位置限定：reason包含位置名称和印花编码
- 测试款式位置限定：reason包含款式编码、位置名称、印花编码
- 测试404错误：传入不存在的款式编码/位置名称/印花编码

**GET /api/restrictions/available-by-style**
- 测试成功场景：返回的位置和印花都是名称而非ID
- 测试款式全禁：返回 `is_banned=True`
- 测试位置限定：返回正确的可用印花编码列表
- 测试款式位置限定：返回正确的位置和印花组合
- 测试404错误：传入不存在的款式编码

**GET /api/restrictions/available-prints**
- 测试成功场景：返回印花编码列表而非ID列表
- 测试款式全禁：返回空列表
- 测试位置限定：返回正确的印花编码列表
- 测试款式位置限定：返回正确的印花编码列表
- 测试404错误：传入不存在的款式编码或位置名称

**GET /api/restrictions/available-positions**
- 测试成功场景：返回位置名称列表而非ID列表
- 测试款式全禁：返回空列表
- 测试位置限定：返回正确的位置名称列表
- 测试款式位置限定：返回正确的位置名称列表
- 测试404错误：传入不存在的款式编码或印花编码

- **Prior Art**：参考 `test_restriction_api.py` 的测试结构，但改为使用pytest框架和FastAPI TestClient

#### 4. 缓存刷新测试（集成测试）
- **测试文件**：`backend/tests/test_cache_refresh.py`
- **测试用例**：
  - 测试定时刷新：模拟时间流逝，验证缓存每小时刷新
  - 测试刷新后查询：新增数据后刷新缓存，验证能查到新数据
  - 测试刷新失败处理：数据库连接失败时，缓存保持旧数据不崩溃

#### 5. 测试脚本测试（手动测试）
- **测试文件**：`backend/test_restriction_api.py`（改造后）
- **测试方法**：运行 `python test_restriction_api.py --auto`，验证所有接口正常工作
- **验证点**：
  - 不再需要name→id转换
  - 返回结果包含名称而非ID
  - 错误信息清晰可读

### 测试数据准备
- 使用pytest fixtures创建测试数据库和测试数据
- 测试数据包括：
  - 至少3个款式（有编码）
  - 至少5个位置（有名称和编号）
  - 至少5个印花（有编码）
  - 至少3条限定规则（覆盖三种类型）

## Out of Scope

以下内容不在本次改造范围内：

1. **其他接口的改造**：只改造这四个查询接口，CRUD接口（list/create/update/delete）保持使用ID
2. **前端改造**：前端尚未实现这四个接口，本次不涉及前端代码修改
3. **数据库schema变更**：不修改数据库表结构，内部仍使用ID存储
4. **Redis缓存**：不引入Redis，使用内存缓存即可
5. **缓存预热**：不实现缓存预热机制，应用启动时加载即可
6. **缓存失效策略**：不实现复杂的缓存失效策略（如监听数据库变更），使用定时刷新
7. **API版本控制**：不引入v1/v2版本，直接修改现有接口
8. **性能监控**：不添加缓存命中率监控，后续可根据需要添加
9. **国际化**：错误信息保持中文，不支持多语言
10. **GraphQL支持**：保持RESTful API，不引入GraphQL

## Further Notes

### 实施顺序建议

1. **第一阶段**：实现名称解析缓存模块和辅助函数，编写单元测试
2. **第二阶段**：改造四个查询接口，修改schemas
3. **第三阶段**：实现缓存刷新定时任务
4. **第四阶段**：编写集成测试
5. **第五阶段**：改造测试脚本，进行端到端测试

### 风险和缓解措施

**风险1：缓存与数据库不一致**
- 缓解：每小时刷新缓存，最多1小时延迟
- 缓解：提供手动刷新缓存的管理接口（可选）

**风险2：缓存占用内存过大**
- 缓解：只缓存启用的数据（`is_active=True`）
- 缓解：估算内存占用（假设10000条数据，每条100字节，总计约1MB，可接受）

**风险3：并发请求时缓存刷新导致性能抖动**
- 缓解：使用读写锁，读操作不阻塞
- 缓解：缓存刷新在后台线程执行，不阻塞请求处理

**风险4：名称不唯一导致查询错误**
- 缓解：数据库已有唯一约束（`style.code`, `position.name`, `print.code`）
- 缓解：缓存初始化时验证唯一性，发现重复记录日志告警

### 性能影响评估

**改造前**：
- 每个请求：1次数据库查询（查限定规则）
- 响应时间：~10ms

**改造后**：
- 每个请求：1次缓存查询（name→id，内存操作）+ 1次数据库查询（查限定规则）
- 响应时间：~10ms（缓存查询<1ms，可忽略）

**结论**：性能影响可忽略，缓存命中时甚至可能更快（避免了JOIN查询）

### 后续优化方向

1. **缓存命中率监控**：添加Prometheus指标，监控缓存命中率和刷新耗时
2. **缓存预热**：应用启动时异步加载缓存，避免阻塞启动
3. **增量刷新**：只刷新变更的数据，而非全量刷新（需要监听数据库变更）
4. **分布式缓存**：如果未来需要多实例部署，考虑使用Redis
5. **GraphQL支持**：提供GraphQL接口，支持更灵活的查询
