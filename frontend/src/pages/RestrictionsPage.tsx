import { useEffect, useState } from 'react'
import {
  Table, Button, Modal, Form, Input, Switch, Popconfirm,
  Space, Tag, message, Card, Tooltip, Typography, Select,
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

const { Text } = Typography

// ── 工具函数 ─────────────────────────────────────────────────

function AllowedPrintsCell({ prints }: { prints: string | null | undefined }) {
  if (!prints) return <Tag color="blue">不限</Tag>
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

function AllowedStylesCell({ styleIds }: { styleIds: string | null | undefined }) {
  if (!styleIds) return <Tag color="blue">不限</Tag>
  const list = styleIds.split(',').filter(Boolean)
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

function AllowedCombosCell({ combos }: { combos: string | null | undefined }) {
  if (!combos) return <Tag color="blue">不限</Tag>
  const list = combos.split(',').filter(Boolean)
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

// ── 主页面 ────────────────────────────────────────────────────

export default function RestrictionsPage() {
  const [rules, setRules] = useState<StylePositionRule[]>([])
  const [loading, setLoading] = useState(false)
  const [styles, setStyles] = useState<Style[]>([])
  const [positions, setPositions] = useState<Position[]>([])
  const [prints, setPrints] = useState<Print[]>([])

  // 过滤状态
  const [filterStyleId, setFilterStyleId] = useState<number | undefined>()
  const [filterPositionId, setFilterPositionId] = useState<number | undefined>()
  const [filterPrintCode, setFilterPrintCode] = useState<string | undefined>()

  // 规则弹窗
  const [ruleModalOpen, setRuleModalOpen] = useState(false)
  const [editingRule, setEditingRule] = useState<StylePositionRule | null>(null)
  const [ruleForm] = Form.useForm()
  const [submitting, setSubmitting] = useState(false)

  // 当前选择的规则类型
  const [selectedRuleType, setSelectedRuleType] = useState<string>('style_position')

  const load = async (sId?: number, pId?: number, pc?: string) => {
    setLoading(true)
    try {
      const r = await listRules({ style_id: sId, position_id: pId, print_code: pc || undefined })
      setRules(r)
    } catch (e: unknown) {
      message.error((e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    Promise.all([
      listStyles('', 5000),
      listPositions(),
      listPrints('', 5000)
    ]).then(([s, p, pr]) => {
      setStyles(s)
      setPositions(p)
      setPrints(pr)
    })
    load()
  }, [])

  // 下拉选项
  const styleOptions = styles.map(s => ({
    value: s.id,
    label: styleLabel(s),
    searchText: [s.code, s.attr, s.product_code, s.product_category].filter(Boolean).join(' '),
  }))
  const positionOptions = positions.map(p => ({ value: p.id, label: p.name }))
  const printOptions = prints.map(p => ({ value: p.code, label: `${p.code} - ${p.name}` }))

  const filterStyleOption = (input: string, option?: { label: string; value: number; searchText?: string }) => {
    const q = input.toLowerCase()
    return (option?.searchText ?? option?.label ?? '').toLowerCase().includes(q)
  }
  const filterPositionOption = (input: string, option?: { label: string; value: number }) =>
    (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
  const filterPrintOption = (input: string, option?: { label: string; value: string }) =>
    (option?.label ?? '').toLowerCase().includes(input.toLowerCase())

  // ── 规则操作 ──

  const openCreateRule = () => {
    setEditingRule(null)
    ruleForm.resetFields()
    ruleForm.setFieldsValue({ rule_type: 'style_position', is_active: true })
    setSelectedRuleType('style_position')
    setRuleModalOpen(true)
  }

  const openEditRule = (r: StylePositionRule) => {
    setEditingRule(r)
    setSelectedRuleType(r.rule_type)
    ruleForm.setFieldsValue({
      rule_type: r.rule_type,
      style_id: r.style_id,
      position_id: r.position_id,
      print_code: r.print_code,
      allowed_prints: r.allowed_prints ?? '',
      allowed_styles: r.allowed_styles ?? '',
      allowed_style_positions: r.allowed_style_positions ?? '',
      is_active: r.is_active,
      remark: r.remark,
    })
    setRuleModalOpen(true)
  }

  const handleDeleteRule = async (id: number) => {
    try {
      await deleteRule(id)
      message.success('删除成功')
      load(filterStyleId, filterPositionId, filterPrintCode)
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

      // 根据规则类型填充对应字段
      if (values.rule_type === 'style_position') {
        payload.style_id = values.style_id
        payload.position_id = values.position_id
        payload.allowed_prints = values.allowed_prints?.trim() || null
      } else if (values.rule_type === 'position_print') {
        payload.position_id = values.position_id
        payload.print_code = values.print_code
        payload.allowed_styles = values.allowed_styles?.trim() || null
      } else if (values.rule_type === 'print_restriction') {
        payload.print_code = values.print_code
        payload.allowed_style_positions = values.allowed_style_positions?.trim() || null
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
      load(filterStyleId, filterPositionId, filterPrintCode)
    } catch (e: unknown) {
      message.error((e as Error).message)
    } finally {
      setSubmitting(false)
    }
  }

  // ── 表格列 ──

  const columns: ColumnsType<StylePositionRule> = [
    {
      title: '规则类型', width: 120, fixed: 'left',
      render: (_, r) => {
        const typeMap = {
          style_position: { label: '款式位置', color: 'blue' },
          position_print: { label: '位置印花', color: 'green' },
          print_restriction: { label: '印花限定', color: 'orange' },
          style_ban: { label: '款式全禁', color: 'red' },
        }
        const t = typeMap[r.rule_type] || { label: r.rule_type, color: 'default' }
        return <Tag color={t.color}>{t.label}</Tag>
      },
    },
    {
      title: '款式', width: 180, ellipsis: true,
      render: (_, r) => {
        if (!r.style_id) return <Text type="secondary">—</Text>
        return r.style ? styleLabel(r.style) : r.style_id
      },
    },
    {
      title: '位置', width: 110,
      render: (_, r) => {
        if (!r.position_id) return <Text type="secondary">—</Text>
        return r.position?.name ?? r.position_id
      },
    },
    {
      title: '印花', width: 120,
      render: (_, r) => {
        if (!r.print_code) return <Text type="secondary">—</Text>
        return r.print_code
      },
    },
    {
      title: '允许印花', width: 200,
      render: (_, r) => {
        if (r.rule_type !== 'style_position') return <Text type="secondary">—</Text>
        return <AllowedPrintsCell prints={r.allowed_prints} />
      },
    },
    {
      title: '允许款式', width: 200,
      render: (_, r) => {
        if (r.rule_type !== 'position_print') return <Text type="secondary">—</Text>
        return <AllowedStylesCell styleIds={r.allowed_styles} />
      },
    },
    {
      title: '允许组合', width: 200,
      render: (_, r) => {
        if (r.rule_type !== 'print_restriction') return <Text type="secondary">—</Text>
        return <AllowedCombosCell combos={r.allowed_style_positions_display || r.allowed_style_positions} />
      },
    },
    {
      title: '创建时间', width: 160,
      render: (_, r) => {
        if (!r.created_at) return null
        return new Date(r.created_at).toLocaleString('zh-CN', { hour12: false })
      },
    },
    {
      title: '备注', ellipsis: true,
      render: (_, r) => r.remark,
    },
    {
      title: '状态', width: 80,
      render: (_, r) => {
        if (r.rule_type === 'style_ban') return null
        return <Tag color={r.is_active ? 'green' : 'red'}>{r.is_active ? '启用' : '停用'}</Tag>
      },
    },
    {
      title: '操作', width: 100, fixed: 'right',
      render: (_, r) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => openEditRule(r)} />
          <Popconfirm title="确认删除？" onConfirm={() => handleDeleteRule(r.id)}>
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ]

  function getEmptyText(): string {
    const hasStyle = filterStyleId !== undefined
    const hasPosition = filterPositionId !== undefined
    const hasPrint = !!filterPrintCode

    if (hasStyle && hasPosition && hasPrint) return '该款式在此位置无包含该印花的限定规则'
    if (hasStyle && hasPosition) return '该款式在此位置暂无限定规则'
    if (hasStyle && hasPrint) return '该款式无包含该印花的限定规则'
    if (hasPosition && hasPrint) return '该位置无包含该印花的限定规则'
    if (hasStyle) return '该款式暂无任何限定'
    if (hasPosition) return '该位置暂无限定规则'
    if (hasPrint) return '未找到与该印花相关的限定规则'
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
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreateRule}>新建规则</Button>
      </Space>

      <Table
        rowKey="id"
        columns={columns}
        dataSource={rules}
        loading={loading}
        pagination={{
          defaultPageSize: 20,
          showSizeChanger: true,
          pageSizeOptions: [10, 20, 50, 100],
          showTotal: t => `共 ${t} 条`,
        }}
        scroll={{ x: 1400 }}
        size="small"
        locale={{ emptyText: getEmptyText() }}
      />

      {/* 规则弹窗 */}
      <Modal
        title={editingRule ? '编辑规则' : '新建规则'}
        open={ruleModalOpen}
        onCancel={() => setRuleModalOpen(false)}
        onOk={() => ruleForm.submit()}
        confirmLoading={submitting}
        destroyOnClose
        width={600}
      >
        <Form form={ruleForm} layout="vertical" onFinish={handleSubmitRule} style={{ marginTop: 8 }}>
          <Form.Item name="rule_type" label="规则类型" rules={[{ required: true }]}>
            <Select
              disabled={!!editingRule}
              onChange={v => setSelectedRuleType(v)}
              options={[
                { value: 'style_position', label: '款式位置规则（款式+位置→印花白名单）' },
                { value: 'position_print', label: '位置印花规则（位置+印花→款式白名单）' },
                { value: 'print_restriction', label: '印花限定规则（印花→款式位置组合白名单）' },
                { value: 'style_ban', label: '款式全禁' },
              ]}
            />
          </Form.Item>

          {/* style_position 字段 */}
          {selectedRuleType === 'style_position' && (
            <>
              <Form.Item name="style_id" label="款式" rules={[{ required: true, message: '请选择款式' }]}>
                <Select
                  disabled={!!editingRule}
                  showSearch
                  options={styleOptions}
                  filterOption={filterStyleOption}
                  placeholder="选择款式"
                />
              </Form.Item>
              <Form.Item name="position_id" label="位置" rules={[{ required: true, message: '请选择位置' }]}>
                <Select
                  disabled={!!editingRule}
                  showSearch
                  options={positionOptions}
                  filterOption={filterPositionOption}
                  placeholder="选择位置"
                />
              </Form.Item>
              <Form.Item
                name="allowed_prints"
                label="允许印花编码（留空 = 该位置不限印花）"
                extra="多个编码用英文逗号分隔"
              >
                <Input.TextArea rows={3} placeholder="爱艺心X,爱心蓝X,花语口袋X" />
              </Form.Item>
            </>
          )}

          {/* position_print 字段 */}
          {selectedRuleType === 'position_print' && (
            <>
              <Form.Item name="position_id" label="位置" rules={[{ required: true, message: '请选择位置' }]}>
                <Select
                  disabled={!!editingRule}
                  showSearch
                  options={positionOptions}
                  filterOption={filterPositionOption}
                  placeholder="选择位置"
                />
              </Form.Item>
              <Form.Item name="print_code" label="印花编码" rules={[{ required: true, message: '请选择印花' }]}>
                <Select
                  disabled={!!editingRule}
                  showSearch
                  options={printOptions}
                  filterOption={filterPrintOption}
                  placeholder="选择印花"
                />
              </Form.Item>
              <Form.Item
                name="allowed_styles"
                label="允许款式ID（留空 = 不限款式）"
                extra="多个ID用英文逗号分隔，如：1,2,3"
              >
                <Input.TextArea rows={3} placeholder="1,2,3,4,5" />
              </Form.Item>
            </>
          )}

          {/* print_restriction 字段 */}
          {selectedRuleType === 'print_restriction' && (
            <>
              <Form.Item name="print_code" label="印花编码" rules={[{ required: true, message: '请选择印花' }]}>
                <Select
                  disabled={!!editingRule}
                  showSearch
                  options={printOptions}
                  filterOption={filterPrintOption}
                  placeholder="选择印花"
                />
              </Form.Item>
              <Form.Item
                name="allowed_style_positions"
                label="允许款式位置组合"
                extra="格式：款式ID:位置ID,款式ID:位置ID，如：1:2,3:4"
                rules={[{ required: true, message: '请输入允许的款式位置组合' }]}
              >
                <Input.TextArea rows={3} placeholder="1:2,3:4,5:6" />
              </Form.Item>
            </>
          )}

          {/* style_ban 字段 */}
          {selectedRuleType === 'style_ban' && (
            <Form.Item name="style_id" label="款式" rules={[{ required: true, message: '请选择款式' }]}>
              <Select
                disabled={!!editingRule}
                showSearch
                options={styleOptions}
                filterOption={filterStyleOption}
                placeholder="选择款式"
              />
            </Form.Item>
          )}

          <Form.Item name="remark" label="备注">
            <Input.TextArea rows={2} />
          </Form.Item>

          {selectedRuleType !== 'style_ban' && (
            <Form.Item name="is_active" label="状态" valuePropName="checked">
              <Switch checkedChildren="启用" unCheckedChildren="停用" />
            </Form.Item>
          )}
        </Form>
      </Modal>
    </Card>
  )
}
