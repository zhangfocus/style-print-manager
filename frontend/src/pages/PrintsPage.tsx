import { useEffect, useState } from 'react'
import {
  Table, Button, Modal, Form, Input, Switch, Popconfirm,
  Space, Tag, message, Card, Divider,
} from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import type { TablePaginationConfig } from 'antd/es/table'
import { useSearchParams } from 'react-router-dom'
import type { Print } from '../types'
import { listPrints, createPrint, updatePrint, deletePrint, getPrintFilterOptions } from '../api/prints'
import type { FilterOptions, ListParams } from '../api/filterTypes'
import FilterToolbar from '../components/filters/FilterToolbar'

export default function PrintsPage() {
  const [data, setData] = useState<Print[]>([])
  const [loading, setLoading] = useState(false)
  const [searchParams, setSearchParams] = useSearchParams()
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Print | null>(null)
  const [form] = Form.useForm()
  const [submitting, setSubmitting] = useState(false)
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 })
  const [filterOptions, setFilterOptions] = useState<FilterOptions>({})

  const filterKeys = ['is_active', 'pattern_size', 'pattern_spec', 'craft_attr']

  const getListParams = (): ListParams => {
    const params: ListParams = {
      keyword: searchParams.get('keyword') || '',
      search_field: searchParams.get('search_field') || 'all',
      page: Number(searchParams.get('page') || 1),
      page_size: Number(searchParams.get('page_size') || 10),
    }
    filterKeys.forEach((key) => {
      const value = searchParams.get(key)
      if (value) params[key] = value
    })
    return params
  }

  const getFilterValues = () => Object.fromEntries(filterKeys.map(key => [key, searchParams.get(key) || '']))

  const updateParams = (updates: Record<string, string | number | undefined>, resetPage = true) => {
    const next = new URLSearchParams(searchParams)
    Object.entries(updates).forEach(([key, value]) => {
      if (value === undefined || value === '') next.delete(key)
      else next.set(key, String(value))
    })
    if (resetPage) next.set('page', '1')
    setSearchParams(next)
  }

  const load = async (params = getListParams()) => {
    setLoading(true)
    try {
      const res = await listPrints(params)
      setData(res.items)
      setPagination({ current: res.page, pageSize: res.page_size, total: res.total })
    }
    catch (e: unknown) { message.error((e as Error).message) }
    finally { setLoading(false) }
  }

  const loadFilterOptions = async (params = getListParams()) => {
    const filters = Object.fromEntries(filterKeys.map(key => [key, params[key]]).filter(([, value]) => value !== undefined && value !== ''))
    try { setFilterOptions(await getPrintFilterOptions(filters)) }
    catch (e: unknown) { message.error((e as Error).message) }
  }

  useEffect(() => { const params = getListParams(); load(params); loadFilterOptions(params) }, [searchParams]) // eslint-disable-line react-hooks/exhaustive-deps

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
      <FilterToolbar
        keyword={searchParams.get('keyword') || ''}
        searchField={searchParams.get('search_field') || 'all'}
        searchFields={[
          { label: '全部', value: 'all' },
          { label: '商品编码', value: 'code' },
          { label: '图案名称', value: 'name' },
          { label: '图案大小', value: 'pattern_size' },
          { label: '图案规格', value: 'pattern_spec' },
          { label: '工艺属性', value: 'craft_attr' },
          { label: '真维斯款号', value: 'zwx_style_code' },
          { label: 'JWCO款号', value: 'jwco_style_code' },
          { label: 'CITY款号', value: 'city_style_code' },
          { label: '唐狮款号', value: 'tangshi_style_code' },
          { label: '备注', value: 'description' },
        ]}
        filters={[
          { key: 'is_active', label: '状态', options: [{ label: '启用', value: 'true' }, { label: '停用', value: 'false' }] },
          { key: 'pattern_size', label: '图案大小', options: (filterOptions.pattern_size || []).map(value => ({ label: String(value), value })) },
          { key: 'pattern_spec', label: '图案规格', options: (filterOptions.pattern_spec || []).map(value => ({ label: String(value), value })) },
          { key: 'craft_attr', label: '工艺属性', options: (filterOptions.craft_attr || []).map(value => ({ label: String(value), value })) },
        ]}
        values={getFilterValues()}
        onSearchFieldChange={value => updateParams({ search_field: value })}
        onKeywordSearch={value => updateParams({ keyword: value })}
        onFilterChange={(key, value) => updateParams({ [key]: value })}
        onReset={() => {
          const next = new URLSearchParams()
          next.set('page', '1')
          next.set('page_size', String(pagination.pageSize))
          setSearchParams(next)
        }}
      />
      <Table
        rowKey="id"
        columns={columns}
        dataSource={data}
        loading={loading}
        pagination={{
          current: pagination.current,
          pageSize: pagination.pageSize,
          total: pagination.total,
          showSizeChanger: true,
          showTotal: t => `共 ${t} 条`,
        }}
        onChange={(next: TablePaginationConfig) => {
          updateParams({ page: next.current || 1, page_size: next.pageSize || pagination.pageSize }, false)
        }}
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
