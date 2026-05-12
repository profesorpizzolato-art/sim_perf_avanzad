from fpdf import FPDF
import datetime

def crear_certificado_pdf(nombre_alumno, puntaje, profundidad):
    # Inicialización del PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Marco del certificado
    pdf.set_line_width(1)
    pdf.rect(10, 10, 190, 277)
    
    # Título Principal
    pdf.set_font('Arial', 'B', 26)
    pdf.ln(50)
    pdf.cell(0, 15, 'CERTIFICADO DE LOGRO', 0, 1, 'C')
    
    pdf.set_font('Arial', '', 16)
    pdf.ln(10)
    pdf.cell(0, 10, 'MENFA Capacitaciones certifica que:', 0, 1, 'C')
    
    # Nombre del Alumno
    pdf.set_font('Arial', 'B', 24)
    pdf.ln(10)
    pdf.cell(0, 15, nombre_alumno.upper(), 0, 1, 'C')
    
    # Detalle Técnico de la simulación
    pdf.set_font('Arial', '', 14)
    pdf.ln(15)
    # Limpiamos el texto para evitar caracteres extraños que rompan el PDF
    texto = (f'Completo exitosamente el modulo de Simulacion de Perforacion Avanzada '
             f'en el yacimiento Mendoza, operando a una profundidad de {profundidad} metros '
             f'con un desempeno de {puntaje}/100.')
    pdf.multi_cell(0, 10, texto, align='C')
    
    # Fecha y Firma
    pdf.ln(30)
    pdf.set_font('Arial', 'I', 12)
    fecha = datetime.date.today().strftime('%d/%m/%Y')
    pdf.cell(0, 10, f'Fecha de Emision: {fecha}', 0, 1, 'C')
    
    # Línea de firma
    pdf.ln(20)
    pdf.line(70, 240, 140, 240)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 10, 'DIRECCION TECNICA - MENFA', 0, 1, 'C')
    
    # --- FIX CRÍTICO ---
    # Obtenemos la salida como string de bytes
    pdf_output = pdf.output(dest="S")
    
    # Si el resultado es una cadena (str), la pasamos a bytes usando latin-1
    # Si ya son bytes (común en Python 3.10+), los retornamos directamente
    if isinstance(pdf_output, str):
        return pdf_output.encode("latin-1")
    return bytes(pdf_output)
