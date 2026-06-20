<template>
  <v-main class="auth-layout">
    <div class="auth-layout__bg" />
    <v-container fluid class="fill-height auth-layout__container">
      <v-row align="center" justify="center">
        <v-col cols="12" sm="10" md="6" lg="5" xl="4">
          <router-view v-slot="{ Component, route }">
            <transition name="fade" mode="out-in">
              <div v-if="Component" :key="route.path" class="page-view">
                <component :is="Component" />
              </div>
            </transition>
          </router-view>
        </v-col>
      </v-row>
    </v-container>
  </v-main>
</template>

<style scoped>
.auth-layout {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
}

.auth-layout__bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 20% 20%, rgba(198, 40, 40, 0.14), transparent 35%),
    radial-gradient(circle at 80% 0%, rgba(230, 81, 0, 0.12), transparent 30%),
    radial-gradient(circle at 60% 90%, rgba(255, 179, 0, 0.1), transparent 28%),
    linear-gradient(135deg, #fff8f0 0%, #fff3e0 45%, #ffebee 100%);
}

.auth-layout__container {
  position: relative;
  z-index: 1;
}
</style>
