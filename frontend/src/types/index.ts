export interface Style {
  id: number
  code: string
  name: string
  category?: string
  color?: string
  description?: string
  is_active: boolean
  created_at?: string
  updated_at?: string
}

export interface Print {
  id: number
  code: string
  name: string
  pattern_type?: string
  color_scheme?: string
  description?: string
  is_active: boolean
  created_at?: string
  updated_at?: string
}

export interface Position {
  id: number
  code: string
  name: string
  area?: string
  description?: string
  is_active: boolean
  created_at?: string
  updated_at?: string
}

export interface Restriction {
  id: number
  style_id: number
  position_id: number
  print_id: number
  is_active: boolean
  remark?: string
  style?: Style
  position?: Position
  print_item?: Print
  created_at?: string
  updated_at?: string
}

export interface ImportResult {
  success: boolean
  message: string
  details: {
    counts: Record<string, number>
    errors: string[]
  }
}
