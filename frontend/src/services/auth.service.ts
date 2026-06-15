import { api } from './api'
import type {
  LoginRequest,
  LogoutRequest,
  MeResponse,
  Permiso,
  Rol,
  TokenResponse,
  Usuario,
} from '@/types/auth.types'

export const authService = {
  login(payload: LoginRequest) {
    return api.post<TokenResponse>('/auth/login', payload)
  },

  refresh(refreshToken: string) {
    return api.post<TokenResponse>('/auth/refresh', { refresh_token: refreshToken })
  },

  logout(payload: LogoutRequest) {
    return api.post('/auth/logout', payload)
  },

  me() {
    return api.get<MeResponse>('/auth/me')
  },

  getUsuarios() {
    return api.get<Usuario[]>('/auth/usuarios')
  },

  getRoles() {
    return api.get<Rol[]>('/auth/roles')
  },

  getPermisos() {
    return api.get<Permiso[]>('/auth/permisos')
  },
}
