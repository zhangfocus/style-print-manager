import { useEffect, useState } from 'react'
import {
  Table, Button, Modal, Form, Input, InputNumber, Switch, Popconfirm,
  Space, Tag, message, Card, Divider, DatePicker,
} from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import type { TablePaginationConfig } from 'antd/es/table'
import dayjs from 'dayjs'
import { useSearchParams } from 'react-router-dom'
import type { Style } from '../types'
import { listStyles, createStyle, updateStyle, deleteStyle, getStyleFilterOptions } from '../api/styles'
import type { FilterOptions, ListParams } from '../api/filterTypes'
import FilterToolbar from '../components/filters/FilterToolbar'

export default function StylesPage() {
  const [data, setData] = useState<Style[]>([])
  const [loading, setLoading] = useState(false)
  const [searchParams, setSearchParams] = useSearchParams()
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Style | null>(null)
  const [form] = Form.useForm()
  const [submitting, setSubmitting] = useState(false)
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 })
  const [filterOptions, setFilterOptions] = useState<FilterOptions>({})

  const filterKeys = ['is_active', 'year', 'gender', 'season', 'category', 'product_category', 'brand_attr', 'attr', 'virtual_category']

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
      const res = await listStyles(params)
      setData(res.items)
      setPagination({ current: res.page, pageSize: res.page_size, total: res.total })
    }
    catch (e: unknown) { message.error((e as Error).message) }
    finally { setLoading(false) }
  }

  const loadFilterOptions = async (params = getListParams()) => {
    const filters = Object.fromEntries(filterKeys.map(key => [key, params[key]]).filter(([, value]) => value !== undefined && value !== ''))
    try { setFilterOptions(await getStyleFilterOptions(filters)) }
    catch (e: unknown) { message.error((e as Error).message) }
  }

  useEffect(() => { const params = getListParams(); load(params); loadFilterOptions(params) }, [searchParams]) // eslint-disable-line react-hooks/exhaustive-deps

  const openCreate = () => {
    setEditing(null)
    form.resetFields()
    form.setFieldsValue({ is_active: true })
    setModalOpen(true)
  }

  const openEdit = (record: Style) => {
    setEditing(record)
    const vals: Record<string, unknown> = { ...record }
    if (record.dev_date) vals.dev_date = dayjs(record.dev_date)
    form.setFieldsValue(vals)
    setModalOpen(true)
  }

  const handleDelete = async (id: number) => {
    try { await deleteStyle(id); message.success('删除成功'); load() }
    catch (e: unknown) { message.error((e as Error).message) }
  }

  const handleSubmit = async (values: Record<string, unknown>) => {
    setSubmitting(true)
    try {
      const payload = {
        ...values,
        dev_date: values.dev_date ? (values.dev_date as dayjs.Dayjs).format('YYYY-MM-DD') : null,
      }
      if (editing) {
        await updateStyle(editing.id, payload as Partial<Style>)
        message.success('更新成功')
      } else {
        await createStyle(payload as Omit<Style, 'id' | 'created_at' | 'updated_at'>)
        message.success('创建成功')
      }
      setModalOpen(false)
      load()
    } catch (e: unknown) { message.error((e as Error).message) }
    finally { setSubmitting(false) }
  }

  const columns: ColumnsType<Style> = [
    { title: '白坯款式编码', dataIndex: 'code', width: 180, fixed: 'left', ellipsis: true },
    { title: '商品款号', dataIndex: 'product_code', width: 120 },
    { title: '品牌属性', dataIndex: 'brand_attr', width: 100 },
    { title: '属性', dataIndex: 'attr', width: 80 },
    { title: '年份', dataIndex: 'year', width: 70 },
    { title: '性别', dataIndex: 'gender', width: 60 },
    { title: '季节', dataIndex: 'season', width: 80 },
    { title: '类目', dataIndex: 'category', width: 80 },
    { title: '商品分类', dataIndex: 'product_category', width: 100 },
    { title: '虚拟分类', dataIndex: 'virtual_category', width: 100 },
    { title: '在售颜色', dataIndex: 'colors_active', width: 140, ellipsis: true },
    { title: '尺码', dataIndex: 'sizes', width: 140, ellipsis: true },
    { title: '可印花范围', dataIndex: 'printable_area', width: 140, ellipsis: true },
    { title: '面料名称', dataIndex: 'fabric_name', width: 120, ellipsis: true },
    { title: '吊牌价', dataIndex: 'tag_price', width: 80 },
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
      <FilterToolbar
        keyword={searchParams.get('keyword') || ''}
        searchField={searchParams.get('search_field') || 'all'}
        searchFields={[
          { label: '全部', value: 'all' },
          { label: '白坯款式编码', value: 'code' },
          { label: '商品款号', value: 'product_code' },
          { label: '品牌属性', value: 'brand_attr' },
          { label: '属性', value: 'attr' },
          { label: '性别', value: 'gender' },
          { label: '季节', value: 'season' },
          { label: '类目', value: 'category' },
          { label: '商品分类', value: 'product_category' },
          { label: '虚拟分类', value: 'virtual_category' },
          { label: '在售颜色', value: 'colors_active' },
          { label: '尺码', value: 'sizes' },
          { label: '可印花范围', value: 'printable_area' },
          { label: '面料名称', value: 'fabric_name' },
        ]}
        filters={[
          { key: 'is_active', label: '状态', options: [{ label: '启用', value: 'true' }, { label: '停用', value: 'false' }] },
          { key: 'year', label: '年份', options: (filterOptions.year || []).map(value => ({ label: String(value), value })) },
          { key: 'season', label: '季节', options: (filterOptions.season || []).map(value => ({ label: String(value), value })) },
          { key: 'category', label: '类目', options: (filterOptions.category || []).map(value => ({ label: String(value), value })) },
          { key: 'product_category', label: '商品分类', options: (filterOptions.product_category || []).map(value => ({ label: String(value), value })) },
          { key: 'gender', label: '性别', options: (filterOptions.gender || []).map(value => ({ label: String(value), value })), advanced: true },
          { key: 'brand_attr', label: '品牌属性', options: (filterOptions.brand_attr || []).map(value => ({ label: String(value), value })), advanced: true },
          { key: 'attr', label: '属性', options: (filterOptions.attr || []).map(value => ({ label: String(value), value })), advanced: true },
          { key: 'virtual_category', label: '虚拟分类', options: (filterOptions.virtual_category || []).map(value => ({ label: String(value), value })), advanced: true },
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
        scroll={{ x: 1600 }}
        size="small"
      />

      <Modal
        title={editing ? '编辑款式' : '新建款式'}
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={submitting}
        destroyOnClose
        width={760}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit} style={{ marginTop: 8 }}>
          {/* 基础标识 */}
          <Divider orientationMargin={0} plain style={{ fontSize: 13 }}>基础标识</Divider>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 16px' }}>
            <Form.Item name="code" label="白坯款式编码" rules={[{ required: true, message: '请输入白坯款式编码' }]}>
              <Input disabled={!!editing} />
            </Form.Item>
            <Form.Item name="product_code" label="商品款号">
              <Input />
            </Form.Item>
          </div>

          {/* 分类属性 */}
          <Divider orientationMargin={0} plain style={{ fontSize: 13 }}>分类属性</Divider>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0 16px' }}>
            <Form.Item name="brand_attr" label="品牌属性"><Input /></Form.Item>
            <Form.Item name="attr" label="属性"><Input /></Form.Item>
            <Form.Item name="fabric_type" label="面料种类"><Input /></Form.Item>
            <Form.Item name="year" label="年份"><InputNumber style={{ width: '100%' }} /></Form.Item>
            <Form.Item name="gender" label="性别"><Input /></Form.Item>
            <Form.Item name="season" label="季节"><Input /></Form.Item>
            <Form.Item name="category" label="类目"><Input /></Form.Item>
            <Form.Item name="product_category" label="商品分类"><Input /></Form.Item>
            <Form.Item name="virtual_category" label="虚拟分类"><Input /></Form.Item>
          </div>

          {/* 颜色 / 尺码 */}
          <Divider orientationMargin={0} plain style={{ fontSize: 13 }}>颜色 / 尺码</Divider>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 16px' }}>
            <Form.Item name="colors_active" label="在售颜色"><Input /></Form.Item>
            <Form.Item name="colors_discontinued" label="淘汰颜色"><Input /></Form.Item>
            <Form.Item name="color_remark" label="颜色备注"><Input /></Form.Item>
            <Form.Item name="sizes" label="尺码"><Input /></Form.Item>
          </div>
          <Form.Item name="size_specs" label="号型"><Input.TextArea rows={2} /></Form.Item>
          <Form.Item name="size_remark" label="尺码备注"><Input.TextArea rows={1} /></Form.Item>

          {/* 印花 */}
          <Divider orientationMargin={0} plain style={{ fontSize: 13 }}>印花</Divider>
          <Form.Item name="printable_area" label="可印花范围"><Input /></Form.Item>

          {/* 面料 */}
          <Divider orientationMargin={0} plain style={{ fontSize: 13 }}>面料信息</Divider>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 16px' }}>
            <Form.Item name="fabric_name" label="面料名称"><Input /></Form.Item>
            <Form.Item name="fabric_weight" label="面料克重"><Input placeholder="如 220g" /></Form.Item>
            <Form.Item name="blank_weight" label="白坯重量(kg)"><InputNumber style={{ width: '100%' }} step={0.001} /></Form.Item>
          </div>
          <Form.Item name="fabric_composition" label="面料成分"><Input /></Form.Item>
          <Form.Item name="fabric_composition_en" label="Fabric Ingredients"><Input /></Form.Item>
          <Form.Item name="hot_wind_composition" label="热风成分"><Input /></Form.Item>

          {/* 商业信息 */}
          <Divider orientationMargin={0} plain style={{ fontSize: 13 }}>商业信息</Divider>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0 16px' }}>
            <Form.Item name="dev_date" label="开发时间"><DatePicker style={{ width: '100%' }} /></Form.Item>
            <Form.Item name="tag_price" label="吊牌价"><InputNumber style={{ width: '100%' }} /></Form.Item>
            <Form.Item name="premium_tag_price" label="高价品牌吊牌价"><InputNumber style={{ width: '100%' }} /></Form.Item>
            <Form.Item name="exec_standard" label="执行标准"><Input /></Form.Item>
            <Form.Item name="safety_category" label="安全技术类别"><Input /></Form.Item>
            <Form.Item name="product_type" label="产品分类"><Input /></Form.Item>
          </div>

          {/* 备注 / 状态 */}
          <Divider orientationMargin={0} plain style={{ fontSize: 13 }}>备注 / 状态</Divider>
          <Form.Item name="description" label="款式备注"><Input.TextArea rows={2} /></Form.Item>
          <Form.Item name="is_active" label="状态" valuePropName="checked">
            <Switch checkedChildren="启用" unCheckedChildren="停用" />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}
