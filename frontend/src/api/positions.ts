import client from './client'
import type { Position } from '../types'

export const listPositions = (keyword = '', page = 1, page_size = 10) =>
  client.get<{ items: Position[]; total: number; page: number; page_size: number }>('/positions/', { params: { keyword, page, page_size } }).then(r => r.data)

export const createPosition = (data: Omit<Position, 'id' | 'created_at' | 'updated_at'>) =>
  client.post<Position>('/positions/', data).then(r => r.data)

export const updatePosition = (id: number, data: Partial<Position>) =>
  client.put<Position>(`/positions/${id}`, data).then(r => r.data)

export const deletePosition = (id: number) =>
  client.delete(`/positions/${id}`)
