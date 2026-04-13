import { useState } from 'react'
import { Button, Card, Upload, Alert, List, Row, Col, Typography, Space, Divider } from 'antd'
import { UploadOutlined, DownloadOutlined, FileExcelOutlined, InboxOutlined } from '@ant-design/icons'
import type { UploadFile } from 'antd'
import type { ImportResult } from '../types'
import { downloadTemplate, exportExcel, importExcel } from '../api/excel'

const { Title, Text } = Typography
const { Dragger } = Upload

export default function ExcelPage() {
  const [fileList, setFileList] = useState<UploadFile[]>([])
  const [importing, setImporting] = useState(false)
  const [result, setResult] = useState<ImportResult | null>(null)

  const handleImport = async () => {
    const file = fileList[0]?.originFileObj
    if (!file) return
    setImporting(true)
    setResult(null)
    try {
      const res = await importExcel(file as File)
      setResult(res)
    } catch (e: unknown) {
      setResult({
        success: false,
        message: (e as Error).message,
        details: { counts: {}, errors: [(e as Error).message] },
      })
    } finally {
      setImporting(false)
    }
  }

  return (
    <Row gutter={24}>
      <Col xs={24} lg={14}>
        <Card title={<Space><UploadOutlined />导入 Excel</Space>}>
          <Dragger
            accept=".xlsx,.xls"
            maxCount={1}
            fileList={fileList}
            beforeUpload={() => false}
            onChange={({ fileList: fl }) => { setFileList(fl); setResult(null) }}
            style={{ marginBottom: 16 }}
          >
            <p className="ant-upload-drag-icon"><InboxOutlined /></p>
            <p className="ant-upload-text">点击或拖拽 Excel 文件到此区域</p>
            <p className="ant-upload-hint">支持 .xlsx / .xls 格式，按模板格式填写后上传</p>
          </Dragger>
          <Button
            type="primary"
            icon={<UploadOutlined />}
            disabled={fileList.length === 0}
            loading={importing}
            onClick={handleImport}
            block
          >
            开始导入
          </Button>

          {result && (
            <div style={{ marginTop: 16 }}>
              <Alert
                type={result.success ? 'success' : 'error'}
                message={result.message}
                showIcon
              />
              {result.details.errors.length > 0 && (
                <List
                  style={{ marginTop: 8, background: '#fff2f0', padding: '8px 12px', borderRadius: 6 }}
                  size="small"
                  header={<Text type="danger">错误详情（共 {result.details.errors.length} 条）：</Text>}
                  dataSource={result.details.errors}
                  renderItem={item => <List.Item style={{ padding: '2px 0' }}><Text type="danger">• {item}</Text></List.Item>}
                />
              )}
            </div>
          )}
        </Card>
      </Col>

      <Col xs={24} lg={10}>
        <Card title={<Space><FileExcelOutlined />模板 &amp; 导出</Space>}>
          <Title level={5} style={{ marginTop: 0 }}>下载导入模板</Title>
          <Text type="secondary" style={{ display: 'block', marginBottom: 12 }}>
            模板包含款式、印花、位置、限定四个 Sheet，按示例格式填写后导入。
          </Text>
          <Button icon={<DownloadOutlined />} onClick={downloadTemplate} block>
            下载模板
          </Button>

          <Divider />

          <Title level={5}>导出全量数据</Title>
          <Text type="secondary" style={{ display: 'block', marginBottom: 12 }}>
            将当前数据库中所有记录导出为 Excel 文件。
          </Text>
          <Button icon={<FileExcelOutlined />} onClick={exportExcel} block>
            导出数据
          </Button>
        </Card>
      </Col>
    </Row>
  )
}
