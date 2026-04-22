---
name: test-form
description: 自动化测试表单功能（填写、验证、提交、错误处理）
tags: [testing, automation, form]
---

# 测试表单功能

使用 Chrome DevTools 自动化测试 Ant Design Form 表单的完整功能。

## 使用方法

调用此 skill 时，会自动执行以下测试：
1. 打开表单页面
2. 填写表单字段
3. 验证表单验证规则
4. 提交表单
5. 验证提交结果
6. 测试错误处理
7. 返回测试报告

## 参数

- `url`: 要测试的页面URL
- `form_data`: 表单数据对象
- `submit_button_text`: 提交按钮文本（默认：'提交'）

## React 表单输入处理

Ant Design Form 使用 React 受控组件，需要特殊处理：

```javascript
// 填写 Input 输入框
const fillInput = (selector, value) => {
  const input = document.querySelector(selector);
  const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
    window.HTMLInputElement.prototype, 'value'
  ).set;
  nativeInputValueSetter.call(input, value);
  input.dispatchEvent(new Event('input', { bubbles: true }));
  input.dispatchEvent(new Event('change', { bubbles: true }));
};

// 选择 Select 下拉框
const selectOption = (selector, optionText) => {
  // 1. 点击打开下拉框
  const select = document.querySelector(selector);
  select?.click();
  
  // 2. 等待下拉选项渲染
  setTimeout(() => {
    // 3. 选择选项（注意：Select 选项渲染在 body 下的 Portal 中）
    const option = Array.from(document.querySelectorAll('.ant-select-item'))
      .find(item => item.textContent === optionText);
    option?.click();
  }, 300);
};

// 选择 Radio 单选框
const selectRadio = (value) => {
  const radio = document.querySelector(`input[type="radio"][value="${value}"]`);
  radio?.click();
};

// 选择 Checkbox 复选框
const selectCheckbox = (selector, checked) => {
  const checkbox = document.querySelector(selector);
  if (checkbox.checked !== checked) {
    checkbox.click();
  }
};
```

## 测试脚本

```javascript
// 步骤1: 验证表单初始状态
const initialState = await evaluate_script(() => {
  const form = document.querySelector('form');
  const inputs = form?.querySelectorAll('input');
  const submitBtn = Array.from(document.querySelectorAll('button'))
    .find(btn => btn.textContent.includes('提交'));
  
  return {
    formExists: !!form,
    inputCount: inputs?.length,
    submitBtnDisabled: submitBtn?.disabled
  };
});

console.log('表单初始状态:', initialState);

// 步骤2: 填写表单
await evaluate_script(() => {
  // 填写文本输入框
  const fillInput = (selector, value) => {
    const input = document.querySelector(selector);
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
      window.HTMLInputElement.prototype, 'value'
    ).set;
    nativeInputValueSetter.call(input, value);
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
  };
  
  fillInput('input[name="name"]', '测试款式');
  fillInput('input[name="code"]', 'TEST001');
});

await sleep(500);

// 步骤3: 选择下拉框
await evaluate_script(() => {
  const select = document.querySelector('.ant-select-selector');
  select?.click();
});

await sleep(300);

await evaluate_script(() => {
  const option = Array.from(document.querySelectorAll('.ant-select-item'))
    .find(item => item.textContent === '选项1');
  option?.click();
});

await sleep(500);

// 步骤4: 验证表单验证
const afterFill = await evaluate_script(() => {
  const errors = document.querySelectorAll('.ant-form-item-explain-error');
  const submitBtn = Array.from(document.querySelectorAll('button'))
    .find(btn => btn.textContent.includes('提交'));
  
  return {
    errorCount: errors.length,
    submitBtnDisabled: submitBtn?.disabled
  };
});

console.log('填写后状态:', afterFill);
// 预期: errorCount=0, submitBtnDisabled=false

// 步骤5: 提交表单
await evaluate_script(() => {
  const submitBtn = Array.from(document.querySelectorAll('button'))
    .find(btn => btn.textContent.includes('提交'));
  submitBtn?.click();
});

await sleep(1000);

// 步骤6: 验证提交结果
const afterSubmit = await evaluate_script(() => {
  const message = document.querySelector('.ant-message-notice-content');
  const modal = document.querySelector('.ant-modal');
  
  return {
    messageText: message?.textContent,
    modalVisible: !!modal
  };
});

console.log('提交后状态:', afterSubmit);
// 预期: messageText="提交成功" 或 modalVisible=false

// 步骤7: 测试验证错误
await evaluate_script(() => {
  // 清空必填字段
  const input = document.querySelector('input[name="name"]');
  const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
    window.HTMLInputElement.prototype, 'value'
  ).set;
  nativeInputValueSetter.call(input, '');
  input.dispatchEvent(new Event('input', { bubbles: true }));
  input.dispatchEvent(new Event('change', { bubbles: true }));
  input.blur();
});

await sleep(500);

const validationError = await evaluate_script(() => {
  const errors = document.querySelectorAll('.ant-form-item-explain-error');
  const errorTexts = Array.from(errors).map(e => e.textContent);
  
  return {
    errorCount: errors.length,
    errorTexts: errorTexts
  };
});

console.log('验证错误:', validationError);
// 预期: errorCount>0, errorTexts包含"请输入名称"
```

## 返回格式

```json
{
  "passed": true,
  "tests": [
    {
      "name": "表单初始化",
      "passed": true,
      "expected": "表单存在，提交按钮可能禁用",
      "actual": "表单存在，5个输入框，提交按钮禁用"
    },
    {
      "name": "填写表单",
      "passed": true,
      "expected": "无验证错误，提交按钮启用",
      "actual": "无验证错误，提交按钮启用"
    },
    {
      "name": "提交表单",
      "passed": true,
      "expected": "显示成功消息",
      "actual": "显示'提交成功'"
    },
    {
      "name": "验证错误",
      "passed": true,
      "expected": "显示验证错误信息",
      "actual": "显示'请输入名称'"
    }
  ]
}
```

## 表单元素选择器

### 常用选择器
```javascript
// 表单容器
const form = document.querySelector('form');

// 表单项
const formItem = document.querySelector('.ant-form-item');

// 输入框（通过 name 属性）
const input = document.querySelector('input[name="fieldName"]');

// 下拉框
const select = document.querySelector('.ant-select-selector');

// 单选框
const radio = document.querySelector('input[type="radio"][value="value"]');

// 复选框
const checkbox = document.querySelector('input[type="checkbox"]');

// 日期选择器
const datePicker = document.querySelector('.ant-picker-input input');

// 提交按钮
const submitBtn = Array.from(document.querySelectorAll('button'))
  .find(btn => btn.textContent.includes('提交'));

// 验证错误信息
const errors = document.querySelectorAll('.ant-form-item-explain-error');

// 成功消息
const message = document.querySelector('.ant-message-notice-content');
```

## 常见问题

**Q: 输入后验证不触发？**
A: 确保触发 input、change 和 blur 事件。

**Q: Select 下拉选项找不到？**
A: Select 选项渲染在 body 下的 Portal 中，不在表单内部，使用全局选择器。

**Q: 提交按钮一直禁用？**
A: 检查表单验证规则，确保所有必填字段都已填写且格式正确。

**Q: 如何测试异步验证？**
A: 增加等待时间，或监听网络请求完成。
