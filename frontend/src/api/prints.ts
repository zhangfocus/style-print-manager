import client from './client'
import type { Print } from '../types'

export const listPrints = (keyword = '', page = 1, page_size = 10) =>
  client.get<{ items: Print[]; total: number; page: number; page_size: number }>('/prints/', { params: { keyword, page, page_size } }).then(r => r.data)

export const createPrint = (data: Omit<Print, 'id' | 'created_at' | 'updated_at'>) =>
  client.post<Print>('/prints/', data).then(r => r.data)

export const updatePrint = (id: number, data: Partial<Print>) =>
  client.put<Print>(`/prints/${id}`, data).then(r => r.data)

export const deletePrint = (id: number) =>
  client.delete(`/prints/${id}`)
