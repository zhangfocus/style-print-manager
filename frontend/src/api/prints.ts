import client from './client'
import type { Print } from '../types'
import type { FilterOptions, ListParams } from './filterTypes'

export const listPrints = (params: ListParams = {}) =>
  client.get<{ items: Print[]; total: number; page: number; page_size: number }>('/prints/', { params: { page: 1, page_size: 10, ...params } }).then(r => r.data)

export const getPrintFilterOptions = (params: ListParams = {}) =>
  client.get<FilterOptions>('/prints/filter-options', { params }).then(r => r.data)

export const createPrint = (data: Omit<Print, 'id' | 'created_at' | 'updated_at'>) =>
  client.post<Print>('/prints/', data).then(r => r.data)

export const updatePrint = (id: number, data: Partial<Print>) =>
  client.put<Print>(`/prints/${id}`, data).then(r => r.data)

export const deletePrint = (id: number) =>
  client.delete(`/prints/${id}`)

export const getPrintsByIds = (ids: number[]) =>
  client.get<Print[]>('/prints/by-ids', { params: { ids: ids.join(',') } }).then(r => r.data)
