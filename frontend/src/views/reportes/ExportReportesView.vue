<script setup lang="ts">
import { computed, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import { reportesService } from '@/services/reportes.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'

interface TipoExportacion {
  value: string
  label: string
  description: string
  icon: string
  color: string
}

const appStore = useAppStore()
const tipo = ref('stock')
const loading = ref(false)
const loadingFormat = ref<'pdf' | 'excel' | null>(null)

const tipos: TipoExportacion[] = [
  {
    value: 'stock',
    label: 'Stock',
    description: 'Existencias por producto y almacén',
    icon: 'mdi-package-variant-closed',
    color: 'primary',
  },
  {
    value: 'productos',
    label: 'Productos',
    description: 'Catálogo completo de productos',
    icon: 'mdi-tag-multiple',
    color: 'secondary',
  },
  {
    value: 'compras',
    label: 'Compras',
    description: 'Órdenes de compra registradas',
    icon: 'mdi-cart-arrow-down',
    color: 'info',
  },
  {
    value: 'ventas',
    label: 'Ventas',
    description: 'Historial de ventas',
    icon: 'mdi-cash-register',
    color: 'success',
  },
  {
    value: 'finanzas',
    label: 'Finanzas',
    description: 'Cuentas por cobrar y por pagar',
    icon: 'mdi-cash-multiple',
    color: 'warning',
  },
]

const tipoSeleccionado = computed(() => tipos.find((t) => t.value === tipo.value) ?? tipos[0])

async function exportar(formato: 'pdf' | 'excel') {
  loading.value = true
  loadingFormat.value = formato
  try {
    const fn = formato === 'pdf' ? reportesService.exportarPdf : reportesService.exportarExcel
    const { data } = await fn(tipo.value)
    const ext = formato === 'pdf' ? 'txt' : 'csv'
    const url = URL.createObjectURL(data)
    const a = document.createElement('a')
    a.href = url
    a.download = `reporte_${tipo.value}.${ext}`
    a.click()
    URL.revokeObjectURL(url)
    appStore.showSuccess(`Reporte ${tipoSeleccionado.value.label} descargado (${formato === 'pdf' ? 'TXT' : 'CSV'})`)
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    loading.value = false
    loadingFormat.value = null
  }
}
</script>

<template>
  <div class="reporte-page">
    <PageHeader
      title="Exportar reportes"
      subtitle="Descarga de datos en CSV o texto"
      icon="mdi-download"
    />

    <div class="export-layout">
      <v-card class="export-types" border elevation="0">
        <div class="export-types__header">
          <span class="export-types__title">Tipo de reporte</span>
          <span class="export-types__hint text-caption text-medium-emphasis">Selecciona el dataset a exportar</span>
        </div>

        <div class="export-types__list">
          <button
            v-for="item in tipos"
            :key="item.value"
            type="button"
            class="export-type"
            :class="{ 'export-type--active': tipo === item.value }"
            @click="tipo = item.value"
          >
            <v-icon :icon="item.icon" :color="tipo === item.value ? item.color : undefined" size="20" />
            <span class="export-type__text">
              <span class="export-type__label">{{ item.label }}</span>
              <span class="export-type__desc text-caption text-medium-emphasis">{{ item.description }}</span>
            </span>
            <v-icon
              v-if="tipo === item.value"
              icon="mdi-check-circle"
              :color="item.color"
              size="18"
              class="export-type__check"
            />
          </button>
        </div>
      </v-card>

      <v-card class="export-actions" border elevation="0">
        <div class="summary-card summary-card--product export-preview">
          <span class="summary-card__label">Reporte seleccionado</span>
          <span class="summary-card__title">
            <v-icon :icon="tipoSeleccionado.icon" :color="tipoSeleccionado.color" size="18" class="mr-1" />
            {{ tipoSeleccionado.label }}
          </span>
          <span class="summary-card__meta text-caption text-medium-emphasis">{{ tipoSeleccionado.description }}</span>
        </div>

        <div class="export-buttons">
          <v-btn
            color="primary"
            variant="tonal"
            prepend-icon="mdi-file-document-outline"
            :loading="loading && loadingFormat === 'pdf'"
            :disabled="loading && loadingFormat !== 'pdf'"
            block
            @click="exportar('pdf')"
          >
            Exportar TXT
          </v-btn>
          <v-btn
            color="success"
            variant="tonal"
            prepend-icon="mdi-file-delimited-outline"
            :loading="loading && loadingFormat === 'excel'"
            :disabled="loading && loadingFormat !== 'excel'"
            block
            @click="exportar('excel')"
          >
            Exportar CSV
          </v-btn>
        </div>

        <p class="export-note text-caption text-medium-emphasis">
          El formato TXT incluye el JSON del reporte. CSV es compatible con Excel.
        </p>
      </v-card>
    </div>
  </div>
</template>

<style scoped>
@import '@/styles/reportes-shared.css';

.export-layout {
  display: grid;
  grid-template-columns: minmax(260px, 1fr) minmax(280px, 400px);
  gap: 12px;
  align-items: start;
}

.export-types {
  padding: 12px;
  background: #fff;
}

.export-types__header {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-bottom: 10px;
}

.export-types__title {
  font-size: var(--mac-text-sm);
  font-weight: 600;
}

.export-types__list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.export-type {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 8px 10px;
  border: 1px solid var(--mac-border);
  border-radius: var(--mac-radius-sm);
  background: #fff;
  text-align: left;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}

.export-type:hover {
  background: rgba(var(--v-theme-on-surface), 0.02);
}

.export-type--active {
  border-color: rgba(var(--v-theme-primary), 0.4);
  background: rgba(var(--v-theme-primary), 0.04);
}

.export-type__text {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.export-type__label {
  font-size: var(--mac-text-sm);
  font-weight: 600;
  line-height: 1.2;
}

.export-type__desc {
  line-height: 1.3;
}

.export-type__check {
  flex-shrink: 0;
}

.export-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 12px;
  background: #fff;
}

.export-preview {
  border: none;
  padding: 0;
  background: transparent;
}

.export-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.export-note {
  margin: 0;
  line-height: 1.4;
}

@media (max-width: 768px) {
  .export-layout {
    grid-template-columns: 1fr;
  }
}
</style>
