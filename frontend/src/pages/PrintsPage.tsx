import { useEffect, useState } from 'react'
import {
  Table, Button, Modal, Form, Input, Switch, Popconfirm,
  Space, Tag, message, Card,
} from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import type { Print } from '../types'
import { listPrints, createPrint, updatePrint, deletePrint } from '../api/prints'

export default function PrintsPage() {
  const [data, setData] = useState<Print[]>([])
  const [loading, setLoading] = useState(false)
  const [keyword, setKeyword] = useState('')
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Print | null>(null)
  const [form] = Form.useForm()
  const [submitting, setSubmitting] = useState(false)

  const load = async (kw = keyword) => {
    setLoading(true)
    try {
      setData(await listPrints(kw))
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

  const openEdit = (record: Print) => {
    setEditing(record)
    form.setFieldsValue(record)
    setModalOpen(true)
  }

  const handleDelete = async (id: number) => {
    try {
      await deletePrint(id)
      message.success('删除成功')
      load()
    } catch (e: unknown) {
      message.error((e as Error).message)
    }
  }

  const handleSubmit = async (values: Partial<Print>) => {
    setSubmitting(true)
    try {
      if (editing) {
        await updatePrint(editing.id, values)
        message.success('更新成功')
      } else {
        await createPrint(values as Omit<Print, 'id' | 'created_at' | 'updated_at'>)
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

  const columns: ColumnsType<Print> = [
    { title: '印花编号', dataIndex: 'code', width: 120 },
    { title: '印花名称', dataIndex: 'name', width: 150 },
    { title: '图案类型', dataIndex: 'pattern_type', width: 110 },
    { title: '色系', dataIndex: 'color_scheme', width: 100 },
    { title: '备注', dataIndex: 'description', ellipsis: true },
    {
      title: '状态', dataIndex: 'is_active', width: 80,
      render: (v: boolean) => <Tag color={v ? 'green' : 'red'}>{v ? '启用' : '停用'}</Tag>,
    },
    {
      title: '操作', width: 120, fixed: 'right',
      render: (_: unknown, record: Print) => (
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
      title="印花管理"
      extra={<Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>新建印花</Button>}
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
        title={editing ? '编辑印花' : '新建印花'}
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={submitting}
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit} style={{ marginTop: 12 }}>
          <Form.Item name="code" label="印花编号" rules={[{ required: true, message: '请输入印花编号' }]}>
            <Input disabled={!!editing} placeholder="如 PT001" />
          </Form.Item>
          <Form.Item name="name" label="印花名称" rules={[{ required: true, message: '请输入印花名称' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="pattern_type" label="图案类型">
            <Input placeholder="如 花卉" />
          </Form.Item>
          <Form.Item name="color_scheme" label="色系">
            <Input placeholder="如 粉色系" />
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
