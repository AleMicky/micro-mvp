import { api } from './api'
import type {
  CuentaPorCobrar,
  CuentaPorPagar,
  Cobro,
  CobroCreate,
  Pago,
  PagoCreate,
  Caja,
  CajaCreate,
  Banco,
  BancoCreate,
  MovimientoCaja,
  MovimientoBancario,
} from '@/types/finanzas.types'

export const finanzasService = {
  getCuentasPorCobrar() {
    return api.get<CuentaPorCobrar[]>('/finanzas/cuentas-por-cobrar')
  },
  getCuentasPorPagar() {
    return api.get<CuentaPorPagar[]>('/finanzas/cuentas-por-pagar')
  },
  getCobros() {
    return api.get<Cobro[]>('/finanzas/cobros')
  },
  registrarCobro(data: CobroCreate) {
    return api.post<Cobro>('/finanzas/cobros', data)
  },
  getPagos() {
    return api.get<Pago[]>('/finanzas/pagos')
  },
  registrarPago(data: PagoCreate) {
    return api.post<Pago>('/finanzas/pagos', data)
  },
  getCajas() {
    return api.get<Caja[]>('/finanzas/cajas')
  },
  createCaja(data: CajaCreate) {
    return api.post<Caja>('/finanzas/cajas', data)
  },
  updateCaja(id: number, data: Partial<CajaCreate>) {
    return api.put<Caja>(`/finanzas/cajas/${id}`, data)
  },
  deleteCaja(id: number) {
    return api.delete(`/finanzas/cajas/${id}`)
  },
  getBancos() {
    return api.get<Banco[]>('/finanzas/bancos')
  },
  createBanco(data: BancoCreate) {
    return api.post<Banco>('/finanzas/bancos', data)
  },
  updateBanco(id: number, data: Partial<BancoCreate>) {
    return api.put<Banco>(`/finanzas/bancos/${id}`, data)
  },
  deleteBanco(id: number) {
    return api.delete(`/finanzas/bancos/${id}`)
  },
  getMovimientosCaja() {
    return api.get<MovimientoCaja[]>('/finanzas/movimientos-caja')
  },
  getMovimientosBancarios() {
    return api.get<MovimientoBancario[]>('/finanzas/movimientos-bancarios')
  },
}
