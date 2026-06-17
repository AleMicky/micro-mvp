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
      { title: 'Clientes', icon: 'mdi-account-outline', to: '/ventas/clientes' },
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
    width="280"
    class="sidebar"
    border="end"
  >
    <div class="sidebar-brand pa-5">
      <v-avatar color="primary" size="42" rounded="lg" class="mr-3">
        <v-icon icon="mdi-cube-outline" color="white" />
      </v-avatar>
      <div>
        <div class="text-subtitle-1 font-weight-bold">Micro MVP</div>
        <div class="text-caption text-medium-emphasis">Panel administrativo</div>
      </div>
    </div>

    <v-divider />

    <v-list v-model:opened="openedGroups" nav density="comfortable" class="py-3 px-3">
      <template v-for="item in menuItems" :key="item.title">
        <v-list-item
          v-if="!item.children"
          :to="item.to"
          :prepend-icon="item.icon"
          :title="item.title"
          rounded="lg"
          color="primary"
          :active="isActive(item.to)"
        />
        <v-list-group v-else :value="item.title">
          <template #activator="{ props: groupProps }">
            <v-list-item v-bind="groupProps" :prepend-icon="item.icon" :title="item.title" rounded="lg" />
          </template>
          <v-list-item
            v-for="child in item.children"
            :key="child.title"
            :to="child.to"
            :prepend-icon="child.icon"
            :title="child.title"
            rounded="lg"
            color="primary"
            class="sidebar-subitem"
            :active="isActive(child.to)"
          />
        </v-list-group>
      </template>
    </v-list>

    <template #append>
      <v-divider />
      <div class="pa-4">
        <v-btn block variant="tonal" color="error" prepend-icon="mdi-logout" @click="handleLogout">Cerrar sesión</v-btn>
      </div>
    </template>
  </v-navigation-drawer>
</template>

<style scoped>
.sidebar { background: rgb(var(--v-theme-surface)); }
.sidebar-brand { display: flex; align-items: center; }
.sidebar-subitem { margin-left: 8px; }
</style>
