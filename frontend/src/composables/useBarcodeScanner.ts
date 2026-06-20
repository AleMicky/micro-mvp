import { onMounted, onUnmounted } from 'vue'
import onScan from 'onscan.js'

interface OnScanOptions {
  suffixKeyCodes?: number[]
  reactToPaste?: boolean
  minLength?: number
  onScan?: (code: string, qty: number) => void
  onScanError?: (debug: unknown) => void
}

interface OnScanLib {
  attachTo: (element: Document | HTMLElement, options: OnScanOptions) => void
  detachFrom: (element: Document | HTMLElement) => void
  isAttachedTo: (element: Document | HTMLElement) => boolean
}

const scanner = onScan as unknown as OnScanLib

export function useBarcodeScanner(onCode: (codigo: string) => void) {
  onMounted(() => {
    if (scanner.isAttachedTo(document)) return
    scanner.attachTo(document, {
      suffixKeyCodes: [13],
      reactToPaste: false,
      minLength: 3,
      onScan: (code) => onCode(code),
      onScanError: (debug) => console.warn('Error de lectura de escáner', debug),
    })
  })

  onUnmounted(() => {
    if (scanner.isAttachedTo(document)) {
      scanner.detachFrom(document)
    }
  })
}
