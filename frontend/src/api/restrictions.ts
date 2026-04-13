import client from './client'
import type { Restriction } from '../types'

export const listRestrictions = (params?: { style_id?: number; position_id?: number; print_id?: number }) =>
  client.get<Restriction[]>('/restrictions/', { params: { ...params, limit: 500 } }).then(r => r.data)

export const createRestriction = (data: {
  style_id: number
  position_id: number
  print_id: number
  is_active?: boolean
  remark?: string
}) => client.post<Restriction>('/restrictions/', data).then(r => r.data)

export const updateRestriction = (id: number, data: { is_active?: boolean; remark?: string }) =>
  client.put<Restriction>(`/restrictions/${id}`, data).then(r => r.data)

export const deleteRestriction = (id: number) =>
  client.delete(`/restrictions/${id}`)
