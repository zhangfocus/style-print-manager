# 自动化测试技能集

本文档记录了款式印花管理系统的自动化测试能力和最佳实践。

## 测试工具

### Chrome DevTools MCP
通过 MCP (Model Context Protocol) 集成的 Chrome DevTools，支持：
- 自动打开浏览器页面
- 执行 JavaScript 脚本
- 模拟用户交互（点击、输入、滚动等）
- 获取页面元素和状态
- 验证页面行为

## 核心测试能力

### 1. 页面导航与加载
```javascript
// 打开指定页面
await navigate('http://localhost:5173/restrictions')

// 等待页面加载完成
await new Promise(resolve => setTimeout(resolve, 2000))
```

### 2. 元素查询与验证
```javascript
// 查询表格行数（包含表头）
const rows = document.querySelectorAll('table tbody tr')
console.log('表格行数:', rows.length)

// 查询分页信息
const pagination = document.querySelector('.ant-pagination')
const pageInfo = pagination?.textContent
console.log('分页信息:', pageInfo)

// 查询特定文本
const hasText = document.body.textContent.includes('共 162 条')
console.log('是否包含文本:', hasText)
```

### 3. 用户交互模拟

#### 点击操作
```javascript
// 点击按钮
const button = document.querySelector('button.ant-btn')
button?.click()

// 点击分页按钮
const nextPage = document.querySelector('.ant-pagination-item[title="2"]')
nextPage?.click()

// 点击表格中的查看按钮
const viewBtn = document.querySelector('table tbody tr:first-child button')
viewBtn?.click()
```

#### 输入操作
```javascript
// 在搜索框输入文本
const input = document.querySelector('input[placeholder="搜索..."]')
if (input) {
  // 方法1: 直接设置值（不触发 React 事件）
  input.value = '关键词'
  
  // 方法2: 触发 React 合成事件
  const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
    window.HTMLInputElement.prototype, 
    'value'
  ).set
  nativeInputValueSetter.call(input, '关键词')
  input.dispatchEvent(new Event('input', { bubbles: true }))
}
```

#### 下拉选择
```javascript
// 打开下拉框
const select = document.querySelector('.ant-select')
select?.click()

// 等待选项加载
await new Promise(resolve => setTimeout(resolve, 500))

// 选择选项
const option = document.querySelector('.ant-select-item[title="选项名"]')
option?.click()
```

### 4. 网络请求监控
```javascript
// 监听 API 请求
const originalFetch = window.fetch
window.fetch = function(...args) {
  console.log('API 请求:', args[0])
  return originalFetch.apply(this, args)
}
```

### 5. 数据验证
```javascript
// 验证表格数据
const cells = document.querySelectorAll('table tbody tr:first-child td')
const rowData = Array.from(cells).map(cell => cell.textContent.trim())
console.log('第一行数据:', rowData)

// 验证 Modal 内容
const modalItems = document.querySelectorAll('.ant-modal ul li')
console.log('Modal 项数:', modalItems.length)

// 验证分页状态
const activePage = document.querySelector('.ant-pagination-item-active')
console.log('当前页码:', activePage?.textContent)
```

## 测试场景示例

### 场景1: 验证分页功能
```javascript
// 1. 打开页面
await navigate('http://localhost:5173/restrictions')
await new Promise(resolve => setTimeout(resolve, 2000))

// 2. 验证初始状态
const initialRows = document.querySelectorAll('table tbody tr').length
console.log('初始行数:', initialRows) // 应为 10 + 1(表头)

// 3. 点击第2页
const page2 = document.querySelector('.ant-pagination-item[title="2"]')
page2?.click()
await new Promise(resolve => setTimeout(resolve, 1000))

// 4. 验证页码变化
const activePage = document.querySelector('.ant-pagination-item-active')
console.log('当前页码:', activePage?.textContent) // 应为 "2"
```

### 场景2: 验证搜索式下拉
```javascript
// 1. 打开下拉框
const select = document.querySelector('.ant-select')
select?.click()
await new Promise(resolve => setTimeout(resolve, 500))

// 2. 输入搜索关键词
const input = document.querySelector('.ant-select-selection-search-input')
const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
  window.HTMLInputElement.prototype, 
  'value'
).set
nativeInputValueSetter.call(input, '防晒')
input.dispatchEvent(new Event('input', { bubbles: true }))

// 3. 等待搜索结果
await new Promise(resolve => setTimeout(resolve, 500))

// 4. 验证选项数量
const options = document.querySelectorAll('.ant-select-item')
console.log('搜索结果数:', options.length)
```

### 场景3: 验证 Modal 弹窗分页
```javascript
// 1. 点击查看按钮
const viewBtn = document.querySelector('table tbody tr:first-child button')
viewBtn?.click()
await new Promise(resolve => setTimeout(resolve, 500))

// 2. 验证 Modal 打开
const modal = document.querySelector('.ant-modal')
console.log('Modal 是否打开:', modal !== null)

// 3. 验证初始数据
const items = document.querySelectorAll('.ant-modal ul[style*="list-style"] li')
console.log('Modal 显示项数:', items.length) // 应为 8

// 4. 验证分页信息
const pagination = document.querySelector('.ant-modal .ant-pagination')
const total = pagination?.textContent.match(/共 (\d+) 条/)?.[1]
console.log('总记录数:', total)

// 5. 点击第2页
const page2 = document.querySelector('.ant-modal .ant-pagination-item[title="2"]')
page2?.click()
await new Promise(resolve => setTimeout(resolve, 500))

// 6. 验证页码变化
const activePage = document.querySelector('.ant-modal .ant-pagination-item-active')
console.log('当前页码:', activePage?.textContent)
```

### 场景4: 验证 Modal 内搜索
```javascript
// 1. 打开 Modal（同场景3）
const viewBtn = document.querySelector('table tbody tr:first-child button')
viewBtn?.click()
await new Promise(resolve => setTimeout(resolve, 500))

// 2. 在搜索框输入关键词
const input = document.querySelector('.ant-modal input[placeholder="搜索..."]')
const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
  window.HTMLInputElement.prototype, 
  'value'
).set
nativeInputValueSetter.call(input, '几何')
input.dispatchEvent(new Event('input', { bubbles: true }))

// 3. 等待过滤完成
await new Promise(resolve => setTimeout(resolve, 300))

// 4. 验证过滤结果
const items = document.querySelectorAll('.ant-modal ul[style*="list-style"] li')
console.log('过滤后项数:', items.length)

// 5. 验证分页重置到第1页
const activePage = document.querySelector('.ant-modal .ant-pagination-item-active')
console.log('当前页码:', activePage?.textContent) // 应为 "1"
```

## 测试最佳实践

### 1. 等待时机
- 页面导航后等待 2000ms
- 点击操作后等待 500-1000ms
- 输入操作后等待 300ms（防抖时间）
- API 请求后等待 1000ms

### 2. 元素选择器
- 优先使用语义化选择器（如 `button.ant-btn`）
- 避免使用过于宽泛的选择器（如 `div`）
- 使用属性选择器提高精确度（如 `input[placeholder="搜索..."]`）
- 对于动态内容，使用 `title` 或 `data-*` 属性

### 3. 错误处理
```javascript
// 使用可选链避免空指针
const text = element?.textContent ?? '默认值'

// 验证元素存在
if (!element) {
  console.error('元素未找到')
  return
}

// 捕获异常
try {
  element.click()
} catch (error) {
  console.error('点击失败:', error)
}
```

### 4. 调试技巧
```javascript
// 输出元素信息
console.log('元素:', element)
console.log('文本:', element?.textContent)
console.log('属性:', element?.getAttribute('class'))

// 输出页面状态
console.log('URL:', window.location.href)
console.log('标题:', document.title)

// 输出查询结果
const elements = document.querySelectorAll('selector')
console.log('找到元素数:', elements.length)
Array.from(elements).forEach((el, i) => {
  console.log(`元素 ${i}:`, el.textContent)
})
```

## 开发测试流程

### 1. 后端开发
```bash
# 修改代码
cd backend/app

# 重启服务（如果需要）
taskkill //F //IM python.exe
cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 前端开发
```bash
# 修改代码
cd frontend/src

# 重新构建
cd frontend && npm run build

# 如果开发服务器在运行，会自动热更新
```

### 3. 自动化测试
```javascript
// 使用 Chrome DevTools MCP 执行测试脚本
// 1. 打开页面
// 2. 执行测试场景
// 3. 验证结果
// 4. 输出测试报告
```

### 4. 手动验证
- 在浏览器中打开页面
- 执行关键操作
- 检查控制台日志
- 验证网络请求

## 常见问题

### Q: 为什么点击后没有反应？
A: 可能需要等待更长时间，或者元素选择器不正确。使用 `console.log` 验证元素是否存在。

### Q: 为什么输入后搜索不生效？
A: 直接修改 `input.value` 不会触发 React 事件，需要使用 `dispatchEvent` 触发合成事件。

### Q: 如何验证 API 请求？
A: 可以在浏览器开发者工具的 Network 面板查看，或者使用 `fetch` 拦截器记录请求。

### Q: 测试脚本执行失败怎么办？
A: 检查元素选择器是否正确，增加等待时间，查看控制台错误信息。

## 扩展阅读

- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [React 合成事件](https://react.dev/learn/responding-to-events)
- [Ant Design 组件文档](https://ant.design/components/overview-cn/)
