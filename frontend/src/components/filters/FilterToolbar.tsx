import { useEffect, useState } from 'react'
import { Button, Input, Select, Space } from 'antd'

export interface SelectOption {
  label: string
  value: string | number | boolean
}

export interface FilterConfig {
  key: string
  label: string
  options: SelectOption[]
  advanced?: boolean
}

interface SearchField {
  label: string
  value: string
}

interface FilterToolbarProps {
  keyword: string
  searchField: string
  searchFields: SearchField[]
  filters: FilterConfig[]
  values: Record<string, string>
  onSearchFieldChange: (value: string) => void
  onKeywordSearch: (value: string) => void
  onFilterChange: (key: string, value?: string) => void
  onReset: () => void
}

export default function FilterToolbar({
  keyword,
  searchField,
  searchFields,
  filters,
  values,
  onSearchFieldChange,
  onKeywordSearch,
  onFilterChange,
  onReset,
}: FilterToolbarProps) {
  const [draftKeyword, setDraftKeyword] = useState(keyword)
  const [expanded, setExpanded] = useState(false)

  useEffect(() => { setDraftKeyword(keyword) }, [keyword])

  const visibleFilters = filters.filter(item => expanded || !item.advanced)
  const hasAdvanced = filters.some(item => item.advanced)

  return (
    <Space style={{ marginBottom: 16 }} wrap align="start">
      <Input.Group compact>
        <Select
          value={searchField}
          style={{ width: 140 }}
          options={searchFields}
          showSearch
          optionFilterProp="label"
          filterOption={(input, option) => String(option?.label ?? '').toLowerCase().includes(input.toLowerCase())}
          onChange={onSearchFieldChange}
        />
        <Input.Search
          allowClear
          value={draftKeyword}
          placeholder="请输入关键词"
          style={{ width: 260 }}
          onChange={e => setDraftKeyword(e.target.value)}
          onSearch={onKeywordSearch}
        />
      </Input.Group>
      {visibleFilters.map(filter => (
        <Select
          key={filter.key}
          allowClear
          showSearch
          optionFilterProp="label"
          filterOption={(input, option) => String(option?.label ?? '').toLowerCase().includes(input.toLowerCase())}
          placeholder={filter.label}
          value={values[filter.key] || undefined}
          style={{ width: 140 }}
          options={filter.options.map(option => ({ ...option, value: String(option.value) }))}
          onChange={value => onFilterChange(filter.key, value)}
        />
      ))}
      {hasAdvanced && (
        <Button type="link" onClick={() => setExpanded(value => !value)}>
          {expanded ? '收起筛选' : '展开筛选'}
        </Button>
      )}
      <Button onClick={onReset}>重置</Button>
    </Space>
  )
}
