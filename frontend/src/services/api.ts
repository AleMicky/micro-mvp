import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import type { ApiError, TokenResponse } from '@/types/auth.types'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const TOKEN_EXPIRES_KEY = 'token_expires_at'
const REFRESH_MARGIN_MS = 60_000

export const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

let isRefreshing = false
let sessionExpiredHandled = false
let refreshTimer: ReturnType<typeof setTimeout> | null = null
let failedQueue: Array<{
  resolve: (token: string) => void
  reject: (error: unknown) => void
}> = []

type SessionExpiredHandler = () => void
let onSessionExpired: SessionExpiredHandler | null = null

export function setSessionExpiredHandler(handler: SessionExpiredHandler) {
  onSessionExpired = handler
}

function processQueue(error: unknown, token: string | null = null) {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error)
    } else if (token) {
      resolve(token)
    }
  })
  failedQueue = []
}

function decodeTokenExpiry(accessToken: string): number | null {
  try {
    const payload = JSON.parse(atob(accessToken.split('.')[1])) as { exp?: number }
    return payload.exp ? payload.exp * 1000 : null
  } catch {
    return null
  }
}

function getAccessTokenExpiry(): number | null {
  const stored = localStorage.getItem(TOKEN_EXPIRES_KEY)
  if (stored) {
    const expiresAt = Number(stored)
    if (!Number.isNaN(expiresAt)) return expiresAt
  }

  const accessToken = localStorage.getItem('access_token')
  if (!accessToken) return null
  return decodeTokenExpiry(accessToken)
}

function isAccessTokenExpired(marginMs = REFRESH_MARGIN_MS): boolean {
  const expiresAt = getAccessTokenExpiry()
  if (!expiresAt) return false
  return Date.now() >= expiresAt - marginMs
}

function clearRefreshTimer() {
  if (refreshTimer) {
    clearTimeout(refreshTimer)
    refreshTimer = null
  }
}

function scheduleTokenRefresh() {
  clearRefreshTimer()

  const refreshToken = localStorage.getItem('refresh_token')
  if (!refreshToken) return

  const expiresAt = getAccessTokenExpiry()
  if (!expiresAt) return

  const delay = Math.max(expiresAt - Date.now() - REFRESH_MARGIN_MS, 0)
  refreshTimer = setTimeout(() => {
    void performTokenRefresh().catch(() => {
      handleSessionExpired()
    })
  }, delay)
}

async function performTokenRefresh(): Promise<TokenResponse> {
  const refreshToken = localStorage.getItem('refresh_token')
  if (!refreshToken) {
    throw new Error('No refresh token')
  }

  const { data } = await axios.post<TokenResponse>(`${BASE_URL}/auth/refresh`, {
    refresh_token: refreshToken,
  })
  saveTokens(data.access_token, data.refresh_token, data.expires_in)
  return data
}

export function saveTokens(accessToken: string, refreshToken: string, expiresIn?: number) {
  localStorage.setItem('access_token', accessToken)
  localStorage.setItem('refresh_token', refreshToken)

  const expiresAt = expiresIn
    ? Date.now() + expiresIn * 1000
    : decodeTokenExpiry(accessToken)
  if (expiresAt) {
    localStorage.setItem(TOKEN_EXPIRES_KEY, String(expiresAt))
  }

  scheduleTokenRefresh()
}

export async function ensureValidSession(): Promise<boolean> {
  const refreshToken = localStorage.getItem('refresh_token')
  if (!refreshToken) return !!localStorage.getItem('access_token')

  if (!isAccessTokenExpired()) {
    scheduleTokenRefresh()
    return true
  }

  try {
    await performTokenRefresh()
    return true
  } catch {
    return false
  }
}

export function startSessionKeepAlive() {
  scheduleTokenRefresh()

  if (typeof document === 'undefined') return

  document.addEventListener('visibilitychange', handleVisibilityChange)
}

export function stopSessionKeepAlive() {
  clearRefreshTimer()
  if (typeof document === 'undefined') return
  document.removeEventListener('visibilitychange', handleVisibilityChange)
}

function handleVisibilityChange() {
  if (document.visibilityState !== 'visible') return
  if (!localStorage.getItem('refresh_token')) return
  if (!isAccessTokenExpired()) return

  void performTokenRefresh().catch(() => {
    handleSessionExpired()
  })
}

function handleSessionExpired() {
  if (sessionExpiredHandled) return
  sessionExpiredHandled = true
  stopSessionKeepAlive()
  clearTokens()
  onSessionExpired?.()
  setTimeout(() => {
    sessionExpiredHandled = false
  }, 500)
}

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiError>) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    if (!originalRequest || error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error)
    }

    const url = originalRequest.url ?? ''
    if (url.includes('/auth/login') || url.includes('/auth/refresh') || url.includes('/auth/logout')) {
      return Promise.reject(error)
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({
          resolve: (token: string) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            resolve(api(originalRequest))
          },
          reject,
        })
      })
    }

    originalRequest._retry = true
    isRefreshing = true

    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) {
      processQueue(error, null)
      isRefreshing = false
      handleSessionExpired()
      return Promise.reject(error)
    }

    try {
      const data = await performTokenRefresh()
      processQueue(null, data.access_token)
      originalRequest.headers.Authorization = `Bearer ${data.access_token}`
      return api(originalRequest)
    } catch (refreshError) {
      processQueue(refreshError, null)
      handleSessionExpired()
      return Promise.reject(refreshError)
    } finally {
      isRefreshing = false
    }
  },
)

export function clearTokens() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem(TOKEN_EXPIRES_KEY)
  clearRefreshTimer()
}

export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError<ApiError>(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) return detail.map((d) => d.msg).join(', ')
    return error.message
  }
  if (error instanceof Error) return error.message
  return 'Error inesperado'
}
