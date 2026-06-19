<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useAppStore } from '@/stores/app.store'
import { useAuthStore } from '@/stores/auth.store'

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
  movimientos: 'Movimientos',
  kardex: 'Kardex',
  ingreso: 'Ingreso de stock',
  salida: 'Salida de stock',
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
  <v-app-bar app flat color="white" elevation="0" height="60" class="topbar">
    <div class="topbar__inner">
      <div class="topbar__left">
        <button
          type="button"
          class="topbar__icon-btn d-lg-none"
          aria-label="Abrir menú"
          @click="appStore.toggleDrawer()"
        >
          <v-icon icon="mdi-menu" size="20" />
        </button>

        <div class="topbar__context">
          <p class="topbar__eyebrow">Micro MVP</p>
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
                  <v-icon v-if="i > 0" icon="mdi-chevron-right" size="12" class="topbar__breadcrumb-sep" />
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
          <v-icon icon="mdi-bell-outline" size="20" />
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

          <v-card min-width="300" elevation="12" rounded="xl" class="topbar__dropdown">
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
  border-bottom: 1px solid #e2e8f0 !important;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}

.topbar :deep(.v-toolbar__content) {
  height: 60px !important;
  padding: 0 16px;
}

@media (min-width: 960px) {
  .topbar :deep(.v-toolbar__content) {
    padding: 0 24px;
  }
}

.topbar__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 16px;
  min-width: 0;
}

.topbar__left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
  flex: 1;
}

.topbar__context {
  min-width: 0;
}

.topbar__eyebrow {
  margin: 0 0 1px;
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #94a3b8;
  line-height: 1.2;
}

.topbar__heading-row {
  display: flex;
  align-items: center;
  gap: 16px;
  min-width: 0;
  flex-wrap: wrap;
}

.topbar__title {
  margin: 0;
  font-size: 1.0625rem;
  font-weight: 700;
  line-height: 1.25;
  letter-spacing: -0.02em;
  color: #0f172a;
  white-space: nowrap;
}

.topbar__breadcrumb-list {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 2px;
  margin: 0;
  padding: 6px 10px;
  list-style: none;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 999px;
}

.topbar__breadcrumb-item {
  display: inline-flex;
  align-items: center;
  font-size: 0.75rem;
  color: #94a3b8;
  line-height: 1;
}

.topbar__breadcrumb-item--active {
  color: #475569;
  font-weight: 500;
}

.topbar__breadcrumb-sep {
  margin: 0 4px;
  opacity: 0.5;
}

.topbar__actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.topbar__actions-divider {
  width: 1px;
  height: 24px;
  background: #e2e8f0;
  margin: 0 4px;
}

.topbar__icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #64748b;
  cursor: pointer;
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
}

.topbar__icon-btn:hover {
  background: #f1f5f9;
  color: #334155;
}

.topbar__icon-btn--active {
  background: #eff6ff;
  color: #2563eb;
}

.topbar__profile {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 8px 4px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #fff;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s, box-shadow 0.15s;
}

.topbar__profile:hover,
.topbar__profile--open {
  background: #f8fafc;
  border-color: #cbd5e1;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
}

.topbar__profile-text {
  flex-direction: column;
  align-items: flex-end;
  text-align: right;
  max-width: 160px;
}

.topbar__profile-name {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.25;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}

.topbar__profile-role {
  font-size: 0.6875rem;
  color: #94a3b8;
  line-height: 1.25;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}

.topbar__profile-chevron {
  color: #94a3b8;
  transition: transform 0.15s;
}

.topbar__profile--open .topbar__profile-chevron {
  transform: rotate(180deg);
}

.topbar__avatar {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  color: #fff;
  font-size: 0.75rem;
  font-weight: 700;
  flex-shrink: 0;
}

.topbar__avatar--lg {
  width: 44px;
  height: 44px;
  font-size: 0.875rem;
}

.topbar__avatar-status {
  position: absolute;
  right: -1px;
  bottom: -1px;
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: #22c55e;
  border: 2px solid #fff;
}

.topbar__avatar-status--lg {
  width: 11px;
  height: 11px;
}

.topbar__dropdown {
  overflow: hidden;
  border: 1px solid #e2e8f0 !important;
}

.topbar__dropdown-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: linear-gradient(180deg, #f8fafc 0%, #fff 100%);
}

.topbar__dropdown-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.topbar__dropdown-name {
  font-size: 0.9375rem;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.3;
}

.topbar__dropdown-email {
  font-size: 0.8125rem;
  color: #64748b;
  margin-top: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.topbar__dropdown-roles {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 12px 16px 0;
}

.topbar__role-chip {
  font-weight: 500;
}

.topbar__dropdown-meta {
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.topbar__meta-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.8125rem;
  color: #64748b;
}

.topbar__dropdown-footer {
  padding: 12px 16px 16px;
}

.topbar__logout-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #fecaca;
  border-radius: 8px;
  background: #fef2f2;
  color: #dc2626;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}

.topbar__logout-btn:hover {
  background: #fee2e2;
  border-color: #fca5a5;
}
</style>
