import { defineStore } from 'pinia'
import { ref } from 'vue'

type SnackbarColor = 'success' | 'error' | 'info' | 'warning'

export const useAppStore = defineStore('app', () => {
  const snackbar = ref({
    show: false,
    message: '',
    color: 'success' as SnackbarColor,
    timeout: 4000,
  })

  const drawer = ref(true)

  function showSnackbar(message: string, color: SnackbarColor = 'success') {
    snackbar.value = {
      show: true,
      message,
      color,
      timeout: 4000,
    }
  }

  function showSuccess(message: string) {
    showSnackbar(message, 'success')
  }

  function showError(message: string) {
    showSnackbar(message, 'error')
  }

  function showInfo(message: string) {
    showSnackbar(message, 'info')
  }

  function toggleDrawer() {
    drawer.value = !drawer.value
  }

  return {
    snackbar,
    drawer,
    showSnackbar,
    showSuccess,
    showError,
    showInfo,
    toggleDrawer,
  }
})
