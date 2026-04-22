# 自动化测试技能集

本目录包含款式印花管理系统的自动化测试技能，基于 Chrome DevTools MCP 实现。

## 可用技能

### 1. test-pagination
测试分页功能（页码切换、每页条数、总数显示）

**使用场景**：
- 验证表格分页是否正常工作
- 测试页码切换功能
- 测试每页条数切换功能

**示例**：
```
/test-pagination url=http://localhost:5173/restrictions
```

---

### 2. test-search
测试搜索功能（输入关键词、验证过滤结果、清空搜索）

**使用场景**：
- 验证搜索框输入和过滤
- 测试搜索结果正确性
- 测试清空搜索功能

**示例**：
```
/test-search url=http://localhost:5173/restrictions search_keyword=防晒
```

---

### 3. test-modal
测试 Modal 弹窗功能（打开、内容验证、分页、搜索、关闭）

**使用场景**：
- 验证 Modal 打开和关闭
- 测试 Modal 内的分页功能
- 测试 Modal 内的搜索功能

**示例**：
```
/test-modal url=http://localhost:5173/restrictions
```

---

### 4. test-tabs
测试标签页切换功能（切换标签、验证内容、验证URL）

**使用场景**：
- 验证标签页切换
- 测试每个标签页的内容加载
- 验证 URL 路由变化

**示例**：
```
/test-tabs url=http://localhost:5173/restrictions
```

---

### 5. test-form
测试表单功能（填写、验证、提交、错误处理）

**使用场景**：
- 验证表单填写和验证规则
- 测试表单提交
- 测试错误处理

**示例**：
```
/test-form url=http://localhost:5173/styles/new
```

---

### 6. test-table
测试表格功能（数据显示、排序、筛选、行操作）

**使用场景**：
- 验证表格数据加载
- 测试排序和筛选功能
- 测试行操作和行选择

**示例**：
```
/test-table url=http://localhost:5173/restrictions
```

---

## 技能特点

### React 事件处理
所有技能都正确处理 React 受控组件的事件触发：

```javascript
// 正确的输入方式
const input = document.querySelector('input');
const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
  window.HTMLInputElement.prototype, 'value'
).set;
nativeInputValueSetter.call(input, '值');
input.dispatchEvent(new Event('input', { bubbles: true }));
```

### Ant Design 组件支持
- Table（表格）
- Modal（弹窗）
- Form（表单）
- Tabs（标签页）
- Pagination（分页）
- Select（下拉框）
- Input（输入框）

### 等待策略
- 页面导航：2000ms
- 点击操作：500-1000ms
- 输入操作：300ms（防抖时间）
- API 请求：1000ms

---

## 开发新技能

### 技能文件格式

```markdown
---
name: skill-name
description: 技能描述
tags: [testing, automation, component]
---

# 技能标题

技能说明...

## 使用方法

调用方式和参数说明...

## 参数

- `param1`: 参数1说明
- `param2`: 参数2说明

## 测试脚本

\```javascript
// 测试代码
\```

## 返回格式

\```json
{
  "passed": true,
  "tests": [...]
}
\```

## 常见问题

Q&A...
```

### 最佳实践

1. **明确的测试目标**：每个技能专注于测试一个特定功能
2. **完整的错误处理**：捕获并报告所有可能的错误
3. **清晰的返回格式**：统一的 JSON 格式，包含测试结果和详细信息
4. **详细的文档**：包含使用示例、参数说明、常见问题

---

## 技术栈

- **Chrome DevTools Protocol**：浏览器自动化
- **MCP (Model Context Protocol)**：工具集成
- **JavaScript**：测试脚本语言
- **Ant Design**：UI 组件库
- **React**：前端框架

---

## 相关文档

- [自动化测试完整文档](../automation-testing-skills.md)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [Ant Design 组件文档](https://ant.design/components/overview-cn/)
