<script setup lang="ts">
import { computed, useSlots } from 'vue'

export interface TableHeader {
  title: string
  key: string
  sortable?: boolean
  align?: 'start' | 'center' | 'end'
  width?: string | number
}

const props = withDefaults(
  defineProps<{
    items: Record<string, unknown>[]
    headers: TableHeader[]
    loading?: boolean
    search?: string
    searchLabel?: string
    title?: string
    subtitle?: string
    showSearch?: boolean
    itemValue?: string
    emptyIcon?: string
    emptyTitle?: string
    emptySubtitle?: string
  }>(),
  {
    loading: false,
    search: '',
    searchLabel: 'Buscar en la tabla...',
    showSearch: true,
    itemValue: 'id',
    emptyIcon: 'mdi-database-off-outline',
    emptyTitle: 'Sin registros',
    emptySubtitle: 'No hay datos para mostrar.',
  },
)

const emit = defineEmits<{
  'update:search': [value: string]
}>()

const slots = useSlots()

const searchModel = computed({
  get: () => props.search,
  set: (value: string) => emit('update:search', value),
})

const tableSlotNames = computed(() =>
  Object.keys(slots).filter((name) => name !== 'actions' && name !== 'toolbar'),
)

function flattenValue(value: unknown): string {
  if (value == null) return ''
  if (typeof value === 'object') {
    if (Array.isArray(value)) {
      return value.map(flattenValue).join(' ')
    }
    return Object.values(value as Record<string, unknown>).map(flattenValue).join(' ')
  }
  return String(value)
}

const filteredItems = computed(() => {
  if (!props.search.trim()) return props.items
  const term = props.search.toLowerCase()
  return props.items.filter((item) => flattenValue(item).toLowerCase().includes(term))
})
</script>

<template>
  <v-card class="data-table-card" elevation="0" border>
    <v-card-title v-if="title || $slots.actions || $slots.toolbar" class="card-toolbar pa-3 pb-0">
      <div v-if="title" class="toolbar-text">
        <div class="text-subtitle-1 font-weight-bold">{{ title }}</div>
        <div v-if="subtitle" class="text-caption text-medium-emphasis mt-0">{{ subtitle }}</div>
      </div>
      <v-spacer />
      <div class="d-flex flex-wrap align-center ga-2">
        <slot name="toolbar" />
        <slot name="actions" />
      </div>
    </v-card-title>

    <v-card-text class="pa-3">
      <v-text-field
        v-if="showSearch"
        v-model="searchModel"
        :label="searchLabel"
        prepend-inner-icon="mdi-magnify"
        clearable
        hide-details
        density="compact"
        class="mb-2 search-field"
        bg-color="surface"
      />

      <v-data-table
        :headers="headers"
        :items="filteredItems"
        :loading="loading"
        :item-value="itemValue"
        density="compact"
        hover
        class="rounded-md data-table"
        :items-per-page="10"
        :items-per-page-options="[10, 25, 50]"
      >
        <template v-for="name in tableSlotNames" #[name]="slotData" :key="name">
          <slot :name="name" v-bind="slotData" />
        </template>

        <template #no-data>
          <div class="empty-state py-6 text-center">
            <v-icon :icon="emptyIcon" size="40" color="grey-lighten-1" class="mb-2" />
            <div class="text-body-2 font-weight-medium">{{ emptyTitle }}</div>
            <div class="text-caption text-medium-emphasis mt-1">{{ emptySubtitle }}</div>
          </div>
        </template>

        <template #loading>
          <v-skeleton-loader type="table-row@5" />
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>
</template>

<style scoped>
.data-table-card {
  overflow: hidden;
}

.card-toolbar {
  gap: 12px;
}

.search-field :deep(.v-field) {
  border-radius: 8px;
}

.data-table :deep(thead th) {
  font-weight: 600 !important;
  text-transform: uppercase;
  font-size: 0.6875rem !important;
  letter-spacing: 0.03em;
  color: rgba(var(--v-theme-on-surface), 0.55) !important;
  background: rgba(var(--v-theme-primary), 0.04);
}

.data-table :deep(tbody tr:hover) {
  background: rgba(var(--v-theme-primary), 0.03) !important;
}
</style>
