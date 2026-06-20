<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useAppStore } from '@/stores/app.store'
import { useAuthStore } from '@/stores/auth.store'
import { SUPERMARKET_COLORS } from '@/config/brand'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const authStore = useAuthStore()
const { user } = storeToRefs(authStore)

const segmentLabels: Record<string, string> = {
  dashboard: 'Dashboard',
  company: 'Empresa',
  empresas: 'Empresas',
  clientes: 'Clientes',
  lista: 'Clientes',
  historial: 'Historial',
  puntos: 'Puntos',
  notificaciones: 'Notificaciones',
  chatbot: 'Chatbot',
  seguridad: 'Seguridad',
  usuarios: 'Usuarios',
  roles: 'Roles',
  permisos: 'Permisos',
  catalogos: 'Catálogos',
  categorias: 'Categorías',
  marcas: 'Marcas',
  'unidades-medida': 'Unidades de medida',
  productos: 'Productos',
  inventario: 'Inventario',
  almacenes: 'Almacenes',
  existencias: 'Existencias',
  movimientos: 'Operaciones de stock',
  operaciones: 'Operaciones de stock',
  kardex: 'Kardex',
  ingreso: 'Operaciones de stock',
  salida: 'Operaciones de stock',
  ajuste: 'Ajuste de stock',
  transferencia: 'Transferencia',
  compras: 'Compras',
  proveedores: 'Proveedores',
  cotizaciones: 'Cotizaciones',
  ordenes: 'Órdenes de compra',
  recepciones: 'Recepciones',
  ventas: 'Ventas',
  facturas: 'Facturas',
  finanzas: 'Finanzas',
  'cuentas-por-cobrar': 'Cuentas por cobrar',
  'cuentas-por-pagar': 'Cuentas por pagar',
  pagos: 'Pagos',
  cobros: 'Cobros',
  cajas: 'Cajas',
  bancos: 'Bancos',
  reportes: 'Reportes',
  stock: 'Reporte de stock',
  'stock-consolidado': 'Stock consolidado',
  'ventas-dia': 'Ventas del día',
  exportar: 'Exportar',
  financiero: 'Reporte financiero',
}

const breadcrumbs = computed(() => {
  const segments = route.path.split('/').filter(Boolean)
  return segments.map((segment, index) => ({
    label: segmentLabels[segment] ?? segment.replace(/-/g, ' '),
    isLast: index === segments.length - 1,
  }))
})

const pageTitle = computed(() => breadcrumbs.value.at(-1)?.label ?? 'Panel')

const initials = computed(() => {
  const name = user.value?.nombre_completo ?? 'U'
  return name
    .split(' ')
    .map((part) => part[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
})

const primaryRole = computed(() => user.value?.roles?.[0] ?? 'Usuario')

const lastLogin = computed(() => {
  const raw = user.value?.ultimo_login_en
  if (!raw) return null
  return new Date(raw).toLocaleString('es-MX', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
})

const isNotificationsActive = computed(() => route.path.startsWith('/notificaciones'))

async function handleLogout() {
  await authStore.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <v-app-bar app flat color="white" elevation="0" :height="44" class="topbar">
    <div class="topbar__inner">
      <div class="topbar__left">
        <button
          type="button"
          class="topbar__icon-btn d-lg-none"
          aria-label="Abrir menú"
          @click="appStore.toggleDrawer()"
        >
          <v-icon icon="mdi-menu" size="18" />
        </button>

        <div class="topbar__context">
          <div class="topbar__heading-row">
            <h1 class="topbar__title">{{ pageTitle }}</h1>
            <nav v-if="breadcrumbs.length > 1" class="topbar__breadcrumb d-none d-md-flex" aria-label="Ruta">
              <ol class="topbar__breadcrumb-list">
                <li
                  v-for="(crumb, i) in breadcrumbs"
                  :key="`${crumb.label}-${i}`"
                  class="topbar__breadcrumb-item"
                  :class="{ 'topbar__breadcrumb-item--active': crumb.isLast }"
                >
                  <v-icon v-if="i > 0" icon="mdi-chevron-right" size="10" class="topbar__breadcrumb-sep" />
                  <span>{{ crumb.label }}</span>
                </li>
              </ol>
            </nav>
          </div>
        </div>
      </div>

      <div class="topbar__actions">
        <router-link
          to="/notificaciones"
          class="topbar__icon-btn"
          :class="{ 'topbar__icon-btn--active': isNotificationsActive }"
          title="Notificaciones"
          aria-label="Notificaciones"
        >
          <v-icon icon="mdi-bell-outline" size="18" />
        </router-link>

        <span class="topbar__actions-divider" />

        <v-menu location="bottom end" offset="8" :close-on-content-click="false">
          <template #activator="{ props, isActive }">
            <button
              v-bind="props"
              type="button"
              class="topbar__profile"
              :class="{ 'topbar__profile--open': isActive }"
              aria-label="Menú de usuario"
            >
              <span class="topbar__profile-text d-none d-sm-flex">
                <span class="topbar__profile-name">{{ user?.nombre_completo }}</span>
                <span class="topbar__profile-role">{{ primaryRole }}</span>
              </span>
              <span class="topbar__avatar">
                {{ initials }}
                <span class="topbar__avatar-status" aria-hidden="true" />
              </span>
              <v-icon icon="mdi-chevron-down" size="16" class="topbar__profile-chevron d-none d-sm-block" />
            </button>
          </template>

          <v-card min-width="260" elevation="8" rounded="lg" class="topbar__dropdown">
            <div class="topbar__dropdown-header">
              <span class="topbar__avatar topbar__avatar--lg">
                {{ initials }}
                <span class="topbar__avatar-status topbar__avatar-status--lg" aria-hidden="true" />
              </span>
              <div class="topbar__dropdown-info">
                <span class="topbar__dropdown-name">{{ user?.nombre_completo }}</span>
                <span class="topbar__dropdown-email">{{ user?.correo }}</span>
              </div>
            </div>

            <div v-if="user?.roles?.length" class="topbar__dropdown-roles">
              <v-chip
                v-for="role in user.roles"
                :key="role"
                size="x-small"
                color="primary"
                variant="tonal"
                class="topbar__role-chip"
              >
                {{ role }}
              </v-chip>
            </div>

            <v-divider />

            <div class="topbar__dropdown-meta">
              <div class="topbar__meta-row">
                <v-icon icon="mdi-account-outline" size="16" />
                <span>{{ user?.nombre_usuario }}</span>
              </div>
              <div v-if="lastLogin" class="topbar__meta-row">
                <v-icon icon="mdi-clock-outline" size="16" />
                <span>Último acceso: {{ lastLogin }}</span>
              </div>
            </div>

            <div class="topbar__dropdown-footer">
              <button type="button" class="topbar__logout-btn" @click="handleLogout">
                <v-icon icon="mdi-logout" size="18" />
                Cerrar sesión
              </button>
            </div>
          </v-card>
        </v-menu>
      </div>
    </div>
  </v-app-bar>
</template>

<style scoped>
.topbar {
  border-bottom: 1px solid rgba(0, 0, 0, 0.06) !important;
  backdrop-filter: saturate(180%) blur(12px);
  background: rgba(255, 255, 255, 0.82) !important;
}

.topbar :deep(.v-toolbar__content) {
  height: 44px !important;
  padding: 0 12px;
}

@media (min-width: 960px) {
  .topbar :deep(.v-toolbar__content) {
    padding: 0 16px;
  }
}

.topbar__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 12px;
  min-width: 0;
}

.topbar__left {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  flex: 1;
}

.topbar__context {
  min-width: 0;
}

.topbar__heading-row {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
  flex-wrap: wrap;
}

.topbar__title {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 600;
  line-height: 1.2;
  letter-spacing: -0.02em;
  color: #1d1d1f;
  white-space: nowrap;
}

.topbar__breadcrumb-list {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 1px;
  margin: 0;
  padding: 3px 8px;
  list-style: none;
  background: rgba(0, 0, 0, 0.04);
  border-radius: 999px;
}

.topbar__breadcrumb-item {
  display: inline-flex;
  align-items: center;
  font-size: 0.6875rem;
  color: #86868b;
  line-height: 1;
}

.topbar__breadcrumb-item--active {
  color: #1d1d1f;
  font-weight: 500;
}

.topbar__breadcrumb-sep {
  margin: 0 3px;
  opacity: 0.45;
}

.topbar__actions {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.topbar__actions-divider {
  width: 1px;
  height: 18px;
  background: rgba(0, 0, 0, 0.08);
  margin: 0 2px;
}

.topbar__icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: #86868b;
  cursor: pointer;
  text-decoration: none;
  transition: background 0.12s, color 0.12s;
}

.topbar__icon-btn:hover {
  background: rgba(0, 0, 0, 0.05);
  color: #1d1d1f;
}

.topbar__icon-btn--active {
  background: #ffebee;
  color: v-bind('SUPERMARKET_COLORS.primary');
}

.topbar__profile {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 2px 6px 2px 8px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  transition: background 0.12s, border-color 0.12s;
}

.topbar__profile:hover,
.topbar__profile--open {
  background: rgba(0, 0, 0, 0.03);
  border-color: rgba(0, 0, 0, 0.12);
  box-shadow: none;
}

.topbar__profile-text {
  flex-direction: column;
  align-items: flex-end;
  text-align: right;
  max-width: 140px;
}

.topbar__profile-name {
  font-size: 0.75rem;
  font-weight: 600;
  color: #1d1d1f;
  line-height: 1.2;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}

.topbar__profile-role {
  font-size: 0.625rem;
  color: #86868b;
  line-height: 1.2;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}

.topbar__profile-chevron {
  color: #86868b;
  transition: transform 0.12s;
}

.topbar__profile--open .topbar__profile-chevron {
  transform: rotate(180deg);
}

.topbar__avatar {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  background: linear-gradient(135deg, v-bind('SUPERMARKET_COLORS.primary') 0%, v-bind('SUPERMARKET_COLORS.primaryDark') 100%);
  color: #fff;
  font-size: 0.6875rem;
  font-weight: 600;
  flex-shrink: 0;
}

.topbar__avatar--lg {
  width: 36px;
  height: 36px;
  font-size: 0.75rem;
}

.topbar__avatar-status {
  position: absolute;
  right: -1px;
  bottom: -1px;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #22c55e;
  border: 1.5px solid #fff;
}

.topbar__avatar-status--lg {
  width: 9px;
  height: 9px;
}

.topbar__dropdown {
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.08) !important;
}

.topbar__dropdown-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.02);
}

.topbar__dropdown-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.topbar__dropdown-name {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #1d1d1f;
  line-height: 1.25;
}

.topbar__dropdown-email {
  font-size: 0.75rem;
  color: #86868b;
  margin-top: 1px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.topbar__dropdown-roles {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  padding: 8px 12px 0;
}

.topbar__role-chip {
  font-weight: 500;
}

.topbar__dropdown-meta {
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.topbar__meta-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.75rem;
  color: #86868b;
}

.topbar__dropdown-footer {
  padding: 8px 12px 12px;
}

.topbar__logout-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  padding: 7px 12px;
  border: 1px solid #fecaca;
  border-radius: 6px;
  background: #fef2f2;
  color: #dc2626;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.12s, border-color 0.12s;
}

.topbar__logout-btn:hover {
  background: #fee2e2;
  border-color: #fca5a5;
}
</style>
