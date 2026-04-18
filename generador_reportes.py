from fpdf import FPDF
from datetime import datetime

def generar_pdf(piz, usuario):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "IPCL MENFA - REPORTE FINAL", 0, 1, 'C')
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, f"Alumno: {usuario}", 0, 1)
    pdf.cell(200, 10, f"Instructor: Fabricio Pizzolato", 0, 1)
    pdf.cell(200, 10, f"Profundidad: {piz['profundidad_actual']:.2f} m", 1, 1)
    return pdf.output(dest='S').encode('latin-1', 'ignore')
