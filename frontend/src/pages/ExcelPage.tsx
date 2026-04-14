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
  accept: string
}

const PANELS: PanelConfig[] = [
  {
    key: 'styles',
    label: '款式',
    accept: '.xlsx,.xls',
    hint: '按模板格式导入，白坯款式编码为主键，重复则更新覆盖',
  },
  {
    key: 'prints',
    label: '印花',
    accept: '.xlsx,.xls',
    hint: '按模板格式导入，商品编码为主键，重复则更新覆盖',
  },
  {
    key: 'positions',
    label: '位置',
    accept: '.txt,.json',
    hint: '上传贴图位置字典 JSON/txt 文件，位置编号为主键，重复则更新',
  },
  {
    key: 'restrictions',
    label: '限定',
    accept: '.xlsx,.xls',
    hint: '按模板格式导入：白坯款式编码 + 位置名称 + 允许印花（逗号分隔，留空=不限）',
  },
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
      style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
      styles={{ body: { flex: 1, display: 'flex', flexDirection: 'column' } }}
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
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <Dragger
          accept={config.accept}
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
            点击或拖拽文件到此处
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
      </div>
    </Card>
  )
}

// ── 导出配置 ──────────────────────────────────────────────

interface ExportOption {
  key: string
  label: string
}

const EXPORT_OPTIONS: ExportOption[] = [
  { key: 'styles',    label: '款式' },
  { key: 'prints',    label: '印花' },
  { key: 'positions', label: '位置' },
  { key: 'rules',     label: '限定规则' },
  { key: 'bans',      label: '全禁款式' },
]

// ── 主页面 ────────────────────────────────────────────────

export default function ExcelPage() {
  return (
    <div>
      {/* 分模块导入 */}
      <Row gutter={[16, 16]} align="stretch">
        {PANELS.map(p => (
          <Col key={p.key} xs={24} sm={12} xl={6} style={{ display: 'flex' }}>
            <ImportPanel config={p} />
          </Col>
        ))}
      </Row>

      <Divider />

      {/* 数据导出 */}
      <Card title={<Space><FileExcelOutlined />数据导出</Space>} style={{ maxWidth: 560 }}>
        <Text type="secondary" style={{ display: 'block', marginBottom: 12 }}>
          单独导出某一模块，或全量导出所有数据为一个 Excel 文件（多 Sheet）。
        </Text>
        <Space wrap>
          {EXPORT_OPTIONS.map(opt => (
            <Button
              key={opt.key}
              icon={<DownloadOutlined />}
              onClick={() => exportExcel(opt.key)}
            >
              导出{opt.label}
            </Button>
          ))}
          <Button
            type="primary"
            icon={<FileExcelOutlined />}
            onClick={() => exportExcel()}
          >
            全量导出
          </Button>
        </Space>
      </Card>
    </div>
  )
}
