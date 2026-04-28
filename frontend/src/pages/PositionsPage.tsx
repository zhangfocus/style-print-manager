import { useEffect, useState } from 'react'
import {
  Table, Button, Modal, Form, Input, Switch, Popconfirm,
  Space, Tag, message, Card,
} from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import type { TablePaginationConfig } from 'antd/es/table'
import { useSearchParams } from 'react-router-dom'
import type { Position } from '../types'
import { listPositions, createPosition, updatePosition, deletePosition, getPositionFilterOptions } from '../api/positions'
import type { FilterOptions, ListParams } from '../api/filterTypes'
import FilterToolbar from '../components/filters/FilterToolbar'

export default function PositionsPage() {
  const [data, setData] = useState<Position[]>([])
  const [loading, setLoading] = useState(false)
  const [searchParams, setSearchParams] = useSearchParams()
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Position | null>(null)
  const [form] = Form.useForm()
  const [submitting, setSubmitting] = useState(false)
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 })
  const [filterOptions, setFilterOptions] = useState<FilterOptions>({})

  const filterKeys = ['is_active', 'area']

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
      const res = await listPositions(params)
      setData(res.items)
      setPagination({ current: res.page, pageSize: res.page_size, total: res.total })
    } catch (e: unknown) {
      message.error((e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  const loadFilterOptions = async (params = getListParams()) => {
    const filters = Object.fromEntries(filterKeys.map(key => [key, params[key]]).filter(([, value]) => value !== undefined && value !== ''))
    try { setFilterOptions(await getPositionFilterOptions(filters)) }
    catch (e: unknown) { message.error((e as Error).message) }
  }

  useEffect(() => { const params = getListParams(); load(params); loadFilterOptions(params) }, [searchParams]) // eslint-disable-line react-hooks/exhaustive-deps

  const openCreate = () => {
    setEditing(null)
    form.resetFields()
    form.setFieldsValue({ is_active: true })
    setModalOpen(true)
  }

  const openEdit = (record: Position) => {
    setEditing(record)
    form.setFieldsValue(record)
    setModalOpen(true)
  }

  const handleDelete = async (id: number) => {
    try {
      await deletePosition(id)
      message.success('删除成功')
      load()
    } catch (e: unknown) {
      message.error((e as Error).message)
    }
  }

  const handleSubmit = async (values: Partial<Position>) => {
    setSubmitting(true)
    try {
      if (editing) {
        await updatePosition(editing.id, values)
        message.success('更新成功')
      } else {
        await createPosition(values as Omit<Position, 'id' | 'created_at' | 'updated_at'>)
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

  const columns: ColumnsType<Position> = [
    { title: '位置编号', dataIndex: 'code', width: 120 },
    { title: '位置名称', dataIndex: 'name', width: 150 },
    { title: '区域', dataIndex: 'area', width: 100 },
    { title: '备注', dataIndex: 'description', ellipsis: true },
    {
      title: '状态', dataIndex: 'is_active', width: 80,
      render: (v: boolean) => <Tag color={v ? 'green' : 'red'}>{v ? '启用' : '停用'}</Tag>,
    },
    {
      title: '操作', width: 120, fixed: 'right',
      render: (_: unknown, record: Position) => (
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
      title="位置管理"
      extra={<Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>新建位置</Button>}
    >
      <FilterToolbar
        keyword={searchParams.get('keyword') || ''}
        searchField={searchParams.get('search_field') || 'all'}
        searchFields={[
          { label: '全部', value: 'all' },
          { label: '位置编号', value: 'code' },
          { label: '位置名称', value: 'name' },
          { label: '区域', value: 'area' },
          { label: '备注', value: 'description' },
        ]}
        filters={[
          { key: 'is_active', label: '状态', options: [{ label: '启用', value: 'true' }, { label: '停用', value: 'false' }] },
          { key: 'area', label: '区域', options: (filterOptions.area || []).map(value => ({ label: String(value), value })) },
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
        scroll={{ x: 700 }}
        size="small"
      />
      <Modal
        title={editing ? '编辑位置' : '新建位置'}
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={submitting}
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit} style={{ marginTop: 12 }}>
          <Form.Item name="code" label="位置编号" rules={[{ required: true, message: '请输入位置编号' }]}>
            <Input disabled={!!editing} placeholder="如 PS001" />
          </Form.Item>
          <Form.Item name="name" label="位置名称" rules={[{ required: true, message: '请输入位置名称' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="area" label="区域">
            <Input placeholder="如 正面" />
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
