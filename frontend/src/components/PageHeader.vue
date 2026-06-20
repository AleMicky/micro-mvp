<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
  icon?: string
}>()
</script>

<template>
  <div class="page-header">
    <div class="d-flex align-center ga-2">
      <v-avatar v-if="icon" color="primary" variant="tonal" size="32" rounded="md">
        <v-icon :icon="icon" size="18" />
      </v-avatar>
      <div>
        <h1 class="page-header__title">{{ title }}</h1>
        <p v-if="subtitle" class="page-header__subtitle">{{ subtitle }}</p>
      </div>
    </div>
    <div v-if="$slots.actions" class="page-header__actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 14px;
}

.page-header__title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  line-height: 1.2;
  letter-spacing: -0.02em;
  color: #1d1d1f;
}

.page-header__subtitle {
  margin: 2px 0 0;
  color: #86868b;
  font-size: 0.75rem;
  line-height: 1.35;
}

.page-header__actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
</style>
