---
name: test-table
description: 自动化测试表格功能（数据显示、排序、筛选、行操作）
tags: [testing, automation, table]
---

# 测试表格功能

使用 Chrome DevTools 自动化测试 Ant Design Table 表格的完整功能。

## 使用方法

调用此 skill 时，会自动执行以下测试：
1. 验证表格数据加载
2. 测试表格排序功能
3. 测试表格筛选功能
4. 测试行操作按钮
5. 测试行选择功能
6. 返回测试报告

## 参数

- `url`: 要测试的页面URL
- `expected_columns`: 预期列数
- `expected_min_rows`: 预期最小行数

## 测试脚本

```javascript
// 步骤1: 验证表格初始状态
const initialState = await evaluate_script(() => {
  const table = document.querySelector('table');
  const headers = table?.querySelectorAll('thead th');
  const rows = table?.querySelectorAll('tbody tr');
  const firstRowCells = rows?.[0]?.querySelectorAll('td');
  
  return {
    tableExists: !!table,
    columnCount: headers?.length,
    rowCount: rows?.length,
    firstRowData: Array.from(firstRowCells || []).map(td => td.textContent.trim())
  };
});

console.log('表格初始状态:', initialState);
// 预期: tableExists=true, columnCount>0, rowCount>0

// 步骤2: 测试排序功能
await evaluate_script(() => {
  // 点击第一个可排序的列头
  const sortableHeader = document.querySelector('th.ant-table-column-has-sorters');
  sortableHeader?.click();
});

await sleep(500);

const afterSort = await evaluate_script(() => {
  const rows = document.querySelectorAll('tbody tr');
  const firstRowCells = rows?.[0]?.querySelectorAll('td');
  const sortIcon = document.querySelector('.ant-table-column-sorter-up.active, .ant-table-column-sorter-down.active');
  
  return {
    rowCount: rows?.length,
    firstRowData: Array.from(firstRowCells || []).map(td => td.textContent.trim()),
    sortActive: !!sortIcon
  };
});

console.log('排序后状态:', afterSort);
// 预期: sortActive=true, 数据顺序改变

// 步骤3: 测试筛选功能
await evaluate_script(() => {
  // 点击筛选图标
  const filterIcon = document.querySelector('.ant-table-filter-trigger');
  filterIcon?.click();
});

await sleep(300);

await evaluate_script(() => {
  // 选择筛选选项
  const filterOption = document.querySelector('.ant-dropdown-menu-item');
  filterOption?.click();
});

await sleep(500);

const afterFilter = await evaluate_script(() => {
  const rows = document.querySelectorAll('tbody tr');
  const filterIcon = document.querySelector('.ant-table-filter-trigger-container-open');
  
  return {
    rowCount: rows?.length,
    filterActive: !!filterIcon
  };
});

console.log('筛选后状态:', afterFilter);
// 预期: rowCount减少, filterActive=true

// 步骤4: 测试行操作按钮
await evaluate_script(() => {
  // 点击第一行的操作按钮
  const actionBtn = document.querySelector('tbody tr:first-child button');
  actionBtn?.click();
});

await sleep(500);

const afterAction = await evaluate_script(() => {
  const modal = document.querySelector('.ant-modal');
  const message = document.querySelector('.ant-message-notice-content');
  
  return {
    modalVisible: !!modal,
    messageVisible: !!message,
    messageText: message?.textContent
  };
});

console.log('操作后状态:', afterAction);
// 预期: modalVisible=true 或 messageVisible=true

// 步骤5: 测试行选择功能
await evaluate_script(() => {
  // 选择第一行
  const checkbox = document.querySelector('tbody tr:first-child .ant-checkbox-input');
  checkbox?.click();
});

await sleep(300);

const afterSelect = await evaluate_script(() => {
  const selectedRows = document.querySelectorAll('tbody tr.ant-table-row-selected');
  const headerCheckbox = document.querySelector('thead .ant-checkbox-indeterminate, thead .ant-checkbox-checked');
  
  return {
    selectedCount: selectedRows.length,
    headerCheckboxState: headerCheckbox?.className
  };
});

console.log('选择后状态:', afterSelect);
// 预期: selectedCount=1

// 步骤6: 测试全选功能
await evaluate_script(() => {
  // 点击表头复选框全选
  const headerCheckbox = document.querySelector('thead .ant-checkbox-input');
  headerCheckbox?.click();
});

await sleep(300);

const afterSelectAll = await evaluate_script(() => {
  const selectedRows = document.querySelectorAll('tbody tr.ant-table-row-selected');
  const headerCheckbox = document.querySelector('thead .ant-checkbox-checked');
  
  return {
    selectedCount: selectedRows.length,
    allSelected: !!headerCheckbox
  };
});

console.log('全选后状态:', afterSelectAll);
// 预期: selectedCount=总行数, allSelected=true
```

## 返回格式

```json
{
  "passed": true,
  "tests": [
    {
      "name": "表格数据加载",
      "passed": true,
      "expected": "表格存在，有数据",
      "actual": "5列，162行数据"
    },
    {
      "name": "排序功能",
      "passed": true,
      "expected": "数据重新排序",
      "actual": "升序排列，第一行数据改变"
    },
    {
      "name": "筛选功能",
      "passed": true,
      "expected": "数据过滤",
      "actual": "从162行过滤到50行"
    },
    {
      "name": "行操作",
      "passed": true,
      "expected": "触发操作",
      "actual": "打开编辑Modal"
    },
    {
      "name": "行选择",
      "passed": true,
      "expected": "选中1行",
      "actual": "选中1行"
    },
    {
      "name": "全选",
      "passed": true,
      "expected": "选中所有行",
      "actual": "选中162行"
    }
  ]
}
```

## 表格元素选择器

### 常用选择器
```javascript
// 表格容器
const table = document.querySelector('table');

// 表头
const headers = document.querySelectorAll('thead th');

// 表格行
const rows = document.querySelectorAll('tbody tr');

// 第一行
const firstRow = document.querySelector('tbody tr:first-child');

// 最后一行
const lastRow = document.querySelector('tbody tr:last-child');

// 第一行的所有单元格
const firstRowCells = document.querySelectorAll('tbody tr:first-child td');

// 可排序的列头
const sortableHeaders = document.querySelectorAll('th.ant-table-column-has-sorters');

// 筛选图标
const filterIcons = document.querySelectorAll('.ant-table-filter-trigger');

// 行操作按钮
const actionBtns = document.querySelectorAll('tbody tr button');

// 行复选框
const rowCheckboxes = document.querySelectorAll('tbody tr .ant-checkbox-input');

// 表头复选框（全选）
const headerCheckbox = document.querySelector('thead .ant-checkbox-input');

// 选中的行
const selectedRows = document.querySelectorAll('tbody tr.ant-table-row-selected');

// 空状态
const emptyState = document.querySelector('.ant-empty');

// 加载状态
const loading = document.querySelector('.ant-spin-spinning');
```

## 常见问题

**Q: 排序后数据没有变化？**
A: 增加等待时间，或检查是否触发了网络请求。

**Q: 筛选下拉框找不到？**
A: 筛选下拉框渲染在 body 下的 Portal 中，使用全局选择器 `.ant-dropdown-menu-item`。

**Q: 如何验证排序正确性？**
A: 获取排序前后第一行的数据，比较是否符合预期顺序。

**Q: 如何测试虚拟滚动表格？**
A: 使用 `window.scrollTo()` 滚动到底部，验证新数据是否加载。

**Q: 行选择不生效？**
A: 确保点击的是 `.ant-checkbox-input` 元素，而不是外层容器。
