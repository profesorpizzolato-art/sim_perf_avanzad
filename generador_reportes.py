import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Polygon, Rect, String

def crear_certificado_pdf(nombre_alumno, score=95, profundidad=2500.0):
    # Validamos que el nombre contenga texto válido
    if not nombre_alumno or str(nombre_alumno).strip() == "": 
        nombre_alumno = "ALUMNO"
        
    alumno_text = str(nombre_alumno).upper()
    fecha_text = datetime.now().strftime("%B / %Y").capitalize()
    
    nombre_archivo = f"Certificado_{alumno_text.replace(' ', '_')}.pdf"
    
    # Configuración de página apaisada sin márgenes para permitir el trazado de los bordes azul/gris
    doc = SimpleDocTemplate(
        nombre_archivo,
        pagesize=landscape(letter),
        leftMargin=0, rightMargin=0, topMargin=0, bottomMargin=0
    )
    
    story = []
    width, height = landscape(letter) # Medidas estables: 792 x 612 puntos
    
    # --- RENDERIZADO DEL LIENZO GEOMÉTRICO (Identidad Visual MENFA) ---
    d = Drawing(width, height)
    
    # Color de fondo institucional crema claro
    d.add(Rect(0, 0, width, height, fillColor=colors.HexColor("#F9F9F6"), strokeColor=None))
    
    # Esquina Superior Izquierda: Ala Azul Oscuro y Línea de acento Gris
    d.add(Polygon(points=[0, height, 250, height, 110, 0, 0, 0], fillColor=colors.HexColor("#0B1D33"), strokeColor=None))
    d.add(Polygon(points=[250, height, 275, height, 125, 0, 110, 0], fillColor=colors.HexColor("#7E8B9B"), strokeColor=None))
    
    # Esquina Inferior Derecha: Ala Azul Oscuro y Línea de acento Gris (Espejo)
    d.add(Polygon(points=[width-250, 0, width, 0, width, 250, width-110, 250], fillColor=colors.HexColor("#0B1D33"), strokeColor=None))
    d.add(Polygon(points=[width-275, 0, width-240, 0, width-110, 250, width-125, 250], fillColor=colors.HexColor("#7E8B9B"), strokeColor=None))
    
    # Contenedor central blanco para realzar los textos
    margin_frame = 35
    d.add(Rect(margin_frame, margin_frame, width - (margin_frame*2), height - (margin_frame*2), fillColor=colors.white, strokeColor=colors.HexColor("#E2E8F0"), strokeWidth=1))
    
    # Bloque superior para el Isotipo MENFA
    center_x = width / 2
    d.add(Rect(center_x - 45, height - 105, 90, 45, fillColor=colors.HexColor("#0B1D33"), strokeColor=None, rx=3, ry=3))
    d.add(String(center_x, height - 91, "MENFA", textAnchor='middle', fontName='Helvetica-Bold', fontSize=14, fillColor=colors.HexColor("#FBBF24")))
    
    story.append(d)
    
    # Ajuste de posición del cursor al interior del recuadro blanco
    story.append(Spacer(1, -height + 160))
    
    # --- DEFINICIÓN DE ESTILOS TIPOGRÁFICOS ---
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
        'SName', fontName='Helvetica-Bold', fontSize=48, leading=54,
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
    
    # --- CARGA DINÁMICA DE TEXTOS ---
    story.append(Paragraph("MENFA CAPACITACIONES", style_menfa_header))
    story.append(Paragraph("Certificado de finalización", style_cert_title))
    story.append(Paragraph("Curso", style_course_label))
    story.append(Paragraph(alumno_text, style_student_name))
    story.append(Paragraph("Curso de perforación y producción petrolera", style_course_name))
    story.append(Paragraph(fecha_text, style_date_footer))
    
    # --- ÁREA NATIVA DE FIRMA ---
    style_director = ParagraphStyle('DirName', fontName='Helvetica-Bold', fontSize=14, leading=16, textColor=colors.HexColor("#7D1E43"), alignment=1)
    style_rank = ParagraphStyle('DirRank', fontName='Helvetica', fontSize=11, leading=13, textColor=colors.HexColor("#64748B"), alignment=1)
    style_hash = ParagraphStyle('HashBlock', fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor("#94A3B8"), alignment=2)
    
    d_linea_firma = Drawing(width, 30)
    d_linea_firma.add(Rect(center_x - 110, 15, 220, 1, fillColor=colors.HexColor("#0B1D33"), strokeColor=None))
    story.append(d_linea_firma)
    
    story.append(Spacer(1, -10))
    story.append(Paragraph("Fabricio Pizzolato", style_director))
    story.append(Paragraph("Dirección general", style_rank))
    
    # Identificación técnica y hash operacional libre de caracteres especiales
    story.append(Spacer(1, -15))
    story.append(Paragraph(f"ID Verificacion: MNF-{profundidad:.0f}-{score}<br>Validacion Operacional", style_hash))
    
    # Construcción final del PDF binario
    doc.build(story)
    
    with open(nombre_archivo, "rb") as f:
        pdf_bytes = f.read()
        
    try:
        os.remove(nombre_archivo)
    except:
        pass
        
    return pdf_bytes
