<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { chatbotService } from '@/services/chatbot.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import type { Conversacion, Mensaje } from '@/types/chatbot.types'

const POLL_MS = 7000

const appStore = useAppStore()
const conversaciones = ref<Conversacion[]>([])
const mensajes = ref<Mensaje[]>([])
const seleccionId = ref<number | null>(null)
const cargandoConversaciones = ref(false)
const cargandoMensajes = ref(false)
const hiloContainer = ref<HTMLElement | null>(null)
let intervalo: ReturnType<typeof setInterval> | null = null

const conversacionSeleccionada = computed(
  () => conversaciones.value.find((c) => c.id === seleccionId.value) ?? null,
)

function formatearHora(fecha: string | null): string {
  if (!fecha) return ''
  return new Date(fecha).toLocaleString('es-BO', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

async function cargarConversaciones() {
  cargandoConversaciones.value = true
  try {
    const { data } = await chatbotService.listarConversaciones()
    conversaciones.value = data
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    cargandoConversaciones.value = false
  }
}

async function cargarMensajes(conversacionId: number) {
  cargandoMensajes.value = true
  try {
    const { data } = await chatbotService.obtenerMensajes(conversacionId)
    mensajes.value = data
    scrollAlFinal()
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    cargandoMensajes.value = false
  }
}

const botEscribiendo = computed(() => {
  if (!mensajes.value.length) return false
  return mensajes.value[mensajes.value.length - 1].direccion === 'entrante'
})

async function scrollAlFinal() {
  await nextTick()
  hiloContainer.value?.scrollTo({ top: hiloContainer.value.scrollHeight, behavior: 'smooth' })
}

function seleccionarConversacion(conversacion: Conversacion) {
  seleccionId.value = conversacion.id
}

watch(seleccionId, (id) => {
  if (id !== null) cargarMensajes(id)
  else mensajes.value = []
})

onMounted(() => {
  cargarConversaciones()
  intervalo = setInterval(() => {
    cargarConversaciones()
    if (seleccionId.value !== null) cargarMensajes(seleccionId.value)
  }, POLL_MS)
})

onUnmounted(() => {
  if (intervalo) clearInterval(intervalo)
})
</script>

<template>
  <div class="bandeja">
    <aside class="bandeja__lista">
      <div class="bandeja__lista-header">
        <v-icon icon="mdi-whatsapp" size="22" class="bandeja__lista-icon" />
        <h1 class="bandeja__lista-title">Chatbot</h1>
      </div>

      <div v-if="cargandoConversaciones && !conversaciones.length" class="bandeja__estado-vacio">
        Cargando conversaciones...
      </div>
      <div v-else-if="!conversaciones.length" class="bandeja__estado-vacio">
        Sin conversaciones todavía.
      </div>

      <button
        v-for="conversacion in conversaciones"
        :key="conversacion.id"
        type="button"
        class="bandeja__item"
        :class="{ 'bandeja__item--activo': conversacion.id === seleccionId }"
        @click="seleccionarConversacion(conversacion)"
      >
        <span class="bandeja__avatar">
          <v-icon icon="mdi-account" size="18" />
        </span>
        <span class="bandeja__item-info">
          <span class="bandeja__item-top">
            <span class="bandeja__item-numero">{{ conversacion.sesion_id }}</span>
            <span class="bandeja__item-hora">{{ formatearHora(conversacion.ultimo_mensaje_en) }}</span>
          </span>
          <span class="bandeja__item-preview">{{ conversacion.ultimo_mensaje ?? 'Sin mensajes' }}</span>
        </span>
      </button>
    </aside>

    <section class="bandeja__hilo">
      <template v-if="conversacionSeleccionada">
        <div class="bandeja__hilo-header">
          <span class="bandeja__avatar">
            <v-icon icon="mdi-account" size="18" />
          </span>
          <div>
            <p class="bandeja__hilo-numero">{{ conversacionSeleccionada.sesion_id }}</p>
            <p class="bandeja__hilo-estado">Estado: {{ conversacionSeleccionada.estado }}</p>
          </div>
        </div>

        <div ref="hiloContainer" class="bandeja__hilo-mensajes">
          <div
            v-for="mensaje in mensajes"
            :key="mensaje.id"
            class="bandeja__fila"
            :class="{ 'bandeja__fila--saliente': mensaje.direccion === 'saliente' }"
          >
            <div class="bandeja__burbuja" :class="`bandeja__burbuja--${mensaje.direccion}`">
              <p class="bandeja__burbuja-texto">{{ mensaje.texto }}</p>
              <span class="bandeja__burbuja-hora">{{ formatearHora(mensaje.creado_en) }}</span>
            </div>
          </div>
          <div v-if="cargandoMensajes && !mensajes.length" class="bandeja__estado-vacio">
            Cargando mensajes...
          </div>
          <div v-if="botEscribiendo" class="bandeja__fila bandeja__fila--saliente">
            <div class="bandeja__burbuja bandeja__burbuja--saliente bandeja__burbuja--typing">
              <span class="bandeja__typing-dot" />
              <span class="bandeja__typing-dot" />
              <span class="bandeja__typing-dot" />
            </div>
          </div>
        </div>
      </template>

      <div v-else class="bandeja__estado-vacio bandeja__estado-vacio--centro">
        <v-icon icon="mdi-whatsapp" size="48" class="bandeja__estado-vacio-icon" />
        <p>Selecciona una conversación para ver el hilo.</p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.bandeja {
  display: flex;
  height: calc(100vh - 140px);
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
}

.bandeja__lista {
  width: 320px;
  flex-shrink: 0;
  border-right: 1px solid #e2e8f0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.bandeja__lista-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
}

.bandeja__lista-icon {
  color: #22c55e;
}

.bandeja__lista-title {
  margin: 0;
  font-size: 1.0625rem;
  font-weight: 700;
  color: #0f172a;
}

.bandeja__item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 12px 16px;
  border: none;
  border-bottom: 1px solid #f1f5f9;
  background: transparent;
  text-align: left;
  cursor: pointer;
  transition: background 0.12s;
}

.bandeja__item:hover {
  background: #f8fafc;
}

.bandeja__item--activo {
  background: #eff6ff;
}

.bandeja__avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #e2e8f0;
  color: #64748b;
  flex-shrink: 0;
}

.bandeja__item-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1;
}

.bandeja__item-top {
  display: flex;
  justify-content: space-between;
  gap: 8px;
}

.bandeja__item-numero {
  font-size: 0.875rem;
  font-weight: 600;
  color: #0f172a;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.bandeja__item-hora {
  font-size: 0.6875rem;
  color: #94a3b8;
  flex-shrink: 0;
}

.bandeja__item-preview {
  font-size: 0.8125rem;
  color: #64748b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.bandeja__hilo {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: #f8fafc;
}

.bandeja__hilo-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
}

.bandeja__hilo-numero {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 700;
  color: #0f172a;
}

.bandeja__hilo-estado {
  margin: 0;
  font-size: 0.75rem;
  color: #94a3b8;
}

.bandeja__hilo-mensajes {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.bandeja__fila {
  display: flex;
  justify-content: flex-start;
}

.bandeja__fila--saliente {
  justify-content: flex-end;
}

.bandeja__burbuja {
  max-width: 70%;
  padding: 8px 12px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.bandeja__burbuja--entrante {
  background: #fff;
  border-bottom-left-radius: 4px;
}

.bandeja__burbuja--saliente {
  background: #dcf8c6;
  border-bottom-right-radius: 4px;
}

.bandeja__burbuja-texto {
  margin: 0;
  font-size: 0.875rem;
  line-height: 1.45;
  white-space: pre-line;
  color: #0f172a;
}

.bandeja__burbuja-hora {
  font-size: 0.6875rem;
  color: #94a3b8;
  align-self: flex-end;
}

.bandeja__burbuja--typing {
  flex-direction: row;
  align-items: center;
  gap: 4px;
  padding: 12px 14px;
}

.bandeja__typing-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #6b7280;
  opacity: 0.4;
  animation: bandeja-typing-bounce 1.2s infinite ease-in-out;
}

.bandeja__typing-dot:nth-child(2) {
  animation-delay: 0.15s;
}

.bandeja__typing-dot:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes bandeja-typing-bounce {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-4px);
    opacity: 1;
  }
}

.bandeja__estado-vacio {
  padding: 24px 16px;
  text-align: center;
  color: #94a3b8;
  font-size: 0.875rem;
}

.bandeja__estado-vacio--centro {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.bandeja__estado-vacio-icon {
  color: #cbd5e1;
}
</style>
