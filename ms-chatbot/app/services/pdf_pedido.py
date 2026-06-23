from fpdf import FPDF


def _ascii_seguro(texto: str) -> str:
    return texto.encode("latin-1", "replace").decode("latin-1")


def generar_pdf_pedido(cotizacion: dict, carrito: dict, numero_whatsapp: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Cotizacion WhatsApp", ln=True)

    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, _ascii_seguro(f"Codigo de cotizacion: {cotizacion['codigo']}"), ln=True)
    pdf.cell(0, 8, _ascii_seguro(f"Cliente: Mostrador WhatsApp ({numero_whatsapp})"), ln=True)
    pdf.cell(0, 8, _ascii_seguro(f"Agencia: {carrito.get('agencia_nombre', '')}"), ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(90, 8, "Producto", border=1)
    pdf.cell(25, 8, "Cantidad", border=1, align="C")
    pdf.cell(35, 8, "Precio Unit.", border=1, align="R")
    pdf.cell(35, 8, "Subtotal", border=1, align="R", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 11)
    for item in carrito["items"]:
        subtotal = item["precio_unitario"] * item["cantidad"]
        pdf.cell(90, 8, _ascii_seguro(item["nombre"][:45]), border=1)
        pdf.cell(25, 8, str(item["cantidad"]), border=1, align="C")
        pdf.cell(35, 8, f"Bs. {item['precio_unitario']:.2f}", border=1, align="R")
        pdf.cell(35, 8, f"Bs. {subtotal:.2f}", border=1, align="R", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, f"TOTAL: Bs. {float(cotizacion['total']):.2f}", align="R")

    return bytes(pdf.output())
