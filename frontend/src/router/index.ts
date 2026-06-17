import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      component: () => import('@/layouts/AuthLayout.vue'),
      meta: { guest: true },
      children: [
        {
          path: '',
          name: 'login',
          component: () => import('@/views/auth/LoginView.vue'),
        },
      ],
    },
    {
      path: '/',
      component: () => import('@/layouts/AdminLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: { name: 'dashboard' } },
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('@/views/dashboard/DashboardView.vue'),
        },
        {
          path: 'catalogos/categorias',
          name: 'categorias',
          component: () => import('@/views/catalogos/CategoriasView.vue'),
        },
        {
          path: 'catalogos/marcas',
          name: 'marcas',
          component: () => import('@/views/catalogos/MarcasView.vue'),
        },
        {
          path: 'catalogos/unidades-medida',
          name: 'unidades-medida',
          component: () => import('@/views/catalogos/UnidadesMedidaView.vue'),
        },
        {
          path: 'catalogos/productos',
          name: 'productos',
          component: () => import('@/views/catalogos/ProductosView.vue'),
        },
        {
          path: 'inventario/almacenes',
          name: 'almacenes',
          component: () => import('@/views/inventario/AlmacenesView.vue'),
        },
        {
          path: 'inventario/existencias',
          name: 'existencias',
          component: () => import('@/views/inventario/ExistenciasView.vue'),
        },
        {
          path: 'inventario/movimientos',
          name: 'movimientos',
          component: () => import('@/views/inventario/MovimientosView.vue'),
        },
        {
          path: 'inventario/kardex',
          name: 'kardex',
          component: () => import('@/views/inventario/KardexView.vue'),
        },
        {
          path: 'inventario/ingreso',
          name: 'ingreso-stock',
          component: () => import('@/views/inventario/IngresoStockView.vue'),
        },
        {
          path: 'inventario/salida',
          name: 'salida-stock',
          component: () => import('@/views/inventario/SalidaStockView.vue'),
        },
        {
          path: 'inventario/ajuste',
          name: 'ajuste-stock',
          component: () => import('@/views/inventario/AjusteStockView.vue'),
        },
        {
          path: 'inventario/transferencia',
          name: 'transferencia-stock',
          component: () => import('@/views/inventario/TransferenciaStockView.vue'),
        },
        {
          path: 'seguridad/usuarios',
          name: 'usuarios',
          component: () => import('@/views/seguridad/UsuariosView.vue'),
        },
        {
          path: 'seguridad/roles',
          name: 'roles',
          component: () => import('@/views/seguridad/RolesView.vue'),
        },
        {
          path: 'seguridad/permisos',
          name: 'permisos',
          component: () => import('@/views/seguridad/PermisosView.vue'),
        },
        { path: 'compras/proveedores', name: 'proveedores', component: () => import('@/views/compras/ProveedoresView.vue') },
        { path: 'compras/cotizaciones', name: 'cotizaciones-compra', component: () => import('@/views/compras/CotizacionesCompraView.vue') },
        { path: 'compras/ordenes', name: 'ordenes-compra', component: () => import('@/views/compras/OrdenesCompraView.vue') },
        { path: 'compras/recepciones', name: 'recepciones-compra', component: () => import('@/views/compras/RecepcionesCompraView.vue') },
        { path: 'ventas/clientes', name: 'clientes', component: () => import('@/views/ventas/ClientesView.vue') },
        { path: 'ventas/cotizaciones', name: 'cotizaciones-venta', component: () => import('@/views/ventas/CotizacionesVentaView.vue') },
        { path: 'ventas/ventas', name: 'ventas', component: () => import('@/views/ventas/VentasView.vue') },
        { path: 'ventas/facturas', name: 'facturas', component: () => import('@/views/ventas/FacturasView.vue') },
        { path: 'finanzas/cuentas-por-cobrar', name: 'cuentas-por-cobrar', component: () => import('@/views/finanzas/CuentasPorCobrarView.vue') },
        { path: 'finanzas/cuentas-por-pagar', name: 'cuentas-por-pagar', component: () => import('@/views/finanzas/CuentasPorPagarView.vue') },
        { path: 'finanzas/pagos', name: 'pagos', component: () => import('@/views/finanzas/PagosView.vue') },
        { path: 'finanzas/cobros', name: 'cobros', component: () => import('@/views/finanzas/CobrosView.vue') },
        { path: 'finanzas/cajas', name: 'cajas', component: () => import('@/views/finanzas/CajasView.vue') },
        { path: 'finanzas/bancos', name: 'bancos', component: () => import('@/views/finanzas/BancosView.vue') },
        { path: 'finanzas/movimientos', name: 'movimientos-financieros', component: () => import('@/views/finanzas/MovimientosFinancierosView.vue') },
        { path: 'reportes/stock', name: 'reporte-stock', component: () => import('@/views/reportes/ReporteStockView.vue') },
        { path: 'reportes/kardex', name: 'reporte-kardex', component: () => import('@/views/reportes/ReporteKardexView.vue') },
        { path: 'reportes/compras', name: 'reporte-compras', component: () => import('@/views/reportes/ReporteComprasView.vue') },
        { path: 'reportes/ventas', name: 'reporte-ventas', component: () => import('@/views/reportes/ReporteVentasView.vue') },
        { path: 'reportes/financiero', name: 'reporte-financiero', component: () => import('@/views/reportes/ReporteFinancieroView.vue') },
        { path: 'reportes/exportar', name: 'exportar-reportes', component: () => import('@/views/reportes/ExportReportesView.vue') },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/login',
    },
  ],
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()

  if (!authStore.initialized) {
    await authStore.initAuth()
  }

  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)
  const isGuest = to.matched.some((record) => record.meta.guest)

  if (requiresAuth && !authStore.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (isGuest && authStore.isAuthenticated) {
    return { name: 'dashboard' }
  }

  return true
})

export default router
