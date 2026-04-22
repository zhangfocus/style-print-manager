---
name: test-modal
description: 自动化测试 Modal 弹窗功能（打开、内容验证、分页、搜索、关闭）
tags: [testing, automation, modal]
---

# 测试 Modal 弹窗功能

使用 Chrome DevTools 自动化测试 Ant Design Modal 弹窗的完整功能。

## 使用方法

调用此 skill 时，会自动执行以下测试：
1. 点击触发按钮打开 Modal
2. 验证 Modal 标题和内容
3. 测试 Modal 内的分页功能
4. 测试 Modal 内的搜索功能
5. 关闭 Modal 并验证
6. 返回测试报告

## 参数

- `url`: 要测试的页面URL（默认：http://localhost:5173/restrictions）
- `trigger_button_text`: 触发按钮文本（默认：'查看'）
- `expected_page_size`: 预期每页条数（默认：8）

## 测试脚本

```javascript
// 步骤1: 点击查看按钮打开 Modal
await evaluate_script(() => {
  const buttons = Array.from(document.querySelectorAll('button'))
    .filter(btn => btn.textContent.includes('查看'));
  buttons[0]?.click();
  return { buttonCount: buttons.length };
});

await sleep(500);

// 步骤2: 验证 Modal 打开
const modalState = await evaluate_script(() => {
  const modal = document.querySelector('.ant-modal');
  const title = modal?.querySelector('.ant-modal-title')?.textContent;
  const items = modal?.querySelectorAll('ul[style*="list-style"] li');
  const pagination = modal?.querySelector('.ant-pagination-total-text')?.textContent;
  
  return {
    modalVisible: !!modal,
    title: title,
    itemCount: items?.length,
    totalText: pagination
  };
});

console.log('Modal 状态:', modalState);
// 预期: modalVisible=true, itemCount=8, totalText="共 X 条"

// 步骤3: 测试 Modal 内分页
await evaluate_script(() => {
  const modal = document.querySelector('.ant-modal');
  const page2 = modal?.querySelector('.ant-pagination-item[title="2"] a');
  page2?.click();
});

await sleep(500);

const afterPageChange = await evaluate_script(() => {
  const modal = document.querySelector('.ant-modal');
  const activePage = modal?.querySelector('.ant-pagination-item-active');
  const items = modal?.querySelectorAll('ul[style*="list-style"] li');
  
  return {
    currentPage: activePage?.textContent,
    itemCount: items?.length
  };
});

console.log('翻页后:', afterPageChange);
// 预期: currentPage="2", itemCount=8

// 步骤4: 测试 Modal 内搜索
await evaluate_script((keyword) => {
  const modal = document.querySelector('.ant-modal');
  const input = modal?.querySelector('input[placeholder*="搜索"]');
  
  const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
    window.HTMLInputElement.prototype, 'value'
  ).set;
  nativeInputValueSetter.call(input, keyword);
  input.dispatchEvent(new Event('input', { bubbles: true }));
}, '几何');

await sleep(500);

const afterSearch = await evaluate_script(() => {
  const modal = document.querySelector('.ant-modal');
  const items = modal?.querySelectorAll('ul[style*="list-style"] li');
  const activePage = modal?.querySelector('.ant-pagination-item-active');
  
  return {
    itemCount: items?.length,
    currentPage: activePage?.textContent,
    itemTexts: Array.from(items || []).map(li => li.textContent)
  };
});

console.log('搜索后:', afterSearch);
// 预期: 数据量减少，页码重置到1，所有项包含关键词

// 步骤5: 关闭 Modal
await evaluate_script(() => {
  const closeBtn = document.querySelector('.ant-modal-close');
  closeBtn?.click();
});

await sleep(300);

// 步骤6: 验证 Modal 关闭
const afterClose = await evaluate_script(() => {
  const modal = document.querySelector('.ant-modal');
  return {
    modalVisible: !!modal
  };
});

console.log('关闭后:', afterClose);
// 预期: modalVisible=false
```

## 返回格式

```json
{
  "passed": true,
  "tests": [
    {
      "name": "Modal 打开",
      "passed": true,
      "expected": "Modal 可见，显示8条数据",
      "actual": "Modal 可见，显示8条数据"
    },
    {
      "name": "Modal 内分页",
      "passed": true,
      "expected": "切换到第2页，显示8条数据",
      "actual": "切换到第2页，显示8条数据"
    },
    {
      "name": "Modal 内搜索",
      "passed": true,
      "expected": "过滤结果，重置到第1页",
      "actual": "从25条过滤到5条，页码重置"
    },
    {
      "name": "Modal 关闭",
      "passed": true,
      "expected": "Modal 不可见",
      "actual": "Modal 不可见"
    }
  ]
}
```

## Modal 元素选择器

### 常用选择器
```javascript
// Modal 容器
const modal = document.querySelector('.ant-modal');

// Modal 标题
const title = modal?.querySelector('.ant-modal-title');

// Modal 内容区域
const content = modal?.querySelector('.ant-modal-body');

// Modal 内的列表项
const items = modal?.querySelectorAll('ul[style*="list-style"] li');

// Modal 内的搜索框
const searchInput = modal?.querySelector('input[placeholder*="搜索"]');

// Modal 内的分页组件
const pagination = modal?.querySelector('.ant-pagination');

// Modal 关闭按钮
const closeBtn = modal?.querySelector('.ant-modal-close');

// Modal 底部按钮
const okBtn = modal?.querySelector('.ant-modal-footer .ant-btn-primary');
const cancelBtn = modal?.querySelector('.ant-modal-footer .ant-btn-default');
```

## 常见问题

**Q: Modal 打开后找不到元素？**
A: 增加等待时间（sleep），确保 Modal 动画完成。

**Q: 如何验证 Modal 内容正确性？**
A: 获取列表项文本，检查是否符合预期数据。

**Q: 如何测试多个 Modal？**
A: 使用更具体的选择器，或通过 data-testid 属性区分。

**Q: Modal 搜索不生效？**
A: 确保使用 nativeInputValueSetter + dispatchEvent 触发 React 事件。
