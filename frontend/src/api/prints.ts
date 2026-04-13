import client from './client'
import type { Print } from '../types'

export const listPrints = (keyword = '') =>
  client.get<Print[]>('/prints/', { params: { keyword, limit: 500 } }).then(r => r.data)

export const createPrint = (data: Omit<Print, 'id' | 'created_at' | 'updated_at'>) =>
  client.post<Print>('/prints/', data).then(r => r.data)

export const updatePrint = (id: number, data: Partial<Print>) =>
  client.put<Print>(`/prints/${id}`, data).then(r => r.data)

export const deletePrint = (id: number) =>
  client.delete(`/prints/${id}`)
