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
    
    # Definimos el documento en formato horizontal (A4/Letter Landscape) sin márgenes para pintar los bordes
    doc = SimpleDocTemplate(
        nombre_archivo,
        pagesize=landscape(letter),
        leftMargin=0, rightMargin=0, topMargin=0, bottomMargin=0
    )
    
    story = []
    width, height = landscape(letter) # Dimensiones reales: 792 x 612 puntos
    
    # --- DIBUJO VECTORIAL DEL TEMPLATE ---
    d = Drawing(width, height)
    
    # 1. Fondo de lienzo (Crema Corporativo muy tenue)
    d.add(Rect(0, 0, width, height, fillColor=colors.HexColor("#F8FAFC"), strokeColor=None))
    
    # 2. Vector de Esquina Superior Izquierda (Azul Oscuro y Franja Gris)
    d.add(Polygon(points=[0, height, 240, height, 110, 0, 0, 0], fillColor=colors.HexColor("#1E293B"), strokeColor=None))
    d.add(Polygon(points=[240, height, 265, height, 125, 0, 110, 0], fillColor=colors.HexColor("#64748B"), strokeColor=None))
    
    # 3. Vector de Esquina Inferior Derecha (Espejo simétrico)
    d.add(Polygon(points=[width-240, 0, width, 0, width, 250, width-110, 250], fillColor=colors.HexColor("#1E293B"), strokeColor=None))
    d.add(Polygon(points=[width-265, 0, width-240, 0, width-110, 250, width-125, 250], fillColor=colors.HexColor("#64748B"), strokeColor=None))
    
    # 4. Recuadro Blanco Interno (Da el efecto de paspartú o marco fino)
    m_pad = 35
    d.add(Rect(m_pad, m_pad, width - (m_pad*2), height - (m_pad*2), fillColor=colors.white, strokeColor=colors.HexColor("#CBD5E1"), strokeWidth=1))
    
    # 5. Isotipo MENFA Superior Centrado
    cx = width / 2
    d.add(Rect(cx - 40, height - 105, 80, 42, fillColor=colors.HexColor("#1E293B"), strokeColor=None, rx=4, ry=4))
    d.add(String(cx, height - 90, "MENFA", textAnchor='middle', fontName='Helvetica-Bold', fontSize=13, fillColor=colors.HexColor("#FBBF24")))
    
    story.append(d)
    
    # Llevamos el cursor de ReportLab hacia arriba para empezar a escribir dentro del recuadro blanco
    story.append(Spacer(1, -height + 155))
    
    # --- ESTILOS TIPOGRÁFICOS ---
    styles = getSampleStyleSheet()
    
    style_institucion = ParagraphStyle(
        'Inst', fontName='Helvetica-Bold', fontSize=13, leading=15,
        textColor=colors.HexColor("#1E293B"), alignment=1, spaceAfter=35
    )
    style_titulo = ParagraphStyle(
        'Tit', fontName='Helvetica', fontSize=24, leading=28,
        textColor=colors.HexColor("#94A3B8"), alignment=1, spaceAfter=6
    )
    style_sub = ParagraphStyle(
        'SubTit', fontName='Helvetica', fontSize=16, leading=20,
        textColor=colors.HexColor("#94A3B8"), alignment=1, spaceAfter=30
    )
    style_alumno = ParagraphStyle(
        'Alum', fontName='Helvetica-Bold', fontSize=44, leading=50,
        textColor=colors.HexColor("#1E293B"), alignment=1, spaceAfter=30
    )
    style_curso = ParagraphStyle(
        'Curs', fontName='Helvetica-Bold', fontSize=26, leading=32,
        textColor=colors.HexColor("#1E293B"), alignment=1, spaceAfter=12
    )
    style_fecha = ParagraphStyle(
        'Fech', fontName='Helvetica', fontSize=13, leading=15,
        textColor=colors.HexColor("#64748B"), alignment=1, spaceAfter=45
    )
    
    # --- INYECCIÓN DE CONTENIDO ---
    story.append(Paragraph("MENFA CAPACITACIONES", style_institucion))
    story.append(Paragraph("CERTIFICADO DE FINALIZACIÓN", style_titulo))
    story.append(Paragraph("Del Curso:", style_sub))
    story.append(Paragraph(alumno_text, style_alumno))
    story.append(Paragraph("Control Avanzado de Pozos", style_curso))
    story.append(Paragraph(fecha_text, style_fecha))
    
    # --- BLOQUE DE FIRMA Y VERIFICACIÓN ---
    style_linea_firma = ParagraphStyle('LineF', fontName='Helvetica', fontSize=12, leading=14, textColor=colors.HexColor("#1E293B"), alignment=1)
    style_cargo_firma = ParagraphStyle('CargoF', fontName='Helvetica', fontSize=10, leading=12, textColor=colors.HexColor("#64748B"), alignment=1)
    style_metadata = ParagraphStyle('MetaD', fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor("#94A3B8"), alignment=2)
    
    # Dibujamos la línea de firma horizontal de forma limpia
    d_linea = Drawing(width, 40)
    d_linea.add(Rect(cx - 100, 25, 200, 1, fillColor=colors.HexColor("#1E293B"), strokeColor=None))
    story.append(d_linea)
    
    story.append(Spacer(1, -20))
    story.append(Paragraph("Fabricio Pizzolato", style_linea_firma))
    story.append(Paragraph("Dirección General", style_cargo_firma))
    
    # Identificador único en la esquina inferior derecha
    story.append(Spacer(1, -15))
    story.append(Paragraph(f"ID Verificación: MNF-{profundidad:.0f}<br>Certificación Operacional", style_metadata))
    
    # Compilar archivo
    doc.build(story)
    
    # Retornar flujo de bytes e higiene de archivos locales
    with open(nombre_archivo, "rb") as f:
        pdf_bytes = f.read()
        
    try:
        os.remove(nombre_archivo)
    except:
        pass
        
    return pdf_bytes
