---
name: test-tabs
description: 自动化测试标签页切换功能（切换标签、验证内容、验证URL）
tags: [testing, automation, tabs]
---

# 测试标签页切换功能

使用 Chrome DevTools 自动化测试 Ant Design Tabs 标签页的切换功能。

## 使用方法

调用此 skill 时，会自动执行以下测试：
1. 打开指定页面
2. 验证初始标签页状态
3. 切换到不同标签页
4. 验证每个标签页的内容
5. 验证 URL 是否正确更新
6. 返回测试报告

## 参数

- `url`: 要测试的页面URL（默认：http://localhost:5173/restrictions）
- `tab_names`: 标签页名称列表（默认：['款式位置规则', '位置限定规则', '款式全禁规则']）

## 测试脚本

```javascript
// 步骤1: 验证初始标签页
const initialState = await evaluate_script(() => {
  const activeTab = document.querySelector('.ant-tabs-tab-active');
  const tabContent = document.querySelector('.ant-tabs-tabpane-active');
  const rows = tabContent?.querySelectorAll('table tbody tr');
  
  return {
    activeTabText: activeTab?.textContent,
    rowCount: rows?.length,
    url: window.location.href
  };
});

console.log('初始标签页:', initialState);
// 预期: activeTabText="款式位置规则", rowCount>0

// 步骤2: 切换到第二个标签页
await evaluate_script(() => {
  const tabs = document.querySelectorAll('.ant-tabs-tab');
  tabs[1]?.click();
});

await sleep(500);

// 步骤3: 验证标签页切换
const afterSwitch = await evaluate_script(() => {
  const activeTab = document.querySelector('.ant-tabs-tab-active');
  const tabContent = document.querySelector('.ant-tabs-tabpane-active');
  const rows = tabContent?.querySelectorAll('table tbody tr');
  
  return {
    activeTabText: activeTab?.textContent,
    rowCount: rows?.length,
    url: window.location.href
  };
});

console.log('切换后标签页:', afterSwitch);
// 预期: activeTabText="位置限定规则", rowCount>0

// 步骤4: 切换到第三个标签页
await evaluate_script(() => {
  const tabs = document.querySelectorAll('.ant-tabs-tab');
  tabs[2]?.click();
});

await sleep(500);

// 步骤5: 验证第三个标签页
const thirdTab = await evaluate_script(() => {
  const activeTab = document.querySelector('.ant-tabs-tab-active');
  const tabContent = document.querySelector('.ant-tabs-tabpane-active');
  const rows = tabContent?.querySelectorAll('table tbody tr');
  
  return {
    activeTabText: activeTab?.textContent,
    rowCount: rows?.length,
    url: window.location.href
  };
});

console.log('第三个标签页:', thirdTab);
// 预期: activeTabText="款式全禁规则", rowCount>0

// 步骤6: 切换回第一个标签页
await evaluate_script(() => {
  const tabs = document.querySelectorAll('.ant-tabs-tab');
  tabs[0]?.click();
});

await sleep(500);

const backToFirst = await evaluate_script(() => {
  const activeTab = document.querySelector('.ant-tabs-tab-active');
  return {
    activeTabText: activeTab?.textContent
  };
});

console.log('返回第一个标签页:', backToFirst);
// 预期: activeTabText="款式位置规则"
```

## 返回格式

```json
{
  "passed": true,
  "tests": [
    {
      "name": "初始标签页",
      "passed": true,
      "expected": "款式位置规则激活",
      "actual": "款式位置规则激活"
    },
    {
      "name": "切换到位置限定规则",
      "passed": true,
      "expected": "位置限定规则激活，显示数据",
      "actual": "位置限定规则激活，显示15条数据"
    },
    {
      "name": "切换到款式全禁规则",
      "passed": true,
      "expected": "款式全禁规则激活，显示数据",
      "actual": "款式全禁规则激活，显示40条数据"
    },
    {
      "name": "返回第一个标签页",
      "passed": true,
      "expected": "款式位置规则激活",
      "actual": "款式位置规则激活"
    }
  ]
}
```

## 标签页元素选择器

### 常用选择器
```javascript
// 所有标签页
const tabs = document.querySelectorAll('.ant-tabs-tab');

// 激活的标签页
const activeTab = document.querySelector('.ant-tabs-tab-active');

// 标签页内容区域
const tabContent = document.querySelector('.ant-tabs-tabpane-active');

// 通过文本查找标签页
const tab = Array.from(document.querySelectorAll('.ant-tabs-tab'))
  .find(t => t.textContent.includes('款式位置规则'));

// 标签页内的表格
const table = document.querySelector('.ant-tabs-tabpane-active table');

// 标签页内的行数
const rows = document.querySelectorAll('.ant-tabs-tabpane-active table tbody tr');
```

## 常见问题

**Q: 切换标签页后内容没有更新？**
A: 增加等待时间（sleep），确保数据加载完成。

**Q: 如何验证标签页内容正确性？**
A: 获取表格行数、特定列的内容，检查是否符合预期。

**Q: 如何测试 URL 路由变化？**
A: 在切换后获取 `window.location.href`，检查 URL 参数或路径是否正确更新。

**Q: 标签页点击无效？**
A: 检查选择器是否正确，或尝试点击 `.ant-tabs-tab-btn` 元素。
