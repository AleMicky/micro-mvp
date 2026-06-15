<script setup lang="ts">
import { storeToRefs } from 'pinia'
import AppSidebar from '@/components/AppSidebar.vue'
import AppTopbar from '@/components/AppTopbar.vue'
import { useAppStore } from '@/stores/app.store'

const appStore = useAppStore()
const { drawer } = storeToRefs(appStore)
</script>

<template>
  <AppSidebar v-model="drawer" />
  <AppTopbar />
  <v-main class="admin-main">
    <v-container fluid class="admin-container">
      <router-view v-slot="{ Component, route }">
        <transition name="fade" mode="out-in">
          <div v-if="Component" :key="route.path" class="page-view">
            <component :is="Component" />
          </div>
        </transition>
      </router-view>
    </v-container>
  </v-main>
</template>

<style scoped>
.admin-main {
  background-color: rgb(var(--v-theme-background));
  min-height: 100vh;
}

.admin-container {
  padding: 24px 20px;
  max-width: 1440px;
}

@media (min-width: 960px) {
  .admin-container {
    padding: 28px 32px;
  }
}

.page-view {
  width: 100%;
}
</style>
