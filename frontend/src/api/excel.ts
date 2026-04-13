import client from './client'
import type { ImportResult } from '../types'

export const downloadTemplate = () => window.open('/api/excel/template', '_blank')

export const exportExcel = () => window.open('/api/excel/export', '_blank')

export const importExcel = (file: File): Promise<ImportResult> => {
  const form = new FormData()
  form.append('file', file)
  return client
    .post<ImportResult>('/excel/import', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    .then(r => r.data)
}
