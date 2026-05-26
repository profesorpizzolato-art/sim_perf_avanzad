import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Polygon, Rect, String

def crear_certificado_pdf(nombre_alumno, desempeno=95, profundidad=2500.0):
    if not nombre_alumno: 
        nombre_alumno = "ALUMNO"
    alumno_text = str(nombre_alumno).upper()
    fecha_text = datetime.now().strftime("%B / %Y").capitalize()
    
    nombre_archivo = f"Certificado_{alumno_text.replace(' ', '_')}.pdf"
    
    # Documento horizontal sin márgenes externos para la pintura geométrica de los bordes
    doc = SimpleDocTemplate(
        nombre_archivo,
        pagesize=landscape(letter),
        leftMargin=0, rightMargin=0, topMargin=0, bottomMargin=0
    )
    
    story = []
    width, height = landscape(letter) # 792 x 612 puntos
    
    # --- CONSTRUCCIÓN DEL LIENZO GEOMÉTRICO (Fiel a la imagen corporativa) ---
    d = Drawing(width, height)
    
    # Fondo Crema Suave de fondo
    d.add(Rect(0, 0, width, height, fillColor=colors.HexColor("#F9F9F6"), strokeColor=None))
    
    # Esquina Superior Izquierda: Polígono Azul y Gris
    d.add(Polygon(points=[0, height, 250, height, 110, 0, 0, 0], fillColor=colors.HexColor("#112233"), strokeColor=None))
    d.add(Polygon(points=[250, height, 275, height, 125, 0, 110, 0], fillColor=colors.HexColor("#7A8A9E"), strokeColor=None))
    
    # Esquina Inferior Derecha: Polígono Azul y Gris (Efecto espejo)
    d.add(Polygon(points=[width-250, 0, width, 0, width, 250, width-110, 250], fillColor=colors.HexColor("#112233"), strokeColor=None))
    d.add(Polygon(points=[width-275, 0, width-240, 0, width-110, 250, width-125, 250], fillColor=colors.HexColor("#7A8A9E"), strokeColor=None))
    
    # Recuadro Blanco Interno (Contenedor del texto)
    m_pad = 35
    d.add(Rect(m_pad, m_pad, width - (m_pad*2), height - (m_pad*2), fillColor=colors.white, strokeColor=colors.HexColor("#E2E8F0"), strokeWidth=1))
    
    # Contenedor del Logo Superior Centrado "MENFA"
    cx = width / 2
    d.add(Rect(cx - 45, height - 105, 90, 45, fillColor=colors.HexColor("#112233"), strokeColor=None, rx=3, ry=3))
    d.add(String(cx, height - 91, "MENFA", textAnchor='middle', fontName='Helvetica-Bold', fontSize=14, fillColor=colors.HexColor("#FBBF24")))
    
    story.append(d)
    
    # Desplazamos el eje de escritura hacia arriba para posicionarlo dentro del contenedor blanco
    story.append(Spacer(1, -height + 160))
    
    # --- ESTILOS DE TEXTO LIMPIOS (Sin etiquetas HTML conflictivas) ---
    styles = getSampleStyleSheet()
    
    style_menfa = ParagraphStyle(
        'MenfaText', fontName='Helvetica', fontSize=15, leading=18,
        textColor=colors.HexColor("#112233"), alignment=1, spaceAfter=40
    )
    style_certificacion = ParagraphStyle(
        'CertText', fontName='Helvetica', fontSize=22, leading=26,
        textColor=colors.HexColor("#8A254B"), alignment=1, spaceAfter=6
    )
    style_curso_label = ParagraphStyle(
        'CursoLabel', fontName='Helvetica', fontSize=18, leading=22,
        textColor=colors.HexColor("#8A254B"), alignment=1, spaceAfter=25
    )
    style_alumno = ParagraphStyle(
        'AlumnoName', fontName='Helvetica-Bold', fontSize=48, leading=54,
        textColor=colors.HexColor("#112233"), alignment=1, spaceAfter=30
    )
    style_nombre_curso = ParagraphStyle(
        'CursoName', fontName='Helvetica-Bold', fontSize=24, leading=28,
        textColor=colors.HexColor("#8A254B"), alignment=1, spaceAfter=12
    )
    style_fecha = ParagraphStyle(
        'FechaText', fontName='Helvetica', fontSize=12, leading=15,
        textColor=colors.HexColor("#64748B"), alignment=1, spaceAfter=50
    )
    
    # --- FLUJO DE ELEMENTOS EN EL PANEL ---
    story.append(Paragraph("MENFA CAPACITACIONES", style_menfa))
    story.append(Paragraph("Certificado de finalización", style_certificacion))
    story.append(Paragraph("Curso", style_curso_label))
    story.append(Paragraph(alumno_text, style_alumno))
    story.append(Paragraph("Curso de perforación y producción petrolera", style_nombre_curso))
    story.append(Paragraph(fecha_text, style_fecha))
    
    # --- LÍNEA DE FIRMA Y DATOS DE VERIFICACIÓN ---
    style_autor = ParagraphStyle('AutorFirma', fontName='Helvetica-Bold', fontSize=14, leading=16, textColor=colors.HexColor("#8A254B"), alignment=1)
    style_cargo = ParagraphStyle('CargoFirma', fontName='Helvetica', fontSize=11, leading=13, textColor=colors.HexColor("#64748B"), alignment=1)
    style_valida = ParagraphStyle('ValidaMeta', fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor("#94A3B8"), alignment=2)
    
    d_line = Drawing(width, 30)
    d_line.add(Rect(cx - 110, 15, 220, 1, fillColor=colors.HexColor("#112233"), strokeColor=None))
    story.append(d_line)
    
    story.append(Spacer(1, -10))
    story.append(Paragraph("Fabricio Pizzolato", style_autor))
    story.append(Paragraph("Dirección general", style_cargo))
    
    story.append(Spacer(1, -15))
    story.append(Paragraph(f"ID: MNF-{profundidad:.0f}-{desempeño}<br>Validación Operacional", style_valida))
    
    # Compilación del documento final
    doc.build(story)
    
    with open(nombre_archivo, "rb") as f:
        pdf_bytes = f.read()
        
    try:
        os.remove(nombre_archivo)
    except:
        pass
        
    return pdf_bytes
