import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify'
import { setSessionExpiredHandler } from './services/api'
import { useAuthStore } from './stores/auth.store'
import './styles/main.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(vuetify)

setSessionExpiredHandler(() => {
  const authStore = useAuthStore()
  authStore.resetSession(true)
  if (router.currentRoute.value.name !== 'login') {
    router.push({ name: 'login' })
  }
})

const authStore = useAuthStore()
authStore.initAuth().finally(() => {
  app.mount('#app')
})
