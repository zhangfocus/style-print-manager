import client from './client'
import type { ImportResult } from '../types'

export type EntityKey = 'styles' | 'prints' | 'positions' | 'restrictions'

export const downloadTemplate = (entity: EntityKey) =>
  window.open(`/api/excel/template/${entity}`, '_blank')

/** entities 为空时全量导出，否则传逗号分隔的实体名 */
export const exportExcel = (entities?: string) => {
  const url = entities
    ? `/api/excel/export?entities=${encodeURIComponent(entities)}`
    : '/api/excel/export'
  window.open(url, '_blank')
}

export const importEntity = (entity: EntityKey, file: File): Promise<ImportResult> => {
  const form = new FormData()
  form.append('file', file)
  return client
    .post<ImportResult>(`/excel/import/${entity}`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000,
    })
    .then(r => r.data)
}
