<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useAppStore } from '@/stores/app.store'
import { useAuthStore } from '@/stores/auth.store'

const route = useRoute()
const appStore = useAppStore()
const authStore = useAuthStore()
const { user } = storeToRefs(authStore)

const breadcrumbs = computed(() => {
  const map: Record<string, string> = {
    dashboard: 'Dashboard',
    categorias: 'Categorías',
    marcas: 'Marcas',
    'unidades-medida': 'Unidades de medida',
    productos: 'Productos',
    almacenes: 'Almacenes',
    existencias: 'Existencias',
    movimientos: 'Movimientos',
    kardex: 'Kardex',
    'ingreso-stock': 'Ingreso de stock',
    'salida-stock': 'Salida de stock',
    'ajuste-stock': 'Ajuste de stock',
    'transferencia-stock': 'Transferencia',
    usuarios: 'Usuarios',
    roles: 'Roles',
    permisos: 'Permisos',
  }
  return map[String(route.name)] ?? 'Panel'
})

const initials = computed(() => {
  const name = user.value?.nombre_completo ?? 'U'
  return name
    .split(' ')
    .map((part) => part[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
})
</script>

<template>
  <v-app-bar app flat color="surface" elevation="0" height="72" border="b" class="topbar">
    <v-app-bar-nav-icon class="d-md-none" @click="appStore.toggleDrawer()" />

    <div class="topbar-content">
      <div class="text-caption text-medium-emphasis">Micro MVP / Admin</div>
      <div class="text-h6 font-weight-bold">{{ breadcrumbs }}</div>
    </div>

    <v-spacer />

    <v-menu location="bottom end" :close-on-content-click="false">
      <template #activator="{ props }">
        <v-btn v-bind="props" variant="text" class="user-menu-btn px-2">
          <div class="text-right d-none d-sm-block mr-3">
            <div class="text-body-2 font-weight-medium">{{ user?.nombre_completo }}</div>
            <div class="text-caption text-medium-emphasis">{{ user?.roles?.join(', ') }}</div>
          </div>
          <v-avatar color="primary" size="40">
            <span class="text-white text-body-2 font-weight-medium">{{ initials }}</span>
          </v-avatar>
        </v-btn>
      </template>
      <v-card min-width="260" class="pa-4">
        <div class="d-flex align-center ga-3 mb-3">
          <v-avatar color="primary" size="48">
            <span class="text-white">{{ initials }}</span>
          </v-avatar>
          <div>
            <div class="font-weight-medium">{{ user?.nombre_completo }}</div>
            <div class="text-caption text-medium-emphasis">{{ user?.correo }}</div>
          </div>
        </div>
        <v-chip size="small" color="primary" variant="tonal" class="mb-2">
          {{ user?.roles?.join(', ') }}
        </v-chip>
      </v-card>
    </v-menu>
  </v-app-bar>
</template>

<style scoped>
.topbar {
  backdrop-filter: blur(8px);
}

.topbar-content {
  padding-left: 4px;
}

.user-menu-btn {
  text-transform: none;
}
</style>
