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
import { listStyles } from '../api/styles'
import { listPositions } from '../api/positions'
import { listPrints } from '../api/prints'

type RuleType = 'style_position' | 'position_restriction' | 'style_ban'

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

  const [activeTab, setActiveTab] = useState<RuleType>('style_position')
  const [filterStyleId, setFilterStyleId] = useState<number | undefined>()
  const [filterPositionId, setFilterPositionId] = useState<number | undefined>()
  const [filterPrintId, setFilterPrintId] = useState<number | undefined>()

  const [ruleModalOpen, setRuleModalOpen] = useState(false)
  const [editingRule, setEditingRule] = useState<StylePositionRule | null>(null)
  const [ruleForm] = Form.useForm()
  const [submitting, setSubmitting] = useState(false)
  const [selectedRuleType, setSelectedRuleType] = useState<RuleType>('style_position')
  const [viewModalOpen, setViewModalOpen] = useState(false)
  const [viewModalTitle, setViewModalTitle] = useState('')
  const [viewModalItems, setViewModalItems] = useState<string[]>([])
  const [viewModalSearch, setViewModalSearch] = useState('')
  const [viewModalPage, setViewModalPage] = useState(1)
  const [viewModalPageSize, setViewModalPageSize] = useState(8)

  const load = async () => {
    setLoading(true)
    try {
      const res = await listRules({
        style_id: filterStyleId,
        position_id: filterPositionId,
        print_id: filterPrintId,
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
  const printOptions = prints.map(p => ({ value: p.id, label: `${p.code} - ${p.name}` }))

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

  const openEditRule = (r: StylePositionRule) => {
    setEditingRule(r)
    setSelectedRuleType(r.rule_type)
    ruleForm.setFieldsValue({
      rule_type: r.rule_type,
      style_id: r.style_id,
      position_id: r.position_id,
      print_id: r.print_id,
      allowed_print_ids: r.allowed_print_ids ? r.allowed_print_ids.split(',').map(id => parseInt(id.trim())) : [],
      allowed_style_ids: r.allowed_style_ids ? r.allowed_style_ids.split(',').map(id => parseInt(id.trim())) : [],
      is_active: r.is_active,
      remark: r.remark,
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
        remark: values.remark,
      }

      if (values.rule_type === 'style_position') {
        payload.style_id = values.style_id
        payload.position_id = values.position_id
        payload.allowed_print_ids = Array.isArray(values.allowed_print_ids)
          ? values.allowed_print_ids.join(',')
          : null
      } else if (values.rule_type === 'position_restriction') {
        payload.position_id = values.position_id
        payload.print_id = values.print_id
        payload.allowed_style_ids = Array.isArray(values.allowed_style_ids)
          ? values.allowed_style_ids.join(',')
          : null
      } else if (values.rule_type === 'style_ban') {
        payload.style_id = values.style_id
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

  const columns: ColumnsType<StylePositionRule> = [
    {
      title: '规则类型', width: 120, fixed: 'left',
      render: (_, r) => {
        const typeMap: Record<string, { label: string; color: string }> = {
          style_position: { label: '款式位置', color: 'blue' },
          position_restriction: { label: '位置限定', color: 'green' },
          style_ban: { label: '款式全禁', color: 'red' },
        }
        const t = typeMap[r.rule_type] || { label: r.rule_type, color: 'default' }
        return <Tag color={t.color}>{t.label}</Tag>
      },
    },
    {
      title: '款式', width: 180, ellipsis: true,
      render: (_, r) => {
        if (!r.style_id) return '—'
        return r.style?.code ?? r.style_id
      },
    },
    {
      title: '位置', width: 110,
      render: (_, r) => {
        if (!r.position_id) return '—'
        return r.position?.name ?? r.position_id
      },
    },
    {
      title: '印花', width: 200,
      render: (_, r) => {
        // 款式位置规则显示限定的印花
        if (r.rule_type === 'style_position') {
          if (!r.allowed_print_ids_display) return <Tag color="blue">不限</Tag>
          const count = r.allowed_print_ids_display.split(',').length
          return (
            <Space>
              <span>共 {count} 个</span>
              <Button
                type="link"
                size="small"
                onClick={() => openViewModal('印花列表', r.allowed_print_ids_display || '')}
              >
                查看
              </Button>
            </Space>
          )
        }
        return '—'
      },
    },
    {
      title: '允许印花', width: 200,
      render: (_, r) => {
        // 位置限定规则显示允许的印花
        if (r.rule_type === 'position_restriction') {
          if (!r.allowed_print_ids_display) return <Tag color="blue">不限</Tag>
          const count = r.allowed_print_ids_display.split(',').length
          return (
            <Space>
              <span>共 {count} 个</span>
              <Button
                type="link"
                size="small"
                onClick={() => openViewModal('允许印花列表', r.allowed_print_ids_display || '')}
              >
                查看
              </Button>
            </Space>
          )
        }
        return '—'
      },
    },
    {
      title: '允许款式', width: 200,
      render: (_, r) => {
        // 位置限定规则显示允许的款式
        if (r.rule_type === 'position_restriction') {
          if (!r.allowed_style_ids_display) return <Tag color="blue">不限</Tag>
          const count = r.allowed_style_ids_display.split(',').length
          return (
            <Space>
              <span>共 {count} 个</span>
              <Button
                type="link"
                size="small"
                onClick={() => openViewModal('允许款式列表', r.allowed_style_ids_display || '')}
              >
                查看
              </Button>
            </Space>
          )
        }
        return '—'
      },
    },
    {
      title: '状态', width: 80,
      render: (_, r) => (
        <Tag color={r.is_active ? 'green' : 'default'}>
          {r.is_active ? '启用' : '禁用'}
        </Tag>
      ),
    },
    {
      title: '备注', width: 150, ellipsis: true,
      dataIndex: 'remark',
      render: (v) => v || '—',
    },
    {
      title: '创建时间', width: 160,
      dataIndex: 'created_at',
      render: (v) => v ? new Date(v).toLocaleString('zh-CN') : '—',
    },
    {
      title: '更新时间', width: 160,
      dataIndex: 'updated_at',
      render: (v) => v ? new Date(v).toLocaleString('zh-CN') : '—',
    },
    {
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
    },
  ]

  const renderFilters = () => {
    if (activeTab === 'style_ban') {
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
        {activeTab === 'position_restriction' && (
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
          activeKey={activeTab}
          onChange={(key) => {
            setActiveTab(key as RuleType)
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
              key: 'style_position',
              label: '款式位置规则',
              children: (
                <>
                  <Space style={{ marginBottom: 16 }} wrap>
                    {renderFilters()}
                  </Space>
                  <Table
                    columns={columns}
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
              key: 'position_restriction',
              label: '位置限定规则',
              children: (
                <>
                  <Space style={{ marginBottom: 16 }} wrap>
                    {renderFilters()}
                  </Space>
                  <Table
                    columns={columns}
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
              key: 'style_ban',
              label: '款式全禁规则',
              children: (
                <>
                  <Space style={{ marginBottom: 16 }} wrap>
                    {renderFilters()}
                  </Space>
                  <Table
                    columns={columns}
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
                { value: 'style_position', label: '款式位置 - 限定某款式+位置允许的印花' },
                { value: 'position_restriction', label: '位置限定 - 限定某位置+印花允许的款式' },
                { value: 'style_ban', label: '款式全禁 - 禁止某款式使用任何印花' },
              ]}
            />
          </Form.Item>

          {(selectedRuleType === 'style_position' || selectedRuleType === 'style_ban') && (
            <Form.Item
              label="款式"
              name="style_id"
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

          {(selectedRuleType === 'style_position' || selectedRuleType === 'position_restriction') && (
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

          {selectedRuleType === 'position_restriction' && (
            <Form.Item
              label="印花"
              name="print_id"
              rules={[{ required: true, message: '请选择印花' }]}
            >
              <Select
                showSearch
                placeholder="选择印花"
                options={printOptions}
                loading={printSearching}
                onSearch={searchPrints}
                filterOption={false}
              />
            </Form.Item>
          )}

          {selectedRuleType === 'style_position' && (
            <Form.Item
              label="允许的印花"
              name="allowed_print_ids"
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

          {selectedRuleType === 'position_restriction' && (
            <Form.Item
              label="允许的款式"
              name="allowed_style_ids"
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
          )}

          <Form.Item label="状态" name="is_active" valuePropName="checked">
            <Switch checkedChildren="启用" unCheckedChildren="禁用" />
          </Form.Item>

          <Form.Item label="备注" name="remark">
            <Input.TextArea rows={3} placeholder="可选" />
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
