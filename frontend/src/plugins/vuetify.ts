import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { es } from 'vuetify/locale'
import { SUPERMARKET_COLORS } from '@/config/brand'

export default createVuetify({
  components,
  directives,
  locale: {
    locale: 'es',
    messages: { es },
  },
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        dark: false,
        colors: {
          primary: SUPERMARKET_COLORS.primary,
          secondary: SUPERMARKET_COLORS.secondary,
          accent: SUPERMARKET_COLORS.accent,
          error: '#EF4444',
          info: '#0284C7',
          success: '#22C55E',
          warning: '#F59E0B',
          background: SUPERMARKET_COLORS.background,
          surface: '#FFFFFF',
          'surface-variant': SUPERMARKET_COLORS.backgroundAlt,
          'on-surface-variant': '#475569',
        },
      },
    },
  },
  defaults: {
    VBtn: {
      rounded: 'md',
      elevation: 0,
    },
    VCard: {
      rounded: 'lg',
      elevation: 0,
    },
    VTextField: {
      variant: 'outlined',
      density: 'compact',
      color: 'primary',
      hideDetails: 'auto',
    },
    VSelect: {
      variant: 'outlined',
      density: 'compact',
      color: 'primary',
      hideDetails: 'auto',
    },
    VTextarea: {
      variant: 'outlined',
      density: 'compact',
      color: 'primary',
      hideDetails: 'auto',
    },
    VChip: {
      rounded: 'md',
      size: 'small',
    },
    VDataTable: {
      density: 'compact',
      hover: true,
    },
    VList: {
      density: 'compact',
    },
    VListItem: {
      density: 'compact',
      rounded: 'md',
    },
  },
})
