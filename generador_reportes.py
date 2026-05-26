import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Polygon, Rect, String

def crear_certificado_pdf(nombre_alumno, score=95, profundidad=2500.0):
    # Control de fallos para nombres vacíos
    if not nombre_alumno or str(nombre_alumno).strip() == "": 
        nombre_alumno = "ALUMNO EN ENTRENAMIENTO"
        
    alumno_text = str(nombre_alumno).upper()
    fecha_text = datetime.now().strftime("%B / %Y").capitalize()
    
    nombre_archivo = f"Certificado_{alumno_text.replace(' ', '_')}.pdf"
    
    # Setup del documento en formato horizontal estricto
    doc = SimpleDocTemplate(
        nombre_archivo,
        pagesize=landscape(letter),
        leftMargin=0, rightMargin=0, topMargin=0, bottomMargin=0
    )
    
    story = []
    width, height = landscape(letter) # Dimensiones de lienzo: 792 x 612 puntos
    
    # --- CAPA VECTORIAL: MAQUETA GEOMÉTRICA DE ALTA FIDELIDAD ---
    d = Drawing(width, height)
    
    # Fondo base crema corporativo tenue
    d.add(Rect(0, 0, width, height, fillColor=colors.HexColor("#F9F9F6"), strokeColor=None))
    
    # Ala Superior Izquierda: Polígono Azul de Control y línea Gris de realce técnico
    d.add(Polygon(points=[0, height, 250, height, 110, 0, 0, 0], fillColor=colors.HexColor("#0B1D33"), strokeColor=None))
    d.add(Polygon(points=[250, height, 275, height, 125, 0, 110, 0], fillColor=colors.HexColor("#7E8B9B"), strokeColor=None))
    
    # Ala Inferior Derecha: Polígono de simetría en espejo
    d.add(Polygon(points=[width-250, 0, width, 0, width, 250, width-110, 250], fillColor=colors.HexColor("#0B1D33"), strokeColor=None))
    d.add(Polygon(points=[width-275, 0, width-240, 0, width-110, 250, width-125, 250], fillColor=colors.HexColor("#7E8B9B"), strokeColor=None))
    
    # Paspartú / Recuadro Blanco de Contención de Texto
    margin_frame = 35
    d.add(Rect(margin_frame, margin_frame, width - (margin_frame*2), height - (margin_frame*2), fillColor=colors.white, strokeColor=colors.HexColor("#E2E8F0"), strokeWidth=1))
    
    # Emblema de la Institución MENFA (Bloque superior sólido)
    center_x = width / 2
    d.add(Rect(center_x - 45, height - 105, 90, 45, fillColor=colors.HexColor("#0B1D33"), strokeColor=None, rx=3, ry=3))
    d.add(String(center_x, height - 91, "MENFA", textAnchor='middle', fontName='Helvetica-Bold', fontSize=14, fillColor=colors.HexColor("#FBBF24")))
    
    story.append(d)
    
    # Desplazamiento inverso para comenzar las líneas de texto dentro del marco blanco
    story.append(Spacer(1, -height + 160))
    
    # --- ESTILOS TIPOGRÁFICOS SANITIZADOS (Sin HTML crudo) ---
    styles = getSampleStyleSheet()
    
    style_menfa_header = ParagraphStyle(
        'MHeader', fontName='Helvetica', fontSize=15, leading=18,
        textColor=colors.HexColor("#0B1D33"), alignment=1, spaceAfter=40
    )
    style_cert_title = ParagraphStyle(
        'CTitle', fontName='Helvetica', fontSize=22, leading=26,
        textColor=colors.HexColor("#7D1E43"), alignment=1, spaceAfter=6
    )
    style_course_label = ParagraphStyle(
        'CLabel', fontName='Helvetica', fontSize=18, leading=22,
        textColor=colors.HexColor("#7D1E43"), alignment=1, spaceAfter=25
    )
    style_student_name = ParagraphStyle(
        'SName', fontName='Helvetica-Bold', fontSize=44, leading=50,
        textColor=colors.HexColor("#0B1D33"), alignment=1, spaceAfter=30
    )
    style_course_name = ParagraphStyle(
        'CName', fontName='Helvetica-Bold', fontSize=24, leading=28,
        textColor=colors.HexColor("#7D1E43"), alignment=1, spaceAfter=12
    )
    style_date_footer = ParagraphStyle(
        'DFooter', fontName='Helvetica', fontSize=12, leading=15,
        textColor=colors.HexColor("#64748B"), alignment=1, spaceAfter=50
    )
    
    # --- ASIGNACIÓN DE CONTENIDO AL STORY ---
    story.append(Paragraph("MENFA CAPACITACIONES", style_menfa_header))
    story.append(Paragraph("Certificado de finalización", style_cert_title))
    story.append(Paragraph("Curso", style_course_label))
    story.append(Paragraph(alumno_text, style_student_name))
    story.append(Paragraph("Curso de perforación y producción petrolera", style_course_name))
    story.append(Paragraph(fecha_text, style_date_footer))
    
    # --- LÍNEA DE ACREDITACIÓN DE AUTORÍA Y DICTADO ---
    style_director = ParagraphStyle('DirName', fontName='Helvetica-Bold', fontSize=14, leading=16, textColor=colors.HexColor("#7D1E43"), alignment=1)
    style_rank = ParagraphStyle('DirRank', fontName='Helvetica', fontSize=11, leading=13, textColor=colors.HexColor("#64748B"), alignment=1)
    style_hash = ParagraphStyle('HashBlock', fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor("#94A3B8"), alignment=2)
    
    # Trazado de línea de firma
    d_linea_firma = Drawing(width, 30)
    d_linea_firma.add(Rect(center_x - 110, 15, 220, 1, fillColor=colors.HexColor("#0B1D33"), strokeColor=None))
    story.append(d_linea_firma)
    
    story.append(Spacer(1, -10))
    story.append(Paragraph("Fabricio Pizzolato", style_director))
    story.append(Paragraph("Dirección general", style_rank))
    
    # Bloque de metadatos del simulador (ID único de verificación analítica)
    story.append(Spacer(1, -15))
    story.append(Paragraph(f"ID Verificacion: MNF-{profundidad:.0f}-{score}<br>Validacion Operacional", style_hash))
    
    # Compilación y cierre de buffer
    doc.build(story)
    
    with open(nombre_archivo, "rb") as f:
        pdf_bytes = f.read()
        
    try:
        os.remove(nombre_archivo)
    except:
        pass
        
    return pdf_bytes
