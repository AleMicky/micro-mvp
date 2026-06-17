import { api } from './api'

export const reportesService = {
  getProductos() {
    return api.get('/reportes/productos')
  },
  getStock() {
    return api.get('/reportes/stock')
  },
  getKardex(productoId: number) {
    return api.get(`/reportes/kardex/producto/${productoId}`)
  },
  getCompras() {
    return api.get('/reportes/compras')
  },
  getVentas() {
    return api.get('/reportes/ventas')
  },
  getFinanzas() {
    return api.get('/reportes/finanzas')
  },
  exportarPdf(tipo = 'stock') {
    return api.get(`/reportes/exportar/pdf?tipo=${tipo}`, { responseType: 'blob' })
  },
  exportarExcel(tipo = 'stock') {
    return api.get(`/reportes/exportar/excel?tipo=${tipo}`, { responseType: 'blob' })
  },
}
