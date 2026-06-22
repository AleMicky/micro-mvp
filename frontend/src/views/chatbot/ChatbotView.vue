<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { chatbotService } from '@/services/chatbot.service'
import { getErrorMessage } from '@/services/api'
import { useAppStore } from '@/stores/app.store'
import type { Conversacion, Etiqueta, Mensaje } from '@/types/chatbot.types'

const POLL_MS = 7000
const TUNNEL_POLL_MS = 5000

const appStore = useAppStore()
const conversaciones = ref<Conversacion[]>([])
const mensajes = ref<Mensaje[]>([])
const seleccionId = ref<number | null>(null)
const cargandoConversaciones = ref(false)
const cargandoMensajes = ref(false)
const hiloContainer = ref<HTMLElement | null>(null)
const tunnelUrl = ref<string | null>(null)
const tunnelActivo = ref(false)
const tunnelCopiado = ref(false)
const respuestaTexto = ref('')
const enviandoRespuesta = ref(false)
const etiquetas = ref<Etiqueta[]>([])
const menuEtiquetasAbierto = ref(false)
const archivoSeleccionado = ref<File | null>(null)
const inputArchivoRef = ref<HTMLInputElement | null>(null)
const subiendoAdjunto = ref(false)
const ACCEPT_ADJUNTOS = '.jpg,.jpeg,.png,.webp,.pdf,.doc,.docx,.xls,.xlsx'
let intervalo: ReturnType<typeof setInterval> | null = null
let intervaloTunnel: ReturnType<typeof setInterval> | null = null

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

const puedeResponder = computed(() => {
  return conversacionSeleccionada.value !== null && conversacionSeleccionada.value.canal === 'whatsapp'
})

async function enviarRespuesta() {
  if (!seleccionId.value || !respuestaTexto.value.trim()) return
  enviandoRespuesta.value = true
  try {
    await chatbotService.responderConversacion(seleccionId.value, { texto: respuestaTexto.value.trim() })
    respuestaTexto.value = ''
    await cargarMensajes(seleccionId.value)
    await cargarConversaciones()
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    enviandoRespuesta.value = false
  }
}

function abrirSelectorArchivo() {
  inputArchivoRef.value?.click()
}

function onArchivoSeleccionado(event: Event) {
  const input = event.target as HTMLInputElement
  archivoSeleccionado.value = input.files?.[0] ?? null
}

function quitarArchivoSeleccionado() {
  archivoSeleccionado.value = null
  if (inputArchivoRef.value) inputArchivoRef.value.value = ''
}

function formatearTamano(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

async function enviarAdjunto() {
  if (!seleccionId.value || !archivoSeleccionado.value) return
  subiendoAdjunto.value = true
  try {
    await chatbotService.responderConversacionConAdjunto(
      seleccionId.value,
      archivoSeleccionado.value,
      respuestaTexto.value.trim() || undefined,
    )
    quitarArchivoSeleccionado()
    respuestaTexto.value = ''
    await cargarMensajes(seleccionId.value)
    await cargarConversaciones()
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  } finally {
    subiendoAdjunto.value = false
  }
}

async function enviarMensajeOAdjunto() {
  if (archivoSeleccionado.value) {
    await enviarAdjunto()
  } else {
    await enviarRespuesta()
  }
}

async function cargarEtiquetas() {
  try {
    const { data } = await chatbotService.getEtiquetas()
    etiquetas.value = data
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  }
}

function tieneEtiqueta(etiquetaId: number): boolean {
  return conversacionSeleccionada.value?.etiquetas.some((e) => e.id === etiquetaId) ?? false
}

async function toggleEtiqueta(etiqueta: Etiqueta) {
  if (!seleccionId.value) return
  try {
    if (tieneEtiqueta(etiqueta.id)) {
      await chatbotService.desasignarEtiqueta(seleccionId.value, etiqueta.id)
    } else {
      await chatbotService.asignarEtiqueta(seleccionId.value, etiqueta.id)
    }
    await cargarConversaciones()
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  }
}

async function cargarTunnelUrl() {
  try {
    const { data } = await chatbotService.obtenerTunnelUrl()
    tunnelUrl.value = data.url
    tunnelActivo.value = data.activo
  } catch {
    tunnelUrl.value = null
    tunnelActivo.value = false
  }
}

async function copiarTunnelUrl() {
  if (!tunnelUrl.value) return
  try {
    await navigator.clipboard.writeText(tunnelUrl.value)
    tunnelCopiado.value = true
    setTimeout(() => (tunnelCopiado.value = false), 2000)
  } catch (e) {
    appStore.showError(getErrorMessage(e))
  }
}

watch(seleccionId, (id) => {
  if (id !== null) cargarMensajes(id)
  else mensajes.value = []
})

onMounted(() => {
  cargarConversaciones()
  cargarTunnelUrl()
  cargarEtiquetas()
  intervalo = setInterval(() => {
    cargarConversaciones()
    if (seleccionId.value !== null) cargarMensajes(seleccionId.value)
  }, POLL_MS)
  intervaloTunnel = setInterval(cargarTunnelUrl, TUNNEL_POLL_MS)
})

onUnmounted(() => {
  if (intervalo) clearInterval(intervalo)
  if (intervaloTunnel) clearInterval(intervaloTunnel)
})
</script>

<template>
  <div class="bandeja">
    <aside class="bandeja__lista">
      <div class="bandeja__lista-header">
        <v-icon icon="mdi-whatsapp" size="22" class="bandeja__lista-icon" />
        <h1 class="bandeja__lista-title">Chatbot</h1>
      </div>

      <div class="tunnel-banner" :class="{ 'tunnel-banner--inactivo': !tunnelActivo }">
        <div class="tunnel-banner__estado">
          <span class="tunnel-banner__dot" :class="{ 'tunnel-banner__dot--activo': tunnelActivo }" />
          <span>{{ tunnelActivo ? 'Túnel activo' : 'Túnel inactivo' }}</span>
        </div>
        <template v-if="tunnelActivo && tunnelUrl">
          <a :href="tunnelUrl" target="_blank" rel="noopener" class="tunnel-banner__url">{{ tunnelUrl }}</a>
          <v-btn
            size="x-small"
            variant="text"
            :icon="tunnelCopiado ? 'mdi-check' : 'mdi-content-copy'"
            @click="copiarTunnelUrl"
          />
        </template>
        <span v-else class="tunnel-banner__hint">make tunnel-chatbot</span>
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
          <span v-if="conversacion.etiquetas.length" class="bandeja__item-etiquetas">
            <span
              v-for="etq in conversacion.etiquetas"
              :key="etq.id"
              class="bandeja__etiqueta-chip"
              :style="{ backgroundColor: etq.color }"
            >
              {{ etq.nombre }}
            </span>
          </span>
        </span>
      </button>
    </aside>

    <section class="bandeja__hilo">
      <template v-if="conversacionSeleccionada">
        <div class="bandeja__hilo-header">
          <span class="bandeja__avatar">
            <v-icon icon="mdi-account" size="18" />
          </span>
          <div class="bandeja__hilo-header-info">
            <p class="bandeja__hilo-numero">{{ conversacionSeleccionada.sesion_id }}</p>
            <p class="bandeja__hilo-estado">Estado: {{ conversacionSeleccionada.estado }}</p>
          </div>
          <v-spacer />
          <span
            v-for="etq in conversacionSeleccionada.etiquetas"
            :key="etq.id"
            class="bandeja__etiqueta-chip bandeja__etiqueta-chip--header"
            :style="{ backgroundColor: etq.color }"
          >
            {{ etq.nombre }}
          </span>
          <v-menu v-model="menuEtiquetasAbierto" :close-on-content-click="false">
            <template #activator="{ props: menuProps }">
              <v-btn v-bind="menuProps" icon="mdi-tag-plus-outline" size="small" variant="text" />
            </template>
            <v-list density="compact">
              <v-list-item v-if="!etiquetas.length" disabled title="Sin etiquetas creadas" />
              <v-list-item
                v-for="etq in etiquetas"
                :key="etq.id"
                :title="etq.nombre"
                @click="toggleEtiqueta(etq)"
              >
                <template #prepend>
                  <v-checkbox-btn :model-value="tieneEtiqueta(etq.id)" density="compact" />
                </template>
                <template #append>
                  <span class="bandeja__etiqueta-dot" :style="{ backgroundColor: etq.color }" />
                </template>
              </v-list-item>
            </v-list>
          </v-menu>
        </div>

        <div ref="hiloContainer" class="bandeja__hilo-mensajes">
          <div
            v-for="mensaje in mensajes"
            :key="mensaje.id"
            class="bandeja__fila"
            :class="{ 'bandeja__fila--saliente': mensaje.direccion === 'saliente' }"
          >
            <div
              class="bandeja__burbuja"
              :class="[
                `bandeja__burbuja--${mensaje.direccion}`,
                { 'bandeja__burbuja--agente': mensaje.origen === 'agente' },
              ]"
            >
              <div v-if="mensaje.tipo_mensaje !== 'texto'" class="bandeja__burbuja-adjunto">
                <v-icon :icon="mensaje.tipo_mensaje === 'imagen' ? 'mdi-image' : 'mdi-file-document'" size="18" />
                <span class="bandeja__burbuja-adjunto-nombre">{{ mensaje.nombre_archivo }}</span>
              </div>
              <p
                v-if="mensaje.tipo_mensaje === 'texto' || mensaje.texto !== mensaje.nombre_archivo"
                class="bandeja__burbuja-texto"
              >
                {{ mensaje.texto }}
              </p>
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

        <div v-if="archivoSeleccionado" class="bandeja__preview-adjunto">
          <v-icon :icon="archivoSeleccionado.type.startsWith('image/') ? 'mdi-image' : 'mdi-file-document'" size="20" />
          <span class="bandeja__preview-adjunto-nombre">{{ archivoSeleccionado.name }}</span>
          <span class="bandeja__preview-adjunto-tamano">{{ formatearTamano(archivoSeleccionado.size) }}</span>
          <v-btn icon="mdi-close" size="x-small" variant="text" :disabled="subiendoAdjunto" @click="quitarArchivoSeleccionado" />
        </div>

        <form class="bandeja__compositor" @submit.prevent="enviarMensajeOAdjunto">
          <input
            ref="inputArchivoRef"
            type="file"
            :accept="ACCEPT_ADJUNTOS"
            class="bandeja__input-archivo-oculto"
            @change="onArchivoSeleccionado"
          />
          <v-btn
            icon="mdi-paperclip"
            variant="text"
            :disabled="!puedeResponder || subiendoAdjunto"
            @click="abrirSelectorArchivo"
          />
          <v-textarea
            v-model="respuestaTexto"
            placeholder="Escribe una respuesta..."
            rows="1"
            auto-grow
            max-rows="4"
            density="compact"
            hide-details
            variant="outlined"
            class="bandeja__compositor-input"
            :disabled="!puedeResponder || enviandoRespuesta || subiendoAdjunto"
            @keydown.enter.exact.prevent="enviarMensajeOAdjunto"
          />
          <v-btn
            icon="mdi-send"
            color="primary"
            :disabled="!puedeResponder || (!archivoSeleccionado && !respuestaTexto.trim())"
            :loading="enviandoRespuesta || subiendoAdjunto"
            type="submit"
          />
        </form>
        <p v-if="conversacionSeleccionada && !puedeResponder" class="bandeja__compositor-hint">
          Solo se puede responder manualmente a conversaciones de WhatsApp.
        </p>
      </template>

      <div v-else class="bandeja__estado-vacio bandeja__estado-vacio--centro">
        <v-icon icon="mdi-whatsapp" size="48" class="bandeja__estado-vacio-icon" />
        <p>Selecciona una conversación para ver el hilo.</p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.tunnel-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-bottom: 1px solid #e2e8f0;
  background: #f0fdf4;
  font-size: 0.75rem;
  flex-shrink: 0;
}

.tunnel-banner--inactivo {
  background: #fef2f2;
}

.tunnel-banner__estado {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  color: #166534;
  flex-shrink: 0;
}

.tunnel-banner--inactivo .tunnel-banner__estado {
  color: #991b1b;
}

.tunnel-banner__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ef4444;
  flex-shrink: 0;
}

.tunnel-banner__dot--activo {
  background: #22c55e;
  animation: tunnel-pulse 1.6s infinite ease-in-out;
}

@keyframes tunnel-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.tunnel-banner__url {
  color: #0f172a;
  text-decoration: none;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 0;
  flex: 1;
}

.tunnel-banner__url:hover {
  text-decoration: underline;
}

.tunnel-banner__hint {
  color: #94a3b8;
  font-family: monospace;
}

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

.bandeja__burbuja--agente {
  background: #dbeafe;
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

.bandeja__hilo-header-info {
  min-width: 0;
}

.bandeja__etiqueta-chip {
  display: inline-flex;
  align-items: center;
  padding: 1px 8px;
  border-radius: 999px;
  font-size: 0.625rem;
  font-weight: 600;
  color: #fff;
  line-height: 1.6;
  white-space: nowrap;
}

.bandeja__etiqueta-chip--header {
  font-size: 0.6875rem;
  padding: 3px 10px;
}

.bandeja__item-etiquetas {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 4px;
}

.bandeja__etiqueta-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-left: 8px;
}

.bandeja__compositor {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  padding: 10px 16px;
  background: #fff;
  border-top: 1px solid #e2e8f0;
  flex-shrink: 0;
}

.bandeja__compositor-input {
  flex: 1;
}

.bandeja__compositor-hint {
  margin: 0;
  padding: 0 16px 8px;
  font-size: 0.6875rem;
  color: #94a3b8;
  text-align: center;
  background: #fff;
}

.bandeja__input-archivo-oculto {
  display: none;
}

.bandeja__preview-adjunto {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  font-size: 0.8125rem;
  color: #334155;
  flex-shrink: 0;
}

.bandeja__preview-adjunto-nombre {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.bandeja__preview-adjunto-tamano {
  color: #94a3b8;
  font-size: 0.75rem;
  flex-shrink: 0;
}

.bandeja__burbuja-adjunto {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 0;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #0f172a;
}
</style>
