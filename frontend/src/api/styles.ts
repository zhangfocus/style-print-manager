import client from './client'
import type { Style } from '../types'

export const listStyles = (keyword = '', page = 1, page_size = 10) =>
  client.get<{ items: Style[]; total: number; page: number; page_size: number }>('/styles/', { params: { keyword, page, page_size } }).then(r => r.data)

export const createStyle = (data: Omit<Style, 'id' | 'created_at' | 'updated_at'>) =>
  client.post<Style>('/styles/', data).then(r => r.data)

export const updateStyle = (id: number, data: Partial<Style>) =>
  client.put<Style>(`/styles/${id}`, data).then(r => r.data)

export const deleteStyle = (id: number) =>
  client.delete(`/styles/${id}`)
