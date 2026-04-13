import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import AppLayout from './components/layout/AppLayout'
import StylesPage from './pages/StylesPage'
import PrintsPage from './pages/PrintsPage'
import PositionsPage from './pages/PositionsPage'
import RestrictionsPage from './pages/RestrictionsPage'
import ExcelPage from './pages/ExcelPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route index element={<Navigate to="/styles" replace />} />
          <Route path="/styles" element={<StylesPage />} />
          <Route path="/prints" element={<PrintsPage />} />
          <Route path="/positions" element={<PositionsPage />} />
          <Route path="/restrictions" element={<RestrictionsPage />} />
          <Route path="/excel" element={<ExcelPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
