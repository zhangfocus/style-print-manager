import { Layout, Menu } from 'antd'
import {
  TagsOutlined,
  HighlightOutlined,
  EnvironmentOutlined,
  ApiOutlined,
  FileExcelOutlined,
} from '@ant-design/icons'
import { useNavigate, useLocation, Outlet } from 'react-router-dom'

const { Sider, Content } = Layout

const menuItems = [
  { key: '/styles', icon: <TagsOutlined />, label: '款式管理' },
  { key: '/prints', icon: <HighlightOutlined />, label: '印花管理' },
  { key: '/positions', icon: <EnvironmentOutlined />, label: '位置管理' },
  { key: '/restrictions', icon: <ApiOutlined />, label: '限定管理' },
  { key: '/excel', icon: <FileExcelOutlined />, label: 'Excel 导入/导出' },
]

export default function AppLayout() {
  const navigate = useNavigate()
  const location = useLocation()
  const selectedKey = menuItems.find(m => location.pathname.startsWith(m.key))?.key ?? '/styles'

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={220} theme="dark" style={{ position: 'fixed', height: '100vh', left: 0, top: 0 }}>
        <div style={{ color: '#fff', padding: '20px 16px 16px', fontWeight: 700, fontSize: 16, borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
          款式印花管理系统
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[selectedKey]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{ marginTop: 8 }}
        />
      </Sider>
      <Layout style={{ marginLeft: 220 }}>
        <Content style={{ padding: 24, background: '#f5f5f5', minHeight: '100vh' }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
