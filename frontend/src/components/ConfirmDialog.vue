<script setup lang="ts">
import { ref, watch } from 'vue'

const props = withDefaults(
  defineProps<{
    modelValue: boolean
    title?: string
    message?: string
    confirmText?: string
    confirmColor?: string
    icon?: string
    iconColor?: string
    loading?: boolean
  }>(),
  {
    title: 'Confirmar eliminación',
    message: '¿Está seguro de que desea eliminar este registro? Esta acción no se puede deshacer.',
    confirmText: 'Eliminar',
    confirmColor: 'error',
    icon: 'mdi-alert-circle-outline',
    iconColor: 'error',
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  confirm: []
}>()

const dialog = ref(props.modelValue)

watch(
  () => props.modelValue,
  (value) => {
    dialog.value = value
  },
)

watch(dialog, (value) => {
  emit('update:modelValue', value)
})

function handleConfirm() {
  emit('confirm')
}
</script>

<template>
  <v-dialog v-model="dialog" max-width="440" persistent>
    <v-card class="confirm-dialog" elevation="8">
      <v-card-text class="text-center pt-8 pb-2">
        <v-avatar :color="iconColor" variant="tonal" size="64" class="mb-4">
          <v-icon :icon="icon" size="32" />
        </v-avatar>
        <div class="text-h6 font-weight-bold mb-2">
          {{ title }}
        </div>
        <p class="text-body-2 text-medium-emphasis px-2">
          {{ message }}
        </p>
      </v-card-text>
      <v-card-actions class="pa-5 pt-2">
        <v-btn variant="outlined" block :disabled="loading" @click="dialog = false">
          Cerrar
        </v-btn>
        <v-btn :color="confirmColor" variant="flat" block :loading="loading" @click="handleConfirm">
          {{ confirmText }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style scoped>
.confirm-dialog :deep(.v-card-actions) {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
</style>
