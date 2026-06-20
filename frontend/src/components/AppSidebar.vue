<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'
import { APP_BRAND, SUPERMARKET_COLORS } from '@/config/brand'

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
  activePaths?: string[]
  children?: MenuItem[]
}

interface MenuSection {
  title: string
  items: MenuItem[]
}

const menuSections: MenuSection[] = [
  {
    title: '',
    items: [
      { title: 'Dashboard', icon: 'mdi-view-dashboard-outline', to: '/dashboard' },
    ],
  },
  {
    title: 'Operaciones',
    items: [
      {
        title: 'Ventas',
        icon: 'mdi-cash-register',
        children: [
          { title: 'Cotizaciones', icon: 'mdi-file-document-edit-outline', to: '/ventas/cotizaciones' },
          { title: 'Ventas', icon: 'mdi-point-of-sale', to: '/ventas/ventas' },
          { title: 'Facturas', icon: 'mdi-receipt-text-outline', to: '/ventas/facturas' },
        ],
      },
      {
        title: 'Compras',
        icon: 'mdi-cart-arrow-down',
        children: [
          { title: 'Cotizaciones', icon: 'mdi-file-document-edit-outline', to: '/compras/cotizaciones' },
          { title: 'Órdenes', icon: 'mdi-clipboard-list-outline', to: '/compras/ordenes' },
          { title: 'Recepciones', icon: 'mdi-package-down', to: '/compras/recepciones' },
        ],
      },
      {
        title: 'Inventario',
        icon: 'mdi-warehouse',
        children: [
          { title: 'Existencias', icon: 'mdi-package-check', to: '/inventario/existencias' },
          {
            title: 'Operaciones',
            icon: 'mdi-swap-vertical',
            to: '/inventario/operaciones',
            activePaths: ['/inventario/operaciones', '/inventario/ingreso', '/inventario/salida', '/inventario/movimientos'],
          },
          { title: 'Ajuste', icon: 'mdi-tune-vertical', to: '/inventario/ajuste' },
          { title: 'Transferencia', icon: 'mdi-truck-delivery-outline', to: '/inventario/transferencia' },
          { title: 'Kardex', icon: 'mdi-file-document-outline', to: '/inventario/kardex' },
        ],
      },
      {
        title: 'Finanzas',
        icon: 'mdi-cash-multiple',
        children: [
          { title: 'Cobros', icon: 'mdi-bank-transfer-in', to: '/finanzas/cobros' },
          { title: 'Pagos', icon: 'mdi-bank-transfer-out', to: '/finanzas/pagos' },
          { title: 'Por cobrar', icon: 'mdi-cash-plus', to: '/finanzas/cuentas-por-cobrar' },
          { title: 'Por pagar', icon: 'mdi-cash-minus', to: '/finanzas/cuentas-por-pagar' },
          { title: 'Cajas', icon: 'mdi-cash', to: '/finanzas/cajas' },
          { title: 'Bancos', icon: 'mdi-bank-outline', to: '/finanzas/bancos' },
          { title: 'Movimientos', icon: 'mdi-chart-timeline-variant', to: '/finanzas/movimientos' },
        ],
      },
    ],
  },
  {
    title: 'Parámetros',
    items: [
      { title: 'Productos', icon: 'mdi-package-variant-closed', to: '/catalogos/productos' },
      {
        title: 'Catálogos',
        icon: 'mdi-book-open-page-variant-outline',
        children: [
          { title: 'Categorías', icon: 'mdi-shape-outline', to: '/catalogos/categorias' },
          { title: 'Marcas', icon: 'mdi-tag-outline', to: '/catalogos/marcas' },
          { title: 'Unidades', icon: 'mdi-ruler', to: '/catalogos/unidades-medida' },
        ],
      },
      { title: 'Almacenes', icon: 'mdi-store-outline', to: '/inventario/almacenes' },
      {
        title: 'Clientes',
        icon: 'mdi-account-group-outline',
        children: [
          { title: 'Listado', icon: 'mdi-account-outline', to: '/clientes/lista' },
          { title: 'Historial', icon: 'mdi-history', to: '/clientes/historial' },
          { title: 'Puntos', icon: 'mdi-star-outline', to: '/clientes/puntos' },
        ],
      },
      { title: 'Proveedores', icon: 'mdi-truck-outline', to: '/compras/proveedores' },
      { title: 'Empresas', icon: 'mdi-domain', to: '/company/empresas' },
    ],
  },
  {
    title: 'Análisis',
    items: [
      {
        title: 'Reportes',
        icon: 'mdi-chart-bar',
        children: [
          { title: 'Stock', icon: 'mdi-package-variant', to: '/reportes/stock' },
          { title: 'Stock consolidado', icon: 'mdi-layers-outline', to: '/reportes/stock-consolidado' },
          { title: 'Kardex', icon: 'mdi-file-document-outline', to: '/reportes/kardex' },
          { title: 'Compras', icon: 'mdi-cart-arrow-down', to: '/reportes/compras' },
          { title: 'Ventas', icon: 'mdi-cart-arrow-up', to: '/reportes/ventas' },
          { title: 'Ventas del día', icon: 'mdi-calendar-today', to: '/reportes/ventas-dia' },
          { title: 'Financiero', icon: 'mdi-finance', to: '/reportes/financiero' },
          { title: 'Exportar', icon: 'mdi-download', to: '/reportes/exportar' },
        ],
      },
    ],
  },
  {
    title: 'Sistema',
    items: [
      {
        title: 'Seguridad',
        icon: 'mdi-shield-account-outline',
        children: [
          { title: 'Usuarios', icon: 'mdi-account-group-outline', to: '/seguridad/usuarios' },
          { title: 'Roles', icon: 'mdi-badge-account-outline', to: '/seguridad/roles' },
          { title: 'Permisos', icon: 'mdi-key-outline', to: '/seguridad/permisos' },
        ],
      },
      { title: 'Asistente IA', icon: 'mdi-robot-outline', to: '/chatbot' },
    ],
  },
]

function flattenMenuItems(): MenuItem[] {
  return menuSections.flatMap((section) => section.items)
}

function matchesMenuPath(item: Pick<MenuItem, 'to' | 'activePaths'>) {
  if (item.activePaths?.some((path) => route.path.startsWith(path))) return true
  return item.to ? route.path === item.to : false
}

function syncOpenedGroups() {
  const path = route.path
  openedGroups.value = flattenMenuItems()
    .filter((item) => item.children?.some((child) => child.to && (path.startsWith(child.to) || child.activePaths?.some((p) => path.startsWith(p)))))
    .map((item) => item.title)
}

watch(() => route.path, syncOpenedGroups, { immediate: true })

function isActive(item: Pick<MenuItem, 'to' | 'activePaths'>) {
  return matchesMenuPath(item)
}

function isGroupActive(item: MenuItem) {
  return item.children?.some((child) => matchesMenuPath(child)) ?? false
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
    width="220"
    class="sidebar"
    :border="false"
  >
    <div class="sidebar__brand">
      <div class="sidebar__logo">
        <v-icon icon="mdi-store" size="16" color="white" />
      </div>
      <div class="sidebar__brand-text">
        <span class="sidebar__brand-name" :title="APP_BRAND.companyName">{{ APP_BRAND.shortName }}</span>
        <span class="sidebar__brand-tag">{{ APP_BRAND.tagline }}</span>
      </div>
    </div>

    <div class="sidebar__nav">
      <v-list v-model:opened="openedGroups" nav density="compact" class="sidebar__list">
        <template v-for="section in menuSections" :key="section.title || 'inicio'">
          <div v-if="section.title" class="sidebar__section">
            <span class="sidebar__section-label">{{ section.title }}</span>
          </div>

          <template v-for="item in section.items" :key="`${section.title}-${item.title}`">
            <v-list-item
              v-if="!item.children"
              :to="item.to"
              class="sidebar__item"
              :class="{ 'sidebar__item--active': isActive(item) }"
            >
              <template #prepend>
                <v-icon :icon="item.icon" size="16" class="sidebar__icon" />
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
                    <v-icon :icon="item.icon" size="16" class="sidebar__icon" />
                  </template>
                  <v-list-item-title class="sidebar__label">{{ item.title }}</v-list-item-title>
                </v-list-item>
              </template>

              <v-list-item
                v-for="child in item.children"
                :key="child.title"
                :to="child.to"
                class="sidebar__item sidebar__item--child"
                :class="{ 'sidebar__item--active': isActive(child) }"
              >
                <template #prepend>
                  <span class="sidebar__dot" />
                </template>
                <v-list-item-title class="sidebar__label sidebar__label--child">{{ child.title }}</v-list-item-title>
              </v-list-item>
            </v-list-group>
          </template>
        </template>
      </v-list>
    </div>

    <template #append>
      <div class="sidebar__footer">
        <button type="button" class="sidebar__logout" @click="handleLogout">
          <v-icon icon="mdi-logout" size="16" />
          <span>Cerrar sesión</span>
        </button>
      </div>
    </template>
  </v-navigation-drawer>
</template>

<style scoped>
.sidebar {
  background: v-bind('SUPERMARKET_COLORS.sidebarBg') !important;
  border-right: 1px solid v-bind('SUPERMARKET_COLORS.sidebarBorder') !important;
}

.sidebar__brand {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-bottom: 1px solid v-bind('SUPERMARKET_COLORS.sidebarBorder');
  flex-shrink: 0;
}

.sidebar__logo {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  background: linear-gradient(135deg, v-bind('SUPERMARKET_COLORS.primary') 0%, v-bind('SUPERMARKET_COLORS.primaryDark') 100%);
  flex-shrink: 0;
}

.sidebar__brand-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.sidebar__brand-name {
  font-size: 0.8125rem;
  font-weight: 600;
  color: v-bind('SUPERMARKET_COLORS.sidebarTextBright');
  line-height: 1.15;
  letter-spacing: -0.02em;
}

.sidebar__brand-tag {
  font-size: 0.625rem;
  color: v-bind('SUPERMARKET_COLORS.sidebarMuted');
  margin-top: 1px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.sidebar__nav {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 6px 8px;
  scrollbar-width: thin;
  scrollbar-color: v-bind('SUPERMARKET_COLORS.sidebarBorder') transparent;
}

.sidebar__nav::-webkit-scrollbar {
  width: 4px;
}

.sidebar__nav::-webkit-scrollbar-thumb {
  background: v-bind('SUPERMARKET_COLORS.sidebarBorder');
  border-radius: 4px;
}

.sidebar__list {
  padding: 0;
  background: transparent;
}

.sidebar__section {
  padding: 10px 8px 4px;
}

.sidebar__section:first-child {
  padding-top: 4px;
}

.sidebar__section-label {
  display: block;
  font-size: 0.625rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: v-bind('SUPERMARKET_COLORS.sidebarMuted');
  opacity: 0.75;
  line-height: 1;
  user-select: none;
}

.sidebar__list :deep(.v-list-group__items) {
  --indent-padding: 0px;
}

.sidebar__list :deep(.v-list-group__header .v-list-item__append) {
  color: v-bind('SUPERMARKET_COLORS.sidebarMuted');
}

.sidebar__item {
  margin-bottom: 0;
  min-height: 28px !important;
  padding-inline: 8px !important;
  border-radius: 6px !important;
  color: v-bind('SUPERMARKET_COLORS.sidebarText') !important;
  transition: background 0.1s, color 0.1s;
}

.sidebar__item:hover {
  background: v-bind('SUPERMARKET_COLORS.sidebarHover') !important;
  color: v-bind('SUPERMARKET_COLORS.sidebarTextBright') !important;
}

.sidebar__item--active {
  background: v-bind('SUPERMARKET_COLORS.sidebarHover') !important;
  color: v-bind('SUPERMARKET_COLORS.sidebarTextBright') !important;
}

.sidebar__item--active .sidebar__icon {
  color: v-bind('SUPERMARKET_COLORS.sidebarActiveIcon') !important;
}

.sidebar__item--active .sidebar__dot {
  background: v-bind('SUPERMARKET_COLORS.sidebarActiveIcon');
}

.sidebar__item--parent-active {
  color: v-bind('SUPERMARKET_COLORS.sidebarTextBright') !important;
}

.sidebar__item--parent-active .sidebar__icon {
  color: v-bind('SUPERMARKET_COLORS.sidebarActiveIcon') !important;
}

.sidebar__item--child {
  padding-inline-start: 22px !important;
  min-height: 26px !important;
}

.sidebar__icon {
  color: v-bind('SUPERMARKET_COLORS.sidebarMuted') !important;
  margin-inline-end: 8px !important;
  opacity: 1 !important;
}

.sidebar__dot {
  display: block;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #8d4f4f;
  margin-inline-end: 8px;
  flex-shrink: 0;
}

.sidebar__label {
  font-size: 0.75rem;
  font-weight: 500;
  line-height: 1.25;
  white-space: normal !important;
  overflow: visible !important;
  text-overflow: unset !important;
  word-break: break-word;
}

.sidebar__label--child {
  font-size: 0.75rem;
  font-weight: 400;
}

.sidebar__item :deep(.v-list-item__overlay) {
  opacity: 0 !important;
}

.sidebar__footer {
  padding: 8px;
  border-top: 1px solid v-bind('SUPERMARKET_COLORS.sidebarBorder');
  flex-shrink: 0;
}

.sidebar__logout {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  padding: 6px 10px;
  border: 1px solid #8d4f4f;
  border-radius: 6px;
  background: transparent;
  color: v-bind('SUPERMARKET_COLORS.sidebarText');
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.1s, color 0.1s, border-color 0.1s;
}

.sidebar__logout:hover {
  background: v-bind('SUPERMARKET_COLORS.sidebarHover');
  color: #fca5a5;
  border-color: #a85a5a;
}
</style>
