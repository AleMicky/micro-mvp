<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useAppStore } from '@/stores/app.store'

const appStore = useAppStore()
const { snackbar } = storeToRefs(appStore)
</script>

<template>
  <v-app>
    <router-view />
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
      location="top right"
      elevation="8"
      rounded="lg"
    >
      <div class="d-flex align-center ga-2">
        <v-icon
          :icon="
            snackbar.color === 'success'
              ? 'mdi-check-circle-outline'
              : snackbar.color === 'error'
                ? 'mdi-alert-circle-outline'
                : 'mdi-information-outline'
          "
        />
        <span>{{ snackbar.message }}</span>
      </div>
      <template #actions>
        <v-btn icon="mdi-close" size="small" variant="text" @click="snackbar.show = false" />
      </template>
    </v-snackbar>
  </v-app>
</template>
