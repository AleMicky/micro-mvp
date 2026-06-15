<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'
import { requiredRule, minLengthRule } from '@/utils/validation'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const identificador = ref('')
const password = ref('')
const showPassword = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

async function handleSubmit() {
  const validation = await formRef.value?.validate()
  if (!validation?.valid) return

  const success = await authStore.login({
    identificador: identificador.value.trim(),
    password: password.value,
  })

  if (success) {
    const redirect = (route.query.redirect as string) || '/dashboard'
    router.push(redirect)
  }
}
</script>

<template>
  <v-card class="login-card" elevation="8" border>
    <v-card-text class="pa-8">
      <div class="text-center mb-8">
        <v-avatar color="primary" size="72" rounded="xl" class="mb-4">
          <v-icon icon="mdi-cube-outline" size="36" color="white" />
        </v-avatar>
        <h1 class="text-h5 font-weight-bold mb-1">Bienvenido</h1>
        <p class="text-body-2 text-medium-emphasis">Ingresa a tu panel administrativo</p>
      </div>

      <v-alert
        v-if="authStore.lastError"
        type="error"
        variant="tonal"
        density="comfortable"
        class="mb-4"
        closable
        @click:close="authStore.lastError = ''"
      >
        {{ authStore.lastError }}
      </v-alert>

      <v-form ref="formRef" @submit.prevent="handleSubmit">
        <v-text-field
          v-model="identificador"
          label="Usuario o correo"
          prepend-inner-icon="mdi-account-outline"
          autocomplete="username"
          :rules="[requiredRule]"
          class="mb-2"
        />
        <v-text-field
          v-model="password"
          label="Contraseña"
          prepend-inner-icon="mdi-lock-outline"
          :type="showPassword ? 'text' : 'password'"
          :append-inner-icon="showPassword ? 'mdi-eye-off-outline' : 'mdi-eye-outline'"
          autocomplete="current-password"
          :rules="[requiredRule, minLengthRule(6)]"
          class="mb-2"
          @click:append-inner="showPassword = !showPassword"
        />
        <v-btn
          type="submit"
          color="primary"
          size="large"
          block
          class="mt-4"
          :loading="authStore.loading"
        >
          Iniciar sesión
        </v-btn>
      </v-form>

      <v-divider class="my-6" />

      <v-alert type="info" variant="tonal" density="compact">
        <div class="text-caption">
          <strong>Demo:</strong> admin / Admin123456
        </div>
      </v-alert>
    </v-card-text>
  </v-card>
</template>

<style scoped>
.login-card {
  backdrop-filter: blur(12px);
  background: rgba(255, 255, 255, 0.96) !important;
}
</style>
