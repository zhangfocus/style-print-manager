import client from './client'
import type { ImportResult } from '../types'

export type EntityKey = 'styles' | 'prints' | 'positions' | 'restrictions'

export const downloadTemplate = (entity: EntityKey) =>
  window.open(`/api/excel/template/${entity}`, '_blank')

export const exportExcel = () => window.open('/api/excel/export', '_blank')

export const importEntity = (entity: EntityKey, file: File): Promise<ImportResult> => {
  const form = new FormData()
  form.append('file', file)
  return client
    .post<ImportResult>(`/excel/import/${entity}`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    .then(r => r.data)
}
