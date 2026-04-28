import client from './client'
import type { Position } from '../types'
import type { FilterOptions, ListParams } from './filterTypes'

export const listPositions = (params: ListParams = {}) =>
  client.get<{ items: Position[]; total: number; page: number; page_size: number }>('/positions/', { params: { page: 1, page_size: 10, ...params } }).then(r => r.data)

export const getPositionFilterOptions = (params: ListParams = {}) =>
  client.get<FilterOptions>('/positions/filter-options', { params }).then(r => r.data)

export const createPosition = (data: Omit<Position, 'id' | 'created_at' | 'updated_at'>) =>
  client.post<Position>('/positions/', data).then(r => r.data)

export const updatePosition = (id: number, data: Partial<Position>) =>
  client.put<Position>(`/positions/${id}`, data).then(r => r.data)

export const deletePosition = (id: number) =>
  client.delete(`/positions/${id}`)
