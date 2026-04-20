import { useEffect, useState } from 'react'
import {
  Table, Button, Modal, Form, Input, Switch, Popconfirm,
  Space, Tag, message, Card, Divider,
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
      const res = await listPrints(kw)
      setData(res.items)
    }
    catch (e: unknown) { message.error((e as Error).message) }
    finally { setLoading(false) }
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
    try { await deletePrint(id); message.success('删除成功'); load() }
    catch (e: unknown) { message.error((e as Error).message) }
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
    } catch (e: unknown) { message.error((e as Error).message) }
    finally { setSubmitting(false) }
  }

  const columns: ColumnsType<Print> = [
    { title: '商品编码', dataIndex: 'code', width: 120, fixed: 'left' },
    { title: '图案名称', dataIndex: 'name', width: 140, ellipsis: true },
    { title: '图案大小', dataIndex: 'pattern_size', width: 90 },
    { title: '图案规格', dataIndex: 'pattern_spec', width: 80 },
    { title: '工艺属性', dataIndex: 'craft_attr', width: 150, ellipsis: true },
    { title: '真维斯款号', dataIndex: 'zwx_style_code', width: 110 },
    { title: 'JWCO款号', dataIndex: 'jwco_style_code', width: 110 },
    { title: 'CITY款号', dataIndex: 'city_style_code', width: 110 },
    { title: '唐狮款号', dataIndex: 'tangshi_style_code', width: 100 },
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
        placeholder="搜索商品编码 / 图案名称 / 工艺属性"
        allowClear
        style={{ width: 320, marginBottom: 16 }}
        onSearch={kw => { setKeyword(kw); load(kw) }}
        onChange={e => { if (!e.target.value) { setKeyword(''); load('') } }}
      />
      <Table
        rowKey="id"
        columns={columns}
        dataSource={data}
        loading={loading}
        pagination={{ pageSize: 20, showTotal: t => `共 ${t} 条` }}
        scroll={{ x: 1200 }}
        size="small"
      />

      <Modal
        title={editing ? '编辑印花' : '新建印花'}
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={submitting}
        destroyOnClose
        width={680}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit} style={{ marginTop: 8 }}>
          {/* 基础信息 */}
          <Divider orientationMargin={0} plain style={{ fontSize: 13 }}>基础信息</Divider>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 16px' }}>
            <Form.Item name="code" label="商品编码" rules={[{ required: true, message: '请输入商品编码' }]}>
              <Input disabled={!!editing} />
            </Form.Item>
            <Form.Item name="name" label="图案名称" rules={[{ required: true, message: '请输入图案名称' }]}>
              <Input />
            </Form.Item>
            <Form.Item name="pattern_size" label="图案大小"><Input placeholder="小图 / 大图 / 超大图 / 中图" /></Form.Item>
            <Form.Item name="pattern_spec" label="图案规格"><Input placeholder="X / D / C" /></Form.Item>
            <Form.Item name="craft_attr" label="工艺属性" style={{ gridColumn: '1 / -1' }}><Input /></Form.Item>
          </div>

          {/* 品牌关联 */}
          <Divider orientationMargin={0} plain style={{ fontSize: 13 }}>品牌关联</Divider>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0 16px' }}>
            <Form.Item name="zwx_style_code" label="真维斯款号"><Input /></Form.Item>
            <Form.Item name="zwx_replace_code" label="真维斯替换编码"><Input /></Form.Item>
            <Form.Item name="zwx_replace_style" label="真维斯替换款号"><Input /></Form.Item>
            <Form.Item name="jwco_style_code" label="JWCO款号"><Input /></Form.Item>
            <Form.Item name="jwco_replace_code" label="JWCO替换编码"><Input /></Form.Item>
            <Form.Item name="jwco_replace_style" label="JWCO替换款号"><Input /></Form.Item>
            <Form.Item name="city_style_code" label="CITY款号"><Input /></Form.Item>
            <Form.Item name="city_replace_code" label="CITY替换编码"><Input /></Form.Item>
            <Form.Item name="city_replace_style" label="CITY替换款号"><Input /></Form.Item>
            <Form.Item name="tangshi_style_code" label="唐狮款号"><Input /></Form.Item>
          </div>

          {/* 备注 / 状态 */}
          <Divider orientationMargin={0} plain style={{ fontSize: 13 }}>备注 / 状态</Divider>
          <Form.Item name="description" label="备注"><Input.TextArea rows={2} /></Form.Item>
          <Form.Item name="is_active" label="状态" valuePropName="checked">
            <Switch checkedChildren="启用" unCheckedChildren="停用" />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}
