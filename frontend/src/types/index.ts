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
  code: string             // 商品编码（唯一）
  name: string             // 图案名称
  pattern_size?: string    // 图案大小
  pattern_spec?: string    // 图案规格
  craft_attr?: string      // 工艺属性
  zwx_style_code?: string
  zwx_replace_code?: string
  zwx_replace_style?: string
  jwco_style_code?: string
  jwco_replace_code?: string
  jwco_replace_style?: string
  city_style_code?: string
  city_replace_code?: string
  city_replace_style?: string
  tangshi_style_code?: string
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

export interface StylePositionRule {
  id: number
  rule_type: 1 | 2 | 3  // 1=style_ban, 2=position_restriction, 3=style_position
  position_id?: number | null
  style_ids?: string | null  // 逗号分隔的款式ID
  print_ids?: string | null  // 逗号分隔的印花ID
  print_ids_display?: string | null  // 可读格式（印花编码）
  style_ids_display?: string | null  // 可读格式（款式编码）
  is_active: boolean
  position?: Position
  created_at?: string
  updated_at?: string
}

export interface StyleBan {
  id: number
  style_id: number
  remark?: string
  style?: Style
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
