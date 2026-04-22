---
name: test-search
description: 自动化测试搜索功能（输入关键词、验证过滤结果、清空搜索）
tags: [testing, automation, search]
---

# 测试搜索功能

使用 Chrome DevTools 自动化测试页面的搜索功能。

## 使用方法

调用此 skill 时，会自动执行以下测试：
1. 打开指定页面
2. 在搜索框输入关键词
3. 验证搜索结果是否正确过滤
4. 清空搜索，验证恢复全部数据
5. 返回测试报告

## 参数

- `url`: 要测试的页面URL（默认：http://localhost:5173/restrictions）
- `search_keyword`: 搜索关键词（默认：根据页面内容自动选择）
- `search_input_selector`: 搜索框选择器（默认：'input[placeholder*="搜索"]'）

## React 输入处理

React 受控组件需要特殊处理才能触发 onChange 事件：

```javascript
// 正确的方式：触发 React 合成事件
const input = document.querySelector('input[placeholder*="搜索"]');
const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
  window.HTMLInputElement.prototype, 'value'
).set;
nativeInputValueSetter.call(input, '搜索关键词');
input.dispatchEvent(new Event('input', { bubbles: true }));
```

## 测试脚本

```javascript
// 步骤1: 记录初始数据量
const initialState = await evaluate_script(() => {
  const rows = document.querySelectorAll('table tbody tr');
  return {
    rowCount: rows.length,
    firstRowText: rows[0]?.textContent
  };
});

console.log('初始数据量:', initialState.rowCount);

// 步骤2: 输入搜索关键词
await evaluate_script((keyword) => {
  const input = document.querySelector('input[placeholder*="搜索"]');
  const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
    window.HTMLInputElement.prototype, 'value'
  ).set;
  nativeInputValueSetter.call(input, keyword);
  input.dispatchEvent(new Event('input', { bubbles: true }));
}, '关键词');

await sleep(1000); // 等待搜索结果

// 步骤3: 验证搜索结果
const afterSearch = await evaluate_script(() => {
  const rows = document.querySelectorAll('table tbody tr');
  const rowTexts = Array.from(rows).map(r => r.textContent);
  return {
    rowCount: rows.length,
    rowTexts: rowTexts
  };
});

console.log('搜索后数据量:', afterSearch.rowCount);

// 验证所有行都包含关键词
const allMatch = afterSearch.rowTexts.every(text => 
  text.includes('关键词')
);

console.log('搜索结果匹配:', allMatch);

// 步骤4: 清空搜索
await evaluate_script(() => {
  const clearBtn = document.querySelector('.ant-input-clear-icon');
  clearBtn?.click();
});

await sleep(1000);

// 步骤5: 验证恢复全部数据
const afterClear = await evaluate_script(() => {
  const rows = document.querySelectorAll('table tbody tr');
  return {
    rowCount: rows.length
  };
});

console.log('清空后数据量:', afterClear.rowCount);
// 预期: 恢复到初始数据量
```

## 返回格式

```json
{
  "passed": true,
  "tests": [
    {
      "name": "搜索过滤",
      "passed": true,
      "expected": "数据量减少，所有行包含关键词",
      "actual": "从100条过滤到15条，全部匹配"
    },
    {
      "name": "清空搜索",
      "passed": true,
      "expected": "恢复到初始数据量",
      "actual": "恢复到100条"
    }
  ]
}
```

## 常见问题

**Q: 输入后没有触发搜索？**
A: 确保使用 nativeInputValueSetter + dispatchEvent 触发 React 事件。

**Q: 如何测试防抖搜索？**
A: 增加等待时间（如 sleep(1500)），确保防抖完成。

**Q: 如何验证搜索结果正确性？**
A: 获取所有行的文本内容，检查是否都包含搜索关键词。
