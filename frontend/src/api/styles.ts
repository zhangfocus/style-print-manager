import client from './client'
import type { Style } from '../types'

export const listStyles = (keyword = '', limit = 500) =>
  client.get<Style[]>('/styles/', { params: { keyword, limit } }).then(r => r.data)

export const createStyle = (data: Omit<Style, 'id' | 'created_at' | 'updated_at'>) =>
  client.post<Style>('/styles/', data).then(r => r.data)

export const updateStyle = (id: number, data: Partial<Style>) =>
  client.put<Style>(`/styles/${id}`, data).then(r => r.data)

export const deleteStyle = (id: number) =>
  client.delete(`/styles/${id}`)
