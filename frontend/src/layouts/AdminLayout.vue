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
    <div class="admin-content">
      <router-view v-slot="{ Component, route }">
        <transition name="page-switch" mode="out-in">
          <div v-if="Component" :key="route.path" class="admin-page">
            <component :is="Component" />
          </div>
        </transition>
      </router-view>
    </div>
  </v-main>
</template>

<style scoped>
.admin-main {
  --admin-bg: #f1f5f9;
  background: var(--admin-bg);
  min-height: 100vh;
}

.admin-content {
  max-width: 1440px;
  margin: 0 auto;
  padding: 24px 20px 40px;
  min-height: calc(100vh - 60px);
}

@media (min-width: 960px) {
  .admin-content {
    padding: 32px 40px 48px;
  }
}

.admin-page {
  width: 100%;
}

.page-switch-enter-active,
.page-switch-leave-active {
  transition: opacity 0.15s ease;
}

.page-switch-enter-from,
.page-switch-leave-to {
  opacity: 0;
}
</style>
