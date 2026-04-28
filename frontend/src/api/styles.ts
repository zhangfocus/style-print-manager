import client from './client'
import type { Style } from '../types'
import type { FilterOptions, ListParams } from './filterTypes'

export const listStyles = (params: ListParams = {}) =>
  client.get<{ items: Style[]; total: number; page: number; page_size: number }>('/styles/', { params: { page: 1, page_size: 10, ...params } }).then(r => r.data)

export const getStyleFilterOptions = (params: ListParams = {}) =>
  client.get<FilterOptions>('/styles/filter-options', { params }).then(r => r.data)

export const createStyle = (data: Omit<Style, 'id' | 'created_at' | 'updated_at'>) =>
  client.post<Style>('/styles/', data).then(r => r.data)

export const updateStyle = (id: number, data: Partial<Style>) =>
  client.put<Style>(`/styles/${id}`, data).then(r => r.data)

export const deleteStyle = (id: number) =>
  client.delete(`/styles/${id}`)

export const getStylesByIds = (ids: number[]) =>
  client.get<Style[]>('/styles/by-ids', { params: { ids: ids.join(',') } }).then(r => r.data)
