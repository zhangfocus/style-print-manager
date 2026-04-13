export interface Style {
  id: number
  code: string             // 白坯款式编码（唯一）
  product_code?: string    // 商品款号
  brand_attr?: string
  attr?: string
  fabric_type?: string
  year?: number
  gender?: string
  season?: string
  category?: string
  product_category?: string
  virtual_category?: string
  colors_active?: string
  colors_discontinued?: string
  color_remark?: string
  sizes?: string
  size_specs?: string
  size_remark?: string
  printable_area?: string
  fabric_composition?: string
  fabric_composition_en?: string
  hot_wind_composition?: string
  fabric_name?: string
  fabric_weight?: string
  blank_weight?: number
  dev_date?: string
  tag_price?: number
  premium_tag_price?: number
  exec_standard?: string
  safety_category?: string
  product_type?: string
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
