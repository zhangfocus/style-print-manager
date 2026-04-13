import client from './client'
import type { Position } from '../types'

export const listPositions = (keyword = '') =>
  client.get<Position[]>('/positions/', { params: { keyword, limit: 500 } }).then(r => r.data)

export const createPosition = (data: Omit<Position, 'id' | 'created_at' | 'updated_at'>) =>
  client.post<Position>('/positions/', data).then(r => r.data)

export const updatePosition = (id: number, data: Partial<Position>) =>
  client.put<Position>(`/positions/${id}`, data).then(r => r.data)

export const deletePosition = (id: number) =>
  client.delete(`/positions/${id}`)
