export interface ListParams {
  keyword?: string
  search_field?: string
  page?: number
  page_size?: number
  [key: string]: string | number | undefined
}

export type FilterOptions = Record<string, Array<string | number | boolean>>
