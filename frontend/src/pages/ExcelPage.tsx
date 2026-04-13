import { useState } from 'react'
import {
  Button, Card, Upload, Alert, List, Row, Col, Typography, Space, Divider,
} from 'antd'
import {
  UploadOutlined, DownloadOutlined, FileExcelOutlined, InboxOutlined,
} from '@ant-design/icons'
import type { UploadFile } from 'antd'
import type { ImportResult } from '../types'
import { downloadTemplate, exportExcel, importEntity, type EntityKey } from '../api/excel'

const { Text } = Typography
const { Dragger } = Upload

interface PanelConfig {
  key: EntityKey
  label: string
  hint: string
}

const PANELS: PanelConfig[] = [
  { key: 'styles',       label: '款式',  hint: '支持原始款式模版格式（31列），按白坯款式编码去重更新' },
  { key: 'prints',       label: '印花',  hint: '列顺序：印花编号*、印花名称*、图案类型、色系、备注' },
  { key: 'positions',    label: '位置',  hint: '列顺序：位置编号*、位置名称*、区域、备注' },
  { key: 'restrictions', label: '限定',  hint: '列顺序：白坯款式编码*、位置编号*、印花编号*、是否启用(1/0)、备注' },
]

interface PanelState {
  fileList: UploadFile[]
  importing: boolean
  result: ImportResult | null
}

function ImportPanel({ config }: { config: PanelConfig }) {
  const [state, setState] = useState<PanelState>({
    fileList: [], importing: false, result: null,
  })

  const update = (patch: Partial<PanelState>) =>
    setState(prev => ({ ...prev, ...patch }))

  const handleImport = async () => {
    const file = state.fileList[0]?.originFileObj
    if (!file) return
    update({ importing: true, result: null })
    try {
      const res = await importEntity(config.key, file as File)
      update({ result: res })
    } catch (e: unknown) {
      const msg = (e as Error).message
      update({
        result: {
          success: false,
          message: msg,
          details: { counts: {}, errors: [msg] },
        },
      })
    } finally {
      update({ importing: false })
    }
  }

  return (
    <Card
      size="small"
      title={
        <Space>
          <FileExcelOutlined />
          <span>{config.label}导入</span>
        </Space>
      }
      extra={
        <Button
          size="small"
          icon={<DownloadOutlined />}
          onClick={() => downloadTemplate(config.key)}
        >
          下载模板
        </Button>
      }
    >
      <Dragger
        accept=".xlsx,.xls"
        maxCount={1}
        fileList={state.fileList}
        beforeUpload={() => false}
        onChange={({ fileList }) => update({ fileList, result: null })}
        style={{ marginBottom: 10 }}
      >
        <p className="ant-upload-drag-icon" style={{ marginBottom: 4 }}>
          <InboxOutlined />
        </p>
        <p className="ant-upload-text" style={{ fontSize: 13 }}>
          点击或拖拽 Excel 文件到此区域
        </p>
        <p className="ant-upload-hint" style={{ fontSize: 12 }}>
          {config.hint}
        </p>
      </Dragger>

      <Button
        type="primary"
        icon={<UploadOutlined />}
        disabled={state.fileList.length === 0}
        loading={state.importing}
        onClick={handleImport}
        block
        size="small"
      >
        开始导入
      </Button>

      {state.result && (
        <div style={{ marginTop: 10 }}>
          <Alert
            type={state.result.success ? 'success' : 'error'}
            message={state.result.message}
            showIcon
          />
          {state.result.details.errors.length > 0 && (
            <List
              style={{ marginTop: 6, background: '#fff2f0', padding: '6px 10px', borderRadius: 6 }}
              size="small"
              dataSource={state.result.details.errors}
              renderItem={item => (
                <List.Item style={{ padding: '2px 0', border: 'none' }}>
                  <Text type="danger" style={{ fontSize: 12 }}>• {item}</Text>
                </List.Item>
              )}
            />
          )}
        </div>
      )}
    </Card>
  )
}

export default function ExcelPage() {
  return (
    <div>
      {/* 分模块导入 */}
      <Row gutter={[16, 16]}>
        {PANELS.map(p => (
          <Col key={p.key} xs={24} sm={12} xl={6}>
            <ImportPanel config={p} />
          </Col>
        ))}
      </Row>

      <Divider />

      {/* 全量导出 */}
      <Card title={<Space><FileExcelOutlined />全量数据导出</Space>} style={{ maxWidth: 400 }}>
        <Text type="secondary" style={{ display: 'block', marginBottom: 12 }}>
          将款式、印花、位置、限定全部数据导出为一个 Excel 文件（4个 Sheet）。
        </Text>
        <Button icon={<FileExcelOutlined />} onClick={exportExcel}>
          导出全部数据
        </Button>
      </Card>
    </div>
  )
}
