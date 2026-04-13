import { useEffect, useState } from 'react'
import {
  Table, Button, Modal, Form, Input, Switch, Popconfirm,
  Space, Tag, message, Card, Select, Typography, Row, Col,
} from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import type { Restriction, Style, Print, Position } from '../types'
import { listRestrictions, createRestriction, updateRestriction, deleteRestriction } from '../api/restrictions'
import { listStyles } from '../api/styles'
import { listPrints } from '../api/prints'
import { listPositions } from '../api/positions'

const { Text } = Typography

export default function RestrictionsPage() {
  const [data, setData] = useState<Restriction[]>([])
  const [loading, setLoading] = useState(false)
  const [styles, setStyles] = useState<Style[]>([])
  const [prints, setPrints] = useState<Print[]>([])
  const [positions, setPositions] = useState<Position[]>([])
  const [filterStyleId, setFilterStyleId] = useState<number | undefined>()
  const [filterPositionId, setFilterPositionId] = useState<number | undefined>()
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Restriction | null>(null)
  const [form] = Form.useForm()
  const [submitting, setSubmitting] = useState(false)

  const loadMeta = async () => {
    const [s, p, pos] = await Promise.all([listStyles(), listPrints(), listPositions()])
    setStyles(s)
    setPrints(p)
    setPositions(pos)
  }

  const load = async (styleId = filterStyleId, positionId = filterPositionId) => {
    setLoading(true)
    try {
      setData(await listRestrictions({ style_id: styleId, position_id: positionId }))
    } catch (e: unknown) {
      message.error((e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadMeta()
    load()
  }, [])

  const openCreate = () => {
    setEditing(null)
    form.resetFields()
    form.setFieldsValue({ is_active: true })
    setModalOpen(true)
  }

  const openEdit = (record: Restriction) => {
    setEditing(record)
    form.setFieldsValue({ is_active: record.is_active, remark: record.remark })
    setModalOpen(true)
  }

  const handleDelete = async (id: number) => {
    try {
      await deleteRestriction(id)
      message.success('删除成功')
      load()
    } catch (e: unknown) {
      message.error((e as Error).message)
    }
  }

  const handleSubmit = async (values: { style_id?: number; position_id?: number; print_id?: number; is_active: boolean; remark?: string }) => {
    setSubmitting(true)
    try {
      if (editing) {
        await updateRestriction(editing.id, { is_active: values.is_active, remark: values.remark })
        message.success('更新成功')
      } else {
        await createRestriction({
          style_id: values.style_id!,
          position_id: values.position_id!,
          print_id: values.print_id!,
          is_active: values.is_active,
          remark: values.remark,
        })
        message.success('创建成功')
      }
      setModalOpen(false)
      load()
    } catch (e: unknown) {
      message.error((e as Error).message)
    } finally {
      setSubmitting(false)
    }
  }

  const filterOption = (input: string, option?: { label: string; value: number }) =>
    (option?.label ?? '').toLowerCase().includes(input.toLowerCase())

  const styleOptions = styles.map(s => ({ value: s.id, label: `${s.code} ${s.name}` }))
  const printOptions = prints.map(p => ({ value: p.id, label: `${p.code} ${p.name}` }))
  const positionOptions = positions.map(p => ({ value: p.id, label: `${p.code} ${p.name}` }))

  const columns: ColumnsType<Restriction> = [
    {
      title: '款式', width: 160,
      render: (_: unknown, r: Restriction) => r.style ? `${r.style.code} ${r.style.name}` : r.style_id,
    },
    {
      title: '位置', width: 160,
      render: (_: unknown, r: Restriction) => r.position ? `${r.position.code} ${r.position.name}` : r.position_id,
    },
    {
      title: '印花', width: 160,
      render: (_: unknown, r: Restriction) => r.print_item ? `${r.print_item.code} ${r.print_item.name}` : r.print_id,
    },
    { title: '备注', dataIndex: 'remark', ellipsis: true },
    {
      title: '状态', dataIndex: 'is_active', width: 80,
      render: (v: boolean) => <Tag color={v ? 'green' : 'red'}>{v ? '启用' : '停用'}</Tag>,
    },
    {
      title: '操作', width: 120, fixed: 'right',
      render: (_: unknown, record: Restriction) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(record)} />
          <Popconfirm title="确认删除？" onConfirm={() => handleDelete(record.id)}>
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <Card
      title="限定管理"
      extra={<Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>新建限定</Button>}
    >
      <Row gutter={12} style={{ marginBottom: 16 }}>
        <Col>
          <Select
            placeholder="按款式过滤"
            allowClear
            showSearch
            style={{ width: 200 }}
            options={styleOptions}
            filterOption={filterOption}
            onChange={v => { setFilterStyleId(v); load(v, filterPositionId) }}
          />
        </Col>
        <Col>
          <Select
            placeholder="按位置过滤"
            allowClear
            showSearch
            style={{ width: 200 }}
            options={positionOptions}
            filterOption={filterOption}
            onChange={v => { setFilterPositionId(v); load(filterStyleId, v) }}
          />
        </Col>
      </Row>

      <Table
        rowKey="id"
        columns={columns}
        dataSource={data}
        loading={loading}
        pagination={{ pageSize: 20, showTotal: t => `共 ${t} 条` }}
        scroll={{ x: 800 }}
        size="small"
      />

      <Modal
        title={editing ? '编辑限定' : '新建限定'}
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={submitting}
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit} style={{ marginTop: 12 }}>
          {editing ? (
            <>
              <Form.Item label="款式">
                <Text>{editing.style ? `${editing.style.code} ${editing.style.name}` : editing.style_id}</Text>
              </Form.Item>
              <Form.Item label="位置">
                <Text>{editing.position ? `${editing.position.code} ${editing.position.name}` : editing.position_id}</Text>
              </Form.Item>
              <Form.Item label="印花">
                <Text>{editing.print_item ? `${editing.print_item.code} ${editing.print_item.name}` : editing.print_id}</Text>
              </Form.Item>
            </>
          ) : (
            <>
              <Form.Item name="style_id" label="款式" rules={[{ required: true, message: '请选择款式' }]}>
                <Select showSearch options={styleOptions} filterOption={filterOption} placeholder="选择款式" />
              </Form.Item>
              <Form.Item name="position_id" label="位置" rules={[{ required: true, message: '请选择位置' }]}>
                <Select showSearch options={positionOptions} filterOption={filterOption} placeholder="选择位置" />
              </Form.Item>
              <Form.Item name="print_id" label="印花" rules={[{ required: true, message: '请选择印花' }]}>
                <Select showSearch options={printOptions} filterOption={filterOption} placeholder="选择印花" />
              </Form.Item>
            </>
          )}
          <Form.Item name="remark" label="备注">
            <Input.TextArea rows={2} />
          </Form.Item>
          <Form.Item name="is_active" label="状态" valuePropName="checked">
            <Switch checkedChildren="启用" unCheckedChildren="停用" />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}
