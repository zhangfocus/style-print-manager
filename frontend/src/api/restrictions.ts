import client from './client'
import type { StylePositionRule, StyleBan } from '../types'

// ── 限定规则 ──────────────────────────────────────────────

export const listRules = (params?: { style_code?: string; position_id?: number; print_code?: string; rule_type?: number; page?: number; page_size?: number }) =>
  client.get<{ items: StylePositionRule[]; total: number; page: number; page_size: number }>('/restrictions/', { params: { page: 1, page_size: 10, ...params } }).then(r => r.data)

export const createRule = (data: {
  rule_type: number
  position_code?: string | null
  style_codes?: string[] | null
  print_codes?: string[] | null
  is_active?: boolean
}) => client.post<StylePositionRule>('/restrictions/', data).then(r => r.data)

export const updateRule = (id: number, data: {
  position_code?: string | null
  style_codes?: string[] | null
  print_codes?: string[] | null
  is_active?: boolean
}) => client.put<StylePositionRule>(`/restrictions/${id}`, data).then(r => r.data)

export const deleteRule = (id: number) =>
  client.delete(`/restrictions/${id}`)

// ── 全禁款式 ──────────────────────────────────────────────

export const listBans = (params?: { keyword?: string; limit?: number }) =>
  client.get<StyleBan[]>('/bans/', { params: { limit: 500, ...params } }).then(r => r.data)

export const createBan = (data: { style_id: number; remark?: string }) =>
  client.post<StyleBan>('/bans/', data).then(r => r.data)

export const updateBan = (id: number, data: { remark?: string }) =>
  client.put<StyleBan>(`/bans/${id}`, data).then(r => r.data)

export const deleteBan = (id: number) =>
  client.delete(`/bans/${id}`)
