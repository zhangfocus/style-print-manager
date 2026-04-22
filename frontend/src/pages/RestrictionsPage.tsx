import { useEffect, useState, useRef } from 'react'
import {
  Table, Button, Modal, Form, Input, Switch, Popconfirm,
  Space, Tag, message, Card, Select, Tabs, Pagination,
} from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import type { StylePositionRule, Style, Position, Print } from '../types'
import {
  listRules, createRule, updateRule, deleteRule,
} from '../api/restrictions'
import { listStyles, getStylesByIds } from '../api/styles'
import { listPositions } from '../api/positions'
import { listPrints, getPrintsByIds } from '../api/prints'

type RuleType = 1 | 2 | 3  // 1=style_ban, 2=position_restriction, 3=style_position

export default function RestrictionsPage() {
  const [rules, setRules] = useState<StylePositionRule[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)

  const [styles, setStyles] = useState<Style[]>([])
  const [positions, setPositions] = useState<Position[]>([])
  const [prints, setPrints] = useState<Print[]>([])
  const [styleSearching, setStyleSearching] = useState(false)
  const [positionSearching, setPositionSearching] = useState(false)
  const [printSearching, setPrintSearching] = useState(false)

  const [activeTab, setActiveTab] = useState<RuleType>(3)
  const [filterStyleId, setFilterStyleId] = useState<number | undefined>()
  const [filterPositionId, setFilterPositionId] = useState<number | undefined>()
  const [filterPrintId, setFilterPrintId] = useState<number | undefined>()

  const [ruleModalOpen, setRuleModalOpen] = useState(false)
  const [editingRule, setEditingRule] = useState<StylePositionRule | null>(null)
  const [ruleForm] = Form.useForm()
  const [submitting, setSubmitting] = useState(false)
  const [selectedRuleType, setSelectedRuleType] = useState<RuleType>(3)
  const [viewModalOpen, setViewModalOpen] = useState(false)
  const [viewModalTitle, setViewModalTitle] = useState('')
  const [viewModalItems, setViewModalItems] = useState<string[]>([])
  const [viewModalSearch, setViewModalSearch] = useState('')
  const [viewModalPage, setViewModalPage] = useState(1)
  const [viewModalPageSize, setViewModalPageSize] = useState(8)

  const load = async () => {
    setLoading(true)
    try {
      const style_code = filterStyleId ? styles.find(s => s.id === filterStyleId)?.code : undefined
      const print_code = filterPrintId ? prints.find(p => p.id === filterPrintId)?.code : undefined

      const res = await listRules({
        style_code,
        position_id: filterPositionId,
        print_code,
        rule_type: activeTab,
        page,
        page_size: pageSize
      })
      setRules(res.items)
      setTotal(res.total)
    } catch (e: unknown) {
      message.error((e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  const searchStylesDebounced = useRef<number | undefined>(undefined)
  const searchStyles = (keyword: string) => {
    if (searchStylesDebounced.current) {
      clearTimeout(searchStylesDebounced.current)
    }
    searchStylesDebounced.current = setTimeout(async () => {
      setStyleSearching(true)
      try {
        const res = await listStyles(keyword, 1, 50)
        setStyles(res.items)
      } catch (e: unknown) {
        message.error((e as Error).message)
      } finally {
        setStyleSearching(false)
      }
    }, 300)
  }

  const searchPositionsDebounced = useRef<number | undefined>(undefined)
  const searchPositions = (keyword: string) => {
    if (searchPositionsDebounced.current) {
      clearTimeout(searchPositionsDebounced.current)
    }
    searchPositionsDebounced.current = setTimeout(async () => {
      setPositionSearching(true)
      try {
        const res = await listPositions(keyword, 1, 50)
        setPositions(res.items)
      } catch (e: unknown) {
        message.error((e as Error).message)
      } finally {
        setPositionSearching(false)
      }
    }, 300)
  }

  const searchPrintsDebounced = useRef<number | undefined>(undefined)
  const searchPrints = (keyword: string) => {
    if (searchPrintsDebounced.current) {
      clearTimeout(searchPrintsDebounced.current)
    }
    searchPrintsDebounced.current = setTimeout(async () => {
      setPrintSearching(true)
      try {
        const res = await listPrints(keyword, 1, 50)
        setPrints(res.items)
      } catch (e: unknown) {
        message.error((e as Error).message)
      } finally {
        setPrintSearching(false)
      }
    }, 300)
  }

  useEffect(() => {
    searchStyles('')
    searchPositions('')
    searchPrints('')
  }, [])

  useEffect(() => {
    setPage(1)
  }, [activeTab, filterStyleId, filterPositionId, filterPrintId])

  useEffect(() => {
    load()
  }, [activeTab, filterStyleId, filterPositionId, filterPrintId, page, pageSize])

  const styleOptions = styles.map(s => ({
    value: s.id,
    label: s.code,
  }))
  const positionOptions = positions.map(p => ({ value: p.id, label: p.name }))
  const printOptions = prints.map(p => ({ value: p.id, label: p.code }))

  const openCreateRule = () => {
    setEditingRule(null)
    ruleForm.resetFields()
    ruleForm.setFieldsValue({ rule_type: activeTab, is_active: true })
    setSelectedRuleType(activeTab)
    setRuleModalOpen(true)
  }

  const openViewModal = (title: string, displayText: string) => {
    setViewModalTitle(title)
    // 解析显示文本，按逗号分隔
    const items = displayText.split(',').map(item => item.trim()).filter(item => item)
    setViewModalItems(items)
    setViewModalSearch('')
    setViewModalPage(1)
    setViewModalPageSize(8)
    setViewModalOpen(true)
  }

  const filteredViewItems = viewModalItems.filter(item =>
    item.toLowerCase().includes(viewModalSearch.toLowerCase())
  )

  // 计算分页后的数据
  const paginatedViewItems = filteredViewItems.slice(
    (viewModalPage - 1) * viewModalPageSize,
    viewModalPage * viewModalPageSize
  )

  const openEditRule = async (r: StylePositionRule) => {
    setEditingRule(r)
    setSelectedRuleType(r.rule_type)

    // 解析ID列表
    const styleIds = r.style_ids ? r.style_ids.split(',').map(id => parseInt(id.trim())) : []
    const printIds = r.print_ids ? r.print_ids.split(',').map(id => parseInt(id.trim())) : []

    // 批量加载款式和印花数据
    try {
      if (styleIds.length > 0) {
        const loadedStyles = await getStylesByIds(styleIds)
        // 合并到现有的styles列表中，避免重复
        setStyles(prev => {
          const existingIds = new Set(prev.map(s => s.id))
          const newStyles = loadedStyles.filter(s => !existingIds.has(s.id))
          return [...prev, ...newStyles]
        })
      }

      if (printIds.length > 0) {
        const loadedPrints = await getPrintsByIds(printIds)
        // 合并到现有的prints列表中，避免重复
        setPrints(prev => {
          const existingIds = new Set(prev.map(p => p.id))
          const newPrints = loadedPrints.filter(p => !existingIds.has(p.id))
          return [...prev, ...newPrints]
        })
      }
    } catch (e: unknown) {
      message.error((e as Error).message)
    }

    ruleForm.setFieldsValue({
      rule_type: r.rule_type,
      position_id: r.position_id,
      style_ids: styleIds,
      print_ids: printIds,
      is_active: r.is_active,
    })
    setRuleModalOpen(true)
  }

  const handleDeleteRule = async (id: number) => {
    try {
      await deleteRule(id)
      message.success('删除成功')
      load()
    } catch (e: unknown) {
      message.error((e as Error).message)
    }
  }

  const handleSubmitRule = async (values: any) => {
    setSubmitting(true)
    try {
      const payload: any = {
        rule_type: values.rule_type,
        is_active: values.is_active,
      }

      // 转换 ID 为 code
      if (values.rule_type === 3) {  // style_position
        const position = positions.find(p => p.id === values.position_id)
        payload.position_code = position?.code || null

        // 类型3款式是单选，转为单元素数组
        if (values.style_ids) {
          const style = styles.find(s => s.id === values.style_ids)
          payload.style_codes = style ? [style.code] : null
        } else {
          payload.style_codes = null
        }

        payload.print_codes = Array.isArray(values.print_ids)
          ? values.print_ids.map((id: number) => prints.find(p => p.id === id)?.code).filter(Boolean)
          : null
      } else if (values.rule_type === 2) {  // position_restriction
        const position = positions.find(p => p.id === values.position_id)
        payload.position_code = position?.code || null

        payload.style_codes = Array.isArray(values.style_ids)
          ? values.style_ids.map((id: number) => styles.find(s => s.id === id)?.code).filter(Boolean)
          : null

        payload.print_codes = Array.isArray(values.print_ids)
          ? values.print_ids.map((id: number) => prints.find(p => p.id === id)?.code).filter(Boolean)
          : null
      } else if (values.rule_type === 1) {  // style_ban
        // 类型1款式是单选，转为单元素数组
        if (values.style_ids) {
          const style = styles.find(s => s.id === values.style_ids)
          payload.style_codes = style ? [style.code] : null
        } else {
          payload.style_codes = null
        }
      }

      if (editingRule) {
        await updateRule(editingRule.id, payload)
        message.success('更新成功')
      } else {
        await createRule(payload)
        message.success('创建成功')
      }
      setRuleModalOpen(false)
      load()
    } catch (e: unknown) {
      message.error((e as Error).message)
    } finally {
      setSubmitting(false)
    }
  }

  // 根据规则类型动态生成列定义
  const getColumns = (): ColumnsType<StylePositionRule> => {
    const baseColumns: ColumnsType<StylePositionRule> = []

    // 款式列
    if (activeTab === 3 || activeTab === 1) {
      baseColumns.push({
        title: '款式', width: 180, ellipsis: true,
        render: (_, r) => {
          if (!r.style_ids_display) return '—'
          return r.style_ids_display
        },
      })
    }

    // 位置列
    if (activeTab === 3 || activeTab === 2) {
      baseColumns.push({
        title: '位置', width: 110,
        render: (_, r) => {
          if (!r.position_id) return '—'
          return r.position?.name ?? r.position_id
        },
      })
    }

    // 印花列（款式位置规则）
    if (activeTab === 3) {
      baseColumns.push({
        title: '印花', width: 200,
        render: (_, r) => {
          if (!r.print_ids_display) return <Tag color="blue">不限</Tag>
          const count = r.print_ids_display.split(',').length
          return (
            <Space>
              <span>共 {count} 个</span>
              <Button
                type="link"
                size="small"
                onClick={() => openViewModal('印花列表', r.print_ids_display || '')}
              >
                查看
              </Button>
            </Space>
          )
        },
      })
    }

    // 允许印花列（位置限定规则）
    if (activeTab === 2) {
      baseColumns.push({
        title: '允许印花', width: 200,
        render: (_, r) => {
          if (!r.print_ids_display) return <Tag color="blue">不限</Tag>
          const count = r.print_ids_display.split(',').length
          return (
            <Space>
              <span>共 {count} 个</span>
              <Button
                type="link"
                size="small"
                onClick={() => openViewModal('允许印花列表', r.print_ids_display || '')}
              >
                查看
              </Button>
            </Space>
          )
        },
      })
    }

    // 允许款式列（位置限定规则）
    if (activeTab === 2) {
      baseColumns.push({
        title: '允许款式', width: 200,
        render: (_, r) => {
          if (!r.style_ids_display) return <Tag color="blue">不限</Tag>
          const count = r.style_ids_display.split(',').length
          return (
            <Space>
              <span>共 {count} 个</span>
              <Button
                type="link"
                size="small"
                onClick={() => openViewModal('允许款式列表', r.style_ids_display || '')}
              >
                查看
              </Button>
            </Space>
          )
        },
      })
    }

    // 状态列
    baseColumns.push({
      title: '状态', width: 80,
      render: (_, r) => (
        <Tag color={r.is_active ? 'green' : 'default'}>
          {r.is_active ? '启用' : '禁用'}
        </Tag>
      ),
    })

    // 创建时间
    baseColumns.push({
      title: '创建时间', width: 160,
      dataIndex: 'created_at',
      render: (v) => v ? new Date(v).toLocaleString('zh-CN') : '—',
    })

    // 更新时间
    baseColumns.push({
      title: '更新时间', width: 160,
      dataIndex: 'updated_at',
      render: (v) => v ? new Date(v).toLocaleString('zh-CN') : '—',
    })

    // 操作列
    baseColumns.push({
      title: '操作', width: 120, fixed: 'right',
      render: (_, r) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => openEditRule(r)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确认删除？"
            onConfirm={() => handleDeleteRule(r.id)}
            okText="确认"
            cancelText="取消"
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    })

    return baseColumns
  }

  const renderFilters = () => {
    if (activeTab === 1) {  // style_ban
      return (
        <Select
          showSearch
          placeholder="筛选款式"
          allowClear
          style={{ width: 200 }}
          value={filterStyleId}
          onChange={setFilterStyleId}
          options={styleOptions}
          loading={styleSearching}
          onSearch={searchStyles}
          filterOption={false}
        />
      )
    }
    return (
      <>
        <Select
          showSearch
          placeholder="筛选款式"
          allowClear
          style={{ width: 200 }}
          value={filterStyleId}
          onChange={setFilterStyleId}
          options={styleOptions}
          loading={styleSearching}
          onSearch={searchStyles}
          filterOption={false}
        />
        <Select
          showSearch
          placeholder="筛选位置"
          allowClear
          style={{ width: 150 }}
          value={filterPositionId}
          onChange={setFilterPositionId}
          options={positionOptions}
          loading={positionSearching}
          onSearch={searchPositions}
          filterOption={false}
        />
        {activeTab === 2 && (  // position_restriction
          <Select
            showSearch
            placeholder="筛选印花"
            allowClear
            style={{ width: 200 }}
            value={filterPrintId}
            onChange={setFilterPrintId}
            options={printOptions}
            loading={printSearching}
            onSearch={searchPrints}
            filterOption={false}
          />
        )}
      </>
    )
  }

  return (
    <div style={{ padding: 24 }}>
      <Card title="限定规则管理">
        <Tabs
          activeKey={String(activeTab)}
          onChange={(key) => {
            setActiveTab(Number(key) as RuleType)
            setFilterStyleId(undefined)
            setFilterPositionId(undefined)
            setFilterPrintId(undefined)
          }}
          tabBarExtraContent={
            <Button type="primary" icon={<PlusOutlined />} onClick={openCreateRule}>
              新建规则
            </Button>
          }
          items={[
            {
              key: '3',
              label: '款式位置规则',
              children: (
                <>
                  <Space style={{ marginBottom: 16 }} wrap>
                    {renderFilters()}
                  </Space>
                  <Table
                    columns={getColumns()}
                    dataSource={rules}
                    rowKey="id"
                    loading={loading}
                    scroll={{ x: 1500 }}
                    pagination={{
                      current: page,
                      pageSize: pageSize,
                      total: total,
                      showSizeChanger: true,
                      pageSizeOptions: ['10', '20', '50'],
                      showTotal: (t) => `共 ${t} 条`,
                      onChange: (p, ps) => {
                        setPage(p)
                        setPageSize(ps)
                      }
                    }}
                  />
                </>
              ),
            },
            {
              key: '2',
              label: '位置限定规则',
              children: (
                <>
                  <Space style={{ marginBottom: 16 }} wrap>
                    {renderFilters()}
                  </Space>
                  <Table
                    columns={getColumns()}
                    dataSource={rules}
                    rowKey="id"
                    loading={loading}
                    scroll={{ x: 1500 }}
                    pagination={{
                      current: page,
                      pageSize: pageSize,
                      total: total,
                      showSizeChanger: true,
                      pageSizeOptions: ['10', '20', '50'],
                      showTotal: (t) => `共 ${t} 条`,
                      onChange: (p, ps) => {
                        setPage(p)
                        setPageSize(ps)
                      }
                    }}
                  />
                </>
              ),
            },
            {
              key: '1',
              label: '款式全禁规则',
              children: (
                <>
                  <Space style={{ marginBottom: 16 }} wrap>
                    {renderFilters()}
                  </Space>
                  <Table
                    columns={getColumns()}
                    dataSource={rules}
                    rowKey="id"
                    loading={loading}
                    scroll={{ x: 1500 }}
                    pagination={{
                      current: page,
                      pageSize: pageSize,
                      total: total,
                      showSizeChanger: true,
                      pageSizeOptions: ['10', '20', '50'],
                      showTotal: (t) => `共 ${t} 条`,
                      onChange: (p, ps) => {
                        setPage(p)
                        setPageSize(ps)
                      }
                    }}
                  />
                </>
              ),
            },
          ]}
        />
      </Card>

      <Modal
        title={editingRule ? '编辑规则' : '新建规则'}
        open={ruleModalOpen}
        onCancel={() => setRuleModalOpen(false)}
        onOk={() => ruleForm.submit()}
        confirmLoading={submitting}
        width={600}
      >
        <Form
          form={ruleForm}
          layout="vertical"
          onFinish={handleSubmitRule}
          style={{ marginTop: 16 }}
        >
          <Form.Item
            label="规则类型"
            name="rule_type"
            rules={[{ required: true, message: '请选择规则类型' }]}
          >
            <Select
              disabled={!!editingRule}
              onChange={(v) => setSelectedRuleType(v)}
              options={[
                { value: 3, label: '款式位置 - 限定某款式+位置允许的印花' },
                { value: 2, label: '位置限定 - 限定某位置允许的印花和款式' },
                { value: 1, label: '款式全禁 - 禁止某款式使用任何印花' },
              ]}
            />
          </Form.Item>

          {(selectedRuleType === 3 || selectedRuleType === 1) && (
            <Form.Item
              label="款式"
              name="style_ids"
              rules={[{ required: true, message: '请选择款式' }]}
            >
              <Select
                showSearch
                placeholder="选择款式"
                options={styleOptions}
                loading={styleSearching}
                onSearch={searchStyles}
                filterOption={false}
              />
            </Form.Item>
          )}

          {(selectedRuleType === 3 || selectedRuleType === 2) && (
            <Form.Item
              label="位置"
              name="position_id"
              rules={[{ required: true, message: '请选择位置' }]}
            >
              <Select
                showSearch
                placeholder="选择位置"
                options={positionOptions}
                loading={positionSearching}
                onSearch={searchPositions}
                filterOption={false}
              />
            </Form.Item>
          )}

          {selectedRuleType === 3 && (
            <Form.Item
              label="允许的印花"
              name="print_ids"
              tooltip="留空表示不限"
            >
              <Select
                mode="multiple"
                showSearch
                placeholder="选择允许的印花（留空=不限）"
                options={printOptions}
                loading={printSearching}
                onSearch={searchPrints}
                filterOption={false}
              />
            </Form.Item>
          )}

          {selectedRuleType === 2 && (
            <>
              <Form.Item
                label="允许的印花"
                name="print_ids"
                tooltip="留空表示不限"
              >
                <Select
                  mode="multiple"
                  showSearch
                  placeholder="选择允许的印花（留空=不限）"
                  options={printOptions}
                  loading={printSearching}
                  onSearch={searchPrints}
                  filterOption={false}
                />
              </Form.Item>
              <Form.Item
                label="允许的款式"
                name="style_ids"
                tooltip="留空表示不限"
              >
                <Select
                  mode="multiple"
                  showSearch
                  placeholder="选择允许的款式（留空=不限）"
                  options={styleOptions}
                  loading={styleSearching}
                  onSearch={searchStyles}
                  filterOption={false}
                />
              </Form.Item>
            </>
          )}

          <Form.Item label="状态" name="is_active" valuePropName="checked">
            <Switch checkedChildren="启用" unCheckedChildren="禁用" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 查看详情Modal */}
      <Modal
        title={viewModalTitle}
        open={viewModalOpen}
        onCancel={() => setViewModalOpen(false)}
        footer={null}
        width={600}
      >
        <Input
          placeholder="搜索..."
          value={viewModalSearch}
          onChange={(e) => {
            setViewModalSearch(e.target.value)
            setViewModalPage(1) // 搜索时重置到第一页
          }}
          style={{ marginBottom: 16 }}
          allowClear
        />
        <div style={{ marginBottom: 16 }}>
          共 {filteredViewItems.length} 条
        </div>
        <div style={{ maxHeight: 400, overflow: 'auto', marginBottom: 16 }}>
          {paginatedViewItems.length > 0 ? (
            <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
              {paginatedViewItems.map((item, idx) => (
                <li key={idx} style={{ padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
                  {item}
                </li>
              ))}
            </ul>
          ) : (
            <div style={{ textAlign: 'center', padding: 20, color: '#999' }}>
              无匹配结果
            </div>
          )}
        </div>
        <Pagination
          current={viewModalPage}
          pageSize={viewModalPageSize}
          total={filteredViewItems.length}
          showSizeChanger
          pageSizeOptions={['8', '20']}
          showTotal={(total) => `共 ${total} 条`}
          onChange={(page, pageSize) => {
            setViewModalPage(page)
            setViewModalPageSize(pageSize)
          }}
          size="small"
          style={{ textAlign: 'right' }}
        />
      </Modal>
    </div>
  )
}
