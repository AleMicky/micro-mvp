<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'
import { requiredRule, minLengthRule } from '@/utils/validation'
import { APP_BRAND } from '@/config/brand'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const identificador = ref('')
const password = ref('')
const showPassword = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

const DEMO_CREDENTIALS = {
  identificador: 'admin',
  password: 'Admin123456',
} as const

function fillDemoCredentials() {
  identificador.value = DEMO_CREDENTIALS.identificador
  password.value = DEMO_CREDENTIALS.password
  authStore.lastError = ''
}

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
  <div class="login-shell">
    <v-card class="login-card" elevation="0">
      <div class="login-card__hero">
        <div class="login-card__hero-glow" aria-hidden="true" />
        <div class="login-card__brand">
          <div class="login-card__logo" aria-hidden="true">
            <v-icon icon="mdi-store-outline" size="28" color="white" />
          </div>
          <div class="login-card__brand-text">
            <h1 class="login-card__title">{{ APP_BRAND.shortName }}</h1>
            <p class="login-card__subtitle">{{ APP_BRAND.tagline }}</p>
          </div>
        </div>
        <p class="login-card__badge">
          <v-icon icon="mdi-shield-account-outline" size="14" class="me-1" />
          Panel de administración
        </p>
      </div>

      <v-card-text class="login-card__body">
        <div class="login-card__intro">
          <h2 class="login-card__form-title">Iniciar sesión</h2>
          <p class="login-card__form-hint">
            Ingresa tus credenciales para acceder al sistema de inventario.
          </p>
        </div>

        <v-alert
          v-if="authStore.lastError"
          type="error"
          variant="tonal"
          density="comfortable"
          class="login-card__alert"
          closable
          icon="mdi-alert-circle-outline"
          @click:close="authStore.lastError = ''"
        >
          {{ authStore.lastError }}
        </v-alert>

        <v-form ref="formRef" class="login-form" @submit.prevent="handleSubmit">
          <v-text-field
            v-model="identificador"
            label="Usuario o correo"
            placeholder="ej. admin@empresa.com"
            prepend-inner-icon="mdi-account-outline"
            autocomplete="username"
            autofocus
            :rules="[requiredRule]"
          />
          <v-text-field
            v-model="password"
            label="Contraseña"
            placeholder="Mínimo 6 caracteres"
            prepend-inner-icon="mdi-lock-outline"
            :type="showPassword ? 'text' : 'password'"
            :append-inner-icon="showPassword ? 'mdi-eye-off-outline' : 'mdi-eye-outline'"
            autocomplete="current-password"
            :rules="[requiredRule, minLengthRule(6)]"
            @click:append-inner="showPassword = !showPassword"
          />

          <v-btn
            type="submit"
            color="primary"
            size="large"
            block
            class="login-card__submit"
            :loading="authStore.loading"
          >
            <v-icon icon="mdi-login" start size="18" />
            Iniciar sesión
          </v-btn>
        </v-form>

        <div class="login-demo">
          <div class="login-demo__label">
            <v-icon icon="mdi-flask-outline" size="16" class="me-1" />
            Acceso de demostración
          </div>
          <button
            type="button"
            class="login-demo__chip"
            :disabled="authStore.loading"
            @click="fillDemoCredentials"
          >
            <span class="login-demo__user">{{ DEMO_CREDENTIALS.identificador }}</span>
            <span class="login-demo__sep" aria-hidden="true">·</span>
            <span class="login-demo__pass">{{ DEMO_CREDENTIALS.password }}</span>
            <v-icon icon="mdi-arrow-right" size="14" class="login-demo__arrow" />
          </button>
          <p class="login-demo__hint">Toca para autocompletar los campos</p>
        </div>
      </v-card-text>

      <div class="login-card__footer">
        <p class="login-card__company">{{ APP_BRAND.companyName }}</p>
      </div>
    </v-card>
  </div>
</template>

<style scoped>
.login-shell {
  animation: login-enter 0.45s cubic-bezier(0.22, 1, 0.36, 1) both;
}

@keyframes login-enter {
  from {
    opacity: 0;
    transform: translateY(12px) scale(0.985);
  }

  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.login-card {
  overflow: hidden;
  border: 1px solid rgba(198, 40, 40, 0.12);
  box-shadow:
    0 1px 2px rgba(74, 21, 21, 0.04),
    0 12px 40px rgba(198, 40, 40, 0.12),
    0 24px 64px rgba(74, 21, 21, 0.08);
  backdrop-filter: blur(16px);
  background: rgba(255, 255, 255, 0.98) !important;
}

.login-card__hero {
  position: relative;
  padding: 28px 28px 24px;
  background: linear-gradient(135deg, #b71c1c 0%, #c62828 48%, #e65100 100%);
  color: #fff;
  overflow: hidden;
}

.login-card__hero-glow {
  position: absolute;
  top: -40%;
  right: -10%;
  width: 220px;
  height: 220px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.18) 0%, transparent 68%);
  pointer-events: none;
}

.login-card__brand {
  position: relative;
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 14px;
}

.login-card__logo {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.16);
  border: 1px solid rgba(255, 255, 255, 0.22);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.16);
  flex-shrink: 0;
}

.login-card__brand-text {
  min-width: 0;
}

.login-card__title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.login-card__subtitle {
  margin: 4px 0 0;
  font-size: 0.8125rem;
  opacity: 0.88;
  line-height: 1.35;
}

.login-card__badge {
  position: relative;
  display: inline-flex;
  align-items: center;
  margin: 0;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.login-card__body {
  padding: 28px !important;
}

.login-card__intro {
  margin-bottom: 22px;
}

.login-card__form-title {
  margin: 0 0 6px;
  font-size: 1.0625rem;
  font-weight: 600;
  letter-spacing: -0.02em;
  color: rgb(var(--v-theme-on-surface));
}

.login-card__form-hint {
  margin: 0;
  font-size: 0.8125rem;
  line-height: 1.45;
  color: rgba(var(--v-theme-on-surface), 0.58);
}

.login-card__alert {
  margin-bottom: 18px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.login-form :deep(.v-field) {
  border-radius: 10px;
}

.login-form :deep(.v-field--focused .v-field__outline) {
  --v-field-border-width: 2px;
}

.login-card__submit {
  margin-top: 10px;
  min-height: 44px !important;
  font-weight: 600;
  letter-spacing: -0.01em;
  box-shadow: 0 8px 20px rgba(198, 40, 40, 0.24);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.login-card__submit:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 10px 24px rgba(198, 40, 40, 0.28);
}

.login-card__submit:active:not(:disabled) {
  transform: translateY(0);
}

.login-demo {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px dashed rgba(198, 40, 40, 0.16);
}

.login-demo__label {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  color: rgba(var(--v-theme-on-surface), 0.52);
}

.login-demo__chip {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 11px 14px;
  border: 1px solid rgba(198, 40, 40, 0.14);
  border-radius: 10px;
  background: linear-gradient(180deg, #fffaf5 0%, #fff3e8 100%);
  color: rgb(var(--v-theme-on-surface));
  font-family: inherit;
  font-size: 0.8125rem;
  text-align: left;
  cursor: pointer;
  transition:
    border-color 0.15s ease,
    background 0.15s ease,
    transform 0.15s ease,
    box-shadow 0.15s ease;
}

.login-demo__chip:hover:not(:disabled) {
  border-color: rgba(198, 40, 40, 0.28);
  background: linear-gradient(180deg, #fff5eb 0%, #ffe8d4 100%);
  box-shadow: 0 4px 14px rgba(198, 40, 40, 0.08);
  transform: translateY(-1px);
}

.login-demo__chip:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-demo__user {
  font-weight: 600;
  color: #b71c1c;
}

.login-demo__sep {
  color: rgba(var(--v-theme-on-surface), 0.35);
}

.login-demo__pass {
  font-family: ui-monospace, 'SF Mono', Menlo, monospace;
  color: rgba(var(--v-theme-on-surface), 0.72);
}

.login-demo__arrow {
  margin-left: auto;
  color: rgba(var(--v-theme-on-surface), 0.42);
  transition: transform 0.15s ease, color 0.15s ease;
}

.login-demo__chip:hover:not(:disabled) .login-demo__arrow {
  transform: translateX(2px);
  color: #c62828;
}

.login-demo__hint {
  margin: 8px 0 0;
  font-size: 0.75rem;
  color: rgba(var(--v-theme-on-surface), 0.46);
}

.login-card__footer {
  padding: 14px 28px 18px;
  background: #fffaf5;
  border-top: 1px solid rgba(198, 40, 40, 0.08);
}

.login-card__company {
  margin: 0;
  font-size: 0.6875rem;
  line-height: 1.45;
  text-align: center;
  color: rgba(var(--v-theme-on-surface), 0.46);
}

@media (max-width: 600px) {
  .login-card__hero,
  .login-card__body {
    padding-left: 20px !important;
    padding-right: 20px !important;
  }

  .login-card__footer {
    padding-left: 20px;
    padding-right: 20px;
  }

  .login-card__title {
    font-size: 1.125rem;
  }
}
</style>
