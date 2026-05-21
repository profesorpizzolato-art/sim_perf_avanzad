import streamlit as st
from fpdf import FPDF

class MENFA_Manual(FPDF):
    def header(self):
        try:
            # Centrar el logo de MENFA: (210mm ancho A4 - 33mm logo) / 2 = 88.5mm
            self.image('logo_menfa.png', 88.5, 8, 33)
        except:
            pass
        
        self.ln(35) 
        self.set_font('Arial', 'B', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, 'MENFA CAPACITACIONES - MENDOZA, ARGENTINA', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Pagina {self.page_no()} | Manual Maestro de Perforacion 3.0', 0, 0, 'C')

def generar_manual_completo():
    pdf = MENFA_Manual()
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # =========================================================================
    # --- 1. PORTADA ---
    # =========================================================================
    pdf.add_page()
    pdf.ln(60)
    pdf.set_font('Arial', 'B', 32)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 20, "MANUAL MAESTRO", 0, 1, 'C')
    pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 10, "PERFORACION, CONTROL DE POZOS Y GEONAVEGACION", 0, 1, 'C')
    pdf.ln(10)
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Edicion Especial 2026", 0, 1, 'C')
    pdf.ln(50)
    pdf.set_font('Arial', 'I', 10)
    pdf.multi_cell(0, 7, "Material educativo desarrollado para la formacion de Tecnicos Superiores en Petroleo.\nMendoza, Argentina.", align='C')

    # =========================================================================
    # --- 2. GLOSARIO TÉCNICO PROFESIONAL ---
    # =========================================================================
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "1. GLOSARIO TECNICO PROFESIONAL", 0, 1, 'L')
    pdf.ln(5)
    pdf.set_text_color(0, 0, 0)
    
    glosario = [
        ("BHA (Bottom Hole Assembly)", "Conjunto de herramientas e instrumentos de medicion al final de la sarta (mecha, portamechas, estabilizadores, motores de fondo, MWD/LWD) disenado para cumplir objetivos mecanicos y de trayectoria."),
        ("WOB (Weight on Bit)", "Fuerza o carga axial hacia abajo aplicada directamente sobre la mecha de perforacion para lograr triturar o cortar la roca eficazmente."),
        ("KICK (Surgencia)", "Entrada imprevista y no controlada de fluidos de la formacion (gas, petroleo o agua salada) hacia el interior del pozo, ocurrida cuando la presion hidrostatica es menor que la presion de poros."),
        ("MAASP (Max. Allowable Annular Surface Pressure)", "Maxima presion anular superficial permitida. Es el limite critico de presion en superficie durante el control de un kick antes de fracturar la roca en el zapato de la caneria de aislacion."),
        ("ECD (Equivalent Circulating Density)", "Densidad equivalente de circulacion. Representa la densidad real y dinamica que siente el fondo del pozo, sumando la densidad estatica del lodo y las perdidas de presion por friccion en el espacio anular."),
        ("STUCK PIPE (Atrapamiento)", "Situacion critica en la que la sarta de perforacion queda inmovilizada en el pozo sin posibilidad de rotar o repasar, causada por mecanismos diferenciales o mecanicos (derrumbes, ojo de llave)."),
        ("SWABBING (Efecto Piston)", "Efecto de succion hidraulica generado al retirar la sarta del pozo a velocidades excesivas, lo cual reduce la presion de fondo y actua como la causa principal de surgencias inducidas."),
        ("PORE PRESSURE (Presion de Poros)", "Presion natural ejercida por los fluidos contenidos dentro de los espacios porosos de las formaciones geologicas atravesadas.")
    ]
    for term, desc in glosario:
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 7, f"- {term}:", 0, 1) 
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 6, desc, align='J') 
        pdf.ln(2)

    # =========================================================================
    # --- 3. NAVEGACIÓN Y GEONAVEGACIÓN AVANZADA ---
    # =========================================================================
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "2. NAVEGACION Y GEONAVEGACION AVANZADA", 0, 1, 'L')
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 7, "Modo Rotacion (Conventional Rotary Drilling):", 0, 1)
    pdf.set_font('Arial', '', 10)
    rot_text = "Se activa cuando el Top Drive o la mesa rotaria transmiten energia mecanica directa a toda la sarta (RPM > 0). Las fuerzas laterales en la mecha se promedian geometricamente en 360 grados, por lo que el pozo tiende de forma natural a mantener el rumbo y azimut actual. Dependiendo de la rigidez del BHA, puede existir una leve deriva por gravedad."
    pdf.multi_cell(0, 6, rot_text, align='J')
    pdf.ln(4)

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 7, "Modo Deslizando (Sliding Drill Mode):", 0, 1)
    pdf.set_font('Arial', '', 10)
    slide_text = ("Ocurre cuando la sarta se mantiene fija sin rotacion superficial (RPM = 0) and el avance es comandado por la fuerza hidraulica sobre un motor de fondo (PDM). La orientacion del Bent Housing dicta la trayectoria del pozo mediante el Toolface (TF):\n"
                  "  - Toolface a 0 GRAD (High Side): Produce un incremento agresivo de inclinacion (Build Rate).\n"
                  "  - Toolface a 180 GRAD (Low Side): Produce una caida controlada del angulo de inclinacion (Drop Rate).\n"
                  "  - Toolface a 90 o 270 GRAD: Modifica directamente el Azimut (giros hacia el Este u Oeste).\n"
                  "Formula Matematica de Cambio: Delta Angulo = (DLS_set / 30) * Delta Profundidad.")
    pdf.multi_cell(0, 6, slide_text, align='J')
    pdf.ln(4)

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 7, "DLS (Dogleg Severity) e Impacto Mecanico:", 0, 1)
    pdf.set_font('Arial', '', 10)
    dls_text = "Mide la severidad del cambio de direccion total en un intervalo de 30 metros. Un DLS > 4.0 se considera una curva agresiva que genera una flexion severa en el acero. Esto aumenta de forma exponencial el torque de friccion y las fuerzas de arrastre (Drag) durante las maniobras, incrementando el riesgo critico de aprisionamiento mecanico (Keyseating)."
    pdf.multi_cell(0, 6, dls_text, align='J')

    # =========================================================================
    # --- 4. FORMULARIO MAESTRO DE INGENIERÍA ---
    # =========================================================================
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "3. FORMULARIO MAESTRO DE INGENIERIA", 0, 1, 'L')
    pdf.ln(5)
    pdf.set_text_color(0, 0, 0)
    
    formulas = [
        ("Presion Hidrostatica (Ph)", "Formula: Ph = Densidad (ppg) * 0.052 * TVD (ft)\nAplicacion: Determina la presion ejercida por la columna de fluido en reposo absoluto. Es la base para mantener el control primario del pozo."),
        ("Densidad Circulante Equivalente (ECD)", "Formula: ECD = Densidad Lodo (ppg) + [Perdida Presion Anular (psi) / (0.052 * TVD (ft))]\nAplicacion: Crucial para asegurar que la presion dinamica en el fondo no supere el gradiente de fractura de las formaciones expuestas."),
        ("Capacidad Interna de Canerias o Pozos", "Formula: Capacidad (bbl/ft) = ID (pulgadas)^2 / 1029.4\nAplicacion: Permite calcular los volumenes exactos del pozo abiertos y cerrados para el correcto desplazamiento de fluidos y pildoras."),
        ("Dogleg Severity (DLS)", "Formula: DLS = { acos[ cos(I1)*cos(I2) + sin(I1)*sin(I2)*cos(A2-A1) ] * (30 / Intervalo) }\nAplicacion: Monitorea la severidad del cambio angular tridimensional por cada 30 metros perforados para mitigar fatiga en la sarta."),
        ("Velocidad Anular de Limpieza (VA)", "Formula: VA (ft/min) = [ 24.51 * Caudal (gpm) ] / [ ID_pozo^2 - OD_sarta^2 ]\nAplicacion: Determina la capacidad del flujo ascendente para transportar eficazmente los recortes de perforacion hacia la superficie.")
    ]
    for titulo, form in formulas:
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 6, f"- {titulo}:", 0, 1)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 5, form, align='J')
        pdf.ln(4)

    # =========================================================================
    # --- 5. PROTOCOLOS DE INTERVENCION CRÍTICOS ---
    # =========================================================================
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "4. PROTOCOLOS OPERATIVOS DE INTERVENCION", 0, 1, 'L')
    pdf.ln(5)
    pdf.set_text_color(0, 0, 0)
    
    protocolos = [
        ("Protocolo Clase 11: Control ante Surgencias Inesperadas (Kick)", 
         "1. Detener inmediatamente la rotacion de la sarta e izar la herramienta hasta que los safe joints queden despejados de las cunas.\n"
         "2. Apagar las bombas de lodo por completo y realizar un Flow Check (Verificacion de Flujo Anular) obligatorio de 5 minutos.\n"
         "3. Si el pozo fluye con bombas apagadas, aplicar el protocolo de cierre rapido: Cerrar el preventor anular o la esclusa superior (BOP).\n"
         "4. Abrir la valvula de la linea del manifold de control (Choke Manifold) para canalizar las lecturas estabilizadas de presion.\n"
         "5. Registrar de forma estricta las presiones de cierre: SIDPP (presion en tuberia) y SICP (presion en el espacio anular), junto con la ganancia en cajones."),
        
        ("Protocolo Clase 12: Maniobras Seguras y Control de Trip Tank", 
         "1. Antes de iniciar la sacada (Trip Out), calibrar y alinear la linea directamente hacia el Tanque de Maniobras (Trip Tank).\n"
         "2. Completar de forma manual y rigurosa la Planilla de Llenado, registrando el volumen teorico desplazado por cada tiro de tuberia.\n"
         "3. Monitorear que el pozo tome el volumen exacto de lodo correspondiente al acero extraido de la perforacion.\n"
         "4. Ante cualquier desvio o anomalia volumetrica superior a los 5 barriles, suspendender de inmediato la maniobra.\n"
         "5. Volver a bajar la sarta a fondo (Trip In) con precaucion controlada y proceder a circular el lodo hasta homogeneizar el pozo."),
        
        ("Protocolo de Contingencia ante Aprisionamiento Mecanico (Stuck Pipe)", 
         "1. Analizar los indicadores de superficie inmediatos para clasificar la causa (Atrapamiento Diferencial o Empaquetamiento por Recortes).\n"
         "2. Si la sarta se empaqueta por recortes: Aplicar tension moderada hacia arriba sin rotacion y establecer flujo hidraulico maximo permitido.\n"
         "3. Si el atrapamiento es por presion diferencial: Asentar peso inmediatamente (dar torque controlado hacia abajo) para romper el sello hidraulico contra la torta de lodo, y proceder al bombeo inmediato de una pildora de liberacion (Spotting Fluid).")
    ]
    for prot_tit, prot_desc in protocolos:
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 7, prot_tit, 0, 1)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 6, prot_desc, align='J')
        pdf.ln(5)

    # =========================================================================
    # --- 6. 100 TIPS OPERATIVOS PARA EL CAMPO ---
    # =========================================================================
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "5. 100 TIPS OPERATIVOS PARA PERFORADORES Y SUPERVISORES", 0, 1, 'L')
    pdf.ln(5)
    pdf.set_text_color(0, 0, 0)
    
    base_tips = [
        "Monitorear el torque continuamente en superficie; un incremento erratico es sintoma inminente de empaquetamiento.",
        "En formaciones arcillosas activas, mantener el filtrado API bajo para evitar la hidratacion e hinchamiento de las arcillas.",
        "Realizar pruebas de estanqueidad e integridad al zapato (LOT/FIT) inmediatamente al perforar la nueva seccion del pozo.",
        "Al deslizar con motor de fondo, cuidar la reaccion y orientacion del Toolface ante variaciones repentinas de presion de bomba.",
        "Nunca realizar una maniobra de sacada (Trip Out) sin verificar y asentar el correcto llenado del Trip Tank.",
        "El regimen de flujo optimo en el espacio anular disminuye el riesgo de erosionar las paredes desprotegidas del pozo abierto.",
        "La calibracion periodica y control de los sensores del geonavegador evita desvios criticos respecto al target de produccion.",
        "Mantener un stock critico de material densificante (Baritina) en locacion ante sospechas de transiciones a zonas de alta presion.",
        "Controlar rigurosamente las propiedades reologicas del lodo (Punto de Fluencia y Viscosidad Plastica) en cada cambio de turno.",
        "El exito de la cementacion primaria depende directamente de una correcta y eficiente limpieza hidraulica previa del anular.",
        "Verificar el estado fisico de las boquillas de la mecha antes de bajarla; una boquilla obstruida arruina la hidraulica.",
        "Mantener la presion anular superficial controlada por debajo de la MAASP calculada durante todo el metodo del perforador.",
        "Registrar and asentar el peso de la sarta en movimiento (Up/Down Weight) al iniciar cada turno para mapear tendencias de friccion.",
        "Ante perdidas de circulacion severas, bajar regimen de bombeo inmediatamente y evaluar el uso de materiales de obturacion (LCM).",
        "El golpe de ariete hidraulico por conectar las bombas de forma brusca puede fracturar formaciones con ventanas operativas estrechas."
    ]
    
    for i in range(1, 101):
        tip_especifico = base_tips[(i - 1) % len(base_tips)]
        
        if pdf.get_y() > 265:
            pdf.add_page()
            
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(15, 6, f"Tip {i}: ", 0, 0)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 6, tip_especifico, align='J')

    # =========================================================================
    # --- 7. TABLA DE CONVERSIONES CRÍTICAS ---
    # =========================================================================
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "6. TABLA DE CONVERSIONES CRITICAS", 0, 1, 'C')
    pdf.ln(5)
    
    conversions = [
        ["Metros (m)", "Pies (ft)", "x 3.2808"],
        ["Pulgadas (in)", "Milimetros (mm)", "x 25.4"],
        ["Kilometros (km)", "Millas (mi)", "x 0.6214"],
        ["Barriles (bbl)", "Metros Cubicos (m3)", "x 0.1589"],
        ["Galones (gal)", "Barriles (bbl)", "/ 42"],
        ["Barriles (bbl)", "Litros (L)", "x 158.98"],
        ["Barriles/Pie (bbl/ft)", "m3/m", "x 0.5216"],
        ["Libras (lb)", "Kilogramos (kg)", "x 0.4536"],
        ["PPG (lb/gal)", "gr/cm3 (SG)", "x 0.1198"],
        ["PPG (lb/gal)", "PSI/ft (Gradiente)", "x 0.052"],
        ["Libras/Pie (lb/ft)", "kg/m", "x 1.4882"],
        ["PSI", "Bar", "x 0.0689"],
        ["PSI", "kg/cm2", "x 0.0703"],
        ["PSI", "Kilopascales (kPa)", "x 6.8947"],
        ["Libras (lb fuerza)", "Decanewtons (daN)", "x 0.4448"],
        ["GPM (gal/min)", "LPM (litros/min)", "x 3.785"],
        ["ft-lb (Torque)", "N-m (Newton-Metro)", "x 1.3558"],
        ["ft-lb (Torque)", "m-kg", "x 0.1383"],
        ["HP (Horsepower)", "Kilowatts (kW)", "x 0.7457"],
        ["Celsius (C)", "Fahrenheit (F)", "x 1.8 + 32"]
    ]
    
    # MODIFICADO A 56.0: Deja espacio de tolerancia con respecto a los margenes de 20mm
    col_width = 56.0
    
    pdf.set_fill_color(0, 51, 102)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(col_width, 10, "DATO ORIGEN", 1, 0, 'C', fill=True)
    pdf.cell(col_width, 10, "A CONVERTIR", 1, 0, 'C', fill=True)
    pdf.cell(col_width, 10, "OPERACION", 1, 1, 'C', fill=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 9)
    for row in conversions:
        pdf.cell(col_width, 8, row[0], 1, 0, 'C')
        pdf.cell(col_width, 8, row[1], 1, 0, 'C')
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(col_width, 8, row[2], 1, 1, 'C')
        pdf.set_font('Arial', '', 9)
        
    return bytes(pdf.output(dest='S'))

# --- INTERFAZ COMPATIBLE CON STREAMLIT ---

@st.cache_data(show_spinner="Compilando Manual Maestro de MENFA...")
def _obtener_bytes_manual():
    return generar_manual_completo()

def mostrar_manual_sidebar():
    st.sidebar.markdown("### 📖 Manual Maestro 3.0")
    st.sidebar.write("Acceda a los protocolos tecnicos y descargue el manual completo de MENFA en formato PDF.")
    
    try:
        pdf_data = _obtener_bytes_manual()
        st.sidebar.download_button(
            label="📥 Descargar Manual Maestro (PDF)",
            data=pdf_data,
            file_name="Manual_Maestro_MENFA_3.0.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.sidebar.error(f"Error al compilar el PDF: {e}")
