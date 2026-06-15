import { api } from './api'
import type {
  Almacen,
  AlmacenCreate,
  AlmacenUpdate,
  Existencia,
  KardexResponse,
  MovimientoInventario,
  StockAjusteRequest,
  StockIngresoRequest,
  StockOperacionResponse,
  StockSalidaRequest,
  StockTransferenciaRequest,
} from '@/types/inventario.types'

export const inventarioService = {
  getAlmacenes() {
    return api.get<Almacen[]>('/inventario/almacenes')
  },
  createAlmacen(data: AlmacenCreate) {
    return api.post<Almacen>('/inventario/almacenes', data)
  },
  updateAlmacen(id: number, data: AlmacenUpdate) {
    return api.put<Almacen>(`/inventario/almacenes/${id}`, data)
  },
  deleteAlmacen(id: number) {
    return api.delete(`/inventario/almacenes/${id}`)
  },

  getExistencias() {
    return api.get<Existencia[]>('/inventario/existencias')
  },
  getExistenciasByProducto(productoId: number) {
    return api.get<Existencia[]>(`/inventario/existencias/producto/${productoId}`)
  },
  getExistenciasByAlmacen(almacenId: number) {
    return api.get<Existencia[]>(`/inventario/existencias/almacen/${almacenId}`)
  },

  getMovimientos() {
    return api.get<MovimientoInventario[]>('/inventario/movimientos')
  },
  getKardex(productoId: number) {
    return api.get<KardexResponse>(`/inventario/kardex/producto/${productoId}`)
  },

  ingresoStock(data: StockIngresoRequest) {
    return api.post<StockOperacionResponse>('/inventario/stock/ingreso', data)
  },
  salidaStock(data: StockSalidaRequest) {
    return api.post<StockOperacionResponse>('/inventario/stock/salida', data)
  },
  ajusteStock(data: StockAjusteRequest) {
    return api.post('/inventario/stock/ajuste', data)
  },
  transferenciaStock(data: StockTransferenciaRequest) {
    return api.post('/inventario/stock/transferencia', data)
  },
}
