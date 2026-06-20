export function formatInteger(value: unknown): string {
  if (value == null || value === '') return '—'
  const n = Number(value)
  if (!Number.isFinite(n)) return String(value)
  return String(Math.trunc(n))
}

/** Formato en bolivianos: Bs 1.234,56 */
export function formatMoney(value: unknown): string {
  if (value == null || value === '') return '—'
  const n = Number(value)
  if (!Number.isFinite(n)) return '—'
  const amount = new Intl.NumberFormat('es-BO', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(n)
  return `Bs ${amount}`
}

export function formatDateCompact(value: string): string {
  return new Date(value).toLocaleString('es-BO', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}
