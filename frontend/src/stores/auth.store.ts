import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { authService } from '@/services/auth.service'
import { clearTokens, getErrorMessage } from '@/services/api'
import type { LoginRequest, MeResponse } from '@/types/auth.types'
import { useAppStore } from './app.store'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<MeResponse | null>(null)
  const loading = ref(false)
  const initialized = ref(false)
  const lastError = ref('')

  const isAuthenticated = computed(() => !!user.value)
  const hasStoredToken = computed(() => !!localStorage.getItem('access_token'))

  function resetSession(showMessage = false) {
    user.value = null
    clearTokens()
    if (showMessage) {
      useAppStore().showInfo('Tu sesión ha expirado. Inicia sesión nuevamente.')
    }
  }

  async function login(payload: LoginRequest) {
    const appStore = useAppStore()
    loading.value = true
    lastError.value = ''
    try {
      const { data } = await authService.login(payload)
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      await fetchMe()
      appStore.showSuccess('Sesión iniciada correctamente')
      return true
    } catch (error) {
      lastError.value = getErrorMessage(error)
      appStore.showError(lastError.value)
      resetSession()
      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchMe() {
    if (!localStorage.getItem('access_token')) {
      user.value = null
      return
    }
    const { data } = await authService.me()
    user.value = data
  }

  async function logout() {
    const appStore = useAppStore()
    const refreshToken = localStorage.getItem('refresh_token')
    try {
      if (refreshToken) {
        await authService.logout({ refresh_token: refreshToken })
      }
    } catch {
      // Ignorar errores al cerrar sesión
    } finally {
      resetSession()
      appStore.showInfo('Sesión cerrada')
    }
  }

  async function initAuth() {
    if (!hasStoredToken.value) {
      initialized.value = true
      return
    }
    try {
      await fetchMe()
    } catch {
      resetSession()
    } finally {
      initialized.value = true
    }
  }

  return {
    user,
    loading,
    initialized,
    lastError,
    isAuthenticated,
    hasStoredToken,
    resetSession,
    login,
    fetchMe,
    logout,
    initAuth,
  }
})
