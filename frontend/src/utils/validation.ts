export const requiredRule = (value: unknown) => !!value || 'Campo requerido'

export const minLengthRule = (min: number) => (value: string) =>
  (value && value.length >= min) || `Mínimo ${min} caracteres`

export const positiveNumberRule = (value: unknown) =>
  (value !== null && value !== '' && Number(value) > 0) || 'Debe ser mayor a 0'

export const positiveIntegerRule = (value: unknown) =>
  (value !== null && value !== '' && Number.isInteger(Number(value)) && Number(value) > 0) ||
  'Debe ser un entero mayor a 0'

export const nonNegativeRule = (value: unknown) =>
  (value !== null && value !== '' && Number(value) >= 0) || 'Debe ser 0 o mayor'
