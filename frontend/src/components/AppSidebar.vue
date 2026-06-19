<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'

const props = defineProps<{ modelValue: boolean }>()
const emit = defineEmits<{ 'update:modelValue': [value: boolean] }>()

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const openedGroups = ref<string[]>([])

const drawer = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit('update:modelValue', value),
})

interface MenuItem {
  title: string
  icon: string
  to?: string
  children?: MenuItem[]
}

const menuItems: MenuItem[] = [
  { title: 'Dashboard', icon: 'mdi-view-dashboard-outline', to: '/dashboard' },
  { title: 'Empresas', icon: 'mdi-domain', to: '/company/empresas' },
  {
    title: 'Clientes',
    icon: 'mdi-account-group-outline',
    children: [
      { title: 'Clientes', icon: 'mdi-account-outline', to: '/clientes/lista' },
      { title: 'Historial', icon: 'mdi-history', to: '/clientes/historial' },
      { title: 'Puntos', icon: 'mdi-star-outline', to: '/clientes/puntos' },
    ],
  },
  {
    title: 'Notificaciones',
    icon: 'mdi-bell-outline',
    children: [
      { title: 'Notificaciones', icon: 'mdi-bell-ring-outline', to: '/notificaciones' },
    ],
  },
  {
    title: 'Seguridad',
    icon: 'mdi-shield-account-outline',
    children: [
      { title: 'Usuarios', icon: 'mdi-account-group-outline', to: '/seguridad/usuarios' },
      { title: 'Roles', icon: 'mdi-badge-account-outline', to: '/seguridad/roles' },
      { title: 'Permisos', icon: 'mdi-key-outline', to: '/seguridad/permisos' },
    ],
  },
  {
    title: 'Catálogos',
    icon: 'mdi-book-open-page-variant-outline',
    children: [
      { title: 'Categorías', icon: 'mdi-shape-outline', to: '/catalogos/categorias' },
      { title: 'Marcas', icon: 'mdi-tag-outline', to: '/catalogos/marcas' },
      { title: 'Unidades de medida', icon: 'mdi-ruler', to: '/catalogos/unidades-medida' },
      { title: 'Productos', icon: 'mdi-package-variant-closed', to: '/catalogos/productos' },
    ],
  },
  {
    title: 'Inventario',
    icon: 'mdi-warehouse',
    children: [
      { title: 'Almacenes', icon: 'mdi-store-outline', to: '/inventario/almacenes' },
      { title: 'Existencias', icon: 'mdi-package-check', to: '/inventario/existencias' },
      { title: 'Movimientos', icon: 'mdi-swap-horizontal', to: '/inventario/movimientos' },
      { title: 'Kardex', icon: 'mdi-file-document-outline', to: '/inventario/kardex' },
      { title: 'Ingreso de stock', icon: 'mdi-arrow-down-bold-circle-outline', to: '/inventario/ingreso' },
      { title: 'Salida de stock', icon: 'mdi-arrow-up-bold-circle-outline', to: '/inventario/salida' },
      { title: 'Ajuste de stock', icon: 'mdi-tune-vertical', to: '/inventario/ajuste' },
      { title: 'Transferencia', icon: 'mdi-truck-delivery-outline', to: '/inventario/transferencia' },
    ],
  },
  {
    title: 'Compras',
    icon: 'mdi-cart-arrow-down',
    children: [
      { title: 'Proveedores', icon: 'mdi-truck-outline', to: '/compras/proveedores' },
      { title: 'Cotizaciones de compra', icon: 'mdi-file-document-edit-outline', to: '/compras/cotizaciones' },
      { title: 'Órdenes de compra', icon: 'mdi-clipboard-list-outline', to: '/compras/ordenes' },
      { title: 'Recepciones de compra', icon: 'mdi-package-down', to: '/compras/recepciones' },
    ],
  },
  {
    title: 'Ventas',
    icon: 'mdi-cart-arrow-up',
    children: [
      { title: 'Cotizaciones de venta', icon: 'mdi-file-document-edit-outline', to: '/ventas/cotizaciones' },
      { title: 'Ventas', icon: 'mdi-cash-register', to: '/ventas/ventas' },
      { title: 'Facturas', icon: 'mdi-receipt-text-outline', to: '/ventas/facturas' },
    ],
  },
  {
    title: 'Finanzas',
    icon: 'mdi-cash-multiple',
    children: [
      { title: 'Cuentas por cobrar', icon: 'mdi-cash-plus', to: '/finanzas/cuentas-por-cobrar' },
      { title: 'Cuentas por pagar', icon: 'mdi-cash-minus', to: '/finanzas/cuentas-por-pagar' },
      { title: 'Pagos', icon: 'mdi-bank-transfer-out', to: '/finanzas/pagos' },
      { title: 'Cobros', icon: 'mdi-bank-transfer-in', to: '/finanzas/cobros' },
      { title: 'Cajas', icon: 'mdi-cash', to: '/finanzas/cajas' },
      { title: 'Bancos', icon: 'mdi-bank-outline', to: '/finanzas/bancos' },
      { title: 'Movimientos financieros', icon: 'mdi-chart-timeline-variant', to: '/finanzas/movimientos' },
    ],
  },
  {
    title: 'Reportes',
    icon: 'mdi-chart-bar',
    children: [
      { title: 'Reporte de stock', icon: 'mdi-package-variant', to: '/reportes/stock' },
      { title: 'Reporte de kardex', icon: 'mdi-file-document-outline', to: '/reportes/kardex' },
      { title: 'Reporte de compras', icon: 'mdi-cart-arrow-down', to: '/reportes/compras' },
      { title: 'Reporte de ventas', icon: 'mdi-cart-arrow-up', to: '/reportes/ventas' },
      { title: 'Reporte financiero', icon: 'mdi-finance', to: '/reportes/financiero' },
      { title: 'Stock consolidado', icon: 'mdi-package-variant', to: '/reportes/stock-consolidado' },
      { title: 'Ventas del día', icon: 'mdi-calendar-today', to: '/reportes/ventas-dia' },
      { title: 'Exportar PDF / Excel', icon: 'mdi-download', to: '/reportes/exportar' },
    ],
  },
]

function syncOpenedGroups() {
  const path = route.path
  openedGroups.value = menuItems
    .filter((item) => item.children?.some((child) => child.to && path.startsWith(child.to)))
    .map((item) => item.title)
}

watch(() => route.path, syncOpenedGroups, { immediate: true })

function isActive(to?: string) {
  return to ? route.path === to : false
}

function isGroupActive(item: MenuItem) {
  return item.children?.some((child) => child.to && route.path.startsWith(child.to)) ?? false
}

async function handleLogout() {
  await authStore.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <v-navigation-drawer
    v-model="drawer"
    app
    :permanent="!$vuetify.display.smAndDown"
    :temporary="$vuetify.display.smAndDown"
    width="272"
    class="sidebar"
    :border="false"
  >
    <div class="sidebar__brand">
      <div class="sidebar__logo">
        <v-icon icon="mdi-cube-outline" size="20" color="white" />
      </div>
      <div class="sidebar__brand-text">
        <span class="sidebar__brand-name">Micro MVP</span>
        <span class="sidebar__brand-tag">ERP Admin</span>
      </div>
    </div>

    <div class="sidebar__nav">
      <v-list v-model:opened="openedGroups" nav density="compact" class="sidebar__list">
        <template v-for="item in menuItems" :key="item.title">
          <v-list-item
            v-if="!item.children"
            :to="item.to"
            class="sidebar__item"
            :class="{ 'sidebar__item--active': isActive(item.to) }"
          >
            <template #prepend>
              <v-icon :icon="item.icon" size="18" class="sidebar__icon" />
            </template>
            <v-list-item-title class="sidebar__label">{{ item.title }}</v-list-item-title>
          </v-list-item>

          <v-list-group v-else :value="item.title" class="sidebar__group">
            <template #activator="{ props: groupProps }">
              <v-list-item
                v-bind="groupProps"
                class="sidebar__item sidebar__item--parent"
                :class="{ 'sidebar__item--parent-active': isGroupActive(item) }"
              >
                <template #prepend>
                  <v-icon :icon="item.icon" size="18" class="sidebar__icon" />
                </template>
                <v-list-item-title class="sidebar__label">{{ item.title }}</v-list-item-title>
              </v-list-item>
            </template>

            <v-list-item
              v-for="child in item.children"
              :key="child.title"
              :to="child.to"
              class="sidebar__item sidebar__item--child"
              :class="{ 'sidebar__item--active': isActive(child.to) }"
            >
              <template #prepend>
                <span class="sidebar__dot" />
              </template>
              <v-list-item-title class="sidebar__label sidebar__label--child">{{ child.title }}</v-list-item-title>
            </v-list-item>
          </v-list-group>
        </template>
      </v-list>
    </div>

    <template #append>
      <div class="sidebar__footer">
        <button type="button" class="sidebar__logout" @click="handleLogout">
          <v-icon icon="mdi-logout" size="18" />
          <span>Cerrar sesión</span>
        </button>
      </div>
    </template>
  </v-navigation-drawer>
</template>

<style scoped>
.sidebar {
  background: #0f172a !important;
  border-right: 1px solid #1e293b !important;
}

.sidebar__brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 16px;
  border-bottom: 1px solid #1e293b;
  flex-shrink: 0;
}

.sidebar__logo {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: #2563eb;
  flex-shrink: 0;
}

.sidebar__brand-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.sidebar__brand-name {
  font-size: 0.9375rem;
  font-weight: 700;
  color: #f8fafc;
  line-height: 1.2;
  letter-spacing: -0.01em;
}

.sidebar__brand-tag {
  font-size: 0.6875rem;
  color: #64748b;
  margin-top: 2px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.sidebar__nav {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 12px 10px;
  scrollbar-width: thin;
  scrollbar-color: #334155 transparent;
}

.sidebar__nav::-webkit-scrollbar {
  width: 4px;
}

.sidebar__nav::-webkit-scrollbar-thumb {
  background: #334155;
  border-radius: 4px;
}

.sidebar__list {
  padding: 0;
  background: transparent;
}

.sidebar__list :deep(.v-list-group__items) {
  --indent-padding: 0px;
}

.sidebar__list :deep(.v-list-group__header .v-list-item__append) {
  color: #64748b;
}

.sidebar__item {
  margin-bottom: 1px;
  min-height: 36px !important;
  padding-inline: 10px !important;
  border-radius: 6px !important;
  color: #94a3b8 !important;
  transition: background 0.12s, color 0.12s;
}

.sidebar__item:hover {
  background: #1e293b !important;
  color: #e2e8f0 !important;
}

.sidebar__item--active {
  background: #1e293b !important;
  color: #f1f5f9 !important;
}

.sidebar__item--active .sidebar__icon {
  color: #60a5fa !important;
}

.sidebar__item--active .sidebar__dot {
  background: #60a5fa;
}

.sidebar__item--parent-active {
  color: #e2e8f0 !important;
}

.sidebar__item--parent-active .sidebar__icon {
  color: #60a5fa !important;
}

.sidebar__item--child {
  padding-inline-start: 28px !important;
  min-height: 34px !important;
}

.sidebar__icon {
  color: #64748b !important;
  margin-inline-end: 10px !important;
  opacity: 1 !important;
}

.sidebar__dot {
  display: block;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #475569;
  margin-inline-end: 10px;
  flex-shrink: 0;
}

.sidebar__label {
  font-size: 0.8125rem;
  font-weight: 500;
  line-height: 1.35;
  white-space: normal !important;
  overflow: visible !important;
  text-overflow: unset !important;
  word-break: break-word;
}

.sidebar__label--child {
  font-size: 0.8125rem;
  font-weight: 400;
}

.sidebar__item :deep(.v-list-item__overlay) {
  opacity: 0 !important;
}

.sidebar__footer {
  padding: 12px 10px 16px;
  border-top: 1px solid #1e293b;
  flex-shrink: 0;
}

.sidebar__logout {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #334155;
  border-radius: 6px;
  background: transparent;
  color: #94a3b8;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.12s, color 0.12s, border-color 0.12s;
}

.sidebar__logout:hover {
  background: #1e293b;
  color: #f87171;
  border-color: #475569;
}
</style>
