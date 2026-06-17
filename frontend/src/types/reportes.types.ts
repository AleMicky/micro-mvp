export interface ReporteResponse {
  tipo: string
  total?: number
  items?: unknown[]
  cuentas_por_cobrar?: unknown[]
  cuentas_por_pagar?: unknown[]
  total_cxc?: number
  total_cxp?: number
  producto_id?: number
}
