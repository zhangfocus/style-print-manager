---
name: test-pagination
description: 自动化测试分页功能（页码切换、每页条数、总数显示）
tags: [testing, automation, pagination]
---

# 测试分页功能

使用 Chrome DevTools 自动化测试页面的分页功能。

## 使用方法

调用此 skill 时，会自动执行以下测试：
1. 打开指定页面
2. 验证初始分页状态（第1页、默认条数、总数）
3. 点击第2页，验证页码切换
4. 切换每页条数，验证数据重新加载
5. 返回测试报告

## 参数

- `url`: 要测试的页面URL（默认：http://localhost:5173/restrictions）
- `initial_page_size`: 初始每页条数（默认：10）

## 测试脚本

```javascript
// 步骤1: 验证初始状态
const initialState = await evaluate_script(() => {
  const rows = document.querySelectorAll('table tbody tr');
  const pagination = document.querySelector('.ant-pagination-total-text');
  const activePage = document.querySelector('.ant-pagination-item-active');
  
  return {
    rowCount: rows.length,
    totalText: pagination?.textContent,
    currentPage: activePage?.textContent
  };
});

console.log('初始状态:', initialState);
// 预期: rowCount=10, currentPage="1", totalText="共 X 条"

// 步骤2: 点击第2页
await evaluate_script(() => {
  const page2 = document.querySelector('.ant-pagination-item[title="2"] a');
  page2?.click();
});

await sleep(1000);

// 步骤3: 验证页码变化
const afterPageChange = await evaluate_script(() => {
  const activePage = document.querySelector('.ant-pagination-item-active');
  return {
    currentPage: activePage?.textContent
  };
});

console.log('切换后页码:', afterPageChange);
// 预期: currentPage="2"

// 步骤4: 切换每页条数
await evaluate_script(() => {
  const sizeChanger = document.querySelector('.ant-select-selector');
  sizeChanger?.click();
});

await sleep(500);

await evaluate_script(() => {
  const option20 = Array.from(document.querySelectorAll('.ant-select-item'))
    .find(item => item.textContent === '20 条/页');
  option20?.click();
});

await sleep(1000);

// 步骤5: 验证条数变化
const afterSizeChange = await evaluate_script(() => {
  const rows = document.querySelectorAll('table tbody tr');
  return {
    rowCount: rows.length
  };
});

console.log('切换后行数:', afterSizeChange);
// 预期: rowCount=20
```

## 返回格式

```json
{
  "passed": true,
  "tests": [
    {
      "name": "初始分页状态",
      "passed": true,
      "expected": "第1页，10条数据",
      "actual": "第1页，10条数据"
    },
    {
      "name": "页码切换",
      "passed": true,
      "expected": "第2页",
      "actual": "第2页"
    },
    {
      "name": "每页条数切换",
      "passed": true,
      "expected": "20条数据",
      "actual": "20条数据"
    }
  ]
}
```

## 常见问题

**Q: 点击后没有反应？**
A: 增加等待时间，或检查元素选择器是否正确。

**Q: 如何测试其他页面？**
A: 传入 `url` 参数指定页面地址。
