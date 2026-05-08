from fpdf import FPDF
import datetime

def crear_certificado_pdf(nombre_alumno, puntaje, profundidad):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_line_width(1)
    pdf.rect(10, 10, 190, 277)
    
    # Título
    pdf.set_font('Arial', 'B', 26)
    pdf.ln(50)
    pdf.cell(0, 15, 'CERTIFICADO DE LOGRO', 0, 1, 'C')
    
    pdf.set_font('Arial', '', 16)
    pdf.ln(10)
    pdf.cell(0, 10, 'MENFA Capacitaciones certifica que:', 0, 1, 'C')
    
    # Nombre
    pdf.set_font('Arial', 'B', 24)
    pdf.ln(10)
    pdf.cell(0, 15, nombre_alumno.upper(), 0, 1, 'C')
    
    # Detalle técnico
    pdf.set_font('Arial', '', 14)
    pdf.ln(15)
    texto = f'Completó exitosamente el módulo de Simulación de Perforación Avanzada en el yacimiento Mendoza, operando a una profundidad de {profundidad} metros con un desempeño de {puntaje}/100.'
    pdf.multi_cell(0, 10, texto, align='C')
    
    # Fecha y Firma
    pdf.ln(30)
    pdf.set_font('Arial', 'I', 12)
    fecha = datetime.date.today().strftime('%d/%m/%Y')
    pdf.cell(0, 10, f'Fecha: {fecha}', 0, 1, 'C')
    
    pdf.ln(20)
    pdf.line(70, 240, 140, 240)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 10, 'DIRECCIÓN TÉCNICA - MENFA', 0, 1, 'C')
    
    return pdf.output(dest="S").encode("latin-1")
