import { useEffect, useState } from 'react'
import {
  Table, Button, Modal, Form, Input, Switch, Popconfirm,
  Space, Tag, message, Card,
} from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import type { Style } from '../types'
import { listStyles, createStyle, updateStyle, deleteStyle } from '../api/styles'

export default function StylesPage() {
  const [data, setData] = useState<Style[]>([])
  const [loading, setLoading] = useState(false)
  const [keyword, setKeyword] = useState('')
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Style | null>(null)
  const [form] = Form.useForm()
  const [submitting, setSubmitting] = useState(false)

  const load = async (kw = keyword) => {
    setLoading(true)
    try {
      setData(await listStyles(kw))
    } catch (e: unknown) {
      message.error((e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const openCreate = () => {
    setEditing(null)
    form.resetFields()
    form.setFieldsValue({ is_active: true })
    setModalOpen(true)
  }

  const openEdit = (record: Style) => {
    setEditing(record)
    form.setFieldsValue(record)
    setModalOpen(true)
  }

  const handleDelete = async (id: number) => {
    try {
      await deleteStyle(id)
      message.success('删除成功')
      load()
    } catch (e: unknown) {
      message.error((e as Error).message)
    }
  }

  const handleSubmit = async (values: Partial<Style>) => {
    setSubmitting(true)
    try {
      if (editing) {
        await updateStyle(editing.id, values)
        message.success('更新成功')
      } else {
        await createStyle(values as Omit<Style, 'id' | 'created_at' | 'updated_at'>)
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

  const columns: ColumnsType<Style> = [
    { title: '款式编号', dataIndex: 'code', width: 120 },
    { title: '款式名称', dataIndex: 'name', width: 150 },
    { title: '品类', dataIndex: 'category', width: 100 },
    { title: '颜色', dataIndex: 'color', width: 100 },
    { title: '备注', dataIndex: 'description', ellipsis: true },
    {
      title: '状态', dataIndex: 'is_active', width: 80,
      render: (v: boolean) => <Tag color={v ? 'green' : 'red'}>{v ? '启用' : '停用'}</Tag>,
    },
    {
      title: '操作', width: 120, fixed: 'right',
      render: (_: unknown, record: Style) => (
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
      title="款式管理"
      extra={<Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>新建款式</Button>}
    >
      <Input.Search
        placeholder="搜索编号或名称"
        allowClear
        style={{ width: 260, marginBottom: 16 }}
        onSearch={kw => { setKeyword(kw); load(kw) }}
        onChange={e => { if (!e.target.value) { setKeyword(''); load('') } }}
      />
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
        title={editing ? '编辑款式' : '新建款式'}
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={submitting}
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit} style={{ marginTop: 12 }}>
          <Form.Item name="code" label="款式编号" rules={[{ required: true, message: '请输入款式编号' }]}>
            <Input disabled={!!editing} placeholder="如 ST001" />
          </Form.Item>
          <Form.Item name="name" label="款式名称" rules={[{ required: true, message: '请输入款式名称' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="category" label="品类">
            <Input placeholder="如 T恤" />
          </Form.Item>
          <Form.Item name="color" label="颜色">
            <Input placeholder="如 白色" />
          </Form.Item>
          <Form.Item name="description" label="备注">
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
