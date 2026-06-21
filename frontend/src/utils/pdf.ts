import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'
import { APP_BRAND, SUPERMARKET_COLORS } from '@/config/brand'
import { formatMoney } from './format'
import type { Cliente, DetalleVenta, Factura, Venta } from '@/types/ventas.types'

function hexToRgb(hex: string): [number, number, number] {
  const n = parseInt(hex.replace('#', ''), 16)
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255]
}

const PRIMARY = hexToRgb(SUPERMARKET_COLORS.primary)
const ACCENT = hexToRgb(SUPERMARKET_COLORS.accent)
const MARGIN_X = 40

function drawHeader(doc: jsPDF, title: string, codigo: string): number {
  const pageWidth = doc.internal.pageSize.getWidth()

  doc.setFillColor(...PRIMARY)
  doc.rect(0, 0, pageWidth, 90, 'F')
  doc.setFillColor(...ACCENT)
  doc.rect(0, 88, pageWidth, 3, 'F')

  doc.setTextColor(255, 255, 255)
  doc.setFont('helvetica', 'bold')
  doc.setFontSize(18)
  doc.text(APP_BRAND.shortName, MARGIN_X, 38)
  doc.setFont('helvetica', 'normal')
  doc.setFontSize(10)
  doc.text(APP_BRAND.tagline, MARGIN_X, 56)

  doc.setFont('helvetica', 'bold')
  doc.setFontSize(16)
  doc.text(title, pageWidth - MARGIN_X, 38, { align: 'right' })
  doc.setFont('helvetica', 'normal')
  doc.setFontSize(11)
  doc.text(codigo, pageWidth - MARGIN_X, 56, { align: 'right' })

  return 120
}

function drawDetalleTable(doc: jsPDF, startY: number, detalles: DetalleVenta[], productoNombre: (productoId: number | null) => string) {
  const rows = detalles.map((d) => {
    const cantidad = Number(d.cantidad)
    const precio = Number(d.precio_unitario)
    const subtotal = d.subtotal != null ? Number(d.subtotal) : cantidad * precio
    return [productoNombre(d.producto_id), String(cantidad), formatMoney(precio), formatMoney(subtotal)]
  })

  autoTable(doc, {
    startY,
    head: [['Producto', 'Cantidad', 'Precio unitario', 'Subtotal']],
    body: rows,
    margin: { left: MARGIN_X, right: MARGIN_X },
    styles: { fontSize: 9, cellPadding: 6 },
    headStyles: { fillColor: PRIMARY, textColor: 255, fontStyle: 'bold' },
    alternateRowStyles: { fillColor: [255, 248, 240] },
    columnStyles: {
      1: { halign: 'right' },
      2: { halign: 'right' },
      3: { halign: 'right' },
    },
  })

  return (doc as unknown as { lastAutoTable: { finalY: number } }).lastAutoTable.finalY + 20
}

function drawFooter(doc: jsPDF) {
  const pageWidth = doc.internal.pageSize.getWidth()
  const pageHeight = doc.internal.pageSize.getHeight()
  doc.setDrawColor(...PRIMARY)
  doc.setLineWidth(0.5)
  doc.line(MARGIN_X, pageHeight - 50, pageWidth - MARGIN_X, pageHeight - 50)
  doc.setTextColor(140, 140, 140)
  doc.setFontSize(8)
  doc.text(`${APP_BRAND.companyName} · Generado el ${new Date().toLocaleString('es-BO')}`, MARGIN_X, pageHeight - 35)
  doc.text('Página 1', pageWidth - MARGIN_X, pageHeight - 35, { align: 'right' })
}

export interface VentaPdfContext {
  venta: Venta
  cliente: Cliente | null
  almacenNombre: string | null
  productoNombre: (productoId: number | null) => string
}

export function generarVentaPdf({ venta, cliente, almacenNombre, productoNombre }: VentaPdfContext): void {
  const doc = new jsPDF({ unit: 'pt', format: 'a4' })
  const pageWidth = doc.internal.pageSize.getWidth()

  let y = drawHeader(doc, 'COMPROBANTE DE VENTA', venta.codigo)
  doc.setTextColor(30, 30, 30)

  doc.setFont('helvetica', 'bold')
  doc.setFontSize(10)
  doc.text('Cliente', MARGIN_X, y)
  doc.text('Detalles de la venta', pageWidth / 2 + 10, y)

  doc.setFont('helvetica', 'normal')
  doc.setFontSize(10)
  doc.setTextColor(90, 90, 90)
  y += 16
  doc.text(cliente?.nombre ?? `Cliente #${venta.cliente_id}`, MARGIN_X, y)
  doc.text(`Estado: ${venta.estado}`, pageWidth / 2 + 10, y)
  y += 14
  if (cliente?.rfc) {
    doc.text(`RFC/NIT: ${cliente.rfc}`, MARGIN_X, y)
  }
  doc.text(`Fecha: ${venta.fecha ?? '—'}`, pageWidth / 2 + 10, y)
  y += 14
  if (cliente?.telefono) {
    doc.text(`Tel: ${cliente.telefono}`, MARGIN_X, y)
  }
  doc.text(`Almacén: ${almacenNombre ?? '—'}`, pageWidth / 2 + 10, y)

  y += 28

  const finalY = drawDetalleTable(doc, y, venta.detalles ?? [], productoNombre)
  const totalBoxWidth = 220
  const totalBoxX = pageWidth - MARGIN_X - totalBoxWidth

  doc.setFillColor(...ACCENT)
  doc.roundedRect(totalBoxX, finalY, totalBoxWidth, 40, 6, 6, 'F')
  doc.setTextColor(40, 30, 10)
  doc.setFont('helvetica', 'bold')
  doc.setFontSize(12)
  doc.text('TOTAL', totalBoxX + 14, finalY + 26)
  doc.text(formatMoney(venta.total), totalBoxX + totalBoxWidth - 14, finalY + 26, { align: 'right' })

  if (venta.observaciones) {
    doc.setTextColor(90, 90, 90)
    doc.setFont('helvetica', 'normal')
    doc.setFontSize(9)
    doc.text('Observaciones:', MARGIN_X, finalY + 16)
    doc.text(doc.splitTextToSize(venta.observaciones, pageWidth - MARGIN_X * 2 - totalBoxWidth - 20), MARGIN_X, finalY + 30)
  }

  drawFooter(doc)
  doc.save(`${venta.codigo}.pdf`)
}

export interface FacturaPdfContext {
  factura: Factura
  venta: Venta | null
  cliente: Cliente | null
  productoNombre: (productoId: number | null) => string
}

export function generarFacturaPdf({ factura, venta, cliente, productoNombre }: FacturaPdfContext): void {
  const doc = new jsPDF({ unit: 'pt', format: 'a4' })
  const pageWidth = doc.internal.pageSize.getWidth()

  let y = drawHeader(doc, 'FACTURA', factura.codigo)
  doc.setTextColor(30, 30, 30)

  doc.setFont('helvetica', 'bold')
  doc.setFontSize(10)
  doc.text('Cliente', MARGIN_X, y)
  doc.text('Detalles de la factura', pageWidth / 2 + 10, y)

  doc.setFont('helvetica', 'normal')
  doc.setFontSize(10)
  doc.setTextColor(90, 90, 90)
  y += 16
  doc.text(cliente?.nombre ?? (venta ? `Cliente #${venta.cliente_id}` : '—'), MARGIN_X, y)
  doc.text(`Estado: ${factura.estado}`, pageWidth / 2 + 10, y)
  y += 14
  if (cliente?.rfc) {
    doc.text(`RFC/NIT: ${cliente.rfc}`, MARGIN_X, y)
  }
  doc.text(`Fecha: ${factura.fecha ?? '—'}`, pageWidth / 2 + 10, y)
  y += 14
  if (cliente?.telefono) {
    doc.text(`Tel: ${cliente.telefono}`, MARGIN_X, y)
  }
  doc.text(`Venta: ${venta?.codigo ?? `#${factura.venta_id}`}`, pageWidth / 2 + 10, y)

  y += 28

  const finalY = drawDetalleTable(doc, y, factura.detalles ?? [], productoNombre)
  const totalBoxWidth = 220
  const totalBoxX = pageWidth - MARGIN_X - totalBoxWidth
  const summaryX = MARGIN_X

  doc.setTextColor(90, 90, 90)
  doc.setFont('helvetica', 'normal')
  doc.setFontSize(10)
  doc.text('Subtotal', summaryX, finalY + 12)
  doc.text(formatMoney(factura.subtotal), summaryX + 120, finalY + 12, { align: 'right' })
  doc.text('Impuesto', summaryX, finalY + 28)
  doc.text(formatMoney(factura.impuesto), summaryX + 120, finalY + 28, { align: 'right' })

  doc.setFillColor(...ACCENT)
  doc.roundedRect(totalBoxX, finalY, totalBoxWidth, 40, 6, 6, 'F')
  doc.setTextColor(40, 30, 10)
  doc.setFont('helvetica', 'bold')
  doc.setFontSize(12)
  doc.text('TOTAL', totalBoxX + 14, finalY + 26)
  doc.text(formatMoney(factura.total), totalBoxX + totalBoxWidth - 14, finalY + 26, { align: 'right' })

  drawFooter(doc)
  doc.save(`${factura.codigo}.pdf`)
}
