import { useEffect, useState } from 'react'
import {
  Table, Button, Modal, Form, Input, Switch, Popconfirm,
  Space, Tag, message, Card, Tooltip, Typography, Select,
} from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import type { StylePositionRule, StyleBan, Style, Position } from '../types'
import {
  listRules, createRule, updateRule, deleteRule,
  listBans, createBan, updateBan, deleteBan,
} from '../api/restrictions'
import { listStyles } from '../api/styles'
import { listPositions } from '../api/positions'

const { Text } = Typography

// ── 工具 ─────────────────────────────────────────────────

function AllowedPrintsCell({ prints }: { prints: string | null }) {
  if (prints === null) return <Tag color="blue">不限</Tag>
  const list = prints.split(',').filter(Boolean)
  if (list.length === 0) return <Tag color="blue">不限</Tag>
  const preview = list.slice(0, 3).join('、')
  return (
    <Tooltip title={<div style={{ maxWidth: 360, wordBreak: 'break-all' }}>{list.join('、')}</div>}>
      <span style={{ cursor: 'default' }}>
        {preview}
        {list.length > 3 && <Text type="secondary" style={{ fontSize: 12 }}> …共 {list.length} 个</Text>}
      </span>
    </Tooltip>
  )
}

function styleLabel(s: Style) { return s.code }

// ── 联合行类型 ────────────────────────────────────────────

type AnyRow =
  | { _type: 'ban';  key: string; data: StyleBan }
  | { _type: 'rule'; key: string; data: StylePositionRule }

// ── 主页面 ────────────────────────────────────────────────

export default function RestrictionsPage() {
  const [rules, setRules] = useState<StylePositionRule[]>([])
  const [bans, setBans] = useState<StyleBan[]>([])
  const [loading, setLoading] = useState(false)
  const [styles, setStyles] = useState<Style[]>([])
  const [positions, setPositions] = useState<Position[]>([])

  // 过滤状态
  const [filterStyleId, setFilterStyleId] = useState<number | undefined>()
  const [filterPositionId, setFilterPositionId] = useState<number | undefined>()
  const [filterPrintCode, setFilterPrintCode] = useState<string | undefined>()

  // 位置规则弹窗
  const [ruleModalOpen, setRuleModalOpen] = useState(false)
  const [editingRule, setEditingRule] = useState<StylePositionRule | null>(null)
  const [ruleForm] = Form.useForm()

  // 全禁弹窗
  const [banModalOpen, setBanModalOpen] = useState(false)
  const [editingBan, setEditingBan] = useState<StyleBan | null>(null)
  const [banForm] = Form.useForm()

  const [submitting, setSubmitting] = useState(false)

  // load 始终接收显式参数，避免 stale closure 问题
  const load = async (sId?: number, pId?: number, pc?: string) => {
    setLoading(true)
    try {
      const [r, b] = await Promise.all([
        listRules({ style_id: sId, position_id: pId, print_code: pc || undefined }),
        listBans(),   // 全量加载，前端按 style_id 过滤
      ])
      setRules(r)
      setBans(b)
    } catch (e: unknown) {
      message.error((e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    Promise.all([listStyles('', 5000), listPositions()]).then(([s, p]) => { setStyles(s); setPositions(p) })
    load()
  }, [])

  // 下拉选项（styleOptions 附加搜索文本，支持按 code/attr/product_code/product_category 搜索）
  const styleOptions = styles.map(s => ({
    value: s.id,
    label: styleLabel(s),
    searchText: [s.code, s.attr, s.product_code, s.product_category].filter(Boolean).join(' '),
  }))
  const positionOptions = positions.map(p => ({ value: p.id, label: p.name }))
  const filterStyleOption = (input: string, option?: { label: string; value: number; searchText?: string }) => {
    const q = input.toLowerCase()
    return (option?.searchText ?? option?.label ?? '').toLowerCase().includes(q)
  }
  const filterPositionOption = (input: string, option?: { label: string; value: number }) =>
    (option?.label ?? '').toLowerCase().includes(input.toLowerCase())

  // 全禁行：有位置或印花过滤时隐藏（全禁无位置概念）；仅按款式过滤时前端筛选
  const showBans = filterPositionId === undefined && filterPrintCode === undefined
  const filteredBans = showBans
    ? (filterStyleId !== undefined ? bans.filter(b => b.style_id === filterStyleId) : bans)
    : []

  const allRows: AnyRow[] = [
    ...filteredBans.map(b => ({ _type: 'ban'  as const, key: `ban-${b.id}`,  data: b })),
    ...rules.map(r =>        ({ _type: 'rule' as const, key: `rule-${r.id}`, data: r })),
  ]

  // ── 位置规则操作 ──

  const openCreateRule = () => {
    setEditingRule(null)
    ruleForm.resetFields()
    ruleForm.setFieldsValue({ is_active: true })
    setRuleModalOpen(true)
  }

  const openEditRule = (r: StylePositionRule) => {
    setEditingRule(r)
    ruleForm.setFieldsValue({
      allowed_prints: r.allowed_prints ?? '',
      is_active: r.is_active,
      remark: r.remark,
    })
    setRuleModalOpen(true)
  }

  const handleDeleteRule = async (id: number) => {
    try { await deleteRule(id); message.success('删除成功'); load(filterStyleId, filterPositionId, filterPrintCode) }
    catch (e: unknown) { message.error((e as Error).message) }
  }

  const handleSubmitRule = async (values: {
    style_id?: number; position_id?: number; allowed_prints?: string; is_active: boolean; remark?: string
  }) => {
    setSubmitting(true)
    try {
      const allowed = values.allowed_prints?.trim() || null
      if (editingRule) {
        await updateRule(editingRule.id, { allowed_prints: allowed, is_active: values.is_active, remark: values.remark })
        message.success('更新成功')
      } else {
        await createRule({
          style_id: values.style_id!,
          position_id: values.position_id!,
          allowed_prints: allowed,
          is_active: values.is_active,
          remark: values.remark,
        })
        message.success('创建成功')
      }
      setRuleModalOpen(false)
      load(filterStyleId, filterPositionId, filterPrintCode)
    } catch (e: unknown) {
      message.error((e as Error).message)
    } finally {
      setSubmitting(false)
    }
  }

  // ── 全禁操作 ──

  const openCreateBan = () => {
    setEditingBan(null)
    banForm.resetFields()
    setBanModalOpen(true)
  }

  const openEditBan = (b: StyleBan) => {
    setEditingBan(b)
    banForm.setFieldsValue({ remark: b.remark })
    setBanModalOpen(true)
  }

  const handleDeleteBan = async (id: number) => {
    try { await deleteBan(id); message.success('删除成功'); load(filterStyleId, filterPositionId, filterPrintCode) }
    catch (e: unknown) { message.error((e as Error).message) }
  }

  const handleSubmitBan = async (values: { style_id?: number; remark?: string }) => {
    setSubmitting(true)
    try {
      if (editingBan) {
        await updateBan(editingBan.id, { remark: values.remark })
        message.success('更新成功')
      } else {
        await createBan({ style_id: values.style_id!, remark: values.remark })
        message.success('创建成功')
      }
      setBanModalOpen(false)
      load(filterStyleId, filterPositionId, filterPrintCode)
    } catch (e: unknown) {
      message.error((e as Error).message)
    } finally {
      setSubmitting(false)
    }
  }

  // ── 表格列 ──

  const columns: ColumnsType<AnyRow> = [
    {
      title: '款式', width: 180, ellipsis: true, fixed: 'left',
      render: (_, row) => {
        const style = row.data.style
        return style ? styleLabel(style) : row.data.style_id
      },
    },
    {
      title: '类型', width: 90,
      render: (_, row) => row._type === 'ban'
        ? <Tag color="red">全禁</Tag>
        : <Tag color="geekblue">位置规则</Tag>,
    },
    {
      title: '位置', width: 110,
      render: (_, row) => {
        if (row._type === 'ban') return <Text type="secondary">—</Text>
        return row.data.position?.name ?? row.data.position_id
      },
    },
    {
      title: '允许印花', width: 300,
      render: (_, row) => {
        if (row._type === 'ban') return <Text type="secondary">—</Text>
        return <AllowedPrintsCell prints={row.data.allowed_prints} />
      },
    },
    {
      title: '创建时间', width: 160,
      render: (_, row) => {
        const v = row.data.created_at
        if (!v) return null
        return new Date(v).toLocaleString('zh-CN', { hour12: false })
      },
    },
    {
      title: '备注', ellipsis: true,
      render: (_, row) => row.data.remark,
    },
    {
      title: '状态', width: 80,
      render: (_, row) => {
        if (row._type === 'ban') return null
        const v = row.data.is_active
        return <Tag color={v ? 'green' : 'red'}>{v ? '启用' : '停用'}</Tag>
      },
    },
    {
      title: '操作', width: 100, fixed: 'right',
      render: (_, row) => (
        <Space>
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => row._type === 'rule' ? openEditRule(row.data) : openEditBan(row.data)}
          />
          <Popconfirm
            title="确认删除？"
            onConfirm={() => row._type === 'rule' ? handleDeleteRule(row.data.id) : handleDeleteBan(row.data.id)}
          >
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ]

  // 当前选中款式是否已在全禁列表中
  const selectedStyleBanned = filterStyleId !== undefined && bans.some(b => b.style_id === filterStyleId)

  const hasStyle    = filterStyleId    !== undefined
  const hasPosition = filterPositionId !== undefined
  const hasPrint    = !!filterPrintCode

  function getEmptyText(): string {
    // 款式已全禁，但因附加了位置/印花过滤，全禁行被隐藏——需要特别说明
    if (selectedStyleBanned && (hasPosition || hasPrint)) {
      return '该款式已全禁，任何位置均不可贴图'
    }
    if (hasStyle && hasPosition && hasPrint) return '该款式在此位置无包含该印花的限定规则'
    if (hasStyle && hasPosition)             return '该款式在此位置暂无限定规则'
    if (hasStyle && hasPrint)                return '该款式无包含该印花的限定规则'
    if (hasPosition && hasPrint)             return '该位置无包含该印花的限定规则'
    if (hasStyle)                            return '该款式暂无任何限定，配所有印花'
    if (hasPosition)                         return '该位置暂无限定规则'
    if (hasPrint)                            return '未找到与该印花相关的限定规则'
    return '暂无限定数据'
  }

  return (
    <Card title="限定管理">
      <Space style={{ marginBottom: 12 }} wrap>
        <Select
          placeholder="按款式过滤"
          allowClear
          showSearch
          style={{ width: 220 }}
          options={styleOptions}
          filterOption={filterStyleOption}
          onChange={v => { setFilterStyleId(v); load(v, filterPositionId, filterPrintCode) }}
        />
        <Select
          placeholder="按位置过滤"
          allowClear
          showSearch
          style={{ width: 150 }}
          options={positionOptions}
          filterOption={filterPositionOption}
          onChange={v => { setFilterPositionId(v); load(filterStyleId, v, filterPrintCode) }}
        />
        <Input.Search
          placeholder="按印花编码搜索"
          allowClear
          style={{ width: 180 }}
          onSearch={v => { setFilterPrintCode(v); load(filterStyleId, filterPositionId, v) }}
          onChange={e => {
            if (!e.target.value) { setFilterPrintCode(undefined); load(filterStyleId, filterPositionId, undefined) }
          }}
        />
        <Button icon={<PlusOutlined />} onClick={openCreateRule}>新建位置规则</Button>
        <Button icon={<PlusOutlined />} danger onClick={openCreateBan}>新建全禁</Button>
      </Space>

      <Table
        rowKey="key"
        columns={columns}
        dataSource={allRows}
        loading={loading}
        pagination={{
          defaultPageSize: 20,
          showSizeChanger: true,
          pageSizeOptions: [10, 20, 50, 100],
          showTotal: t => `共 ${t} 条`,
        }}
        scroll={{ x: 900 }}
        size="small"
        locale={{ emptyText: getEmptyText() }}
      />

      {/* 位置规则弹窗 */}
      <Modal
        title={editingRule ? '编辑位置规则' : '新建位置规则'}
        open={ruleModalOpen}
        onCancel={() => setRuleModalOpen(false)}
        onOk={() => ruleForm.submit()}
        confirmLoading={submitting}
        destroyOnClose
        width={560}
      >
        <Form form={ruleForm} layout="vertical" onFinish={handleSubmitRule} style={{ marginTop: 8 }}>
          {editingRule ? (
            <>
              <Form.Item label="款式">
                <Text code>{editingRule.style ? styleLabel(editingRule.style) : editingRule.style_id}</Text>
              </Form.Item>
              <Form.Item label="位置">
                <Text code>{editingRule.position?.name ?? editingRule.position_id}</Text>
              </Form.Item>
            </>
          ) : (
            <>
              <Form.Item name="style_id" label="款式" rules={[{ required: true, message: '请选择款式' }]}>
                <Select showSearch options={styleOptions} filterOption={filterStyleOption} placeholder="选择款式" />
              </Form.Item>
              <Form.Item name="position_id" label="位置" rules={[{ required: true, message: '请选择位置' }]}>
                <Select showSearch options={positionOptions} filterOption={filterPositionOption} placeholder="选择位置" />
              </Form.Item>
            </>
          )}
          <Form.Item
            name="allowed_prints"
            label="允许印花编码（留空 = 该位置不限印花）"
            extra="多个编码用英文逗号分隔"
          >
            <Input.TextArea rows={3} placeholder="爱艺心X,爱心蓝X,花语口袋X" />
          </Form.Item>
          <Form.Item name="remark" label="备注">
            <Input.TextArea rows={2} />
          </Form.Item>
          <Form.Item name="is_active" label="状态" valuePropName="checked">
            <Switch checkedChildren="启用" unCheckedChildren="停用" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 全禁弹窗 */}
      <Modal
        title={editingBan ? '编辑全禁记录' : '新建全禁记录'}
        open={banModalOpen}
        onCancel={() => setBanModalOpen(false)}
        onOk={() => banForm.submit()}
        confirmLoading={submitting}
        destroyOnClose
      >
        <Form form={banForm} layout="vertical" onFinish={handleSubmitBan} style={{ marginTop: 8 }}>
          {editingBan ? (
            <Form.Item label="款式">
              <Text code>{editingBan.style ? styleLabel(editingBan.style) : editingBan.style_id}</Text>
            </Form.Item>
          ) : (
            <Form.Item name="style_id" label="款式" rules={[{ required: true, message: '请选择款式' }]}>
              <Select showSearch options={styleOptions} filterOption={filterStyleOption} placeholder="选择款式" />
            </Form.Item>
          )}
          <Form.Item name="remark" label="备注">
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}
