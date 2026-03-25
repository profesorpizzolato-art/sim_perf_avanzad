import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.graph_objects as go
from fpdf import FPDF
import datetime
import os
import time
import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime
import os

# --- 1. CONFIGURACIÓN E IDENTIDAD ---
st.set_page_config(page_title="IPCL MENFA V13 - SISTEMA INTEGRAL", layout="wide")

# Estilo para emular una cabina de perforación
st.markdown("""
    <style>
    .main { background-color: #050505; color: #E0E0E0; }
    .stMetric { background-color: #111; border: 1px solid #00FFCC; padding: 10px; border-radius: 10px; }
    [data-testid="stMetricValue"] { color: #00FFCC; font-family: 'Courier New'; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. INICIALIZACIÓN DE ESTADOS ---
if "auth" not in st.session_state:
    st.session_state.update({
        "auth": False, "usuario": "", "legajo": "", "kick_alert": False,
        "vida_sarta": 100.0, "pesca_activa": False, "densidad_lodo": 1.15,
        "presion_anular": 0, "score": 0, "finalizado": False,
        "history": pd.DataFrame([{
            "DEPTH": 2500.0, "WOB": 20.0, "RPM": 100, "ROP": 0.0, "GR": 110, "TANQUES": 1200, "DENS": 1.15
        }])
    })

# --- 3. FUNCIÓN DE CERTIFICADO PDF ---
def generar_pdf(nombre, dni, profundidad):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(2)
    pdf.rect(10, 10, 277, 190)
    
    pdf.set_font('Arial', 'B', 30)
    pdf.cell(0, 40, 'CERTIFICADO DE COMPETENCIA', ln=True, align='C')
    pdf.set_font('Arial', '', 18)
    pdf.cell(0, 10, 'El proyecto educativo MENFA (Mendoza) certifica a:', ln=True, align='C')
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 25)
    pdf.cell(0, 20, nombre.upper(), ln=True, align='C')
    pdf.set_font('Arial', '', 14)
    pdf.cell(0, 10, f'DNI/Legajo: {dni}', ln=True, align='C')
    pdf.ln(10)
    pdf.set_font('Arial', '', 16)
    cuerpo = f"Ha operado con éxito el simulador MENFA V13, alcanzando una profundidad de {profundidad}m y demostrando habilidades en Control de Pozos, Geología y Operaciones de Perforación."
    pdf.multi_cell(0, 10, cuerpo, align='C')
    pdf.ln(20)
    pdf.set_font('Arial', 'I', 12)
    pdf.cell(0, 10, f"Emitido el {datetime.now().strftime('%d/%m/%Y')} - Mendoza, Argentina", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1')

# --- 4. ACCESO (LOGIN) ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #00FFCC;'>🛡️ IPCL MENFA - CONTROL DE ACCESO</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        u_reg = st.text_input("Nombre y Apellido:")
        l_reg = st.text_input("DNI / Legajo:")
        if st.button("INGRESAR A CABINA", use_container_width=True):
            if u_reg and l_reg:
                st.session_state.usuario, st.session_state.legajo, st.session_state.auth = u_reg, l_reg, True
                st.rerun()
    st.stop()

# --- 5. LÓGICA DE SIMULACIÓN (SIDEBAR) ---
curr = st.session_state.history.iloc[-1]
with st.sidebar:
    st.header(f"Op: {st.session_state.usuario}")
    st.divider()
    wob = st.slider("WOB (klbs)", 0, 60, int(curr['WOB']))
    rpm = st.slider("RPM", 0, 180, int(curr['RPM']))
    
    if st.button("⏩ AVANZAR PERFORACIÓN", use_container_width=True):
        if not st.session_state.pesca_activa and not st.session_state.kick_alert:
            st.session_state.vida_sarta -= (wob * 0.15)
            if st.session_state.vida_sarta <= 0: st.session_state.pesca_activa = True
            
            n_prof = curr['DEPTH'] + random.randint(5, 15)
            # Lógica de Gamma Ray: Reservorio en 2850-2950m
            gr = random.randint(20, 40) if 2850 < n_prof < 2950 else random.randint(80, 130)
            
            # Lógica de Kick (Surgencia)
            tanques = curr['TANQUES']
            if random.random() < 0.10: # 10% de probabilidad
                st.session_state.kick_alert = True
                tanques += 40
                st.session_state.presion_anular = random.randint(350, 750)

            nueva_fila = {
                "DEPTH": n_prof, "WOB": wob, "RPM": rpm,
                "ROP": (wob * rpm) / 400, "GR": gr, 
                "TANQUES": tanques, "DENS": st.session_state.densidad_lodo
            }
            st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([nueva_fila])], ignore_index=True)
            st.rerun()

# --- 6. PANELES OPERATIVOS (TABS) ---
if st.session_state.kick_alert:
    st.error("🚨 KICK DETECTADO: ¡GANANCIA EN TANQUES! CIERRE EL BOP DE INMEDIATO.")

tabs = st.tabs(["📊 SCADA", "🛡️ WELL CONTROL", "🔩 SARTA & PESCA", "📈 GEOLOGÍA", "📖 MANUAL & EXAMEN"])

with tabs[0]: # SCADA MODERNO
    c1, c2, c3 = st.columns(3)
    c1.metric("BIT DEPTH", f"{curr['DEPTH']} m")
    c2.metric("WEIGHT ON BIT", f"{curr['WOB']} klbs")
    c3.metric("ROP", f"{round(curr['ROP'], 1)} m/h")
    
    # Gráfico de Martin-Decker
    fig_md = go.Figure(go.Indicator(
        mode="gauge+number", value=120 - curr['WOB'],
        title={'text': "HOOK LOAD (TN)"},
        gauge={'axis': {'range': [0, 150]}, 'bar': {'color': "#00FFCC"}}
    ))
    fig_md.update_layout(paper_bgcolor="black", height=250, margin=dict(t=30, b=0))
    st.plotly_chart(fig_md, use_container_width=True)

with tabs[1]: # WELL CONTROL
    st.subheader("Sistema de Prevención de Reventones")
    if st.session_state.kick_alert:
        st.metric("SICP (Presión Anular)", f"{st.session_state.presion_anular} psi")
        if st.button("🔒 CERRAR BOP ANULAR", type="primary"):
            st.session_state.kick_alert = False
            st.success("Pozo Controlado. Aumente la densidad del lodo.")
    else:
        st.success("Presiones equilibradas.")

with tabs[2]: # SARTA Y PESCA
    st.subheader("Vida útil de la herramienta")
    vida = max(0, st.session_state.vida_sarta)
    st.progress(vida / 100)
    if st.session_state.pesca_activa:
        st.warning("⚠️ SARTA CORTADA POR EXCESO DE PESO.")
        if st.button("🎣 OPERACIÓN DE PESCA"):
            st.session_state.vida_sarta, st.session_state.pesca_activa = 100.0, False
            st.rerun()

with tabs[3]: # GEOLOGÍA
    fig_gr = go.Figure()
    fig_gr.add_trace(go.Scatter(x=st.session_state.history['GR'], y=st.session_state.history['DEPTH'], name="Gamma Ray"))
    fig_gr.update_layout(yaxis=dict(autorange="reversed", title="Profundidad (m)"), xaxis=dict(title="GR (API)"))
    # Resaltar zona de interés
    fig_gr.add_hrect(y0=2850, y1=2950, fillcolor="green", opacity=0.2, annotation_text="POTENCIAL RESERVORIO")
    st.plotly_chart(fig_gr, use_container_width=True)

with tabs[4]: # EXAMEN Y CERTIFICADO
    st.header("Evaluación Técnica IPCL")
    q1 = st.radio("1. Si apoyas más peso (WOB), ¿qué ocurre con el Martin Decker (Hook Load)?", ["Sube", "Baja", "No cambia"])
    q2 = st.radio("2. ¿Cuál es el protocolo inmediato ante un Kick?", ["Aumentar RPM", "Cerrar BOP", "Perforar más rápido"])
    
    if st.button("🏁 FINALIZAR Y CALIFICAR"):
        aciertos = 0
        if q1 == "Baja": aciertos += 1
        if q2 == "Cerrar BOP": aciertos += 1
        
        if aciertos == 2:
            st.balloons()
            st.success("¡EXAMEN APROBADO 100%!")
            pdf_out = generar_pdf(st.session_state.usuario, st.session_state.legajo, curr['DEPTH'])
            st.download_button("🎓 DESCARGAR CERTIFICADO OFICIAL (PDF)", pdf_out, f"Certificado_{st.session_state.usuario}.pdf", "application/pdf")
        else:
            st.error(f"Aciertos: {aciertos}/2. Revisa el manual y reintenta.")

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="MENFA WELL ENGINEERING SIM v8", layout="wide")

# Inicialización de estados (Session State)
if "certificado" not in st.session_state:
    st.session_state.update({
        "certificado": False,
        "md": 2000.0,
        "tvd": 2000.0,
        "inc": 0.0,
        "vs": 0.0,
        "mw": 10.5,
        "wob": 0.0,
        "kop": 1800.0,
        "bur": 3.0,
        "well_type": "CONVENCIONAL",
        "total_cost": 500000.0
    })

# --- 2. MOTOR DE CÁLCULO TÉCNICO ---
def calcular_avance(md_nuevo):
    d_md = md_nuevo - st.session_state.md
    
    # Lógica de Construcción de Ángulo (Clase 7)
    if md_nuevo > st.session_state.kop:
        st.session_state.inc += (st.session_state.bur * (d_md / 30))
    
    rad = np.radians(st.session_state.inc)
    st.session_state.tvd += d_md * np.cos(rad)
    st.session_state.vs += d_md * np.sin(rad)
    st.session_state.md = md_nuevo
    
    # Lógica Económica (Clase 6)
    rig_rate = 45000 if st.session_state.well_type == "SHALE" else 35000
    costo_tramo = (d_md * 150) + (rig_rate / 24) 
    st.session_state.total_cost += costo_tramo

# --- 3. MÓDULO DE EXAMEN ---
def render_examen():
    st.title("🔒 CERTIFICACIÓN TÉCNICA OBLIGATORIA")
    st.warning("Debe aprobar con 16/20 (80%) para desbloquear la consola de perforación.")
    
    # Banco de preguntas resumido para esta versión
    preguntas = [
        {"id": 1, "p": "¿Método con 0% error? (Clase 1)", "o": ["Tangencial", "Mínima Curvatura"], "r": "Mínima Curvatura"},
        {"id": 2, "p": "¿Espera para reset MWD? (Clase 1)", "o": ["30s", "90s"], "r": "90s"},
        {"id": 3, "p": "¿Qué es MWD? (Clase 2)", "o": ["Measuring While Drilling", "Mechanical Weight"], "r": "Measuring While Drilling"},
        {"id": 4, "p": "¿Cómo transmite el MWD? (Clase 2)", "o": ["Cable", "Pulsos de lodo"], "r": "Pulsos de lodo"},
        {"id": 5, "p": "Fórmula HKLD (Clase 3):", "o": ["Peso Efectivo - WOB", "Peso Aire + WOB"], "r": "Peso Efectivo - WOB"},
        {"id": 6, "p": "¿Ubicación del Punto Neutro? (Clase 3)", "o": ["DP", "DC (Portamechas)"], "r": "DC (Portamechas)"},
        {"id": 7, "p": "¿Función de las toberas? (Clase 3)", "o": ["Fuerza hidráulica y limpieza", "Enfriar solamente"], "r": "Fuerza hidráulica y limpieza"},
        {"id": 8, "p": "Densidad del agua (ppg) (Clase 4):", "o": ["8.33", "1.0"], "r": "8.33"},
        {"id": 9, "p": "¿Qué evita el asentamiento? (Clase 4)", "o": ["Gel", "Filtrado"], "r": "Gel"},
        {"id": 10, "p": "Fórmula Factor Flotación (Clase 4):", "o": ["1 - (MW/65.5)", "MW * 0.052"], "r": "1 - (MW/65.5)"},
        {"id": 11, "p": "¿Zapato Flotador? (Clase 5)", "o": ["Válvula check y flotación", "Corte de roca"], "r": "Válvula check y flotación"},
        {"id": 12, "p": "¿Maniobra antes de TR? (Clase 5)", "o": ["Calibrar e inyectar tapón", "Aumentar GPM"], "r": "Calibrar e inyectar tapón"},
        {"id": 13, "p": "Permeabilidad Tight (Clase 6):", "o": [">10 mD", "<0.1 mD"], "r": "<0.1 mD"},
        {"id": 14, "p": "¿Técnica Shale? (Clase 6)", "o": ["Perf & Plug", "Open Hole"], "r": "Perf & Plug"},
        {"id": 15, "p": "¿Qué es el Flow Back? (Clase 6)", "o": ["Fluido retorno post-fractura", "Lodo nuevo"], "r": "Fluido retorno post-fractura"},
        {"id": 16, "p": "¿Qué es KOP? (Clase 7)", "o": ["Inicio de desvío", "Fin de pozo"], "r": "Inicio de desvío"},
        {"id": 17, "p": "Si Inc=0, ¿MD es igual a TVD?", "o": ["Sí", "No"], "r": "Sí"},
        {"id": 18, "p": "División de la sarta (Clase 8):", "o": ["BHA y DP", "Bomba y Motor"], "r": "BHA y DP"},
        {"id": 19, "p": "¿Función Drill Collars? (Clase 8)", "o": ["Dar peso al trépano", "Medir"], "r": "Dar peso al trépano"},
        {"id": 20, "p": "¿Qué afecta el Torque? (Clase 8)", "o": ["Geometría y fricción", "Color lodo"], "r": "Geometría y fricción"}
    ]
    
    score = 0
    for q in preguntas:
        res = st.radio(q['p'], q['o'], key=f"ex_{q['id']}")
        if res == q['r']: score += 1
    
    if st.button("FINALIZAR EXAMEN"):
        if score >= 16:
            st.session_state.certificado = True
            st.success(f"🏆 ¡APROBADO! {score}/20. Acceso concedido.")
            st.rerun()
        else:
            st.error(f"❌ REPROBADO ({score}/20). Revise los fundamentos técnicos.")

# --- 4. INTERFAZ DEL SIMULADOR ---
def render_simulador():
    st.sidebar.title("🎮 PANEL DE CONTROL")
    st.session_state.well_type = st.sidebar.selectbox("TIPO DE POZO", ["CONVENCIONAL", "SHALE"])
    st.session_state.mw = st.sidebar.number_input("DENSIDAD LODO (ppg)", 8.3, 18.0, 10.5)
    st.session_state.wob = st.sidebar.slider("WOB (TN)", 0, 40, 10)
    
    if st.sidebar.button("▶️ PERFORAR 30 METROS"):
        calcular_avance(st.session_state.md + 30)
        st.toast("Avanzando trayectoria...")

    # KPIs Principales
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("MD (Profundidad)", f"{st.session_state.md:.1f} m")
    c2.metric("TVD (Vertical)", f"{st.session_state.tvd:.1f} m")
    c3.metric("Inclinación", f"{st.session_state.inc:.2f} °")
    c4.metric("Costo Total", f"USD {st.session_state.total_cost:,.0f}")

    t1, t2, t3 = st.tabs(["🏗️ INGENIERÍA", "💰 ECONOMÍA", "📊 TRAYECTORIA"])
    
    with t1:
        st.subheader("Configuración de Sarta (BHA)")
        st.write(f"**Punto Neutro estimado:** En sección de Drill Collars.")
        st.info(f"Factor de Flotación (FF): {1 - (st.session_state.mw / 65.5):.3f}")
        
    with t2:
        st.subheader("Análisis de Costos")
        st.write(f"Tarifa del Equipo: {'USD 45,000/día' if st.session_state.well_type == 'SHALE' else 'USD 35,000/día'}")
        if st.session_state.well_type == "SHALE":
            st.warning("Escenario Shale detectado: Se requiere logística de Fractura Hidráulica.")

    with t3:
        # Gráfico simple de trayectoria
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[0, st.session_state.vs], y=[0, -st.session_state.tvd], mode='lines+markers', name='Pozo'))
        fig.update_layout(title="Perfil del Pozo (Vista Lateral)", xaxis_title="Sección Vertical (m)", yaxis_title="TVD (m)")
        st.plotly_chart(fig)

# --- EJECUCIÓN PRINCIPAL ---
if not st.session_state.certificado:
    render_examen()
else:
    render_simulador()
    if st.button("Cerrar Sesión"):
        st.session_state.certificado = False
        st.rerun()

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# Configuración de página
st.set_page_config(page_title="Oil Rig SCADA Simulator", layout="wide")

st.title("📊 Monitor de Perforación en Tiempo Real (SCADA)")

# 1. Simulación de Modelo Geológico (Base de Datos)
geology_data = {
    "Formación": ["Post-Sal", "Sello Anhidrita", "Reservorio Carbonato", "Basamento"],
    "Tope (m)": [0, 1500, 2800, 3500],
    "Dureza (1-10)": [3, 5, 7, 9],
    "Presión Poro (psi/ft)": [0.45, 0.47, 0.52, 0.55]
}
df_geo = pd.DataFrame(geology_data)

# 2. Sidebar para parámetros de control
st.sidebar.header("Control de Perforación")
rop_target = st.sidebar.slider("ROP Deseado (m/h)", 5, 50, 20)
wob = st.sidebar.slider("Peso sobre la Mecha (WOB - klbs)", 10, 60, 30)

# 3. Lógica del Simulador
if st.button('Iniciar Perforación'):
    placeholder = st.empty()
    depth = 0
    
    for i in range(100):
        depth += rop_target * (np.random.uniform(0.8, 1.2)) / 10
        # Buscamos en qué formación estamos según la profundidad
        current_layer = df_geo[df_geo["Tope (m)"] <= depth].iloc[-1]
        
        with placeholder.container():
            col1, col2, col3 = st.columns(3)
            col1.metric("Profundidad Actual", f"{depth:.2f} m")
            col2.metric("Formación", current_layer["Formación"])
            col3.metric("Presión Estada", f"{depth * current_layer['Presión Poro (psi/ft)']:.0f} psi")

            # Gráfico de la trayectoria
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[0, 0], y=[0, depth], mode='lines+markers', name='Pozo'))
            fig.update_yaxis(autorange="reversed", title="Profundidad (m)")
            fig.update_layout(height=400, title="Perfil del Pozo")
            st.plotly_chart(fig, use_container_width=True)
            
            time.sleep(0.5)
            import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import lasio # Librería estándar para geofísica

st.set_page_config(page_title="Advanced Drilling & Logging SCADA", layout="wide")

# --- FUNCIONES DE CÁLCULO ---
def calculate_trajectory(md, inc, azi):
    """Calcula TVD y coordenadas usando Curvatura Mínima simplificada"""
    tvd = [0]
    norte = [0]
    este = [0]
    
    for i in range(1, len(md)):
        d_md = md[i] - md[i-1]
        rad_inc1 = np.radians(inc[i-1])
        rad_inc2 = np.radians(inc[i])
        rad_azi1 = np.radians(azi[i-1])
        rad_azi2 = np.radians(azi[i])
        
        # Simplificación de promedio de ángulos para el ejemplo
        tvd.append(tvd[-1] + d_md * np.cos((rad_inc1 + rad_inc2)/2))
        norte.append(norte[-1] + d_md * np.sin((rad_inc1 + rad_inc2)/2) * np.cos((rad_azi1 + rad_azi2)/2))
        este.append(este[-1] + d_md * np.sin((rad_inc1 + rad_inc2)/2) * np.sin((rad_azi1 + rad_azi2)/2))
        
    return tvd, norte, este

# --- UI DE STREAMLIT ---
st.title("🚀 Simulador de Perforación Direccional & Real-Time Logging")

tabs = st.tabs(["Navegación Direccional", "Interpretación Petro física (LAS)"])

with tabs[0]:
    st.subheader("Control de Trayectoria")
    col_input, col_plot = st.columns([1, 2])
    
    with col_input:
        # Simulación de un plan de pozo
        data_plan = {
            "MD (m)": [0, 500, 1200, 2500],
            "INC (deg)": [0, 0, 45, 60],
            "AZI (deg)": [0, 0, 90, 110]
        }
        df_plan = st.data_editor(pd.DataFrame(data_plan))
        
        tvd, n, e = calculate_trajectory(df_plan["MD (m)"].values, 
                                        df_plan["INC (deg)"].values, 
                                        df_plan["AZI (deg)"].values)

    with col_plot:
        fig_3d = go.Figure(data=[go.Scatter3d(x=e, y=n, z=tvd, mode='lines+markers',
                                           line=dict(color='red', width=6))])
        fig_3d.update_scenes(zaxis_autorange="reversed", xaxis_title="Este (m)", 
                           yaxis_title="Norte (m)", zaxis_title="TVD (m)")
        fig_3d.update_layout(title="Vista 3D del Trayecto del Pozo")
        st.plotly_chart(fig_3d, use_container_width=True)

with tabs[1]:
    st.subheader("Carga de Registros Geofísicos")
    uploaded_file = st.file_uploader("Cargar archivo .LAS", type=["las"])
    
    if uploaded_file:
        # Para demostración, si no subes uno, puedes usar una lógica de dummy data
        # l = lasio.read(uploaded_file)
        # df_las = l.df()
        st.success("Archivo LAS cargado con éxito. Visualizando Rayos Gamma vs Profundidad...")
        # Aquí iría el plot de registros tipo log-track
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import lasio

# --- FUNCIÓN DE CARGA Y SIMULACIÓN DE DATOS (PARA ESTA DEMO) ---
def get_log_data(uploaded_file):
    """Lee un LAS o genera datos sintéticos realistas."""
    if uploaded_file is not None:
        try:
            # En un entorno real, lasio lee el string del uploader
            # stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
            # l = lasio.read(stringio)
            # return l.df().reset_index() # Retorna DataFrame con 'DEPT'
            pass
        except Exception as e:
            st.error(f"Error leyendo LAS: {e}")
            
    # Datos Sintéticos si no hay archivo
    st.warning("Usando datos sintéticos de demostración.")
    depth = np.linspace(1000, 2000, 1000)
    # Simulación de GR (Lutita vs Arenisca)
    gr = 60 + 40 * np.sin(depth/20) + np.random.normal(0, 5, 1000)
    # Simulación de Resistividad (Inversa a GR, alta en hidrocarburo)
    res = 10** (2 - (gr/100) + np.random.normal(0, 0.1, 1000))
    # Simulación de Densidad (RHOB)
    rhob = 2.2 + 0.3 * (gr/150) + np.random.normal(0, 0.02, 1000)
    
    return pd.DataFrame({'DEPT': depth, 'GR': gr, 'ILD': res, 'RHOB': rhob})

# --- PESTAÑA OPTIMIZADA ---
with tabs[1]:
    st.subheader("Visualizador Profesional de Registros de Pozo (Log Tracks)")
    
    uploaded_file = st.file_uploader("Cargar archivo .LAS", type=["las"])
    df_logs = get_log_data(uploaded_file)
    
    if not df_logs.empty:
        # Configuración de los Tracks Profesionales
        # Creamos 3 columnas (tracks) compartiendo el eje Y
        fig_logs = make_subplots(rows=1, cols=3, shared_yaxes=True, 
                                 horizontal_spacing=0.02,
                                 subplot_titles=('Track 1: Litología', 'Track 2: Resistividad', 'Track 3: Porosidad'))

        # --- TRACK 1: Rayos Gamma (GR) ---
        # Representa arcillosidad. Estándar: 0 a 150 API
        fig_logs.add_trace(go.Scatter(x=df_logs['GR'], y=df_logs['DEPT'], 
                                     name='GR', line=dict(color='green', width=1.5)),
                          row=1, col=1)
        
        # Sombreado de Lutitas (Shale Baseline > 75 API)
        fig_logs.add_trace(go.Scatter(x=df_logs['GR'].where(df_logs['GR'] >= 75), y=df_logs['DEPT'],
                                     fill='tozerox', fillcolor='rgba(139, 69, 19, 0.3)', # Marrón suave
                                     line=dict(color='rgba(255,255,255,0)'), showlegend=False),
                          row=1, col=1)

        # --- TRACK 2: Resistividad (ILD) ---
        # Indica fluidos. Logarítmico es ESTÁNDAR (0.2 a 2000 ohm.m)
        fig_logs.add_trace(go.Scatter(x=df_logs['ILD'], y=df_logs['DEPT'], 
                                     name='Resistividad', line=dict(color='red', width=1.5)),
                          row=1, col=2)

        # --- TRACK 3: Densidad (RHOB) ---
        # Para porosidad. Escala invertida es ESTÁNDAR (1.95 a 2.95 g/cc)
        fig_logs.add_trace(go.Scatter(x=df_logs['RHOB'], y=df_logs['DEPT'], 
                                     name='Densidad', line=dict(color='black', width=1.5, dash='dash')),
                          row=1, col=3)

        # --- CONFIGURACIÓN DE EJES (CRÍTICO PARA FORMATO PETROFÍSICO) ---
        # Eje Y: Compartido, invertido (profundidad hacia abajo)
        fig_logs.update_yaxes(title_text="Profundidad (m)", autorange="reversed", row=1, col=1)
        
        # Ejes X específicos
        fig_logs.update_xaxes(title_text="GR (API)", range=[0, 150], row=1, col=1)
        fig_logs.update_xaxes(title_text="ILD (ohm.m)", type="log", range=[np.log10(0.2), np.log10(2000)], row=1, col=2)
        fig_logs.update_xaxes(title_text="RHOB (g/cc)", range=[2.95, 1.95], row=1, col=3) # Escala invertida!

        fig_logs.update_layout(height=800, template="plotly_white", 
                              legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        
        # Mostramos el gráfico
        st.plotly_chart(fig_logs, use_container_width=True)
        
        # Pequeña interpretación automática
        st.markdown("---")
        st.write("**Análisis Rápido:**")
        # Buscamos zonas con bajo GR (arenisca) y alta resistividad (hidrocarburo)
        potential_zones = df_logs[(df_logs['GR'] < 50) & (df_logs['ILD'] > 20)]
        if not potential_zones.empty:
            st.success(f"🎯 Se detectaron {len(potential_zones)} metros de posible Reservorio con Hidrocarburo.")
        else:
            st.info("No se detectaron zonas obvias de hidrocarburo con los criterios actuales.")
            import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- 1. Sidebar de Telemetría Real-Time ---
st.sidebar.header("🕹️ Telemetría de Perforación")
with st.sidebar:
    st.metric("Weight on Bit (WOB)", "35 klbs", "+2")
    st.metric("RPM", "120", "-5")
    st.metric("Torque", "1500 ft-lb", "Steady")
    st.progress(85, text="Carga del Gancho (Hook Load)")

# --- 2. Simulación de Ventana de Presiones (Mud Window) ---
def plot_mud_window(max_depth):
    depths = np.linspace(0, max_depth, 100)
    pore_pressure = 0.44 * depths # Gradiente normal
    frac_pressure = 0.75 * depths # Gradiente de fractura
    current_mw = 0.52 * depths    # Lodo actual
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=pore_pressure, y=depths, name="Presión Poro", line=dict(color='blue', dash='dot')))
    fig.add_trace(go.Scatter(x=frac_pressure, y=depths, name="Presión Fractura", line=dict(color='red', dash='dot')))
    fig.add_trace(go.Scatter(x=current_mw, y=depths, name="Lodo (Mud Weight)", fill='tonextx', line=dict(color='green')))
    
    fig.update_yaxes(autorange="reversed", title="Profundidad (m)")
    fig.update_xaxes(title="Presión (psi)")
    fig.update_layout(title="Ventana de Navegación de Lodo (Mud Window)")
    return fig

st.plotly_chart(plot_mud_window(3000), use_container_width=True)
import streamlit as st
import time

# --- CONFIGURACIÓN DE UMBRALES (Thresholds) ---
SAFE_MUD_WEIGHT_MIN = 9.5  # ppg
SAFE_MUD_WEIGHT_MAX = 12.5 # ppg
CRITICAL_TORQUE = 2500     # ft-lb

def check_alarms(mw, torque, r_temp):
    """Procesa los datos y retorna el nivel de severidad y mensaje."""
    if mw < SAFE_MUD_WEIGHT_MIN:
        return "CRITICAL", "⚠️ ALERTA: Presión de Poro excedida! Riesgo de INFLUJO (Kick)."
    elif mw > SAFE_MUD_WEIGHT_MAX:
        return "CRITICAL", "⚠️ ALERTA: Presión de Fractura excedida! PÉRDIDA DE CIRCULACIÓN."
    elif torque > CRITICAL_TORQUE:
        return "WARNING", "📢 PRECAUCIÓN: Torque elevado. Posible pega de tubería."
    return "OK", "Sistema Operando en Parámetros Normales"

# --- INTERFAZ SCADA CON ALERTAS ---
st.title("🚨 Panel de Control de Alarmas - Drilling SCADA")

# Simulamos entradas de sensores
col_sensors, col_status = st.columns([1, 2])

with col_sensors:
    st.subheader("Sensores en Tiempo Real")
    curr_mw = st.slider("Mud Weight (ppg)", 8.0, 14.0, 11.0)
    curr_torque = st.number_input("Torque Actual (ft-lb)", value=1200)

# Procesar Alertas
status_level, message = check_alarms(curr_mw, curr_torque, 0)

with col_status:
    st.subheader("Estado del Pozo")
    
    if status_level == "CRITICAL":
        st.error(message)
        # Efecto visual: Fondo o borde rojo (vía Markdown/CSS)
        st.markdown("<style>stApp {background-color: #ffcccc;}</style>", unsafe_allow_html=True)
    elif status_level == "WARNING":
        st.warning(message)
        st.markdown("<style>stApp {background-color: #fff4cc;}</style>", unsafe_allow_html=True)
    else:
        st.success(message)
        st.balloons() # Animación opcional para éxito

# --- HISTORIAL DE EVENTOS (Log) ---
st.markdown("### 📜 Log de Eventos SCADA")
event_log = st.empty()
if 'history' not in st.session_state:
    st.session_state.history = []

if status_level != "OK":
    st.session_state.history.append(f"{time.strftime('%H:%M:%S')} - {status_level}: {message}")

st.write(st.session_state.history[-5:]) # Mostrar últimos 5 eventos
from fpdf import FPDF
import base64

def generate_drilling_report(depth, formation, mw, status_msg, history):
    pdf = FPDF()
    pdf.add_page()
    
    # Encabezado Profesional
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="REPORTE DIARIO DE PERFORACIÓN (DDR)", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
    pdf.ln(10)

    # Sección 1: Parámetros del Pozo
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="1. Parámetros de Operación Actuales", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.cell(100, 8, txt=f"Profundidad Medida (MD): {depth:.2f} m", ln=True)
    pdf.cell(100, 8, txt=f"Formación Geológica: {formation}", ln=True)
    pdf.cell(100, 8, txt=f"Densidad del Lodo (MW): {mw} ppg", ln=True)
    pdf.ln(5)

    # Sección 2: Estado de Seguridad
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="2. Evaluación de Seguridad y Alertas", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, txt=f"Estado del Sistema: {status_msg}")
    pdf.ln(5)

    # Sección 3: Log de Eventos (Últimos 10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="3. Historial de Eventos Recientes", ln=True)
    pdf.set_font("Arial", size=9)
    for event in history[-10:]:
        pdf.cell(0, 6, txt=event, ln=True)

    return pdf.output(dest='S').encode('latin-1')

# --- INTEGRACIÓN EN STREAMLIT ---
st.markdown("---")
st.subheader("📋 Generación de Documentación Técnica")

if st.button("📄 Generar Reporte PDF"):
    # Obtenemos los datos actuales (asumiendo que las variables existen en tu script)
    pdf_data = generate_drilling_report(
        depth=2850.5, # Ejemplo
        formation="Reservorio Carbonato", 
        mw=curr_mw, 
        status_msg=message, 
        history=st.session_state.history
    )
    
    # Botón de descarga automática
    st.download_button(
        label="⬇️ Descargar Reporte (.pdf)",
        data=pdf_data,
        file_name=f"Drilling_Report_{time.strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf"
    )
    st.success("Reporte generado correctamente.")

# Ejemplo de cómo importar tus nuevos módulos en tu código existente
from engine.geology import calculate_pore_pressure
from ui.alerts import trigger_scada_visuals

# En tu flujo principal:
current_data = get_sensor_data() # Tu función existente
pressure = calculate_pore_pressure(current_data['depth'])

if pressure > threshold:
    trigger_scada_visuals("CRITICAL")

import streamlit as st

def load_training_scenario(level):
    if level == "Principiante":
        return {"target_depth": 1000, "risk": "Bajo", "anomaly_depth": 0}
    elif level == "Intermedio (Control de Pozos)":
        # Inyecta un kick a los 1500m
        return {"target_depth": 2000, "risk": "Alto", "anomaly_depth": 1500}

# En tu app principal de GitHub:
st.title("🎓 Academia de Perforación Virtual")
nivel = st.select_slider("Selecciona tu nivel de entrenamiento", ["Principiante", "Intermedio (Control de Pozos)"])
config = load_training_scenario(nivel)

# Lógica: Si profundidad actual == anomaly_depth, disparar alerta roja.

import numpy as np

def calculate_pressures(depth, mud_density, pore_gradient, frac_gradient):
    """
    Calcula las presiones críticas en el fondo del pozo (BHP).
    
    Parámetros:
    - depth: Profundidad Vertical Verdadera (TVD) en metros.
    - mud_density: Densidad del lodo en ppg.
    - pore_gradient: Gradiente de presión de poro (psi/ft).
    - frac_gradient: Gradiente de fractura (psi/ft).
    """
    # Conversión de metros a pies para cálculos estándar de la industria
    depth_ft = depth * 3.28084
    
    # Presión Hidrostática (PH = 0.052 * MW * TVD)
    hydrostatic_pressure = 0.052 * mud_density * depth_ft
    
    # Presión de Poro y Fractura en el fondo
    pore_pressure = pore_gradient * depth_ft
    frac_pressure = frac_gradient * depth_ft
    
    # Determinación del estado del pozo
    status = "Estable"
    if hydrostatic_pressure < pore_pressure:
        status = "KICK"  # Entrada de fluido de la formación
    elif hydrostatic_pressure > frac_pressure:
        status = "LOSS"  # Pérdida de circulación (fractura)
        
    return {
        "BHP": hydrostatic_pressure,
        "Pore_P": pore_pressure,
        "Frac_P": frac_pressure,
        "Status": status,
        "Margin": frac_pressure - hydrostatic_pressure
    }

# Sugerencia de layout para tu app.py
import streamlit as st
from motor_cálculos_avanzados import calcular_presiones
from bop_panel import render_bop
from bombas_de_lodo import render_pumps

# Layout de 3 columnas para simular la cabina del perforador
col_izq, col_centro, col_der = st.columns([1, 2, 1])

with col_izq:
    st.subheader("🛠️ Control de Bombas")
    render_pumps() # Llamamos a tu módulo existente

with col_centro:
    st.subheader("🌎 Modelo Geológico & Trayectoria")
    # Aquí insertamos el gráfico 3D y los Log Tracks que optimizamos
    render_geological_view() 

with col_der:
    st.subheader("🛡️ Seguridad (BOP)")
    render_bop() # Tu panel de preventoras

import streamlit as st
import pandas as pd
import numpy as np
import time
# Importamos tus módulos (ajusta los nombres si es necesario)
from motor_cálculos_avanzados import calcular_presiones 
from bop_panel import render_bop

st.set_page_config(page_title="Simulador Menfa - Capacitación", layout="wide")

# --- INICIALIZACIÓN DE ESTADO ---
if 'depth' not in st.session_state:
    st.session_state.depth = 0.0
    st.session_state.is_drilling = False
    st.session_state.history = []

# --- MODELO GEOLÓGICO ---
geology_data = {
    "Formación": ["Post-Sal", "Sello Anhidrita", "Reservorio Carbonato", "Basamento"],
    "Tope (m)": [0, 1500, 2800, 3500],
    "Gradiente (psi/ft)": [0.45, 0.47, 0.52, 0.55]
}
df_geo = pd.DataFrame(geology_data)

# --- SIDEBAR DE CONTROL ---
st.sidebar.image("logo_menfa.png", width=200)
st.sidebar.header("🕹️ Consola del Perforador")
rop = st.sidebar.slider("ROP (m/h)", 5, 50, 20)
mw = st.sidebar.number_input("Densidad del Lodo (ppg)", value=10.0, step=0.1)

col_ctrl1, col_ctrl2 = st.sidebar.columns(2)
if col_ctrl1.button("▶️ Iniciar"): st.session_state.is_drilling = True
if col_ctrl2.button("⏸️ Pausar"): st.session_state.is_drilling = False

# --- LÓGICA PRINCIPAL ---
main_placeholder = st.empty()

while st.session_state.is_drilling:
    # 1. Avanzar profundidad
    st.session_state.depth += (rop / 3600) * 2  # Incremento por ciclo de simulación
    
    # 2. Obtener datos geológicos actuales
    current_layer = df_geo[df_geo["Tope (m)"] <= st.session_state.depth].iloc[-1]
    
    # 3. Cálculo de Presiones (Tu motor avanzado)
    res_fisica = calcular_presiones(st.session_state.depth, mw, current_layer["Gradiente (psi/ft)"], 0.8)

    with main_placeholder.container():
        # Layout SCADA
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Profundidad", f"{st.session_state.depth:.2f} m")
        c2.metric("Formación", current_layer["Formación"])
        c3.metric("BHP (Presión Fondo)", f"{res_fisica['BHP']:.0f} psi")
        
        # Alerta de Seguridad
        if res_fisica['Status'] == "KICK":
            c4.error("⚠️ INFLUJO DETECTADO")
        else:
            c4.success("✅ POZO ESTABLE")

        # Visualización dual: Gráfico de Pozo y Panel BOP
        col_plot, col_bop = st.columns([2, 1])
        
        with col_plot:
            # Aquí va tu gráfico de Plotly (Trayectoria/Logs)
            st.write("Gráfico de Trayectoria...") 
            
        with col_bop:
            # Llamamos a tu archivo bop_panel.py
            render_bop()

    time.sleep(1) # Velocidad del simulador

import numpy as np

def calcular_hidrostatica(densidad_lodo, profundidad_tvd):
    """Calcula la Presión Hidrostática (psi). 0.052 es la constante de conversión."""
    return 0.052 * densidad_lodo * (profundidad_tvd * 3.28084)

def evaluar_estado_pozo(presion_hidro, profundidad_tvd, gradiente_poro, gradiente_frac):
    """Compara la presión del lodo contra la roca."""
    p_poro = gradiente_poro * (profundidad_tvd * 3.28084)
    p_frac = gradiente_frac * (profundidad_tvd * 3.28084)
    
    if presion_hidro < p_poro:
        return "KICK", p_poro, p_frac
    elif presion_hidro > p_frac:
        return "LOSS", p_poro, p_frac
    else:
        return "ESTABLE", p_poro, p_frac

import numpy as np

def calcular_posicion_3d(md_actual, inc_actual, azi_actual, md_anterior, inc_ant, azi_ant):
    """Cálculo simplificado de trayectoria para simulador en tiempo real."""
    d_md = md_actual - md_anterior
    # Promedio de ángulos para simplificar el motor de tiempo real
    rad_inc = np.radians((inc_actual + inc_ant) / 2)
    rad_azi = np.radians((azi_actual + azi_ant) / 2)
    
    tvd_incremento = d_md * np.cos(rad_inc)
    norte_incremento = d_md * np.sin(rad_inc) * np.cos(rad_azi)
    este_incremento = d_md * np.sin(rad_inc) * np.sin(rad_azi)
    
    return tvd_incremento, norte_incremento, este_incremento

def balance_tanques(volumen_inicial, flujo_entrada, flujo_salida, dt):
    """
    Simula el nivel de lodo en los tanques (Pits).
    Si entrada > salida = Ganancia (posible Kick).
    Si salida > entrada = Pérdida (fractura).
    """
    cambio_volumen = (flujo_entrada - flujo_salida) * dt
    nuevo_volumen = volumen_inicial + cambio_volumen
    return nuevo_volumen

def calcular_ecd(mw_estatico, profundidad_tvd, caudal_gpm, diametro_hoyo, diametro_dp):
    """
    Calcula la Densidad Equivalente de Circulación (ECD).
    Una simplificación de la fórmula de Bingham para simuladores:
    """
    if caudal_gpm <= 0:
        return mw_estatico
    
    # Estimación de pérdida de carga anular (Regla de dedo pulgar para capacitación)
    # DeltaP = (0.00001 * MW * L * V^2) / (Dh - Dp)
    velocidad_anular = (24.51 * caudal_gpm) / (diametro_hoyo**2 - diametro_dp**2)
    perdid_friccion = (0.1 * mw_estatico * (profundidad_tvd * 3.28) * velocidad_anular**2) / (2000 * (diametro_hoyo - diametro_dp))
    
    # ECD = MW + (Pérdida Fricción / (0.052 * TVD))
    ecd = mw_estatico + (perdid_friccion / (0.052 * profundidad_tvd * 3.28))
    return round(ecd, 2)

def monitorear_tanques(vol_actual, gpm_in, gpm_out, dt=1):
    """
    Simula la ganancia o pérdida en los colchones de lodo (Pits).
    dt es el diferencial de tiempo en segundos.
    """
    delta_vol = (gpm_in - gpm_out) * (dt / 60) # galones
    return vol_actual + delta_vol

from motor_calculos.fisica_presiones import calcular_hidrostatica, evaluar_estado_pozo
from motor_calculos.dinamica_lodo import calcular_ecd, monitorear_tanques

# ... dentro del bucle de simulación ...

# 1. El alumno ajusta las bombas en bombas_de_lodo.py (supongamos 400 GPM)
caudal = 400 

# 2. El motor calcula el ECD real (Presión Dinámica)
ecd_real = calcular_ecd(mw_estatico=10.5, profundidad_tvd=st.session_state.depth, 
                        caudal_gpm=caudal, diametro_hoyo=8.5, diametro_dp=5.0)

# 3. Evaluamos si ese ECD rompe la formación o permite un flujo
presion_fondo = calcular_hidrostatica(ecd_real, st.session_state.depth)
status, p_poro, p_frac = evaluar_estado_pozo(presion_fondo, st.session_state.depth, 0.45, 0.85)

# 4. Mostrar en el SCADA
st.metric("ECD (Dinámico)", f"{ecd_real} ppg")
if status == "KICK":
    st.error("🚨 ¡REVENTÓN EN PROGRESO! Cierre el BOP inmediatamente.")

import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go

# --- IMPORTACIÓN DE TUS MÓDULOS ---
from motor_calculos.fisica_presiones import calcular_hidrostatica, evaluar_estado_pozo
from motor_calculos.dinamica_lodo import calcular_ecd, monitorear_tanques
# from bop_panel import render_bop  # Asegúrate de que bop_panel tenga una función render_bop()

# 1. Configuración de Interfaz
st.set_page_config(page_title="Simulador de Perforación Menfa", layout="wide")

# Estilo CSS para el "Modo Dark SCADA"
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1a1c24; padding: 10px; border-radius: 10px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización del Estado Global (Persistencia)
if 'depth' not in st.session_state:
    st.session_state.depth = 1000.0  # Profundidad inicial
    st.session_state.is_drilling = False
    st.session_state.pit_volume = 500.0 # Galones iniciales
    st.session_state.history = []

# 3. Sidebar:
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time

# --- IMPORTACIÓN DE TUS MÓDULOS ---
# Asegúrate de haber cargado la carpeta motor_calculos con sus archivos
from motor_calculos.fisica_presiones import calcular_hidrostatica, evaluar_estado_pozo
from motor_calculos.dinamica_lodo import calcular_ecd, monitorear_tanques
# from bop_panel import render_bop # Descomenta cuando bop_panel.py esté listo

# 1. Configuración de Interfaz Profesional
st.set_page_config(page_title="Simulador de Perforación Menfa", layout="wide")

# Estilo CSS para apariencia de Consola Real
st.markdown("""
    <style>
    .stMetric { background-color: #1e2129; border: 1px solid #3b3f4b; padding: 10px; border-radius: 5px; }
    [data-testid="stSidebar"] { background-color: #0e1117; }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización del Session State (Evita que el simulador se reinicie)
if 'depth' not in st.session_state:
    st.session_state.update({
        'depth': 1000.0,
        'is_drilling': False,
        'pit_volume': 500.0,
        'log_history': [],
        'status': "ESTABLE",
        'last_update': time.time()
    })

# 3. Sidebar: Controles de Operación
st.sidebar.image("logo_menfa.png", width=200) # Asegúrate de que el archivo exista
st.sidebar.header("🕹️ Controles del Perforador")

rop = st.sidebar.slider("Velocidad (ROP m/h)", 0, 60, 20)
mw_static = st.sidebar.number_input("Densidad Lodo (ppg)", 8.0, 18.0, 10.5)
pump_gpm = st.sidebar.slider("Bombas (GPM)", 0, 800, 400)

col_btn1, col_btn2 = st.sidebar.columns(2)
if col_btn1.button("▶️ INICIAR"): st.session_state.is_drilling = True
if col_btn2.button("🛑 PARAR"): st.session_state.is_drilling = False

# 4. Lógica de Simulación (Cuerpo Principal)
st.title("📊 Monitor SCADA - Perforación en Tiempo Real")

# Contenedor dinámico para que la página no parpadee
placeholder = st.empty()

# Bucle de ejecución (Solo si está en Play)
if st.session_state.is_drilling:
    # Simulación de avance (dt = 1 segundo de simulación)
    st.session_state.depth += (rop / 3600) 
    
    # Motor de Cálculo: ECD y Presiones
    ecd = calcular_ecd(mw_static, st.session_state.depth, pump_gpm, 8.5, 5.0)
    presion_fondo = calcular_hidrostatica(ecd, st.session_state.depth)
    
    # Evaluación Geológica (Simulamos gradiente de poro de 0.47 y fractura 0.82)
    res_fisica, p_poro, p_frac = evaluar_estado_pozo(presion_fondo, st.session_state.depth, 0.47, 0.82)
    st.session_state.status = res_fisica

    # Balance de Tanques (Si hay pérdida o ganancia)
    gpm_out = pump_gpm if res_fisica == "ESTABLE" else (pump_gpm * 1.2 if res_fisica == "KICK" else pump_gpm * 0.8)
    st.session_state.pit_volume = monitorear_tanques(st.session_state.pit_volume, pump_gpm, gpm_out)

# --- VISUALIZACIÓN ---
with placeholder.container():
    # Fila 1: Métricas Críticas
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Profundidad (MD)", f"{st.session_state.depth:.2f} m")
    m2.metric("ECD Dinámico", f"{ecd if 'ecd' in locals() else mw_static} ppg")
    m3.metric("Nivel Tanques", f"{st.session_state.pit_volume:.1f} bbl")
    
    if st.session_state.status == "KICK":
        m4.error("🚨 KICK DETECTADO")
    elif st.session_state.status == "LOSS":
        m4.warning("📉 PÉRDIDA CIRC.")
    else:
        m4.success("✅ OPERACIÓN NORMAL")

    # Fila 2: Gráficos SCADA
    col_chart, col_bop = st.columns([2, 1])
    
    with col_chart:
        # Gráfico de Perfil del Pozo
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[0, 0], y=[0, st.session_state.depth], 
                                 mode='lines+markers', line=dict(color='yellow', width=4)))
        fig.update_yaxis(autorange="reversed", title="Profundidad (m)")
        fig.update_layout(title="Perfil de Perforación Actual", template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col_bop:
        st.subheader("🛡️ Panel de Seguridad")
        st.info("Aquí se integrará bop_panel.py")
        # render_bop() # Llamada a tu módulo de preventoras

# Auto-refresh (simula tiempo real)
if st.session_state.is_drilling:
    time.sleep(0.5)
    st.rerun()

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from fpdf import FPDF

# --- 1. IMPORTACIÓN DE MÓDULOS DE MOTOR ---
try:
    from motor_calculos.fisica_presiones import calcular_hidrostatica, evaluar_estado_pozo
    from motor_calculos.dinamica_lodo import calcular_ecd, monitorear_tanques
except ImportError:
    st.error("⚠️ Carpeta 'motor_calculos' no detectada. Verifique la estructura en GitHub.")

# --- 2. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="IPCL MENFA WELL SIM V5", layout="wide", initial_sidebar_state="expanded")

# CSS para estilo SCADA Dark
st.markdown("""
    <style>
    .stMetric {background-color: #1c222d; border: 1px solid #34495e; border-radius: 8px; padding: 10px;}
    .main { background-color: #0e1117; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. INICIALIZACIÓN DE ESTADO PERSISTENTE ---
if "menu" not in st.session_state: st.session_state.menu = "HOME"
if "depth" not in st.session_state:
    st.session_state.update({
        "depth": 2850.0,
        "is_drilling": False,
        "pit_volume": 500.0,
        "history": pd.DataFrame(columns=["DEPTH", "WOB", "RPM", "ECD", "STATUS", "GR"])
    })

# --- 4. FUNCIONES DE APOYO (Reporte y Visualización) ---
def generate_pdf_report():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="REPORTE OPERATIVO - MENFA SIM", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Profundidad Final: {st.session_state.depth:.2f} m", ln=True)
    pdf.cell(200, 10, txt=f"Estado Final del Pozo: {st.session_state.status}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- 5. SIDEBAR (CONSOLA DEL INSTRUCTOR) ---
with st.sidebar:
    st.image("logo_menfa.png", width=150)
    st.header("🎮 Mando del Instructor")
    target_rop = st.slider("Set ROP (m/h)", 0, 60, 20)
    target_mw = st.number_input("Densidad Lodo (ppg)", 8.0, 16.0, 10.5)
    target_gpm = st.slider("Caudal Bombas (GPM)", 0, 800, 400)
    
    col_bt1, col_bt2 = st.columns(2)
    if col_bt1.button("▶️ START"): st.session_state.is_drilling = True
    if col_bt2.button("🛑 STOP"): st.session_state.is_drilling = False

# --- 6. LÓGICA DE SIMULACIÓN EN TIEMPO REAL ---
if st.session_state.is_drilling:
    # Simulación de avance
    st.session_state.depth += (target_rop / 3600) * 2
    
    # Cálculo dinámico usando el motor de cálculos
    ecd = calcular_ecd(target_mw, st.session_state.depth, target_gpm, 8.5, 5.0)
    presion = calcular_hidrostatica(ecd, st.session_state.depth)
    status, p_poro, p_frac = evaluar_estado_pozo(presion, st.session_state.depth, 0.47, 0.85)
    
    st.session_state.status = status
    # Registro en historial
    new_data = pd.DataFrame([{"DEPTH": st.session_state.depth, "WOB": 30, "RPM": 120, "ECD": ecd, "STATUS": status, "GR": 120}])
    st.session_state.history = pd.concat([st.session_state.history, new_data], ignore_index=True)

# --- 7. RENDERIZADO DE INTERFAZ (MENÚS) ---
if st.session_state.menu == "HOME":
    st.title("🖥️ IPCL MENFA WELL SIM V5.0")
    c1, c2, c3 = st.columns(3)
    with c1: 
        if st.button("📊 SCADA MONITOR"): st.session_state.menu = "SCADA"
    with c2:
        if st.button("🛡️ WELL CONTROL (BOP)"): st.session_state.menu = "BOP"
    with c3:
        if st.button("🏆 REPORTE FINAL"): st.session_state.menu = "REPORTE"

elif st.session_state.menu == "SCADA":
    if st.button("🔙 HOME"): st.session_state.menu = "HOME"
    
    col_met1, col_met2, col_met3 = st.columns(3)
    col_met1.metric("Profundidad", f"{st.session_state.depth:.2f} m")
    col_met2.metric("ECD Real", f"{ecd:.2f} ppg" if st.session_state.is_drilling else "N/A")
    
    if st.session_state.status == "KICK":
        col_met3.error("🚨 KICK DETECTADO")
    else:
        col_met3.success("✅ OPERACIÓN SEGURA")

    # Gráfico de Log Track en Tiempo Real
    fig_scada = make_subplots(rows=1, cols=2)
    fig_scada.add_trace(go.Scatter(y=st.session_state.history["DEPTH"], x=st.session_state.history["ECD"], name="ECD"), row=1, col=1)
    fig_scada.update_yaxes(autorange="reversed", title="Profundidad (m)")
    st.plotly_chart(fig_scada, use_container_width=True)

elif st.session_state.menu == "REPORTE":
    st.title("🏆 Evaluación de Capacitación")
    st.table(st.session_state.history.tail(5))
    if st.button("Generar PDF"):
        pdf_file = generate_pdf_report()
        st.download_button("Descargar Reporte", pdf_file, "DDR_Menfa.pdf", "application/pdf")

# Loop de refresco para simular tiempo real
if st.session_state.is_drilling:
    time.sleep(0.5)
    st.rerun()

# --- INICIALIZACIÓN DE ESTADO (Asegúrate de que 'status' esté aquí) ---
if 'depth' not in st.session_state:
    st.session_state.update({
        'depth': 2850.0,
        'is_drilling': False,
        'pit_volume': 500.0,
        'status': "ESTABLE",  # <--- AGREGA ESTA LÍNEA CRÍTICA
        'history': pd.DataFrame(columns=["DEPTH", "WOB", "RPM", "ECD", "STATUS", "GR"])
    })

# Reemplaza la línea 93 por:
if st.session_state.get('status') == "KICK":
    col_met3.error("🚨 KICK DETECTADO")

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from fpdf import FPDF

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="IPCL MENFA WELL SIM V5", layout="wide", initial_sidebar_state="collapsed")

# Estilo CSS SCADA Profesional
st.markdown("""
    <style>
    .stMetric {background-color: #1c222d; border: 1px solid #34495e; border-radius: 8px; padding: 15px;}
    .module-card {
        text-align: center; padding: 25px; border-radius: 15px; 
        background-color: #161b22; border: 2px solid #34495e;
        height: 200px;
    }
    .status-active { color: #2ecc71; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. INICIALIZACIÓN CRÍTICA DE ESTADOS (Evita el AttributeError) ---
if "menu" not in st.session_state: st.session_state.menu = "HOME"
if "depth" not in st.session_state: st.session_state.depth = 2850.0
if "is_drilling" not in st.session_state: st.session_state.is_drilling = False
if "status" not in st.session_state: st.session_state.status = "ESTABLE"
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame([{
        "DEPTH": 2850.0, "WOB": 25.0, "RPM": 120, "TORQUE": 18500, 
        "SPP": 3200, "ROP": 15.0, "MSE": 35.0, "GR": 140, "ECD": 10.5
    }])

# --- 3. IMPORTACIÓN DE MOTORES (Con respaldo si fallan) ---
try:
    from motor_calculos.fisica_presiones import calcular_hidrostatica, evaluar_estado_pozo
    from motor_calculos.dinamica_lodo import calcular_ecd
except ImportError:
    # Lógica de respaldo por si la carpeta no está lista
    def calcular_ecd(mw, d, gpm, dh, dp): return mw + (gpm/1000)
    def evaluar_estado_pozo(p, d, poro, frac): return ("ESTABLE", 0, 0)
    def calcular_hidrostatica(mw, d): return 0.052 * mw * d * 3.28

# --- 4. DEFINICIÓN DE MÓDULOS DE INTERFAZ ---

def render_home():
    st.image("logo_menfa.png", width=180)
    st.title("🖥️ IPCL MENFA WELL SIM V5.0")
    st.subheader("Unidad de Control Operativo | Vaca Muerta, Mendoza")
    st.divider()
    
    st.markdown("### 🕹️ SELECCIONAR UNIDAD DE MANDO")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="module-card"><h1>📊</h1><h3>SCADA & MSE</h3><p class="status-active">ONLINE</p></div>', unsafe_allow_html=True)
        if st.button("ABRIR MONITOR", use_container_width=True): st.session_state.menu = "SCADA"
    with c2:
        st.markdown('<div class="module-card"><h1>💺</h1><h3>CABINA CHAIR</h3><p class="status-active">CONNECTED</p></div>', unsafe_allow_html=True)
        if st.button("TOMAR MANDOS", use_container_width=True): st.session_state.menu = "CABINA"
    with c3:
        st.markdown('<div class="module-card"><h1>📡</h1><h3>LWD / MWD</h3><p class="status-active">SYNCED</p></div>', unsafe_allow_html=True)
        if st.button("GEONAVEGACIÓN", use_container_width=True): st.session_state.menu = "LWD"

    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown('<div class="module-card"><h1>🛡️</h1><h3>SEGURIDAD BOP</h3></div>', unsafe_allow_html=True)
        if st.button("CONTROL POZOS", use_container_width=True): st.session_state.menu = "BOP"
    with c5:
        st.markdown('<div class="module-card"><h1>🌀</h1><h3>SARTA & VIB</h3></div>', unsafe_allow_html=True)
        if st.button("VER VIBRACIONES", use_container_width=True): st.session_state.menu = "SARTA"
    with c6:
        st.markdown('<div class="module-card"><h1>🏆</h1><h3>EVALUACIÓN</h3></div>', unsafe_allow_html=True)
        if st.button("GENERAR REPORTE", use_container_width=True): st.session_state.menu = "REPORTE"

def render_scada():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    curr = st.session_state.history.iloc[-1]
    
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("WOB (klbs)", f"{curr['WOB']}")
    m2.metric("RPM", f"{curr['RPM']}")
    m3.metric("ECD (ppg)", f"{curr['ECD']:.2f}")
    m4.metric("MSE (kpsi)", f"{curr['MSE']:.1f}")
    m5.metric("DEPTH (m)", f"{st.session_state.depth:.2f}")

    if st.session_state.status == "KICK":
        st.error("🚨 ALERTA: INFLUJO DETECTADO (KICK)")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=st.session_state.history['ECD'], x=st.session_state.history['DEPTH'], name="ECD Log"))
    fig.update_layout(template="plotly_dark", height=400, title="Registro de ECD vs Profundidad")
    st.plotly_chart(fig, use_container_width=True)

# --- 5. SIDEBAR INSTRUCTOR (Controla la simulación) ---
with st.sidebar:
    st.header("🎮 MANDO INSTRUCTOR")
    rop_in = st.slider("ROP (m/h)", 0, 60, 15)
    mw_in = st.slider("Mud Weight (ppg)", 8.5, 16.0, 10.5)
    gpm_in = st.slider("Bombas (GPM)", 0, 800, 400)
    
    if st.button("▶️ INICIAR PERFORACIÓN"): st.session_state.is_drilling = True
    if st.button("🛑 PARAR"): st.session_state.is_drilling = False

# --- 6. BUCLE DE CÁLCULO EN TIEMPO REAL ---
if st.session_state.is_drilling:
    # 1. Avanzar
    st.session_state.depth += (rop_in / 3600) * 5 # Acelerado para la demo
    
    # 2. Calcular Física
    ecd = calcular_ecd(mw_in, st.session_state.depth, gpm_in, 8.5, 5.0)
    presion = calcular_hidrostatica(ecd, st.session_state.depth)
    status, _, _ = evaluar_estado_pozo(presion, st.session_state.depth, 0.47, 0.85)
    st.session_state.status = status
    
    # 3. Guardar Historial
    new_row = {
        "DEPTH": st.session_state.depth, "WOB": 25.0, "RPM": 120, 
        "TORQUE": 18000, "SPP": 3000, "ROP": rop_in, "MSE": 30.0, "GR": 120, "ECD": ecd
    }
    st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([new_row])], ignore_index=True)
    
    time.sleep(0.5)
    st.rerun()

# --- 7. NAVEGACIÓN ---
if st.session_state.menu == "HOME": render_home()
elif st.session_state.menu == "SCADA": render_scada()
elif st.session_state.menu == "BOP":
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("🛡️ CONTROL DE POZOS (BOP)")
    st.image("Gemini_Generated_Image_dn7zasdn7zasdn7z.png", width=600)
    if st.button("🔒 CERRAR PREVENTORAS"): st.toast("BOP CERRADO")
elif st.session_state.menu == "LWD":
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("📡 GEONAVEGACIÓN LWD")
    # Aquí puedes poner tu gráfico 3D que tenías antes
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from fpdf import FPDF
import io

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="IPCL MENFA WELL SIM V5.0", layout="wide", initial_sidebar_state="expanded")

# Inicialización de todas las variables de estado para evitar el AttributeError
if "initialized" not in st.session_state:
    st.session_state.update({
        "initialized": True,
        "menu": "HOME",
        "depth": 2500.0,
        "is_drilling": False,
        "status": "ESTABLE",
        "pit_volume": 500.0,
        "history": pd.DataFrame([{
            "DEPTH": 2500.0, "WOB": 20.0, "RPM": 100, "TORQUE": 15000, 
            "SPP": 2800, "ROP": 10.0, "MSE": 30.0, "GR": 120, "ECD": 10.2, "TEMP": 85.0
        }]),
        "bop_closed": False,
        "alarms": []
    })

# --- 2. MOTOR DE CÁLCULOS INTEGRADO (Física y Lodo) ---
def engine_run(rop, mw_in, gpm, wob, rpm):
    # Avance de profundidad
    st.session_state.depth += (rop / 3600) * 5 
    depth = st.session_state.depth
    
    # Cálculo de ECD (Fricción simplificada)
    v_ann = (24.51 * gpm) / (8.5**2 - 5.0**2) if gpm > 0 else 0
    friccion = (0.1 * mw_in * (depth * 3.28) * v_ann**2) / 20000
    ecd = mw_in + (friccion / (0.052 * depth * 3.28))
    
    # Presiones y Estado
    p_fondo = 0.052 * ecd * (depth * 3.28)
    p_poro = 0.47 * (depth * 3.28)
    p_frac = 0.82 * (depth * 3.28)
    
    status = "ESTABLE"
    if p_fondo < p_poro: status = "KICK"
    elif p_fondo > p_frac: status = "LOSS"
    
    # Torque y ROP simulado
    torque = (wob * 400) + (rpm * 15) + np.random.normal(0, 200)
    mse = (wob / 50) + (480 * torque * rpm) / (50 * rop * 3.28) if rop > 0 else 0
    
    return round(ecd, 2), status, round(torque, 0), round(mse, 1)

# --- 3. COMPONENTES DE INTERFAZ ---

def render_scada():
    st.button("🔙 VOLVER AL INICIO", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    curr = st.session_state.history.iloc[-1]
    
    # Panel de Alertas dinámico
    if st.session_state.status == "KICK":
        st.error(f"🚨 ALERT: WELL INFLUX DETECTED! BHP ({curr['ECD']} ppg) < PORE PRESSURE")
    elif st.session_state.status == "LOSS":
        st.warning("📉 ALERT: CIRCULATION LOSS! PRESSURE EXCEEDS FRACTURE GRADIENT")

    cols = st.columns(6)
    cols[0].metric("DEPTH (m)", f"{st.session_state.depth:.2f}")
    cols[1].metric("WOB (klbs)", f"{curr['WOB']}")
    cols[2].metric("RPM", f"{curr['RPM']}")
    cols[3].metric("TORQUE (ft-lb)", f"{curr['TORQUE']}")
    cols[4].metric("ECD (ppg)", f"{curr['ECD']}")
    cols[5].metric("MSE (kpsi)", f"{curr['MSE']}")

    # Gráficos SCADA
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Presiones de Fondo", "Log de Perforación"))
    fig.add_trace(go.Scatter(y=st.session_state.history["DEPTH"], x=st.session_state.history["ECD"], name="ECD"), row=1, col=1)
    fig.add_trace(go.Scatter(y=st.session_state.history["DEPTH"], x=st.session_state.history["ROP"], name="ROP"), row=1, col=2)
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(height=500, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

def render_bop():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image("Gemini_Generated_Image_dn7zasdn7zasdn7z.png", caption="BOP Stack Status")
    with col2:
        st.subheader("Panel de Control de Reventones")
        if st.button("🔥 EMERGENCY CLOSE (RAMS)", type="primary"):
            st.session_state.bop_closed = True
            st.session_state.is_drilling = False
            st.error("BOP CLOSED - WELL SECURED")
        if st.button("🔓 OPEN ANNULAR"):
            st.session_state.bop_closed = False
            st.success("BOP OPEN")

def render_lwd():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("📡 Geonavegación LWD & 3D")
    # Generar trayectoria 3D
    z = st.session_state.history["DEPTH"]
    x = np.sin(z/500) * 100 # Simulación de curva
    fig3d = go.Figure(data=[go.Scatter3d(x=x, y=np.zeros(len(z)), z=z, mode='lines', line=dict(color='yellow', width=5))])
    fig3d.update_layout(scene=dict(zaxis=dict(autorange="reversed")), template="plotly_dark")
    st.plotly_chart(fig3d, use_container_width=True)

# --- 4. SIDEBAR (CONSOLA DEL INSTRUCTOR) ---
with st.sidebar:
    st.image("logo_menfa.png", width=150)
    st.header("🎮 MANDO INSTRUCTOR")
    rop_set = st.slider("ROP (m/h)", 0, 60, 20)
    mw_set = st.number_input("Mud Weight (ppg)", 8.5, 16.0, 10.5)
    gpm_set = st.slider("Flow Rate (GPM)", 0, 800, 450)
    wob_set = st.slider("WOB (klbs)", 0, 60, 25)
    rpm_set = st.slider("RPM", 0, 200, 120)

    if st.button("▶️ INICIAR PERFORACIÓN"): st.session_state.is_drilling = True
    if st.button("🛑 PARAR"): st.session_state.is_drilling = False

# --- 5. BUCLE PRINCIPAL DE SIMULACIÓN ---
if st.session_state.is_drilling and not st.session_state.bop_closed:
    ecd, status, torque, mse = engine_run(rop_set, mw_set, gpm_set, wob_set, rpm_set)
    st.session_state.status = status
    
    # Guardar en Historial
    new_row = {
        "DEPTH": st.session_state.depth, "WOB": wob_set, "RPM": rpm_set, 
        "TORQUE": torque, "SPP": 3000 + (st.session_state.depth*0.1), 
        "ROP": rop_set, "MSE": mse, "GR": 120 + np.random.normal(0, 5), "ECD": ecd
    }
    st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([new_row])], ignore_index=True)
    time.sleep(0.3)
    st.rerun()

# --- 6. NAVEGACIÓN DEL MENÚ ---
if st.session_state.menu == "HOME":
    st.title("🖥️ IPCL MENFA WELL SIM V5.0")
    # Grilla de selección
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📊 MONITOR SCADA", use_container_width=True): st.session_state.menu = "SCADA"
    with c2:
        if st.button("🛡️ SEGURIDAD BOP", use_container_width=True): st.session_state.menu = "BOP"
    with c3:
        if st.button("📡 LWD / 3D", use_container_width=True): st.session_state.menu = "LWD"
    
    st.image("Gemini_Generated_Image_jl30d0jl30d0jl30.png", use_container_width=True)

elif st.session_state.menu == "SCADA": render_scada()
elif st.session_state.menu == "BOP": render_bop()
elif st.session_state.menu == "LWD": render_lwd()

"bit_wear": 0.0,       # 0 = Nuevo, 1 = Destruido
        "gas_total": 0.5,      # Unidades de gas
        "casing_depth": 1500.0 # Profundidad del último casing

# Simulación de Desgaste del Trépano (Bit Wear)
    # Se gasta más rápido en formaciones duras (supongamos dureza 7)
    st.session_state.bit_wear += (rpm * wob) / 1000000 
    rop_efectivo = rop * (1 - st.session_state.bit_wear)
    
    # Simulación de Gas de Formación
    if 2800 < depth < 3200: # Zona de reservorio
        gas = 5.0 + np.random.normal(0, 2)
    else:
        gas = 0.5 + np.random.normal(0, 0.1)
    st.session_state.gas_total = gas

def render_integrity():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("🏗️ Integridad del Pozo e Ingeniería")
    
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**Zapata del Casing:** {st.session_state.casing_depth} m")
        st.write(f"**Open Hole:** {st.session_state.depth - st.session_state.casing_depth:.2f} m")
        st.metric("Estado del Trépano (Wear)", f"{st.session_state.bit_wear*100:.1f} %")
    with c2:
        # Visualización de la sarta
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Drilling_rig_schema.png/300px-Drilling_rig_schema.png", width=200)

c4, c5, c6 = st.columns(3)
    with c4:
        if st.button("🏗️ INTEGRIDAD / CASING", use_container_width=True): st.session_state.menu = "INTEGRIDAD"
    with c5:
        if st.button("🧪 GAS / CROMATOGRAFÍA", use_container_width=True): st.session_state.menu = "GAS"
    with c6:
        if st.button("🚜 LOGÍSTICA TANQUES", use_container_width=True): st.session_state.menu = "LOGISTICA"

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="MENFA WELL SIM - DIRECCIONAL V6", layout="wide")

if "initialized" not in st.session_state:
    st.session_state.update({
        "initialized": True,
        "menu": "HOME",
        "md": 1000.0,
        "tvd": 1000.0,
        "inc": 0.0,
        "azi": 0.0,
        "norte": 0.0,
        "este": 0.0,
        "vs": 0.0, # Vertical Section
        "is_drilling": False,
        "survey_ready": False,
        "history": pd.DataFrame([{
            "MD": 1000.0, "TVD": 1000.0, "INC": 0.0, "AZI": 0.0, "NORTE": 0.0, "ESTE": 0.0, "VS": 0.0
        }]),
        "target_type": "TANGENCIAL" # Basado en CLASE 1
    })

# --- 2. MOTOR MATEMÁTICO: MÍNIMA CURVATURA (Concepto CLASE 1) ---
def calcular_minima_curvatura(md_new, inc_new, azi_new):
    prev = st.session_state.history.iloc[-1]
    d_md = md_new - prev["MD"]
    
    # Convertir a radianes
    i1, i2 = np.radians(prev["INC"]), np.radians(inc_new)
    a1, a2 = np.radians(prev["AZI"]), np.radians(azi_new)
    
    # Ángulo de perro (Dogleg)
    cos_dl = np.cos(i2 - i1) - (np.sin(i1) * np.sin(i2) * (1 - np.cos(a2 - a1)))
    dl = np.arccos(np.clip(cos_dl, -1, 1))
    
    # Factor de Calibración (RF)
    rf = (2 / dl) * np.tan(dl / 2) if dl != 0 else 1
    
    # Incrementos
    d_tvd = (d_md / 2) * (np.cos(i1) + np.cos(i2)) * rf
    d_norte = (d_md / 2) * (np.sin(i1) * np.cos(a1) + np.sin(i2) * np.cos(a2)) * rf
    d_este = (d_md / 2) * (np.sin(i1) * np.sin(a1) + np.sin(i2) * np.sin(a2)) * rf
    
    return prev["TVD"] + d_tvd, prev["NORTE"] + d_norte, prev["ESTE"] + d_este

# --- 3. MÓDULOS DE INTERFAZ ---

def render_direccional():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("🏹 UNIDAD DE NAVEGACIÓN DIRECCIONAL")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Datos del Survey Actual")
        curr = st.session_state.history.iloc[-1]
        st.metric("Profundidad Medida (MD)", f"{curr['MD']:.2f} m")
        st.metric("Inclinación", f"{curr['INC']}°")
        st.metric("Azimuth", f"{curr['AZI']}°")
        st.divider()
        st.metric("Profundidad Vertical (TVD)", f"{curr['TVD']:.2f} m")
        st.metric("Sección Vertical (VS)", f"{curr['VS']:.2f} m")

    with col2:
        # Gráfico de Proyección Horizontal (Plan View)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=st.session_state.history["ESTE"], y=st.session_state.history["NORTE"], 
                                 mode='lines+markers', name='Trayectoria Real', line=dict(color='cyan')))
        fig.update_layout(title="Vista de Planta (Coordenadas N/S - E/O)", template="plotly_dark", height=500)
        fig.update_xaxes(title="Este (+)")
        fig.update_yaxes(title="Norte (+)")
        st.plotly_chart(fig, use_container_width=True)

def render_survey_tool():
    st.title("📡 PROTOCOLO DE TOMA DE SURVEY (MWD)")
    st.info("Siga el procedimiento técnico: 1. Detener rotación -> 2. Apagar bombas -> 3. Esperar reset.")
    
    c1, c2, c3 = st.columns(3)
    if c1.button("1. APAGAR BOMBAS"):
        with st.spinner("Reseteando herramienta MWD..."):
            time.sleep(2)
            st.session_state.survey_ready = True
            st.success("Herramienta reseteada. Lista para Survey.")
            
    if c2.button("2. ENCENDER BOMBAS"):
        if st.session_state.survey_ready:
            st.toast("Recibiendo pulsos de lodo...")
            time.sleep(3)
            st.session_state.survey_ready = "DONE"
        else:
            st.error("Debe resetear (apagar bombas) primero.")

    if c3.button("3. DECODIFICAR DATOS"):
        if st.session_state.survey_ready == "DONE":
            st.balloons()
            st.write("✅ Datos Recibidos: MD, INC, AZI procesados con éxito.")
        else:
            st.warning("No hay datos en el buffer.")

# --- 4. SIDEBAR INSTRUCTOR ---
with st.sidebar:
    st.header("⚙️ CONTROL DIRECCIONAL")
    st.session_state.target_type = st.selectbox("Tipo de Pozo (Plan)", ["TANGENCIAL", "TIPO S"])
    
    inc_set = st.slider("Inclinación (°) en Toolface", 0.0, 90.0, st.session_state.inc)
    azi_set = st.slider("Azimuth (°)", 0.0, 360.0, st.session_state.azi)
    rop_set = st.slider("ROP (m/h)", 0, 50, 15)
    
    if st.button("▶️ PERFORAR TRAMO"): 
        st.session_state.is_drilling = True
        st.session_state.inc = inc_set
        st.session_state.azi = azi_set

# --- 5. LÓGICA DE AVANCE ---
if st.session_state.is_drilling:
    # Simular avance de 10 metros
    new_md = st.session_state.md + 10
    new_tvd, new_norte, new_este = calcular_minima_curvatura(new_md, st.session_state.inc, st.session_state.azi)
    
    # Cálculo de Sección Vertical (VS) simplificado
    new_vs = np.sqrt(new_norte**2 + new_este**2)
    
    # Actualizar estado
    st.session_state.md = new_md
    new_row = {
        "MD": new_md, "TVD": new_tvd, "INC": st.session_state.inc, 
        "AZI": st.session_state.azi, "NORTE": new_norte, "ESTE": new_este, "VS": new_vs
    }
    st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([new_row])], ignore_index=True)
    st.session_state.is_drilling = False # Perforamos por tramos (Surveys)
    st.rerun()

# --- 6. MENÚ PRINCIPAL ---
if st.session_state.menu == "HOME":
    st.title("🖥️ MENFA WELL SIM - PANEL DE EXPERTO")
    st.markdown("### Seleccione el Módulo de Control")
    ca, cb = st.columns(2)
    with ca:
        if st.button("🏹 NAVEGACIÓN DIRECCIONAL (Mínima Curvatura)", use_container_width=True): 
            st.session_state.menu = "DIRECCIONAL"
    with cb:
        if st.button("📡 PROTOCOLO SURVEY MWD", use_container_width=True): 
            st.session_state.menu = "SURVEY"
            
    # Gráfico de Perfil (Vertical Section)
    fig_v = go.Figure()
    fig_v.add_trace(go.Scatter(x=st.session_state.history["VS"], y=st.session_state.history["TVD"], 
                               mode='lines+markers', name='Perfil del Pozo'))
    fig_v.update_yaxes(autorange="reversed", title="TVD (m)")
    fig_v.update_xaxes(title="Sección Vertical (m)")
    fig_v.update_layout(title=f"Perfil de Pozo {st.session_state.target_type}", template="plotly_dark")
    st.plotly_chart(fig_v, use_container_width=True)

elif st.session_state.menu == "DIRECCIONAL": render_direccional()
elif st.session_state.menu == "SURVEY": render_survey_tool()

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time

# --- FUNCIONES TÉCNICAS (Lógica de Verificación) ---
def verificar_calculos(md, inc, azi, tvd_user, norte_user, este_user):
    # El simulador calcula el valor real (Mínima Curvatura) para comparar
    prev = st.session_state.history.iloc[-1]
    d_md = md - prev["MD"]
    rad_inc = np.radians(inc)
    
    # Cálculo simplificado para validación pedagógica (Tangencial)
    # Según CLASE 1: El método tangencial tiene margen de error, pero sirve para práctica
    tvd_real = prev["TVD"] + (d_md * np.cos(rad_inc))
    norte_real = prev["NORTE"] + (d_md * np.sin(rad_inc) * np.cos(np.radians(azi)))
    
    # Margen de error aceptable 1%
    error_tvd = abs(tvd_user - tvd_real) < (tvd_real * 0.01)
    error_norte = abs(norte_user - norte_real) < 1.0 # 1 metro de margen
    
    return error_tvd and error_norte, tvd_real, norte_real

# --- NUEVO MÓDULO: EXAMEN DE PLANILLA ---
def render_planilla_examen():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("📝 EXAMEN: Planilla de Cálculos Direccionales")
    st.subheader("Complete los valores calculados según el último Survey")

    # Datos que el MWD "envió" (MD, INC, AZI)
    md_actual = st.session_state.md
    inc_actual = st.session_state.inc
    azi_actual = st.session_state.azi
    
    st.info(f"📋 **DATOS DE CAMPO:** MD: {md_actual} m | INC: {inc_actual}° | AZI: {azi_actual}°")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        tvd_u = st.number_input("Calcule TVD (m)", value=0.0)
    with col2:
        norte_u = st.number_input("Coordenada NORTE (m)", value=0.0)
    with col3:
        este_u = st.number_input("Coordenada ESTE (m)", value=0.0)
        
    if st.button("✔️ VALIDAR Y REGISTRAR SURVEY"):
        es_valido, t_r, n_r = verificar_calculos(md_actual, inc_actual, azi_actual, tvd_u, norte_u, este_u)
        
        if es_valido:
            st.success("🎯 ¡CÁLCULOS CORRECTOS! Datos registrados en el historial del pozo.")
            # Guardamos los datos del usuario como oficiales
            new_row = {
                "MD": md_actual, "TVD": tvd_u, "INC": inc_actual, 
                "AZI": azi_actual, "NORTE": norte_u, "ESTE": este_u, "VS": np.sqrt(norte_u**2 + este_u**2)
            }
            st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([new_row])], ignore_index=True)
            st.session_state.menu = "DIRECCIONAL"
            st.rerun()
        else:
            st.error(f"❌ ERROR EN CÁLCULOS. El TVD teórico debería estar cerca de {t_r:.2f}. Revise sus fórmulas.")

# --- ACTUALIZACIÓN DEL MENÚ HOME ---
# Agregamos el acceso al examen en el render_home
def render_home():
    st.title("🖥️ MENFA WELL SIM - PANEL DE EXPERTO")
    st.image("logo_menfa.png", width=150)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏹 MONITOR DIRECCIONAL", use_container_width=True): 
            st.session_state.menu = "DIRECCIONAL"
    with c2:
        if st.button("📡 TOMA DE SURVEY (MWD)", use_container_width=True): 
            st.session_state.menu = "SURVEY"
    with c3:
        # Solo se habilita si hay un MD nuevo sin procesar
        if st.button("📝 COMPLETAR PLANILLA", use_container_width=True): 
            st.session_state.menu = "PLANILLA"

# --- AGREGAR AL NAVEGADOR ---
if st.session_state.menu == "PLANILLA":
    render_planilla_examen()

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="IPCL MENFA WELL SIM V6 - FULL", layout="wide", initial_sidebar_state="expanded")

# Inicialización de todas las variables de estado (EVITA ATTRIBUTE ERROR)
if "initialized" not in st.session_state:
    st.session_state.update({
        "initialized": True,
        "menu": "HOME",
        "md": 1000.0,
        "tvd": 1000.0,
        "inc": 0.0,
        "azi": 0.0,
        "norte": 0.0,
        "este": 0.0,
        "vs": 0.0,
        "is_drilling": False,
        "status": "ESTABLE",
        "pit_volume": 500.0,
        "survey_ready": False,
        "gas_total": 0.5,
        "history": pd.DataFrame([{
            "MD": 1000.0, "TVD": 1000.0, "INC": 0.0, "AZI": 0.0, "NORTE": 0.0, "ESTE": 0.0, "VS": 0.0, "ECD": 10.5, "GAS": 0.5
        }]),
        "target_type": "TANGENCIAL"
    })

# --- 2. MOTORES DE CÁLCULO (Física, Lodo y Direccional) ---

def calcular_minima_curvatura(md_new, inc_new, azi_new):
    prev = st.session_state.history.iloc[-1]
    d_md = md_new - prev["MD"]
    i1, i2 = np.radians(prev["INC"]), np.radians(inc_new)
    a1, a2 = np.radians(prev["AZI"]), np.radians(azi_new)
    cos_dl = np.cos(i2 - i1) - (np.sin(i1) * np.sin(i2) * (1 - np.cos(a2 - a1)))
    dl = np.arccos(np.clip(cos_dl, -1, 1))
    rf = (2 / dl) * np.tan(dl / 2) if dl != 0 else 1
    d_tvd = (d_md / 2) * (np.cos(i1) + np.cos(i2)) * rf
    d_norte = (d_md / 2) * (np.sin(i1) * np.cos(a1) + np.sin(i2) * np.cos(a2)) * rf
    d_este = (d_md / 2) * (np.sin(i1) * np.sin(a1) + np.sin(i2) * np.sin(a2)) * rf
    return prev["TVD"] + d_tvd, prev["NORTE"] + d_norte, prev["ESTE"] + d_este

def engine_physics(mw_static, depth, gpm):
    # ECD simplificado
    v_ann = (24.51 * gpm) / (8.5**2 - 5.0**2) if gpm > 0 else 0
    ecd = mw_static + (v_ann / 100)
    # Presiones
    p_fondo = 0.052 * ecd * (depth * 3.28)
    p_poro = 0.47 * (depth * 3.28)
    p_frac = 0.82 * (depth * 3.28)
    
    status = "ESTABLE"
    if p_fondo < p_poro: status = "KICK"
    elif p_fondo > p_frac: status = "LOSS"
    
    gas = 5.0 + np.random.normal(0, 1) if 1200 < depth < 1500 else 0.5
    return ecd, status, gas

# --- 3. MÓDULOS DE INTERFAZ (RENDERS) ---

def render_scada():
    st.header("📊 Monitor SCADA - Tiempo Real")
    curr = st.session_state.history.iloc[-1]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("MD (m)", f"{st.session_state.md:.2f}")
    m2.metric("ECD (ppg)", f"{curr['ECD']:.2f}")
    m3.metric("Gas Total", f"{curr['GAS']:.2f} u")
    if st.session_state.status == "KICK": m4.error("🚨 KICK")
    elif st.session_state.status == "LOSS": m4.warning("📉 PÉRDIDA")
    else: m4.success("✅ ESTABLE")

    fig = make_subplots(rows=1, cols=2, subplot_titles=("Perfil Vertical", "Cromatografía"))
    fig.add_trace(go.Scatter(x=st.session_state.history["VS"], y=st.session_state.history["TVD"], name="Trayectoria"), row=1, col=1)
    fig.add_trace(go.Scatter(x=st.session_state.history["GAS"], y=st.session_state.history["MD"], name="Gas"), row=1, col=2)
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

def render_survey_mwd():
    st.title("📡 Protocolo Survey MWD")
    st.info("Siga la secuencia CLASE 1: Apagar Bombas -> Esperar Reset -> Recibir")
    c1, c2, c3 = st.columns(3)
    if c1.button("1. STOP PUMPS (Reset)"): 
        st.session_state.survey_ready = "WAITING"
        st.toast("MWD Reseteando...")
    if c2.button("2. START PUMPS (Pulsos)"):
        if st.session_state.survey_ready == "WAITING":
            st.session_state.survey_ready = "READY"
            st.success("Pulsos decodificados")
    if c3.button("3. LEER DATOS"):
        if st.session_state.survey_ready == "READY":
            st.write(f"**DATOS CRUDOS:** MD: {st.session_state.md} | INC: {st.session_state.inc} | AZI: {st.session_state.azi}")
            if st.button("Ir a Planilla"): st.session_state.menu = "PLANILLA"

def render_planilla_examen():
    st.title("📝 Planilla de Cálculos (Examen)")
    st.warning("Ingrese los valores calculados manualmente para validar el tramo.")
    md_a = st.session_state.md
    c1, c2, c3 = st.columns(3)
    tvd_u = c1.number_input("TVD Calculado")
    norte_u = c2.number_input("Norte Calculado")
    este_u = c3.number_input("Este Calculado")
    
    if st.button("Validar Survey"):
        # Validación lógica
        t_real, n_real, e_real = calcular_minima_curvatura(md_a, st.session_state.inc, st.session_state.azi)
        if abs(tvd_u - t_real) < 2.0:
            st.success("🎯 CÁLCULO CORRECTO")
            new_row = {"MD": md_a, "TVD": tvd_u, "INC": st.session_state.inc, "AZI": st.session_state.azi, 
                       "NORTE": norte_u, "ESTE": este_u, "VS": np.sqrt(norte_u**2 + este_u**2), 
                       "ECD": 10.5, "GAS": 0.5}
            st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([new_row])], ignore_index=True)
            st.session_state.menu = "SCADA"
        else:
            st.error(f"❌ ERROR. TVD esperado cerca de {t_real:.2f}")

# --- 4. SIDEBAR (CONTROLES) ---
with st.sidebar:
    st.image("logo_menfa.png", width=150)
    st.header("🕹️ Mando del Instructor")
    rop = st.slider("ROP (m/h)", 0, 60, 20)
    mw_static = st.number_input("Densidad Lodo (ppg)", 8.0, 18.0, 10.5)
    gpm = st.slider("Caudal (GPM)", 0, 800, 450)
    st.divider()
    st.header("🏹 Navegación Direccional")
    inc_set = st.slider("Ajustar INC", 0.0, 90.0, st.session_state.inc)
    azi_set = st.slider("Ajustar AZI", 0.0, 360.0, st.session_state.azi)
    
    if st.button("▶️ PERFORAR TRAMO (10m)"):
        st.session_state.is_drilling = True
        st.session_state.inc = inc_set
        st.session_state.azi = azi_set

# --- 5. LÓGICA DE SIMULACIÓN ---
if st.session_state.is_drilling:
    st.session_state.md += 10
    ecd, status, gas = engine_physics(mw_static, st.session_state.md, gpm)
    st.session_state.status = status
    # Agregamos temporalmente al historial para ver el SCADA
    temp_row = {"MD": st.session_state.md, "TVD": st.session_state.tvd, "INC": st.session_state.inc, 
                "AZI": st.session_state.azi, "NORTE": st.session_state.norte, "ESTE": st.session_state.este, 
                "VS": st.session_state.vs, "ECD": ecd, "GAS": gas}
    st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([temp_row])], ignore_index=True)
    st.session_state.is_drilling = False
    st.toast("Tramo perforado. Tome Survey.")

# --- 6. NAVEGACIÓN Y MENÚ ---
if st.session_state.menu == "HOME":
    st.title("🖥️ MENFA WELL SIM - SISTEMA INTEGRADO")
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("📊 SCADA", use_container_width=True): st.session_state.menu = "SCADA"
    if c2.button("📡 SURVEY MWD", use_container_width=True): st.session_state.menu = "SURVEY"
    if c3.button("📝 PLANILLA", use_container_width=True): st.session_state.menu = "PLANILLA"
    if c4.button("🛡️ BOP", use_container_width=True): st.session_state.menu = "BOP"
    st.image("Gemini_Generated_Image_jl30d0jl30d0jl30.png", use_container_width=True)

elif st.session_state.menu == "SCADA":
    st.button("🔙 HOME", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    render_scada()
elif st.session_state.menu == "SURVEY":
    st.button("🔙 HOME", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    render_survey_mwd()
elif st.session_state.menu == "PLANILLA":
    st.button("🔙 HOME", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    render_planilla_examen()
elif st.session_state.menu == "BOP":
    st.button("🔙 HOME", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("🛡️ Panel de Seguridad BOP")
    st.image("Gemini_Generated_Image_dn7zasdn7zasdn7z.png", width=500)
    if st.button("🔥 CIERRE DE EMERGENCIA", type="primary"): st.error("POZO CERRADO")

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# --- 1. CONFIGURACIÓN TÉCNICA E INICIALIZACIÓN ---
st.set_page_config(page_title="MENFA WELL SIMULATION ENGINE V7", layout="wide")

if "initialized" not in st.session_state:
    st.session_state.update({
        "initialized": True,
        "menu": "HOME",
        "md": 1500.0,
        "tvd": 1500.0,
        "inc": 0.0,
        "azi": 0.0,
        "is_drilling": False,
        "pit_volume": 450.0, # bbl
        "pump_press": 0.0,   # SPP (psi)
        "bit_wear": 0.0,     # Desgaste de broca
        "history": pd.DataFrame([{
            "MD": 1500.0, "TVD": 1500.0, "INC": 0.0, "AZI": 0.0, 
            "SPP": 0.0, "ECD": 10.5, "GPM": 400.0, "WOB": 0.0, "ROP": 0.0
        }]),
        "status": "OFFLINE"
    })

# --- 2. MOTOR DE INGENIERÍA (HIDRÁULICA Y MECÁNICA) ---

def calcular_hidraulica(mw, depth, gpm, nozzles):
    """Cálculos basados en el documento HIDRAULICA DE PERFORACION"""
    # Velocidad en las boquillas (Vn) - Eq 4.31
    total_area = sum([0.7854 * (d/32)**2 for d in nozzles]) # Area en pulgadas2
    vn = (0.3208 * gpm) / total_area if total_area > 0 else 0 # ft/s
    
    # Caída de presión en la broca (delta P bit)
    dp_bit = (mw * vn**2) / 1085.8
    
    # Pérdidas por fricción estimadas (Pérdidas en el sistema)
    dp_system = (mw**0.8 * gpm**1.8 * depth) / (1000 * 8.5**4.8)
    
    spp = dp_bit + dp_system
    # Cálculo de ECD (Equivalent Circulating Density)
    ecd = mw + (dp_system / (0.052 * depth * 3.28))
    
    return round(spp, 1), round(ecd, 2), round(vn, 1)

def calcular_mecanica_perforacion(wob, rpm, bit_wear):
    """Cálculos basados en PROCESO DE PERFORACION ROTATORIA"""
    # ROP simplificado basado en WOB y RPM considerando desgaste
    base_rop = (wob * 0.8) * (rpm / 100)
    rop_final = base_rop * (1 - bit_wear)
    return round(rop_final, 1)

# --- 3. COMPONENTES DE LA INTERFAZ ---

def render_scada():
    st.header("📊 SISTEMA DE MONITOREO EN TIEMPO REAL (SCADA)")
    curr = st.session_state.history.iloc[-1]
    
    # Layout de métricas críticas
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("SPP (psi)", f"{st.session_state.pump_press}")
    c2.metric("ECD (ppg)", f"{curr['ECD']}")
    c3.metric("ROP (m/h)", f"{curr['ROP']}")
    c4.metric("TVD (m)", f"{curr['TVD']:.2f}")
    
    if st.session_state.status == "KICK":
        c5.error("🚨 KICK DETECTADO")
    else:
        c5.success("✅ OPERACIÓN NORMAL")

    # Gráficos de Ingeniería
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Presión de Bomba vs MD", "Log de Gas/Litología"))
    fig.add_trace(go.Scatter(x=st.session_state.history["SPP"], y=st.session_state.history["MD"], name="SPP"), row=1, col=1)
    fig.add_trace(go.Scatter(x=np.random.normal(2, 0.5, len(st.session_state.history)), y=st.session_state.history["MD"], name="Gas"), row=1, col=2)
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(height=450, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

def render_hidraulica_bit():
    st.title("🌊 OPTIMIZACIÓN HIDRÁULICA DE LA BROCA")
    st.info("Ajuste el programa de boquillas (nozzles) para maximizar la fuerza de impacto.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Configuración de Toberas (1/32 in)")
        n1 = st.number_input("Nozzle 1", 10, 16, 12)
        n2 = st.number_input("Nozzle 2", 10, 16, 12)
        n3 = st.number_input("Nozzle 3", 10, 16, 12)
    
    with col_b:
        spp, ecd, vn = calcular_hidraulica(10.5, st.session_state.md, 450, [n1, n2, n3])
        st.metric("Velocidad en Boquillas (Vn)", f"{vn} ft/s")
        st.progress(min(vn/400, 1.0), text="Limpieza de Fondo")
        st.write(f"**Área de Flujo Total (TFA):** {0.7854 * ((n1/32)**2 + (n2/32)**2 + (n3/32)**2):.4f} in²")

# --- 4. PANEL LATERAL (CONSOLA DEL PERFORADOR) ---
with st.sidebar:
    st.image("logo_menfa.png", width=180)
    st.header("🎮 CONSOLA DE MANDO")
    
    # Parámetros Operativos
    mw_in = st.number_input("MW (Density - ppg)", 8.3, 18.0, 10.5)
    gpm_in = st.slider("Flow Rate (GPM)", 0, 800, 420)
    wob_in = st.slider("WOB (Weight on Bit - klbs)", 0, 50, 25)
    rpm_in = st.slider("RPM", 0, 180, 110)
    
    st.divider()
    if st.button("▶️ INICIAR CIRCULACIÓN/PERFORACIÓN"):
        st.session_state.is_drilling = True
    if st.button("🛑 PARADA DE EMERGENCIA"):
        st.session_state.is_drilling = False

# --- 5. BUCLE DE CÁLCULO Y SIMULACIÓN ---
if st.session_state.is_drilling:
    # 1. Hidráulica
    spp, ecd, vn = calcular_hidraulica(mw_in, st.session_state.md, gpm_in, [12, 12, 12])
    st.session_state.pump_press = spp
    
    # 2. Mecánica (Avanzar 5m por ciclo)
    rop = calcular_mecanica_perforacion(wob_in, rpm_in, st.session_state.bit_wear)
    st.session_state.md += (rop / 60) # Avance en el tiempo
    st.session_state.tvd = st.session_state.md # Asumiendo vertical para este módulo
    
    # 3. Guardar en Historial Técnico
    new_data = {
        "MD": st.session_state.md, "TVD": st.session_state.tvd, "INC": 0.0, "AZI": 0.0,
        "SPP": spp, "ECD": ecd, "GPM": gpm_in, "WOB": wob_in, "ROP": rop
    }
    st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([new_data])], ignore_index=True)
    
    # 4. Desgaste de broca (Documento Proceso Rotatorio)
    st.session_state.bit_wear += 0.001
    
    time.sleep(0.5)
    st.rerun()

# --- 6. NAVEGACIÓN ---
if st.session_state.menu == "HOME":
    st.title("🚀 MENFA WELL SIM V7 - INGENIERÍA AVANZADA")
    c1, c2, c3 = st.columns(3)
    if c1.button("📊 MONITOR SCADA", use_container_width=True): st.session_state.menu = "SCADA"
    if c2.button("🌊 HIDRÁULICA DE BROCA", use_container_width=True): st.session_state.menu = "HIDRAULICA"
    if c3.button("🛡️ PANEL BOP / SEGURIDAD", use_container_width=True): st.session_state.menu = "BOP"
    
    st.image("Gemini_Generated_Image_jl30d0jl30d0jl30.png", use_container_width=True)

elif st.session_state.menu == "SCADA":
    if st.button("🔙 VOLVER"): st.session_state.menu = "HOME"
    render_scada()
elif st.session_state.menu == "HIDRAULICA":
    if st.button("🔙 VOLVER"): st.session_state.menu = "HOME"
    render_hidraulica_bit()

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# --- 1. CONFIGURACIÓN TÉCNICA E INICIALIZACIÓN ---
st.set_page_config(page_title="MENFA WELL SIM V7 - INGENIERÍA TOTAL", layout="wide")

if "initialized" not in st.session_state:
    st.session_state.update({
        "initialized": True,
        "menu": "HOME",
        "md": 1500.0,
        "tvd": 1500.0,
        "inc": 0.0,
        "azi": 0.0,
        "norte": 0.0,
        "este": 0.0,
        "vs": 0.0,
        "is_drilling": False,
        "survey_timer": 0,
        "survey_status": "IDLE",
        "bit_wear": 0.0,
        "mud_type": "Bentonítico",
        "nozzles": [12, 12, 12], # en 1/32"
        "history": pd.DataFrame([{
            "MD": 1500.0, "TVD": 1500.0, "INC": 0.0, "AZI": 0.0, 
            "SPP": 0.0, "ECD": 10.5, "GPM": 400.0, "ROP": 0.0, "BIT_WEAR": 0.0
        }]),
        "status": "ESTABLE"
    })

# --- 2. MOTORES DE CÁLCULO BASADOS EN DOCUMENTACIÓN ---

def motor_hidraulico(mw, depth, gpm, nozzles):
    """Basado en HIDRAULICA DE PERFORACION - Cálculo de Vn y SPP"""
    tfa = sum([0.7854 * (n/32)**2 for n in nozzles])
    vn = (0.3208 * gpm) / tfa if tfa > 0 else 0 # Velocidad en boquillas (ft/s)
    
    # Caída de presión en la broca (Ecuación 4.31)
    pb = (mw * vn**2) / 1085.8
    # Pérdidas en el sistema (estimación por fricción anular y tubería)
    ps = (mw**0.8 * gpm**1.8 * depth) / (1000 * 8.5**4.8)
    
    spp = pb + ps
    ecd = mw + (ps / (0.052 * depth * 3.28))
    hhp_bit = (pb * gpm) / 1714 # Potencia hidráulica en la broca
    return round(spp, 1), round(ecd, 2), round(vn, 1), round(hhp_bit, 2)

def motor_direccional(md_n, inc_n, azi_n):
    """Basado en CLASE 1 - Método de Mínima Curvatura"""
    prev = st.session_state.history.iloc[-1]
    d_md = md_n - prev["MD"]
    i1, i2 = np.radians(prev["INC"]), np.radians(inc_n)
    a1, a2 = np.radians(prev["AZI"]), np.radians(azi_n)
    
    cos_dl = np.cos(i2 - i1) - (np.sin(i1) * np.sin(i2) * (1 - np.cos(a2 - a1)))
    dl = np.arccos(np.clip(cos_dl, -1, 1))
    rf = (2 / dl) * np.tan(dl / 2) if dl != 0 else 1
    
    tvd = prev["TVD"] + (d_md / 2) * (np.cos(i1) + np.cos(i2)) * rf
    norte = prev["NORTE"] + (d_md / 2) * (np.sin(i1) * np.cos(a1) + np.sin(i2) * np.cos(a2)) * rf
    este = prev["ESTE"] + (d_md / 2) * (np.sin(i1) * np.sin(a1) + np.sin(i2) * np.sin(a2)) * rf
    return round(tvd, 2), round(norte, 2), round(este, 2)

# --- 3. MÓDULOS DE INTERFAZ ---

def render_scada():
    st.header("📊 SCADA - UNIDAD DE PERFORACIÓN")
    curr = st.session_state.history.iloc[-1]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("MD / TVD", f"{curr['MD']:.1f} / {curr['TVD']:.1f} m")
    col2.metric("SPP (Stand Pipe)", f"{curr['SPP']} psi")
    col3.metric("ECD", f"{curr['ECD']} ppg")
    col4.metric("ROP", f"{curr['ROP']} m/h")

    # Gráfico de Perfil del Pozo (Vertical Section)
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Trayectoria Vertical", "Hidráulica de Fondo"))
    fig.add_trace(go.Scatter(x=st.session_state.history["VS"], y=st.session_state.history["TVD"], name="Well Path"), row=1, col=1)
    fig.add_trace(go.Scatter(x=st.session_state.history["SPP"], y=st.session_state.history["MD"], name="SPP Log"), row=1, col=2)
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

def render_mwd_protocol():
    st.title("📡 MWD SURVEY PROTOCOL (CLASE 1)")
    st.write("Siga los pasos técnicos para decodificar la trayectoria.")
    
    if st.session_state.survey_status == "IDLE":
        if st.button("1. APAGAR BOMBAS (Reset Tool)"):
            st.session_state.survey_status = "RESETTING"
            st.session_state.survey_timer = time.time()
            st.rerun()
            
    if st.session_state.survey_status == "RESETTING":
        elapsed = int(time.time() - st.session_state.survey_timer)
        st.warning(f"Esperando Reset de Herramienta... {elapsed}/90 seg (Según Documento)")
        if elapsed >= 10: # Reducido para demo, real son 90s
            st.success("Herramienta Reseteada.")
            if st.button("2. ENCENDER BOMBAS (Enviar Pulsos)"):
                st.session_state.survey_status = "RECEIVING"
                st.rerun()

    if st.session_state.survey_status == "RECEIVING":
        st.info("Recibiendo pulsos de lodo... Decodificando Secuencia binaria.")
        time.sleep(2)
        st.session_state.survey_status = "DONE"
        st.rerun()

    if st.session_state.survey_status == "DONE":
        st.success(f"SURVEY RECIBIDO: INC {st.session_state.inc}° | AZI {st.session_state.azi}°")
        if st.button("Ir a Planilla de Cálculos"):
            st.session_state.menu = "PLANILLA"

# --- 4. SIDEBAR (CONSOLA DE INGENIERÍA) ---
with st.sidebar:
    st.header("⚙️ PARÁMETROS TÉCNICOS")
    mud_w = st.number_input("Mud Weight (ppg)", 8.3, 18.0, 10.5)
    gpm_in = st.slider("Caudal (GPM)", 0, 800, 420)
    wob_in = st.slider("WOB (klbs)", 0, 50, 25)
    rpm_in = st.slider("RPM", 0, 150, 100)
    
    st.divider()
    st.header("🏹 DIRECCIONAL")
    inc_target = st.slider("Nueva INC", 0.0, 90.0, st.session_state.inc)
    azi_target = st.slider("Nuevo AZI", 0.0, 360.0, st.session_state.azi)
    
    if st.button("▶️ PERFORAR TRAMO (30m)"):
        st.session_state.is_drilling = True
        st.session_state.inc = inc_target
        st.session_state.azi = azi_target

# --- 5. LÓGICA DE SIMULACIÓN ---
if st.session_state.is_drilling:
    # Cálculos de Ingeniería
    new_md = st.session_state.md + 30
    spp, ecd, vn, hhp = motor_hidraulico(mud_w, new_md, gpm_in, st.session_state.nozzles)
    tvd, norte, este = motor_direccional(new_md, st.session_state.inc, st.session_state.azi)
    
    # Basado en Proceso Rotatorio: ROP depende de WOB/RPM y desgaste
    rop = (wob_in * 0.5) * (rpm_in / 100) * (1 - st.session_state.bit_wear)
    
    # Actualizar estado
    st.session_state.md = new_md
    st.session_state.bit_wear += 0.02 # Desgaste por tramo
    
    new_row = {
        "MD": new_md, "TVD": tvd, "INC": st.session_state.inc, "AZI": st.session_state.azi,
        "NORTE": norte, "ESTE": este, "VS": np.sqrt(norte**2 + este**2),
        "SPP": spp, "ECD": ecd, "GPM": gpm_in, "ROP": rop, "BIT_WEAR": st.session_state.bit_wear
    }
    st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([new_row])], ignore_index=True)
    st.session_state.is_drilling = False
    st.toast("Tramo perforado. Proceda a tomar Survey.")

# --- 6. NAVEGACIÓN ---
if st.session_state.menu == "HOME":
    st.title("🖥️ IPCL MENFA WELL SIM V7.0")
    cols = st.columns(4)
    if cols[0].button("📊 SCADA", use_container_width=True): st.session_state.menu = "SCADA"
    if cols[1].button("📡 SURVEY MWD", use_container_width=True): st.session_state.menu = "SURVEY"
    if cols[2].button("📝 PLANILLA", use_container_width=True): st.session_state.menu = "PLANILLA"
    if cols[3].button("🛡️ BOP", use_container_width=True): st.session_state.menu = "BOP"
    st.image("Gemini_Generated_Image_jl30d0jl30d0jl30.png", use_container_width=True)

elif st.session_state.menu == "SCADA":
    if st.button("🔙 HOME"): st.session_state.menu = "HOME"
    render_scada()
elif st.session_state.menu == "SURVEY":
    if st.button("🔙 HOME"): st.session_state.menu = "HOME"
    render_mwd_protocol()

if "initialized" not in st.session_state:
    st.session_state.update({
        "mud_density": 10.5,       # ppg
        "buoyancy_factor": 0.839,  # Factor de flotación (Clase 4)
        "hook_load": 75.0,         # Carga del gancho (Toneladas)
        "neutral_point": 0.0,      # Punto neutro en los Portamechas (Clase 3)
        "casing_depth": 0.0,       # Profundidad de la TR (Clase 5)
        "annular_velocity": 0.0,    # Velocidad Anular para limpieza (Clase 4)
    })

def render_mecanica_sarta():
    st.title("🏗️ Mecánica de la Sarta y Cargas")
    
    # Cálculo de Factor de Flotación (Clase 4: f = 1 - (MW / 65.5))
    ff = 1 - (st.session_state.mud_density / 65.5)
    
    col1, col2 = st.columns(2)
    with col1:
        wob_aplicado = st.slider("Peso sobre el Trépano (WOB - TN)", 0, 40, 15)
        peso_teorico = 80.0 # Peso de la sarta en el aire
        peso_efectivo = peso_teorico * ff
        
        # Clase 3: Peso de la sarta = Carga del gancho + WOB
        carga_gancho = peso_efectivo - wob_aplicado
        st.metric("Carga en el Gancho (Hook Load)", f"{carga_gancho:.2f} TN")
        
    with col2:
        st.subheader("Análisis de Punto Neutro")
        # El punto neutro debe quedar en los Portamechas (DC) para evitar fallas
        if wob_aplicado > (25 * ff): # Asumiendo 25 TN de DC
            st.error("⚠️ PUNTO NEUTRO EN BHA - RIESGO DE PANDEO (Buckling)")
        else:
            st.success("✅ Punto Neutro en Portamechas")

def render_fluidos_avanzado():
    st.title("🧪 Propiedades del Fluido y Limpieza")
    
    c1, c2 = st.columns(2)
    with c1:
        viscosidad = st.number_input("Viscosidad Marsh (seg/qt)", 35, 60, 45)
        st.write("**Funciones del Lodo activas:**")
        st.write("- Suspensión de recortes (Gel)")
        st.write("- Control de presión de formación")
        
    with col2:
        # Lógica de Velocidad Anular (Clase 4)
        v_anular = (24.51 * st.session_state.gpm) / (8.5**2 - 5.0**2)
        st.metric("Velocidad Anular", f"{v_anular:.1f} ft/min")
        
        if v_anular < 100:
            st.warning("⚠️ Velocidad insuficiente para transporte de recortes")

def render_casing_cementacion():
    st.title("🛠️ Entubación y Cementación")
    
    st.info("Secuencia: Calibrar pozo -> Bajar Casing -> Circular -> Cementar")
    
    if st.button("Bajar Zapato Guía"):
        with st.spinner("Bajando Casing con Zapato Flotador..."):
            time.sleep(2)
            st.session_state.casing_depth = st.session_state.md
            st.success(f"TR asentada en {st.session_state.casing_depth} m")
            
    st.divider()
    st.subheader("Equipo de Flotación")
    col_tr1, col_tr2 = st.columns(2)
    col_tr1.checkbox("Zapato Flotador (Válvula Check)", value=True)
    col_tr2.checkbox("Rascadores de Pared (Limpieza de Revoque)")

def render_home_completo():
    st.title("🖥️ SIMULADOR INTEGRAL DE PERFORACIÓN - MENFA")
    
    # Grilla técnica 2x3
    fil1_c1, fil1_c2, fil1_c3 = st.columns(3)
    fil2_c1, fil2_c2, fil2_c3 = st.columns(3)
    
    with fil1_c1:
        if st.button("📊 SCADA / DRILLING", use_container_width=True): st.session_state.menu = "SCADA"
    with fil1_c2:
        if st.button("🏹 DIRECCIONAL / MWD", use_container_width=True): st.session_state.menu = "SURVEY"
    with fil1_c3:
        if st.button("🌊 HIDRÁULICA BIT", use_container_width=True): st.session_state.menu = "HIDRAULICA"
        
    with fil2_c1:
        if st.button("🏗️ MECÁNICA (WOB/FF)", use_container_width=True): st.session_state.menu = "MECANICA"
    with fil2_c2:
        if st.button("🧪 FLUIDOS / LIMPIEZA", use_container_width=True): st.session_state.menu = "FLUIDOS"
    with fil2_c3:
        if st.button("🛠️ CASING / CEMENTO", use_container_width=True): st.session_state.menu = "CASING"

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN TÉCNICA ---
st.set_page_config(page_title="MENFA WELL SIM - FULL ENGINEERING", layout="wide")

if "initialized" not in st.session_state:
    st.session_state.update({
        "initialized": True,
        "menu": "HOME",
        "md": 2000.0,
        "tvd": 2000.0,
        "mw": 10.5,           # Densidad (ppg)
        "gpm": 450.0,         # Caudal
        "wob": 0.0,           # Peso sobre trépano (TN)
        "rpm": 0,
        "bit_wear": 0.1,      # Desgaste (0 a 1)
        "casing_status": "OPEN HOLE",
        "history": pd.DataFrame([{
            "MD": 2000.0, "TVD": 2000.0, "HKLD": 80.0, "ECD": 10.5, "ROP": 0.0
        }])
    })

# --- 2. MOTORES DE CÁLCULO (FÍSICA DE CAMPO) ---

def calcular_mecanica_sarta(mw, wob_aplicado):
    """Basado en CLASE 3 y 4: Factor de Flotación y Cargas"""
    # Factor de Flotación (FF) - Clase 4
    ff = 1 - (mw / 65.5)
    
    # Peso de la sarta en el aire (Teórico: 100 TN para este ejemplo)
    peso_aire = 100.0 
    peso_efectivo = peso_aire * ff
    
    # Carga del Gancho (Hook Load) - Clase 3
    # HKLD = Peso Efectivo - WOB
    hkld = peso_efectivo - wob_aplicado
    
    # Punto Neutro (Estimación técnica)
    # Debe estar en los Portamechas (DC). Si WOB > Peso DC * FF, hay riesgo.
    peso_dc_efectivo = 30.0 * ff 
    punto_neutro_ok = wob_aplicado < peso_dc_efectivo
    
    return round(hkld, 2), round(ff, 4), punto_neutro_ok

def calcular_limpieza_pozo(gpm, mw):
    """Basado en CLASE 4: Velocidad Anular"""
    # Diámetros: Hole 8.5", DP 5.0"
    v_anular = (24.51 * gpm) / (8.5**2 - 5.0**2)
    # Estado de limpieza (Criterio técnico > 120 ft/min)
    limpieza_ok = v_anular > 120
    return round(v_anular, 2), limpieza_ok

# --- 3. MÓDULOS TÉCNICOS ---

def render_mecanica():
    st.header("🏗️ MECÁNICA DE SARTA Y CONTROL DE CARGAS")
    st.info("Cálculo de boyancia y punto neutro según Clase 3.")
    
    col1, col2 = st.columns(2)
    with col1:
        wob = st.slider("WOB - Peso sobre Trépano (TN)", 0, 40, int(st.session_state.wob))
        hkld, ff, pn_ok = calcular_mecanica_sarta(st.session_state.mw, wob)
        st.session_state.wob = wob
        
        st.metric("Hook Load (Carga Gancho)", f"{hkld} TN")
        st.metric("Factor de Flotación (FF)", f"{ff}")

    with col2:
        st.subheader("Estado de Esfuerzos")
        if pn_ok:
            st.success("✅ PUNTO NEUTRO EN PORTAMECHAS (Seguro)")
        else:
            st.error("🚨 CRÍTICO: PUNTO NEUTRO EN BARRAS (Riesgo de Pandeo)")
        
        # Visualización de la sarta
        st.write("**Distribución de Pesos:**")
        st.progress(min(wob/40, 1.0), text=f"Compresión en el fondo: {wob} TN")

def render_lodos():
    st.header("🧪 LABORATORIO DE FLUIDOS Y LIMPIEZA")
    st.info("Funciones del lodo y transporte de recortes (Clase 4).")
    
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.mw = st.number_input("Densidad del Lodo (ppg)", 8.3, 18.0, st.session_state.mw)
        st.session_state.gpm = st.slider("Caudal de Bomba (GPM)", 0, 800, int(st.session_state.gpm))
        
    with c2:
        va, clean_ok = calcular_limpieza_pozo(st.session_state.gpm, st.session_state.mw)
        st.metric("Velocidad Anular (VA)", f"{va} ft/min")
        if clean_ok:
            st.success("🌊 Limpieza de pozo eficiente")
        else:
            st.warning("⚠️ Riesgo de embotamiento / Asentamiento de recortes")

def render_casing():
    st.header("🛠️ INTEGRIDAD: CASING Y CEMENTACIÓN")
    st.info("Operaciones previas y accesorios (Clase 5).")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("**Lista de Chequeo Pre-Entubado:**")
        st.checkbox("Calibración de pozo realizada")
        st.checkbox("Tapón densificado inyectado")
        
        if st.button("🚀 BAJAR CASING (TR)"):
            with st.spinner("Bajando sarta con Zapato Flotador..."):
                time.sleep(2)
                st.session_state.casing_status = "CASING SET"
                st.success("TR posicionada en fondo.")

    with col_b:
        st.subheader("Accesorios de Fondo")
        st.write("- **Zapato Flotador:** Válvula check activa.")
        st.write("- **Rascadores:** Limpiando revoque para cementación.")
        if st.session_state.casing_status == "CASING SET":
            if st.button("🏗️ INICIAR CEMENTACIÓN"):
                st.toast("Desplazando lechada de cemento...")

# --- 4. PANEL PRINCIPAL (HOME) ---

def render_home():
    st.title("🖥️ MENFA WELL SIM - CONSOLA DE INGENIERÍA INTEGRAL")
    st.markdown("---")
    
    # Navegación por Módulos Técnicos
    m1, m2, m3 = st.columns(3)
    with m1:
        if st.button("🏗️ MECÁNICA DE SARTA", use_container_width=True): st.session_state.menu = "MECANICA"
    with m2:
        if st.button("🧪 FLUIDOS Y LIMPIEZA", use_container_width=True): st.session_state.menu = "LODOS"
    with m3:
        if st.button("🛠️ CASING Y CEMENTO", use_container_width=True): st.session_state.menu = "CASING"

    # Gráfico SCADA de resumen
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=st.session_state.history["HKLD"], y=st.session_state.history["MD"], name="Hook Load Log"))
    fig.update_yaxes(autorange="reversed", title="Profundidad (m)")
    fig.update_layout(title="Registro de Parámetros de Perforación", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# --- 5. NAVEGACIÓN ---
if st.session_state.menu == "HOME": render_home()
elif st.session_state.menu == "MECANICA":
    if st.button("🔙 VOLVER"): st.session_state.menu = "HOME"
    render_mecanica()
elif st.session_state.menu == "LODOS":
    if st.button("🔙 VOLVER"): st.session_state.menu = "HOME"
    render_lodos()
elif st.session_state.menu == "CASING":
    if st.button("🔙 VOLVER"): st.session_state.menu = "HOME"
    render_casing()

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN TÉCNICA ---
st.set_page_config(page_title="MENFA WELL SIM - FULL ENGINEERING", layout="wide")

if "initialized" not in st.session_state:
    st.session_state.update({
        "initialized": True,
        "menu": "HOME",
        "md": 2000.0,
        "tvd": 2000.0,
        "mw": 10.5,           # Densidad (ppg)
        "gpm": 450.0,         # Caudal
        "wob": 0.0,           # Peso sobre trépano (TN)
        "rpm": 0,
        "bit_wear": 0.1,      # Desgaste (0 a 1)
        "casing_status": "OPEN HOLE",
        "history": pd.DataFrame([{
            "MD": 2000.0, "TVD": 2000.0, "HKLD": 80.0, "ECD": 10.5, "ROP": 0.0
        }])
    })

# --- 2. MOTORES DE CÁLCULO (FÍSICA DE CAMPO) ---

def calcular_mecanica_sarta(mw, wob_aplicado):
    """Basado en CLASE 3 y 4: Factor de Flotación y Cargas"""
    # Factor de Flotación (FF) - Clase 4: 1 - (Densidad Lodo / Densidad Acero)
    ff = 1 - (mw / 65.5)
    
    # Peso de la sarta en el aire (Teórico: 100 TN para este ejemplo)
    peso_aire = 100.0 
    peso_efectivo = peso_aire * ff
    
    # Carga del Gancho (Hook Load) - Clase 3
    # Peso de la sarta = carga del gancho + peso sobre la broca (WOB)
    hkld = peso_efectivo - wob_aplicado
    
    # Punto Neutro (Estimación técnica)
    # El punto neutro debe estar en los Portamechas (DC). 
    # Si WOB > Peso DC * FF, el punto neutro sube a las barras (Riesgo).
    peso_dc_efectivo = 30.0 * ff 
    punto_neutro_ok = wob_aplicado < peso_dc_efectivo
    
    return round(hkld, 2), round(ff, 4), punto_neutro_ok

def calcular_limpieza_pozo(gpm, mw):
    """Basado en CLASE 4: Velocidad Anular para transporte de recortes"""
    # Diámetros: Hole 8.5", DP 5.0"
    v_anular = (24.51 * gpm) / (8.5**2 - 5.0**2)
    # Estado de limpieza (Criterio técnico de transporte)
    limpieza_ok = v_anular > 120
    return round(v_anular, 2), limpieza_ok

# --- 3. MÓDULOS TÉCNICOS ---

def render_mecanica():
    st.header("🏗️ MECÁNICA DE SARTA Y CONTROL DE CARGAS")
    st.info("Cálculo de boyancia (FF) y punto neutro según Clase 3 y 4.")
    
    col1, col2 = st.columns(2)
    with col1:
        wob = st.slider("WOB - Peso sobre Trépano (TN)", 0, 40, int(st.session_state.wob))
        hkld, ff, pn_ok = calcular_mecanica_sarta(st.session_state.mw, wob)
        st.session_state.wob = wob
        
        st.metric("Hook Load (Carga Gancho)", f"{hkld} TN")
        st.metric("Factor de Flotación (FF)", f"{ff}")

    with col2:
        st.subheader("Análisis de Esfuerzos")
        if pn_ok:
            st.success("✅ PUNTO NEUTRO EN PORTAMECHAS (Operación Segura)")
        else:
            st.error("🚨 CRÍTICO: PUNTO NEUTRO EN BARRAS DE SONDEO (Riesgo de Pandeo)")
        
        st.write("**Distribución de Carga:**")
        st.progress(min(wob/40, 1.0), text=f"Compresión en el fondo: {wob} TN")

def render_lodos():
    st.header("🧪 LABORATORIO DE FLUIDOS Y LIMPIEZA")
    st.info("Funciones del lodo: Transporte de recortes y control de presión (Clase 4).")
    
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.mw = st.number_input("Densidad del Lodo (ppg)", 8.3, 18.0, st.session_state.mw)
        st.session_state.gpm = st.slider("Caudal de Bomba (GPM)", 0, 800, int(st.session_state.gpm))
        
    with c2:
        va, clean_ok = calcular_limpieza_pozo(st.session_state.gpm, st.session_state.mw)
        st.metric("Velocidad Anular (VA)", f"{va} ft/min")
        if clean_ok:
            st.success("🌊 Velocidad suficiente para transporte de recortes")
        else:
            st.warning("⚠️ VA Crítica: Riesgo de asentamiento de sólidos en el fondo")

def render_casing():
    st.header("🛠️ INTEGRIDAD: CASING Y CEMENTACIÓN")
    st.info("Protocolo de bajada de TR y accesorios de flotación (Clase 5).")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("**Maniobras Previas y Seguridad:**")
        check_calibrar = st.checkbox("Calibración de pozo (Check log)")
        check_tapon = st.checkbox("Inyección de Tapón Densificado")
        
        if st.button("🚀 BAJAR CASING (TR)"):
            if check_calibrar and check_tapon:
                with st.spinner("Bajando sarta con Zapato Flotador..."):
                    time.sleep(2)
                    st.session_state.casing_status = "CASING SET"
                    st.success("TR posicionada en profundidad final.")
            else:
                st.error("Debe completar las maniobras previas (Calibrar/Tapón).")

    with col_b:
        st.subheader("Accesorios de Fondo")
        st.write("- **Zapato Flotador:** Válvula check unidireccional activa.")
        st.write("- **Rascadores:** Instalados para remover revoque del lodo.")
        if st.session_state.casing_status == "CASING SET":
            if st.button("🏗️ INICIAR BOMBEO DE CEMENTO"):
                st.toast("Desplazando lechada... Cuidado con las presiones.")

# --- 4. PANEL PRINCIPAL (HOME) ---

def render_home():
    st.title("🖥️ MENFA WELL SIM - CONSOLA DE INGENIERÍA INTEGRAL")
    st.markdown("---")
    
    # Navegación Técnica
    m1, m2, m3 = st.columns(3)
    with m1:
        if st.button("🏗️ MECÁNICA DE SARTA (Clase 3)", use_container_width=True): st.session_state.menu = "MECANICA"
    with m2:
        if st.button("🧪 FLUIDOS Y LIMPIEZA (Clase 4)", use_container_width=True): st.session_state.menu = "LODOS"
    with m3:
        if st.button("🛠️ CASING Y CEMENTO (Clase 5)", use_container_width=True): st.session_state.menu = "CASING"

    # Registro Gráfico
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=st.session_state.history["HKLD"], y=st.session_state.history["MD"], name="Log Hook Load"))
    fig.update_yaxes(autorange="reversed", title="MD (m)")
    fig.update_layout(title="Registro Histórico de Cargas", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# --- 5. LÓGICA DE NAVEGACIÓN ---
if st.session_state.menu == "HOME": render_home()
elif st.session_state.menu == "MECANICA":
    if st.button("🔙 VOLVER"): st.session_state.menu = "HOME"
    render_mecanica()
elif st.session_state.menu == "LODOS":
    if st.button("🔙 VOLVER"): st.session_state.menu = "HOME"
    render_lodos()
elif st.session_state.menu == "CASING":
    if st.button("🔙 VOLVER"): st.session_state.menu = "HOME"
    render_casing()

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="MENFA WELL SIM - TOTAL CONTROL", layout="wide")

if "initialized" not in st.session_state:
    st.session_state.update({
        "initialized": True,
        "menu": "HOME",
        "md": 2000.0,
        "tvd": 2000.0,
        "mw": 10.5,
        "gpm": 450.0,
        "wob": 0.0,
        "bit_wear": 0.0,
        # --- NUEVAS VARIABLES DE COSTOS ---
        "rig_rate_hour": 1500.0, # Costo alquiler equipo USD/Hora
        "total_cost": 500000.0,  # Costo acumulado USD
        "total_hours": 120.0,    # Horas de operación
        "bit_cost": 15000.0,     # Costo del trépano actual
        "history": pd.DataFrame([{
            "MD": 2000.0, "COSTO_M": 250.0, "HKLD": 80.0, "ROP": 0.0
        }])
    })

# --- 2. MOTOR DE COSTOS (BUSINESS INTELLIGENCE) ---

def calcular_economia(rop, depth_increment):
    """Calcula el impacto económico del tramo perforado"""
    # Tiempo invertido en perforar el tramo (horas)
    tiempo_tramo = depth_increment / rop if rop > 0 else 0
    
    # Costo del tramo = (Tiempo * Rig Rate) + Insumos estimados
    costo_tramo = (tiempo_tramo * st.session_state.rig_rate_hour) + (depth_increment * 50)
    
    st.session_state.total_cost += costo_tramo
    st.session_state.total_hours += tiempo_tramo
    
    # Costo por metro acumulado
    costo_por_metro = st.session_state.total_cost / st.session_state.md
    return round(costo_por_metro, 2), round(costo_tramo, 2)

# --- 3. MÓDULOS TÉCNICOS INTEGRADOS ---

def render_costos():
    st.title("💰 ANÁLISIS ECONÓMICO Y EFICIENCIA")
    st.info("Gestión de presupuesto operativo y optimización de ROP.")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Costo Total Proyecto", f"USD {st.session_state.total_cost:,.2f}")
    c2.metric("Horas Operativas", f"{st.session_state.total_hours:.1f} hrs")
    
    costo_m = st.session_state.total_cost / st.session_state.md
    c3.metric("Costo por Metro", f"USD {costo_m:.2f}/m")

    # Gráfico de Eficiencia: Costo vs Profundidad
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=st.session_state.history["MD"], y=st.session_state.history["COSTO_M"], 
                             fill='tozeroy', name="Curva de Aprendizaje/Costo"))
    fig.update_layout(title="Evolución del Costo por Metro", template="plotly_dark", yaxis_title="USD/m")
    st.plotly_chart(fig, use_container_width=True)

def render_mecanica_avanzada():
    st.header("🏗️ MECÁNICA Y PUNTO NEUTRO")
    # Usamos el Factor de Flotación de la Clase 4
    ff = 1 - (st.session_state.mw / 65.5)
    wob = st.slider("Aplicar WOB (TN)", 0, 40, int(st.session_state.wob))
    
    hkld = (120.0 * ff) - wob # 120 TN peso sarta aire
    st.metric("Hook Load Actual", f"{hkld:.2f} TN")
    
    if wob > (35 * ff):
        st.error("🚨 PUNTO NEUTRO FUERA DE PORTAMECHAS - PELIGRO DE ROTURA")
    else:
        st.success("✅ Punto Neutro bajo control (DC)")

# --- 4. LÓGICA DE PERFORACIÓN (OPERACIONES) ---

def ejecutar_perforacion(incremento):
    # Física de la Clase 3: ROP depende de WOB, RPM y Bit Wear
    rop_base = (st.session_state.wob * 1.2) * (1 - st.session_state.bit_wear)
    
    if rop_base > 0:
        st.session_state.md += incremento
        st.session_state.bit_wear += (incremento / 1000) # El trépano se gasta
        
        # Cálculo económico
        c_m, c_t = calcular_economia(rop_base, incremento)
        
        # Guardar historial
        new_row = {
            "MD": st.session_state.md, 
            "COSTO_M": c_m, 
            "HKLD": 80.0, # Simplificado para el log
            "ROP": rop_base
        }
        st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([new_row])], ignore_index=True)
        st.toast(f"Tramo completado. Costo del tramo: USD {c_t}")
    else:
        st.error("No hay avance. Aplique WOB y verifique circulación.")

# --- 5. INTERFAZ DE NAVEGACIÓN ---

with st.sidebar:
    st.header("🎮 PANEL DEL PERFORADOR")
    st.session_state.mw = st.number_input("Densidad Lodo (ppg)", 8.3, 18.0, 10.5)
    st.session_state.wob = st.slider("WOB (TN)", 0, 45, 15)
    
    if st.button("▶️ PERFORAR 10 METROS"):
        ejecutar_perforacion(10)

if st.session_state.menu == "HOME":
    st.title("🖥️ IPCL WELL SIM V7 - MANAGEMENT & ENGINEERING")
    m1, m2, m3, m4 = st.columns(4)
    if m1.button("🏗️ MECÁNICA", use_container_width=True): st.session_state.menu = "MECANICA"
    if m2.button("🧪 FLUIDOS", use_container_width=True): st.session_state.menu = "LODOS"
    if m3.button("🛠️ CASING", use_container_width=True): st.session_state.menu = "CASING"
    if m4.button("💰 COSTOS", use_container_width=True): st.session_state.menu = "COSTOS"
    st.image("Gemini_Generated_Image_jl30d0jl30d0jl30.png", use_container_width=True)

elif st.session_state.menu == "MECANICA":
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    render_mecanica_avanzada()
elif st.session_state.menu == "COSTOS":
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    render_costos()

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. CONFIGURACIÓN DE PARÁMETROS TÉCNICOS ---
if "initialized" not in st.session_state:
    st.session_state.update({
        "md": 2500.0,
        "tvd": 2500.0,
        "inc": 0.0,
        "kop": 2000.0,       # Kick Off Point (Clase 7)
        "bur": 3.0,          # Build Up Rate (°/30m)
        "bha_weight": 35.0,  # Peso del BHA (TN)
        "drill_pipe_weight": 18.5, # lb/ft
        "is_unconventional": True, # Modo Shale (Clase 6)
        "history": pd.DataFrame(columns=["MD", "TVD", "INC", "BUR", "TYPE"])
    })

# --- 2. MÓDULO DE TRAYECTORIA Y GEOMETRÍA (BASADO EN CLASE 7) ---

def calcular_trayectoria(md_actual, inc_actual, target_md):
    """Calcula la construcción de ángulo (Build-up section)"""
    distancia = target_md - md_actual
    # Si estamos después del KOP, aplicamos el BUR
    if md_actual >= st.session_state.kop:
        nueva_inc = inc_actual + (st.session_state.bur * (distancia / 30))
    else:
        nueva_inc = inc_actual
    
    # Cálculo simplificado de TVD (Clase 7: Funciones trigonométricas)
    nuevo_tvd = st.session_state.tvd + (distancia * np.cos(np.radians(nueva_inc)))
    return round(nueva_inc, 2), round(nuevo_tvd, 2)

def render_modulo_direccional():
    st.header("🏹 INGENIERÍA DE TRAYECTORIA")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("KOP (Kick Off Point)", f"{st.session_state.kop} m")
    with col2:
        st.metric("BUR (Build Up Rate)", f"{st.session_state.bur} °/30m")
    with col3:
        st.metric("EOB (End of Build)", "Calculando...")

    # Visualización de la curva de construcción
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, 0, 50, 150], y=[0, 2000, 2300, 2500], name="Wellpath Design"))
    fig.update_yaxes(autorange="reversed", title="TVD (m)")
    fig.update_layout(title="Perfil de Construcción de Ángulo", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# --- 3. MÓDULO DE SARTA Y BHA (BASADO EN CLASE 8) ---

def render_modulo_sarta():
    st.header("🏗️ CONFIGURACIÓN DEL BHA (BOTTOM HOLE ASSEMBLY)")
    st.info("Componentes: Trépano + Bit Sub + Drill Collars + HWDP + DP")
    
    c1, c2 = st.columns(2)
    with c1:
        st.write("**Componentes de la Sarta:**")
        st.checkbox("Drill Collars (Collares de Perforación)", value=True)
        st.checkbox("Heavy Weight Drill Pipe (HWDP)", value=True)
        st.checkbox("Motores de Fondo / RSS")
        
    with c2:
        # Cálculo de Arrastre (Drag) - Clase 8
        peso_total = st.session_state.bha_weight + (st.session_state.md * 0.02)
        st.metric("Peso Teórico (Hook Load)", f"{peso_total:.2f} TN")
        st.write("**Factores de Fricción:**")
        st.progress(0.15, text="Drag / Arrastre Estimado")

# --- 4. MÓDULO DE YACIMIENTOS NO CONVENCIONALES (BASADO EN CLASE 6) ---

def render_modulo_shale():
    st.header("🛢️ OPERACIONES EN SHALE / TIGHT (FRACKING)")
    
    if st.session_state.is_unconventional:
        st.warning("MODO: Yacimiento de Baja Permeabilidad (Lutitas/Esquistos)")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.subheader("Estimulación Hidráulica")
            st.write("- Técnica: Perf & Plug (Disparo y Tapón)")
            st.write("- Fluido: Gel Lineal (40-60 cp)")
            if st.button("Simular Etapa de Fractura"):
                st.success("Fractura exitosa. Flow back estimado: 500 m³")
        
        with col_s2:
            st.subheader("Parámetros de Formación")
            st.metric("Permeabilidad", "< 0.1 mD")
            st.metric("Producción Estimada", "190,000 bbl/d (Referencia Vaca Muerta)")

# --- 5. NAVEGACIÓN Y CONTROL ---

def main():
    st.title("🛡️ MENFA WELL ENGINEERING SYSTEM")
    
    menu = st.tabs(["Trayectoria", "Sarta/BHA", "No Convencionales", "Costos"])
    
    with menu[0]:
        render_modulo_direccional()
    with menu[1]:
        render_modulo_sarta()
    with menu[2]:
        render_modulo_shale()
    with menu[3]:
        # Integración con el módulo de costos anterior
        st.header("💰 CONTROL DE INVERSIÓN")
        st.metric("Inversión Shale (u$s)", "1,650 Millones (Plan Anual)")

if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
import time

# --- 1. INICIALIZACIÓN DE VARIABLES ECONÓMICAS ---
if "initialized_econ" not in st.session_state:
    st.session_state.update({
        "rig_rate_day": 36000.0,  # Costo diario del equipo (USD/día)
        "bit_cost": 15000.0,      # Costo del trépano (USD)
        "daily_ops_cost": 5000.0, # Lodos, personal, servicios
        "total_drilled_meters": 0.0,
        "total_cost_accumulated": 0.0,
        "active_well_type": "CONVENCIONAL",
        "spread_rate_min": 25.0   # USD por minuto operativo
    })

# --- 2. MÓDULO DE CÁLCULO DE COSTO POR METRO (CpM) ---

def calcular_cpm(rop, depth_increment):
    """
    Fórmula técnica: CpM = (Cost_Bit + Cost_Rig * (T_drilling + T_tripping)) / Meters
    Basado en lógica de eficiencia operativa.
    """
    if rop <= 0: return 0
    
    # Tiempo de perforación en horas
    t_drilling = depth_increment / rop
    # Costo operativo del tramo (Rig Rate Horario * Horas)
    rig_rate_hour = st.session_state.rig_rate_day / 24
    costo_tramo = t_drilling * rig_rate_hour
    
    st.session_state.total_cost_accumulated += costo_tramo
    st.session_state.total_drilled_meters += depth_increment
    
    # Costo por metro acumulado
    cpm_total = st.session_state.total_cost_accumulated / st.session_state.total_drilled_meters
    return round(cpm_total, 2), round(costo_tramo, 2)

# --- 3. MÓDULO DE INTERFAZ: ECONOMÍA Y PRODUCTIVIDAD ---

def render_modulo_economia():
    st.header("💰 GESTIÓN ECONÓMICA DEL PROYECTO")
    
    # Indicadores Clave (KPIs)
    kpi1, kpi2, kpi3 = st.columns(3)
    
    with kpi1:
        st.metric("Costo Acumulado", f"USD {st.session_state.total_cost_accumulated:,.2f}")
    with kpi2:
        cpm = 0
        if st.session_state.total_drilled_meters > 0:
            cpm = st.session_state.total_cost_accumulated / st.session_state.total_drilled_meters
        st.metric("Costo por Metro (CpM)", f"USD {cpm:.2f}/m")
    with kpi3:
        # Referencia Clase 6: Inversión Shale
        valor_mercado = 1650.0 if st.session_state.active_well_type == "SHALE" else 500.0
        st.metric("Presupuesto Restante (M u$s)", f"{valor_mercado - (st.session_state.total_cost_accumulated/1e6):.2f}")

    st.divider()
    
    # Selector de escenario técnico (Clase 6)
    tipo = st.radio("Configuración de Objetivo:", ["CONVENCIONAL", "SHALE (VACA MUERTA)"], horizontal=True)
    st.session_state.active_well_type = "SHALE" if "SHALE" in tipo else "CONVENCIONAL"
    
    if st.session_state.active_well_type == "SHALE":
        st.info("⚠️ Configuración No Convencional: Requiere mayor ROP y control de fractura.")
        st.write("- **Rig Rate:** USD 45,000/día (High Spec Rig)")
        st.session_state.rig_rate_day = 45000.0
    else:
        st.session_state.rig_rate_day = 36000.0

# --- 4. MÓDULO DE TIEMPOS OPERATIVOS (NPT - NON PRODUCTIVE TIME) ---

def render_modulo_tiempos():
    st.header("⏱️ TIEMPOS OPERATIVOS Y NPT")
    
    # Basado en Clase 5 y 8: Maniobras y Tripping
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.subheader("Distribución de Tiempos")
        labels = ['Perforación Efectiva', 'Conexiones', 'Tripping (Maniobras)', 'NPT (Fallas)']
        values = [65, 15, 15, 5]
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
        fig.update_layout(template="plotly_dark", height=300)
        st.plotly_chart(fig, use_container_width=True)
        
    with col_t2:
        st.subheader("Control de Maniobra (Tripping)")
        st.write("Costo de sacar herramienta (Clase 5):")
        tiempo_estimado = (st.session_state.md / 300) # 300 m/hr promedio
        costo_maniobra = (tiempo_estimado * (st.session_state.rig_rate_day / 24))
        st.warning(f"Estimado de Maniobra: {tiempo_estimado:.1f} hrs")
        st.error(f"Costo de 'Stand-by': USD {costo_maniobra:,.2f}")

# --- 5. LÓGICA DE CONTROL ---

def main_gestion():
    tab1, tab2 = st.tabs(["Dashboard Económico", "Eficiencia Operativa"])
    
    with tab1:
        render_modulo_economia()
    with tab2:
        render_modulo_tiempos()

if __name__ == "__main__":
    main_gestion()

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time

# --- 1. CONFIGURACIÓN DE PARÁMETROS AVANZADOS (Clase 6 y 7) ---
if "initialized_adv" not in st.session_state:
    st.session_state.update({
        "well_type": "CONVENCIONAL", # O "SHALE"
        "kop": 1800.0,               # Kick Off Point (m)
        "bur": 3.0,                  # Build Up Rate (°/30m)
        "target_inc": 0.0,           # Inclinación actual
        "vertical_section": 0.0,     # VS calculada
        "rig_cost_day": 35000.0,     # USD/día
        "total_investment": 0.0      # Capex acumulado
    })

# --- 2. MÓDULO DE CÁLCULOS TRIGONOMÉTRICOS (BASADO EN CLASE 7) ---

def calcular_geometria_pozo(md_nuevo):
    """
    Aplica funciones trigonométricas para determinar la nueva posición.
    TVD = MD * cos(Inc) | VS = MD * sen(Inc)
    """
    d_md = md_nuevo - st.session_state.md
    
    # Si cruzamos el KOP, empezamos a construir ángulo (BUR)
    if md_nuevo > st.session_state.kop:
        # Incremento de ángulo basado en la tasa de construcción
        st.session_state.target_inc += (st.session_state.bur * (d_md / 30))
    
    rad = np.radians(st.session_state.target_inc)
    
    # Cálculos según Planilla Técnica (Clase 1 y 7)
    delta_tvd = d_md * np.cos(rad)
    delta_vs = d_md * np.sin(rad)
    
    st.session_state.tvd += delta_tvd
    st.session_state.vertical_section += delta_vs
    st.session_state.md = md_nuevo

# --- 3. MÓDULO DE DISEÑO DE SARTA Y BHA (BASADO EN CLASE 8) ---

def render_modulo_bha():
    st.header("🏗️ CONFIGURACIÓN TÉCNICA DE LA SARTA (BHA)")
    st.info("Ensamblaje de Fondo: Trépano + Bit Sub + Drill Collars + HWDP")
    
    col_bha1, col_bha2 = st.columns(2)
    with col_bha1:
        st.write("**Componentes Seleccionados:**")
        st.checkbox("Portamechas (Drill Collars) - Rigidez", value=True)
        st.checkbox("Barras de Sondeo (Drill Pipe) - Tensión", value=True)
        st.checkbox("Motores de Fondo (Para Direccional)")
        
    with col_bha2:
        # Lógica de Arrastre/Drag (Clase 8)
        st.subheader("Análisis de Torque y Arrastre")
        friccion = 0.25 if st.session_state.target_inc > 30 else 0.15
        st.metric("Factor de Fricción Estimado", f"{friccion} μ")
        if st.session_state.target_inc > 60:
            st.warning("⚠️ ALTO ARRASTE: Riesgo de aprisionamiento diferencial")

# --- 4. MÓDULO DE ECONOMÍA Y ESCENARIO SHALE (BASADO EN CLASE 6) ---

def render_modulo_gestion():
    st.header("💰 GESTIÓN DE INVERSIONES Y COSTOS")
    
    tipo = st.selectbox("Seleccione Escenario de Yacimiento:", ["CONVENCIONAL", "NO CONVENCIONAL (SHALE)"])
    st.session_state.well_type = tipo
    
    if tipo == "NO CONVENCIONAL (SHALE)":
        st.warning("Escenario: VACA MUERTA. Requiere fracturación hidráulica (Fracking).")
        st.write("- Inversión estimada por etapa: u$s 1,650 Millones (Plan Anual)")
        st.write("- Técnica: Perf & Plug (Disparo y Tapón)")
        st.session_state.rig_cost_day = 45000.0 # Equipo de alta especificación
    else:
        st.session_state.rig_cost_day = 35000.0

    st.metric("Costo Operativo Diario", f"USD {st.session_state.rig_cost_day:,.2f}")

# --- 5. INTERFAZ PRINCIPAL ---

def main_v7():
    st.title("🛡️ IPCL WELL SIM V7.0 - INGENIERÍA Y GESTIÓN")
    
    tab_tr, tab_bha, tab_gest = st.tabs(["Trayectoria", "Sarta/BHA", "Gestión/Shale"])
    
    with tab_tr:
        st.subheader("Control de Trayectoria (Survey)")
        md_input = st.number_input("Nueva Profundidad Medida (MD)", value=st.session_state.md + 30)
        if st.button("CALCULAR AVANCE (SURVEY)"):
            calcular_geometria_pozo(md_input)
            st.success("Cálculos trigonométricos actualizados en Planilla.")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("TVD (Vertical)", f"{st.session_state.tvd:.2f} m")
        c2.metric("Incl. (°)", f"{st.session_state.target_inc:.2f}°")
        c3.metric("VS (Horizontal)", f"{st.session_state.vertical_section:.2f} m")

    with tab_bha:
        render_modulo_bha()
        
    with tab_gest:
        render_modulo_gestion()

if __name__ == "__main__":
    main_v7()

def render_examen_final():
    st.title("📝 EXAMEN DE CERTIFICACIÓN - INGENIERÍA DE PERFORACIÓN")
    st.warning("Debe responder las 20 preguntas basadas en las unidades técnicas. Se requiere 80% para aprobar.")

    preguntas = [
        # --- CLASE 1 & 2: DIRECCIONAL Y MWD ---
        {"p": "1. ¿Cuál es el método de cálculo de trayectoria con 0% de margen de error según la Clase 1?", "o": ["Método Tangencial", "Mínima Curvatura", "Radio de Curvatura"], "r": "Mínima Curvatura"},
        {"p": "2. ¿Qué significan las siglas MWD?", "o": ["Measuring While Drilling", "Mechanical Weight Device", "Movement With Direction"], "r": "Measuring While Drilling"},
        {"p": "3. En el protocolo MWD, ¿cuánto tiempo se debe esperar para resetear la herramienta apagando bombas?", "o": ["30 segundos", "90 segundos", "5 minutos"], "r": "90 segundos"},
        {"p": "4. ¿Qué componente del MWD se encarga de enviar las señales a superficie en tiempo real?", "o": ["Baterías", "Transmisor de pulsos de lodo", "Sensor de inclinación"], "r": "Transmisor de pulsos de lodo"},
        
        # --- CLASE 3: TRÉPANOS Y PESOS ---
        {"p": "5. ¿Cuál es la fórmula correcta de la carga en el gancho?", "o": ["HKLD = Peso Aire + WOB", "HKLD = Peso Efectivo - WOB", "HKLD = WOB / FF"], "r": "HKLD = Peso Efectivo - WOB"},
        {"p": "6. ¿Dónde debe ubicarse idealmente el Punto Neutro para evitar fatiga en la tubería?", "o": ["En las Barras de Sondeo (DP)", "En los Portamechas (DC)", "En el Trépano"], "r": "En los Portamechas (DC)"},
        {"p": "7. ¿Qué función cumplen las toberas (jets) en el trépano?", "o": ["Solo enfriar", "Fuerza hidráulica para romper roca y refrigerar", "Sujetar los conos"], "r": "Fuerza hidráulica para romper roca y refrigerar"},
        
        # --- CLASE 4: FLUIDOS ---
        {"p": "8. ¿Cuál es el factor de conversión para obtener la densidad en ppg a partir de SG?", "o": ["8.33", "14.22", "0.052"], "r": "8.33"},
        {"p": "9. ¿Qué propiedad del lodo permite mantener los recortes en suspensión cuando se detiene la bomba?", "o": ["Viscosidad Plástica", "Esfuerzo de Gel", "Filtrado"], "r": "Esfuerzo de Gel"},
        {"p": "10. ¿Cuál es la fórmula del Factor de Flotación (FF)?", "o": ["1 - (MW / 65.5)", "MW * 0.052 * TVD", "GPM / Velocidad Anular"], "r": "1 - (MW / 65.5)"},
        
        # --- CLASE 5: CASING Y CEMENTACIÓN ---
        {"p": "11. ¿Cuál es el objetivo del Zapato Flotador?", "o": ["Limpiar el pozo", "Válvula check para evitar retorno de cemento y dar flotación", "Medir la profundidad"], "r": "Válvula check para evitar retorno de cemento y dar flotación"},
        {"p": "12. ¿Qué maniobra se debe realizar inmediatamente antes de bajar el Casing?", "o": ["Perforar 100m más", "Calibrar pozo e inyectar tapón densificado", "Cambiar el lodo a base aceite"], "r": "Calibrar pozo e inyectar tapón densificado"},
        
        # --- CLASE 6: SHALE / NO CONVENCIONAL ---
        {"p": "13. ¿Qué permeabilidad caracteriza a un reservorio de Tight Gas?", "o": ["> 100 mD", "< 0.1 mD", "1 Darcy"], "r": "< 0.1 mD"},
        {"p": "14. ¿En qué consiste la técnica 'Perf & Plug' en pozos horizontales?", "o": ["Perforar y tapar el pozo", "Disparo y colocación de tapón para fractura por etapas", "Cementación a presión"], "r": "Disparo y colocación de tapón para fractura por etapas"},
        {"p": "15. ¿Cuál es el fluido de retorno generado tras una fractura hidráulica?", "o": ["Lodo Bentonítico", "Flow back", "Petróleo puro"], "r": "Flow back"},
        
        # --- CLASE 7: GEOMETRÍA ---
        {"p": "16. ¿Qué es el KOP (Kick Off Point)?", "o": ["El fin del pozo", "El punto donde se inicia la desviación del pozo", "La máxima inclinación"], "r": "El punto donde se inicia la desviación del pozo"},
        {"p": "17. ¿Cómo se calcula el TVD de forma simplificada en un tramo recto?", "o": ["MD * sen(Inc)", "MD * cos(Inc)", "MD / tan(Inc)"], "r": "MD * cos(Inc)"},
        
        # --- CLASE 8: SARTA Y BHA ---
        {"p": "18. ¿Cómo se divide principalmente la sarta de perforación?", "o": ["Trépano y Vástago", "BHA (Ensamblaje de fondo) y Tubería de perforación", "Motores y Bombas"], "r": "BHA (Ensamblaje de fondo) y Tubería de perforación"},
        {"p": "19. ¿Cuál es un factor que afecta el par (torque) y el arrastre (drag)?", "o": ["El color del lodo", "La geometría del pozo y la fricción", "La marca del equipo"], "r": "La geometría del pozo y la fricción"},
        {"p": "20. ¿Qué componente del BHA proporciona el peso necesario al trépano?", "o": ["Drill Pipe", "Drill Collars (Portamechas)", "Kelly"], "r": "Drill Collars (Portamechas)"}
    ]

    respuestas_usuario = []
    for i, pregunta in enumerate(preguntas):
        res = st.radio(pregunta["p"], pregunta["o"], key=f"p{i}")
        respuestas_usuario.append(res)

    if st.button("Finalizar y Calificar"):
        aciertos = sum(1 for u, p in zip(respuestas_usuario, preguntas) if u == p["r"])
        nota = (aciertos / 20) * 100
        
        if nota >= 80:
            st.success(f"✅ APROBADO. Calificación: {nota}% ({aciertos}/20 aciertos).")
            st.balloons()
        else:
            st.error(f"❌ REPROBADO. Calificación: {nota}% ({aciertos}/20 aciertos). Repase las unidades técnicas.")

import streamlit as st

def render_examen_tecnico():
    st.title("🎓 EXAMEN DE CERTIFICACIÓN DE INGENIERÍA - MENFA")
    st.markdown("---")
    
    # Estructura de las 20 preguntas basadas en las 8 clases
    banco_preguntas = [
        # --- BLOQUE: DIRECCIONAL Y MWD (Clase 1 y 2) ---
        {"id": 1, "p": "Según la Clase 1, ¿cuál es el método de cálculo con 0% de margen de error?", 
         "o": ["Tangencial", "Mínima Curvatura", "Promedio de Ángulos"], "r": "Mínima Curvatura", "f": "La Mínima Curvatura usa arcos circulares para suavizar la trayectoria."},
        
        {"id": 2, "p": "¿Cuál es la función principal del MWD?", 
         "o": ["Medir la porosidad", "Monitorear trayectoria (Azimut/Inc) en tiempo real", "Solo dar peso"], "r": "Monitorear trayectoria (Azimut/Inc) en tiempo real", "f": "MWD: Measuring While Drilling."},
        
        {"id": 3, "p": "En el protocolo de Survey, ¿cuánto tiempo se debe esperar para resetear la herramienta?", 
         "o": ["10 seg", "90 seg", "5 min"], "r": "90 seg", "f": "Según Clase 1, se apaga bomba y se esperan 90 segundos para el reset."},

        {"id": 4, "p": "¿Cómo transmite el MWD los datos a superficie?", 
         "o": ["Cable eléctrico", "Pulsos de lodo (binario 1 y 0)", "Señal de radio"], "r": "Pulsos de lodo (binario 1 y 0)", "f": "Un transductor convierte pulsos de presión en datos digitales."},

        # --- BLOQUE: MECÁNICA Y TRÉPANOS (Clase 3) ---
        {"id": 5, "p": "¿Cuál es la fórmula de la Carga del Gancho (HKLD) al tocar fondo?", 
         "o": ["HKLD = Peso Aire + WOB", "HKLD = Peso Efectivo - WOB", "HKLD = WOB / 0.052"], "r": "HKLD = Peso Efectivo - WOB", "f": "Al apoyar peso en el fondo (WOB), la carga en el gancho disminuye."},

        {"id": 6, "p": "¿Dónde debe ubicarse el Punto Neutro para proteger la sarta?", 
         "o": ["En las Barras de Sondeo (DP)", "En los Portamechas (DC)", "En el Vástago"], "r": "En los Portamechas (DC)", "f": "Los DC están diseñados para trabajar en compresión; las DP no."},

        {"id": 7, "p": "¿Qué componente del trépano usa la fuerza hidráulica para romper la roca?", 
         "o": ["Los cojinetes", "Las toberas (Jets)", "El cuerpo de acero"], "r": "Las toberas (Jets)", "f": "La energía hidráulica limpia y ayuda al corte."},

        # --- BLOQUE: FLUIDOS (Clase 4) ---
        {"id": 8, "p": "¿Qué es el Factor de Flotación (FF)?", 
         "o": ["La viscosidad del lodo", "El factor que reduce el peso de la sarta por boyancia", "La presión de formación"], "r": "El factor que reduce el peso de la sarta por boyancia", "f": "Ff = 1 - (Densidad Lodo / Densidad Acero)."},

        {"id": 9, "p": "¿Cuál es el valor de densidad del agua usado como referencia (en ppg)?", 
         "o": ["1.0", "8.33", "10.0"], "r": "8.33", "f": "8.33 ppg es la densidad estándar del agua a 60°F."},

        {"id": 10, "p": "¿Qué propiedad del lodo evita el asentamiento de recortes al apagar bombas?", 
         "o": ["Densidad", "Esfuerzo de Gel", "Filtrado"], "r": "Esfuerzo de Gel", "f": "El gel mantiene los recortes en suspensión estática."},

        # --- BLOQUE: CASING Y CEMENTO (Clase 5) ---
        {"id": 11, "p": "¿Qué función cumple el Zapato Flotador?", 
         "o": ["Perforar más rápido", "Válvula check que permite flotación y evita retorno de cemento", "Limpiar el lodo"], "r": "Válvula check que permite flotación y evita retorno de cemento", "f": "Evita que el cemento regrese al interior del casing."},

        {"id": 12, "p": "Antes de entubar, ¿qué maniobra es obligatoria?", 
         "o": ["Aumentar las RPM", "Calibrar pozo e inyectar tapón densificado", "Cambiar el trépano"], "r": "Calibrar pozo e inyectar tapón densificado", "f": "Asegura que la TR baje sin atascarse."},

        # --- BLOQUE: SHALE Y GESTIÓN (Clase 6) ---
        {"id": 13, "p": "¿Cuál es la permeabilidad típica de un reservorio de Tight Gas?", 
         "o": ["> 10 mD", "< 0.1 mD", "50 mD"], "r": "< 0.1 mD", "f": "Son reservorios de muy baja permeabilidad que requieren fractura."},

        {"id": 14, "p": "¿En qué consiste la técnica 'Perf & Plug'?", 
         "o": ["Rotar la tubería", "Disparo y tapón para fractura por etapas", "Cementación primaria"], "r": "Disparo y tapón para fractura por etapas", "f": "Es la técnica estándar en pozos horizontales de Shale."},

        {"id": 15, "p": "¿Qué es el 'Flow Back'?", 
         "o": ["Lodo nuevo", "Fluido de retorno tras una fractura hidráulica", "Petróleo puro"], "r": "Fluido de retorno tras una fractura hidráulica", "f": "Es el agua cargada de químicos que regresa tras fracturar."},

        # --- BLOQUE: TRAYECTORIA Y SARTA (Clase 7 y 8) ---
        {"id": 16, "p": "¿Qué significa KOP?", 
         "o": ["Keep On Perforating", "Kick Off Point (Inicio de desvío)", "Known Oil Point"], "r": "Kick Off Point (Inicio de desvío)", "f": "Es la profundidad donde el pozo empieza a ganar inclinación."},

        {"id": 17, "p": "Si MD es 100m e Inc es 0°, ¿cuánto es el TVD?", 
         "o": ["0m", "50m", "100m"], "r": "100m", "f": "Si no hay inclinación, la profundidad medida es igual a la vertical."},

        {"id": 18, "p": "¿Cómo se divide principalmente la sarta de perforación?", 
         "o": ["Motor y Bomba", "BHA y Tubería de perforación (DP)", "Corona y Chango"], "r": "BHA y Tubería de perforación (DP)", "f": "BHA: Bottom Hole Assembly."},

        {"id": 19, "p": "¿Cuál es la función de los Drill Collars (Portamechas)?", 
         "o": ["Dar peso al trépano", "Hacer circular el lodo", "Medir la presión"], "r": "Dar peso al trépano", "f": "Su gran espesor y peso proporcionan el WOB necesario."},

        {"id": 20, "p": "¿Qué factores afectan el Torque y el Arrastre (Drag)?", 
         "o": ["La marca del lodo", "La geometría del pozo y la fricción", "La temperatura ambiente"], "r": "La geometría del pozo y la fricción", "f": "A mayor inclinación, mayor contacto y fricción de la sarta."}
    ]

    score = 0
    for q in banco_preguntas:
        st.subheader(f"Pregunta {q['id']}")
        respuesta = st.radio(q['p'], q['o'], key=f"q_{q['id']}")
        
        if st.button(f"Validar Pregunta {q['id']}", key=f"btn_{q['id']}"):
            if respuesta == q['r']:
                st.success("¡Correcto!")
            else:
                st.error(f"Incorrecto. Nota técnica: {q['f']}")

    if st.button("CALCULAR RESULTADO FINAL"):
        # Lógica para sumar aciertos y dar diploma...
        pass

import streamlit as st

# --- 1. ESTADO DE CERTIFICACIÓN ---
if "certificado" not in st.session_state:
    st.session_state.certificado = False

# --- 2. BANCO DE DATOS TÉCNICOS (CLASES 1-8) ---
def obtener_examen():
    return [
        {"id": 1, "p": "¿Cuál es el método de cálculo con 0% de margen de error (Clase 1)?", "o": ["Tangencial", "Mínima Curvatura", "Promedio"], "r": "Mínima Curvatura", "t": "Clase 1: La Mínima Curvatura es el estándar de mayor precisión."},
        {"id": 2, "p": "¿Cuánto tiempo se espera para resetear el MWD (Clase 1)?", "o": ["10 seg", "90 seg", "5 min"], "r": "90 seg", "t": "Clase 1: Se apaga la bomba y se esperan 90 seg para el reset."},
        {"id": 3, "p": "¿Qué significan las siglas MWD?", "o": ["Measuring While Drilling", "Mechanical Weight", "Main Well Data"], "r": "Measuring While Drilling", "t": "Clase 2: Medición durante la perforación."},
        {"id": 4, "p": "¿Cómo transmite datos el MWD a superficie?", "o": ["Cable", "Pulsos de lodo", "Radio"], "r": "Pulsos de lodo", "t": "Clase 2: Usa pulsos de presión convertidos a binario (1 y 0)."},
        {"id": 5, "p": "Fórmula de Carga del Gancho al tocar fondo (Clase 3):", "o": ["Peso Aire + WOB", "Peso Efectivo - WOB", "WOB * FF"], "r": "Peso Efectivo - WOB", "t": "Clase 3: El WOB resta carga al gancho (Martin Decker)."},
        {"id": 6, "p": "¿Dónde debe estar el Punto Neutro (Clase 3)?", "o": ["En las DP", "En los Portamechas (DC)", "En el Top Drive"], "r": "En los Portamechas (DC)", "t": "Clase 3: Para evitar fallas por compresión en las barras de sondeo."},
        {"id": 7, "p": "¿Para qué sirven las toberas/jets (Clase 3)?", "o": ["Enfriar", "Fuerza hidráulica para romper roca y limpiar", "Sujetar"], "r": "Fuerza hidráulica para romper roca y limpiar", "t": "Clase 3: La energía del fluido ayuda al avance."},
        {"id": 8, "p": "Valor de densidad del agua en ppg (Clase 4):", "o": ["1.0", "8.33", "10.0"], "r": "8.33", "t": "Clase 4: El agua pura a 60°F tiene 8.33 lb/gal."},
        {"id": 9, "p": "Propiedad que evita el asentamiento de recortes (Clase 4):", "o": ["Densidad", "Esfuerzo de Gel", "Filtrado"], "r": "Esfuerzo de Gel", "t": "Clase 4: Capacidad de suspensión del lodo en parada."},
        {"id": 10, "p": "Fórmula del Factor de Flotación (Clase 4):", "o": ["1 - (MW/65.5)", "MW * 0.052", "GPM/VA"], "r": "1 - (MW/65.5)", "t": "Clase 4: Determina la boyancia de la sarta en el lodo."},
        {"id": 11, "p": "¿Qué hace el Zapato Flotador (Clase 5)?", "o": ["Perfora", "Válvula check para flotación y evitar retorno", "Rasca"], "r": "Válvula check para flotación y evitar retorno", "t": "Clase 5: Permite el bombeo pero no el ingreso al casing."},
        {"id": 12, "p": "Maniobra previa obligatoria a entubar (Clase 5):", "o": ["Rotar", "Calibrar pozo e inyectar tapón densificado", "Sacar"], "r": "Calibrar pozo e inyectar tapón densificado", "t": "Clase 5: Asegura que la TR baje sin obstrucciones."},
        {"id": 13, "p": "Permeabilidad en Tight Gas (Clase 6):", "o": ["> 10 mD", "< 0.1 mD", "50 mD"], "r": "< 0.1 mD", "t": "Clase 6: Muy baja permeabilidad que requiere estimulación."},
        {"id": 14, "p": "Técnica estándar en pozos Shale (Clase 6):", "o": ["Perf & Plug", "Open Hole", "Gravel Pack"], "r": "Perf & Plug", "t": "Clase 6: Disparo y tapón para fractura por etapas."},
        {"id": 15, "p": "¿Qué es el Flow Back (Clase 6)?", "o": ["Petróleo", "Fluido de retorno post-fractura", "Lodo"], "r": "Fluido de retorno post-fractura", "t": "Clase 6: Agua con químicos que retorna tras la fractura."},
        {"id": 16, "p": "¿Qué es el KOP (Clase 7)?", "o": ["Fin del pozo", "Kick Off Point (Inicio de desvío)", "Azimut"], "r": "Kick Off Point (Inicio de desvío)", "t": "Clase 7: Profundidad donde se inicia la construcción de ángulo."},
        {"id": 17, "p": "Si MD=500 e Inc=0°, el TVD es (Clase 7):", "o": ["0", "250", "500"], "r": "500", "t": "Clase 7: En tramos verticales MD = TVD."},
        {"id": 18, "p": "División de la sarta (Clase 8):", "o": ["Motor/Bomba", "BHA y Tubería (DP)", "Corona/Piso"], "r": "BHA y Tubería (DP)", "t": "Clase 8: El BHA es el ensamblaje de fondo."},
        {"id": 19, "p": "Función de los Drill Collars (Clase 8):", "o": ["Dar peso al trépano", "Circular", "Medir"], "r": "Dar peso al trépano", "t": "Clase 8: Su espesor y peso generan el WOB."},
        {"id": 20, "p": "¿Qué afecta el Torque y el Drag (Clase 8)?", "o": ["Color lodo", "Geometría del pozo y fricción", "Marca"], "r": "Geometría del pozo y fricción", "t": "Clase 8: A mayor ángulo, mayor contacto y fricción."}
    ]

# --- 3. LÓGICA DE PANTALLA ---
if not st.session_state.certificado:
    st.title("🔒 ACCESO RESTRINGIDO: EXAMEN DE INGENIERÍA")
    st.info("Para operar el simulador debe aprobar con 16/20 (80%).")
    
    examen = obtener_examen()
    respuestas = {}
    
    for item in examen:
        respuestas[item['id']] = st.radio(item['p'], item['o'], key=f"ex_{item['id']}")
    
    if st.button("ENVIAR EXAMEN"):
        aciertos = 0
        errores_info = []
        for item in examen:
            if respuestas[item['id']] == item['r']:
                aciertos += 1
            else:
                errores_info.append(f"Pregunta {item['id']}: {item['t']}")
        
        if aciertos >= 16:
            st.session_state.certificado = True
            st.success(f"🏆 ¡APROBADO! {aciertos}/20. Acceso concedido.")
            st.balloons()
            st.rerun()
        else:
            st.error(f"❌ REPROBADO ({aciertos}/20). Debe repasar:")
            for e in errores_info: st.write(f"- {e}")

else:
    # --- AQUÍ VA EL CÓDIGO DEL SIMULADOR QUE YA TENEMOS ---
    st.title("🖥️ SIMULADOR DE PERFORACIÓN - ACCESO AUTORIZADO")
    if st.button("Cerrar Sesión / Bloquear"):
        st.session_state.certificado = False
        st.rerun()

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTADOS ---
st.set_page_config(page_title="MENFA WELL ENGINEERING SIM v8", layout="wide")

if "certificado" not in st.session_state:
    st.session_state.update({
        "certificado": False,
        "menu": "HOME",
        "md": 2000.0,
        "tvd": 2000.0,
        "inc": 0.0,
        "vs": 0.0,
        "mw": 10.5,
        "wob": 0.0,
        "gpm": 450.0,
        "kop": 1800.0,
        "bur": 3.0,
        "well_type": "CONVENCIONAL",
        "total_cost": 500000.0,
        "history": pd.DataFrame([{"MD": 2000.0, "TVD": 2000.0, "INC": 0.0, "COST": 500000.0}])
    })

# --- 2. MOTOR DE CÁLCULO (INGENIERÍA CLASES 1-8) ---

def calcular_avance(md_nuevo):
    """Cálculos trigonométricos (Clase 7) y Económicos (Clase 6)"""
    d_md = md_nuevo - st.session_state.md
    
    # Lógica de Construcción de Ángulo
    if md_nuevo > st.session_state.kop:
        st.session_state.inc += (st.session_state.bur * (d_md / 30))
    
    rad = np.radians(st.session_state.inc)
    st.session_state.tvd += d_md * np.cos(rad)
    st.session_state.vs += d_md * np.sin(rad)
    st.session_state.md = md_nuevo
    
    # Lógica Económica
    rig_rate = 45000 if st.session_state.well_type == "SHALE" else 35000
    costo_tramo = (d_md * 150) + (rig_rate / 24) 
    st.session_state.total_cost += costo_tramo

# --- 3. MÓDULO DE EXAMEN (BLOQUEO DE ACCESO) ---

def render_examen():
    st.title("🔒 CERTIFICACIÓN TÉCNICA OBLIGATORIA")
    st.info("Debe aprobar con 16/20 (80%) para desbloquear la consola de perforación.")
    
    preguntas = [
        {"id": 1, "p": "¿Método con 0% error? (Clase 1)", "o": ["Tangencial", "Mínima Curvatura"], "r": "Mínima Curvatura", "t": "Clase 1: Mínima Curvatura es el estándar."},
        {"id": 2, "p": "¿Espera para reset MWD? (Clase 1)", "o": ["30s", "90s"], "r": "90s", "t": "Clase 1: 90 segundos apagado."},
        {"id": 3, "p": "¿Qué es MWD? (Clase 2)", "o": ["Measuring While Drilling", "Mechanical Weight"], "r": "Measuring While Drilling", "t": "Clase 2: Medición en tiempo real."},
        {"id": 4, "p": "¿Cómo transmite el MWD? (Clase 2)", "o": ["Cable", "Pulsos de lodo"], "r": "Pulsos de lodo", "t": "Clase 2: Binario por pulsos."},
        {"id": 5, "p": "Fórmula HKLD (Clase 3):", "o": ["Peso Efectivo - WOB", "Peso Aire + WOB"], "r": "Peso Efectivo - WOB", "t": "Clase 3: El WOB resta carga al gancho."},
        {"id": 6, "p": "¿Ubicación del Punto Neutro? (Clase 3)", "o": ["DP", "DC (Portamechas)"], "r": "DC (Portamechas)", "t": "Clase 3: Para evitar pandeo en DP."},
        {"id": 7, "p": "¿Función de las toberas? (Clase 3)", "o": ["Fuerza hidráulica y limpieza", "Enfriar solamente"], "r": "Fuerza hidráulica y limpieza", "t": "Clase 3: Ayuda a la rotura de roca."},
        {"id": 8, "p": "Densidad del agua (ppg) (Clase 4):", "o": ["8.33", "1.0"], "r": "8.33", "t": "Clase 4: 8.33 ppg es el estándar."},
        {"id": 9, "p": "¿Qué evita el asentamiento? (Clase 4)", "o": ["Gel", "Filtrado"], "r": "Gel", "t": "Clase 4: El gel suspende recortes en estático."},
        {"id": 10, "p": "Fórmula Factor Flotación (Clase 4):", "o": ["1 - (MW/65.5)", "MW * 0.052"], "r": "1 - (MW/65.5)", "t": "Clase 4: Determina la boyancia."},
        {"id": 11, "p": "¿Zapato Flotador? (Clase 5)", "o": ["Válvula check y flotación", "Corte de roca"], "r": "Válvula check y flotación", "t": "Clase 5: Evita retorno de cemento."},
        {"id": 12, "p": "¿Maniobra antes de TR? (Clase 5)", "o": ["Calibrar e inyectar tapón", "Aumentar GPM"], "r": "Calibrar e inyectar tapón", "t": "Clase 5: Obligatorio para bajar TR."},
        {"id": 13, "p": "Permeabilidad Tight (Clase 6):", "o": [">10 mD", "<0.1 mD"], "r": "<0.1 mD", "t": "Clase 6: Muy baja permeabilidad."},
        {"id": 14, "p": "¿Técnica Shale? (Clase 6)", "o": ["Perf & Plug", "Open Hole"], "r": "Perf & Plug", "t": "Clase 6: Disparo y tapón por etapas."},
        {"id": 15, "p": "¿Qué es el Flow Back? (Clase 6)", "o": ["Fluido retorno post-fractura", "Lodo nuevo"], "r": "Fluido retorno post-fractura", "t": "Clase 6: Retorno tras fracturar."},
        {"id": 16, "p": "¿Qué es KOP? (Clase 7)", "o": ["Inicio de desvío", "Fin de pozo"], "r": "Inicio de desvío", "t": "Clase 7: Kick Off Point."},
        {"id": 17, "p": "Si Inc=0, ¿MD es igual a TVD?", "o": ["Sí", "No"], "r": "Sí", "t": "Clase 7: En vertical son iguales."},
        {"id": 18, "p": "División de la sarta (Clase 8):", "o": ["BHA y DP", "Bomba y Motor"], "r": "BHA y DP", "t": "Clase 8: Ensamblaje de fondo y tubería."},
        {"id": 19, "p": "¿Función Drill Collars? (Clase 8)", "o": ["Dar peso al trépano", "Medir"], "r": "Dar peso al trépano", "t": "Clase 8: Generan el WOB."},
        {"id": 20, "p": "¿Qué afecta el Torque? (Clase 8)", "o": ["Geometría y fricción", "Color lodo"], "r": "Geometría y fricción", "t": "Clase 8: A mayor ángulo, mayor torque."}
    ]
    
    respuestas = {}
    for q in preguntas:
        respuestas[q['id']] = st.radio(f"{q['id']}. {q['p']}", q['o'], key=f"ex_{q['id']}")
    
    if st.button("FINALIZAR EXAMEN"):
        aciertos = sum(1 for q in preguntas if respuestas[q['id']] == q['r'])
        if aciertos >= 16:
            st.session_state.certificado = True
            st.success(f"¡APROBADO! {aciertos}/20. Acceso concedido.")
            st.rerun()
        else:
            st.error(f"REPROBADO ({aciertos}/20). Revise los fundamentos técnicos.")

# --- 4. INTERFAZ DE SIMULACIÓN (DESBLOQUEADA) ---

def render_simulador():
    st.sidebar.title("🎮 PANEL DE CONTROL")
    st.session_state.well_type = st.sidebar.selectbox("TIPO DE POZO", ["CONVENCIONAL", "SHALE"])
    st.session_state.mw = st.sidebar.number_input("DENSIDAD LODO (ppg)", 8.3, 18.0, 10.5)
    st.session_state.wob = st.sidebar.slider("WOB (TN)", 0, 40, 10)
    
    if st.sidebar.button("▶️ PERFORAR 30 METROS"):
        calcular_avance(st.session_state.md + 30)

    # Tabs de Especialidades
    t1, t2, t3, t4 = st.tabs(["🏗️ MECÁNICA/DIRECCIONAL", "🧪 FLUIDOS", "🛠️ CASING/SHALE", "💰 GESTIÓN"])
    
    with t1:
        c1, c2 = st.columns(2)
        ff = 1 - (st.session_state.mw / 65.5)
        hkld = (120 * ff) - st.session_state.wob
        c1.metric("Carga Gancho (HKLD)", f"{hkld:.1f} TN")
        c2.metric("Inclinación", f"{st.session_state.inc:.2f}°")
        st.write(f"**Punto Neutro:** {'✅ OK (DC)' if st.session_state.wob < (30*ff) else '🚨 PELIGRO (DP)'}")

    with t2:
        st.metric("Factor de Flotación", f"{ff:.4f}")
        st.info("Propiedad de Gel activa para suspensión de recortes.")

    with t3:
        if st.session_state.well_type == "SHALE":
            st.warning("Estrategia Shale: Perf & Plug habilitado.")
        st.write("- Zapato Flotador instalado.")

    with t4:
        st.metric("Costo Total Proyecto", f"USD {st.session_state.total_cost:,.2f}")
        st.metric("Profundidad Vertical (TVD)", f"{st.session_state.tvd:.2f} m")

# --- 5. LÓGICA DE ARRANQUE ---
if not st.session_state.certificado:
    render_examen()
else:
    render_simulador()

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. CONFIGURACIÓN INICIAL Y ESTADOS (MEMORIA DEL SIMULADOR) ---
st.set_page_config(page_title="MENFA WELL SIM - INGENIERÍA INTEGRAL", layout="wide")

if "certificado" not in st.session_state:
    st.session_state.update({
        "certificado": False,       # Bloqueo por examen
        "md": 2000.0,               # Profundidad Medida
        "tvd": 2000.0,              # Profundidad Vertical (Clase 7)
        "inc": 0.0,                 # Inclinación
        "vs": 0.0,                  # Sección Vertical
        "mw": 10.5,                 # Densidad Lodo (Clase 4)
        "wob": 0.0,                 # Peso sobre trépano (Clase 3)
        "kop": 1800.0,              # Kick Off Point (Clase 7)
        "bur": 3.0,                 # Build Up Rate (°/30m)
        "well_type": "CONVENCIONAL", # Clase 6
        "total_cost": 500000.0,     # Gestión Económica
        "history": pd.DataFrame([{"MD": 2000.0, "TVD": 2000.0, "INC": 0.0, "COST": 500000.0}])
    })

# --- 2. BANCO DE PREGUNTAS (CLASES 1 A 8) ---
def obtener_banco_examen():
    return [
        {"id": 1, "p": "¿Cuál es el método de cálculo con 0% de margen de error? (Clase 1)", "o": ["Tangencial", "Mínima Curvatura"], "r": "Mínima Curvatura", "t": "Clase 1: Mínima Curvatura es el estándar de precisión."},
        {"id": 2, "p": "¿Cuánto tiempo se espera para resetear el MWD apagando bombas? (Clase 1)", "o": ["30 seg", "90 seg"], "r": "90 seg", "t": "Clase 1: Se requieren 90 seg para el reset."},
        {"id": 3, "p": "¿Qué significan las siglas MWD? (Clase 2)", "o": ["Measuring While Drilling", "Mechanical Weight"], "r": "Measuring While Drilling", "t": "Clase 2: Medición durante la perforación."},
        {"id": 4, "p": "¿Cómo transmite el MWD los datos a superficie? (Clase 2)", "o": ["Cable eléctrico", "Pulsos de lodo (binario)"], "r": "Pulsos de lodo (binario)", "t": "Clase 2: Usa pulsos de presión en el lodo."},
        {"id": 5, "p": "Fórmula de Carga del Gancho (HKLD) al tocar fondo (Clase 3):", "o": ["Peso Efectivo - WOB", "Peso Aire + WOB"], "r": "Peso Efectivo - WOB", "t": "Clase 3: El WOB resta carga al gancho."},
        {"id": 6, "p": "¿Dónde debe ubicarse el Punto Neutro? (Clase 3)", "o": ["En las barras (DP)", "En los portamechas (DC)"], "r": "En los portamechas (DC)", "t": "Clase 3: Para proteger las barras de la compresión."},
        {"id": 7, "p": "¿Qué componente usa la fuerza hidráulica para romper la roca? (Clase 3)", "o": ["Toberas (Jets)", "Cojinetes"], "r": "Toberas (Jets)", "t": "Clase 3: Los jets limpian y ayudan al corte."},
        {"id": 8, "p": "Densidad del agua dulce en ppg (Clase 4):", "o": ["1.0", "8.33"], "r": "8.33", "t": "Clase 4: 8.33 ppg es la densidad estándar del agua."},
        {"id": 9, "p": "¿Qué propiedad evita el asentamiento de recortes en parada? (Clase 4)", "o": ["Esfuerzo de Gel", "Viscosidad Plástica"], "r": "Esfuerzo de Gel", "t": "Clase 4: El gel mantiene los recortes en suspensión."},
        {"id": 10, "p": "Fórmula del Factor de Flotación (FF) (Clase 4):", "o": ["1 - (MW / 65.5)", "MW * 0.052"], "r": "1 - (MW / 65.5)", "t": "Clase 4: 65.5 ppg es la densidad del acero."},
        {"id": 11, "p": "¿Cuál es la función del Zapato Flotador? (Clase 5)", "o": ["Válvula check y flotación", "Rascar el pozo"], "r": "Válvula check y flotación", "t": "Clase 5: Evita el retorno del cemento a la TR."},
        {"id": 12, "p": "Maniobra obligatoria antes de bajar el Casing (Clase 5):", "o": ["Calibrar pozo e inyectar tapón", "Aumentar RPM"], "r": "Calibrar pozo e inyectar tapón", "t": "Clase 5: Asegura que la TR baje suavemente."},
        {"id": 13, "p": "Permeabilidad típica en Tight Gas (Clase 6):", "o": ["> 10 mD", "< 0.1 mD"], "r": "< 0.1 mD", "t": "Clase 6: Muy baja permeabilidad que requiere fracking."},
        {"id": 14, "p": "Técnica estándar en pozos Shale (Vaca Muerta) (Clase 6):", "o": ["Perf & Plug", "Open Hole completion"], "r": "Perf & Plug", "t": "Clase 6: Disparo y tapón por etapas."},
        {"id": 15, "p": "¿Qué es el Flow Back? (Clase 6)", "o": ["Fluido de retorno post-fractura", "Lodo nuevo"], "r": "Fluido de retorno post-fractura", "t": "Clase 6: Agua que retorna tras fracturar."},
        {"id": 16, "p": "¿Qué significa KOP? (Clase 7)", "o": ["Kick Off Point", "Keep On Pressure"], "r": "Kick Off Point", "t": "Clase 7: Punto de inicio del desvío."},
        {"id": 17, "p": "Si la Inclinación es 0°, ¿cómo es el TVD respecto al MD? (Clase 7)", "o": ["TVD es menor", "TVD es igual al MD"], "r": "TVD es igual al MD", "t": "Clase 7: En vertical, las profundidades coinciden."},
        {"id": 18, "p": "¿Cómo se divide principalmente la sarta? (Clase 8)", "o": ["BHA y Tubería (DP)", "Bombas y Tanques"], "r": "BHA y Tubería (DP)", "t": "Clase 8: Ensamblaje de fondo y tubería de perforación."},
        {"id": 19, "p": "¿Qué componente del BHA da el peso al trépano? (Clase 8)", "o": ["Drill Collars (DC)", "Drill Pipe (DP)"], "r": "Drill Collars (DC)", "t": "Clase 8: Los portamechas proveen el WOB."},
        {"id": 20, "p": "¿Qué factores afectan el Torque y el Arrastre? (Clase 8)", "o": ["Geometría del pozo y fricción", "Color del lodo"], "r": "Geometría del pozo y fricción", "t": "Clase 8: El contacto tubería-pozo genera fricción."}
    ]

# --- 3. MOTOR TÉCNICO DE AVANCE ---
def ejecutar_perforacion(incremento):
    # Física Clase 7: Trigonometría
    d_md = incremento
    if st.session_state.md >= st.session_state.kop:
        st.session_state.inc += (st.session_state.bur * (d_md / 30))
    
    rad = np.radians(st.session_state.inc)
    st.session_state.tvd += d_md * np.cos(rad)
    st.session_state.vs += d_md * np.sin(rad)
    st.session_state.md += d_md
    
    # Economía Clase 6
    rig_rate = 45000 if st.session_state.well_type == "SHALE" else 35000
    costo_tramo = (d_md * 200) + (rig_rate / 24)
    st.session_state.total_cost += costo_tramo
    
    # Historial
    new_data = pd.DataFrame([{"MD": st.session_state.md, "TVD": st.session_state.tvd, "INC": st.session_state.inc, "COST": st.session_state.total_cost}])
    st.session_state.history = pd.concat([st.session_state.history, new_data], ignore_index=True)

# --- 4. INTERFAZ DE EXAMEN (BLOQUEO) ---
def modulo_examen():
    st.title("🛡️ MENFA ENGINEERING - ACCESO NIVEL 1")
    st.warning("BLOQUEO DE SEGURIDAD: Apruebe con 16/20 (80%) para desbloquear el simulador.")
    
    banco = obtener_banco_examen()
    respuestas_alumno = {}
    
    with st.form("form_examen"):
        for q in banco:
            respuestas_alumno[q['id']] = st.radio(f"{q['id']}. {q['p']}", q['o'], key=f"q{q['id']}")
        
        if st.form_submit_button("VALIDAR CREDENCIALES"):
            aciertos = sum(1 for q in banco if respuestas_alumno[q['id']] == q['r'])
            if aciertos >= 16:
                st.session_state.certificado = True
                st.success(f"✅ CERTIFICADO OBTENIDO: {aciertos}/20. Accediendo...")
                st.balloons()
                time.sleep(2)
                st.rerun()
            else:
                st.error(f"❌ REPROBADO ({aciertos}/20). Revise los fundamentos de las Clases 1-8.")
                for q in banco:
                    if respuestas_alumno[q['id']] != q['r']:
                        st.info(f"Refuerzo: {q['t']}")

# --- 5. INTERFAZ DEL SIMULADOR (CONSOLA DE INGENIERÍA) ---
def modulo_simulador():
    st.sidebar.title("🎮 PERFORADOR AL MANDO")
    st.sidebar.divider()
    
    st.session_state.well_type = st.sidebar.selectbox("🎯 OBJETIVO", ["CONVENCIONAL", "SHALE"])
    st.session_state.mw = st.sidebar.number_input("🧪 DENSIDAD LODO (ppg)", 8.3, 18.0, 10.5)
    st.session_state.wob = st.sidebar.slider("🏗️ WOB (TN)", 0, 40, 15)
    
    if st.sidebar.button("▶️ PERFORAR TRAMO (30m)"):
        ejecutar_perforacion(30)
        st.toast("Avanzando trayectoria...")

    # Dashboard Principal
    tab1, tab2, tab3 = st.tabs(["📊 ESTADO DEL POZO", "🏹 TRAYECTORIA", "💰 ECONOMÍA"])
    
    with tab1:
        c1, c2, c3 = st.columns(3)
        ff = 1 - (st.session_state.mw / 65.5)
        hkld = (120 * ff) - st.session_state.wob # 120 TN peso aire
        
        c1.metric("Hook Load", f"{hkld:.1f} TN")
        c2.metric("Prof. Medida (MD)", f"{st.session_state.md} m")
        c3.metric("F. Flotación (FF)", f"{ff:.4f}")
        
        if st.session_state.wob > (30 * ff):
            st.error("🚨 PUNTO NEUTRO EN BARRAS (Peligro de Pandeo)")
        else:
            st.success("✅ Punto Neutro en Portamechas (Operación Segura)")

    with tab2:
        st.subheader("Perfil Direccional")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=st.session_state.history["INC"], y=st.session_state.history["TVD"], name="Log de Inclinación"))
        fig.update_yaxes(autorange="reversed", title="TVD (m)")
        fig.update_xaxes(title="Inclinación (°)")
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.metric("Inversión Total Acumulada", f"USD {st.session_state.total_cost:,.2f}")
        if st.session_state.well_type == "SHALE":
            st.info("Estrategia Shale activada: Incluye costos de High Spec Rig y Fracking.")

    if st.button("🔴 CERRAR SESIÓN"):
        st.session_state.certificado = False
        st.rerun()

# --- 6. FLUJO PRINCIPAL ---
if not st.session_state.certificado:
    modulo_examen()
else:
    modulo_simulador()
    import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN TÉCNICA ---
st.set_page_config(page_title="MENFA WELL SIM - FULL ENGINEERING", layout="wide", initial_sidebar_state="expanded")

if "initialized" not in st.session_state:
    st.session_state.update({
        "initialized": True,
        "menu": "HOME",
        "md": 2000.0,
        "tvd": 2000.0,
        "inc": 0.0,
        "azi": 0.0,
        "norte": 0.0,
        "este": 0.0,
        "vs": 0.0,
        "mw": 10.5,           # Densidad (ppg)
        "gpm": 450.0,         # Caudal
        "wob": 0.0,           # Peso sobre trépano (TN)
        "rpm": 80,
        "bit_wear": 0.1,      # Desgaste (0 a 1)
        "casing_status": "OPEN HOLE",
        "survey_status": "IDLE",
        "is_drilling": False,
        "history": pd.DataFrame([{
            "MD": 2000.0, "TVD": 2000.0, "INC": 0.0, "AZI": 0.0, 
            "NORTE": 0.0, "ESTE": 0.0, "VS": 0.0, "HKLD": 80.0, 
            "ECD": 10.5, "ROP": 0.0, "SPP": 0.0
        }])
    })

# --- 2. MOTORES DE CÁLCULO (INGENIERÍA DE CAMPO) ---

def motor_hidraulico(mw, depth, gpm):
    """Basado en HIDRAULICA DE PERFORACION - Cálculos de SPP y ECD"""
    nozzles = [12, 12, 12]
    tfa = sum([0.7854 * (n/32)**2 for n in nozzles])
    vn = (0.3208 * gpm) / tfa if tfa > 0 else 0
    pb = (mw * vn**2) / 1085.8
    ps = (mw**0.8 * gpm**1.8 * depth) / (1000 * 8.5**4.8)
    spp = pb + ps
    ecd = mw + (ps / (0.052 * depth * 3.28))
    return round(spp, 1), round(ecd, 2), round(vn, 1)

def calcular_mecanica_sarta(mw, wob_aplicado):
    """Basado en CLASE 3 y 4: Factor de Flotación y Cargas"""
    ff = 1 - (mw / 65.5) # Factor de Flotación (Clase 4)
    peso_aire = 100.0    # Sarta teórica 100 TN
    peso_efectivo = peso_aire * ff
    hkld = peso_efectivo - wob_aplicado # Hook Load (Clase 3)
    # Punto Neutro: Debe estar en los DC (estimados en 30 TN)
    pn_ok = wob_aplicado < (30.0 * ff)
    return round(hkld, 2), round(ff, 4), pn_ok

def motor_direccional(md_n, inc_n, azi_n):
    """Basado en CLASE 1 - Mínima Curvatura"""
    prev = st.session_state.history.iloc[-1]
    d_md = md_n - prev["MD"]
    if d_md <= 0: return prev["TVD"], prev["NORTE"], prev["ESTE"]
    
    i1, i2 = np.radians(prev["INC"]), np.radians(inc_n)
    a1, a2 = np.radians(prev["AZI"]), np.radians(azi_n)
    
    cos_dl = np.cos(i2 - i1) - (np.sin(i1) * np.sin(i2) * (1 - np.cos(a2 - a1)))
    dl = np.arccos(np.clip(cos_dl, -1, 1))
    rf = (2 / dl) * np.tan(dl / 2) if dl != 0 else 1
    
    tvd = prev["TVD"] + (d_md / 2) * (np.cos(i1) + np.cos(i2)) * rf
    norte = prev["NORTE"] + (d_md / 2) * (np.sin(i1) * np.cos(a1) + np.sin(i2) * np.cos(a2)) * rf
    este = prev["ESTE"] + (d_md / 2) * (np.sin(i1) * np.sin(a1) + np.sin(i2) * np.sin(a2)) * rf
    return round(tvd, 2), round(norte, 2), round(este, 2)

# --- 3. RENDERS DE INTERFAZ ---

def render_scada():
    st.header("📊 MONITOR SCADA - TIEMPO REAL")
    curr = st.session_state.history.iloc[-1]
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("MD (m)", f"{st.session_state.md:.1f}")
    m2.metric("Hook Load (TN)", f"{curr['HKLD']}")
    m3.metric("SPP (psi)", f"{curr['SPP']}")
    m4.metric("ECD (ppg)", f"{curr['ECD']}")

    fig = make_subplots(rows=1, cols=2, subplot_titles=("Perfil Vertical", "Registro de Carga"))
    fig.add_trace(go.Scatter(x=st.session_state.history["VS"], y=st.session_state.history["TVD"], name="Trayectoria"), row=1, col=1)
    fig.add_trace(go.Scatter(x=st.session_state.history["HKLD"], y=st.session_state.history["MD"], name="Carga Gancho"), row=1, col=2)
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(template="plotly_dark", height=500)
    st.plotly_chart(fig, use_container_width=True)

def render_mecanica():
    st.header("🏗️ MECÁNICA DE SARTA Y CARGAS")
    hkld, ff, pn_ok = calcular_mecanica_sarta(st.session_state.mw, st.session_state.wob)
    
    c1, c2 = st.columns(2)
    c1.metric("Factor de Flotación", f"{ff}")
    if pn_ok: c2.success("✅ PUNTO NEUTRO EN DC (SEGURO)")
    else: c2.error("🚨 CRÍTICO: PUNTO NEUTRO EN BARRAS")
    
    st.info("Nota: El WOB aplicado resta carga al gancho (HKLD = Peso Efectivo - WOB).")

def render_mwd():
    st.header("📡 PROTOCOLO SURVEY MWD")
    st.write("Según Clase 1: Procedimiento de Reset para toma de datos.")
    if st.button("Toma de Survey (Reset 90s Simulados)"):
        with st.spinner("Apagando bombas... Reseteando herramienta..."):
            time.sleep(2)
            st.success(f"SURVEY RECIBIDO: INC {st.session_state.inc}° | AZI {st.session_state.azi}°")
            st.session_state.survey_status = "DONE"

# --- 4. PANEL DE CONTROL (SIDEBAR) ---
with st.sidebar:
    st.title("🕹️ CONSOLA")
    st.session_state.mw = st.number_input("Densidad (ppg)", 8.3, 18.0, st.session_state.mw)
    st.session_state.gpm = st.slider("Caudal (GPM)", 0, 800, int(st.session_state.gpm))
    st.session_state.wob = st.slider("WOB (TN)", 0, 40, int(st.session_state.wob))
    st.session_state.rpm = st.slider("RPM", 0, 160, st.session_state.rpm)
    
    st.divider()
    st.header("🏹 DIRECCIONAL")
    inc_target = st.slider("Ajustar Inclinación", 0.0, 90.0, st.session_state.inc)
    azi_target = st.slider("Ajustar Azimut", 0.0, 360.0, st.session_state.azi)
    
    if st.button("▶️ PERFORAR TRAMO (30m)", type="primary"):
        st.session_state.is_drilling = True
        st.session_state.inc = inc_target
        st.session_state.azi = azi_target

# --- 5. LÓGICA DE SIMULACIÓN (BACKEND) ---
if st.session_state.is_drilling:
    new_md = st.session_state.md + 30
    spp, ecd, vn = motor_hidraulico(st.session_state.mw, new_md, st.session_state.gpm)
    tvd, norte, este = motor_direccional(new_md, st.session_state.inc, st.session_state.azi)
    hkld, ff, pn_ok = calcular_mecanica_sarta(st.session_state.mw, st.session_state.wob)
    
    rop = (st.session_state.wob * 0.4) * (st.session_state.rpm / 60)
    
    st.session_state.md = new_md
    st.session_state.tvd = tvd
    
    new_data = {
        "MD": new_md, "TVD": tvd, "INC": st.session_state.inc, "AZI": st.session_state.azi,
        "NORTE": norte, "ESTE": este, "VS": np.sqrt(norte**2 + este**2),
        "HKLD": hkld, "ECD": ecd, "ROP": rop, "SPP": spp
    }
    st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([new_data])], ignore_index=True)
    st.session_state.is_drilling = False
    st.toast("Tramo perforado con éxito.")

# --- 6. MENÚ DE NAVEGACIÓN ---
if st.session_state.menu == "HOME":
    st.title("🖥️ SIMULADOR INTEGRAL MENFA V7.0")
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("📊 SCADA", use_container_width=True): st.session_state.menu = "SCADA"
    if c2.button("🏗️ MECÁNICA", use_container_width=True): st.session_state.menu = "MECANICA"
    if c3.button("📡 SURVEY MWD", use_container_width=True): st.session_state.menu = "MWD"
    if c4.button("🛡️ BOP", use_container_width=True): st.session_state.menu = "BOP"
    
    st.markdown("---")
    st.subheader("Estado de la Formación")
    st.info(f"Pozo en modo: {st.session_state.casing_status} | Profundidad Actual: {st.session_state.md} m")

elif st.session_state.menu == "SCADA":
    if st.button("🔙 VOLVER"): st.session_state.menu = "HOME"
    render_scada()
elif st.session_state.menu == "MECANICA":
    if st.button("🔙 VOLVER"): st.session_state.menu = "HOME"
    render_mecanica()
elif st.session_state.menu == "MWD":
    if st.button("🔙 VOLVER"): st.session_state.menu = "HOME"
    render_mwd()
elif st.session_state.menu == "BOP":
    if st.button("🔙 VOLVER"): st.session_state.menu = "HOME"
    st.title("🛡️ CONTROL DE POZO (BOP)")
    st.error("PANEL DE CIERRE DE EMERGENCIA")
    if st.button("🔥 CIERRE TOTAL"): st.balloons()

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# --- 1. CONFIGURACIÓN E ICONOGRAFÍA ---
st.set_page_config(page_title="MENFA WELL SIM V8 - CYBERBASE", layout="wide", initial_sidebar_state="collapsed")

# Estilo CSS para emular una pantalla de cabina (fondo oscuro, fuentes neón)
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    .stMetric { background-color: #1A1C24; border: 1px solid #4A4A4A; padding: 10px; border-radius: 5px; }
    [data-testid="stMetricValue"] { color: #00FFCC; }
    </style>
    """, unsafe_allow_html=True)

if "initialized" not in st.session_state:
    st.session_state.update({
        "menu": "CABINA", "md": 2500.0, "tvd": 2500.0, "mw": 11.2, "gpm": 550.0,
        "wob": 0.0, "rpm": 90, "torq": 12000, "spm": 110, "hkld_max": 120.0,
        "history": pd.DataFrame([{"MD": 2500.0, "TVD": 2500.0, "HKLD": 95.0, "SPP": 2800, "ROP": 0.0, "VS": 0.0}])
    })

# --- 2. MOTORES DE CÁLCULO TÉCNICO ---

def calcular_parametros():
    # Factor de Flotación (Clase 4)
    ff = 1 - (st.session_state.mw / 65.5)
    # Peso efectivo de sarta (Asumiendo 115 TN en aire)
    peso_efectivo = 115.0 * ff
    # Martin Decker: Hook Load = Peso Efectivo - WOB
    hkld = peso_efectivo - st.session_state.wob
    
    # Hidráulica (Clase 3) - Stand Pipe Pressure
    spp = (st.session_state.mw**0.8 * st.session_state.gpm**1.8 * st.session_state.md) / (1500 * 8.5**4.8) + 1200
    
    # ROP empírica (Clase 3: Proceso Rotatorio)
    rop = (st.session_state.wob * 0.5) * (st.session_state.rpm / 100)
    
    return round(hkld, 1), round(spp, 0), round(rop, 1)

# --- 3. COMPONENTES VISUALES (INSTRUMENTACIÓN) ---

def render_martin_decker(hkld):
    """Crea un indicador de aguja para el peso (Martin Decker)"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = hkld,
        title = {'text': "HOOK LOAD (TN)", 'font': {'size': 20, 'color': "white"}},
        gauge = {
            'axis': {'range': [0, 150], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "#00FFCC"},
            'bgcolor': "#1A1C24",
            'steps': [
                {'range': [0, 100], 'color': '#2E3136'},
                {'range': [100, 150], 'color': '#FF3333'}],
            'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 140}
        }
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)")
    return fig

def render_manometro_presion(spp):
    """Manómetro de presión de bomba"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = spp,
        title = {'text': "SPP (PSI)", 'font': {'size': 20, 'color': "white"}},
        gauge = {
            'axis': {'range': [0, 5000], 'tickcolor': "white"},
            'bar': {'color': "#3399FF"},
            'steps': [{'range': [0, 4000], 'color': '#2E3136'}, {'range': [4000, 5000], 'color': 'red'}]
        }
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)")
    return fig

# --- 4. VISTA PRINCIPAL: CABINA DE PERFORACIÓN ---

def render_cabina():
    hkld, spp, rop = calcular_parametros()
    
    # --- FILA 1: INDICADORES ANÁLOGOS ---
    st.markdown("### 🕹️ CONSOLA DE PERFORACIÓN - DOGHOUSE")
    col_md, col_spp, col_rop = st.columns([1.5, 1.5, 2])
    
    with col_md:
        st.plotly_chart(render_martin_decker(hkld), use_container_width=True)
    with col_spp:
        st.plotly_chart(render_manometro_presion(spp), use_container_width=True)
    with col_rop:
        # Gráfico de tendencia ROP/Profundidad
        fig_traj = go.Figure()
        fig_traj.add_trace(go.Scatter(x=st.session_state.history["ROP"], y=st.session_state.history["MD"], name="ROP", line=dict(color='#00FFCC')))
        fig_traj.update_yaxes(autorange="reversed", title="Profundidad (m)")
        fig_traj.update_layout(title="REGISTRO ROP (m/h)", height=300, template="plotly_dark", margin=dict(t=50, b=20))
        st.plotly_chart(fig_traj, use_container_width=True)

    # --- FILA 2: PARÁMETROS DIGITALES ---
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("WOB (TN)", f"{st.session_state.wob}")
    c2.metric("RPM", f"{st.session_state.rpm}")
    c3.metric("CAUDAL (GPM)", f"{st.session_state.gpm}")
    c4.metric("DENSIDAD (PPG)", f"{st.session_state.mw}")
    c5.metric("TORQUE (ft-lb)", f"{st.session_state.torq}")

    # --- FILA 3: CONTROLES DEL PERFORADOR ---
    st.markdown("---")
    ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([1,1,1,1])
    
    with ctrl1:
        new_wob = st.select_slider("AJUSTAR PESO (WOB)", options=list(range(0, 41, 2)), value=int(st.session_state.wob))
        st.session_state.wob = new_wob
    with ctrl2:
        new_rpm = st.slider("SET RPM", 0, 160, st.session_state.rpm)
        st.session_state.rpm = new_rpm
    with ctrl3:
        if st.button("🚀 PERFORAR 10m", use_container_width=True, type="primary"):
            st.session_state.md += 10
            # Guardar en historial
            h, s, r = calcular_parametros()
            new_row = {"MD": st.session_state.md, "TVD": st.session_state.md, "HKLD": h, "SPP": s, "ROP": r, "VS": 0.0}
            st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([new_row])], ignore_index=True)
            st.toast("Avanzando...")
    with ctrl4:
        if st.button("🚨 STOP / SLIPS", use_container_width=True):
            st.session_state.rpm = 0
            st.session_state.wob = 0
            st.warning("OPERACIÓN DETENIDA")

# --- 5. NAVEGACIÓN ---
if st.session_state.menu == "CABINA":
    render_cabina()

# Barra lateral para navegación entre módulos
with st.sidebar:
    st.header("MENÚ RIG")
    if st.button("📟 CABINA (Cyberbase)"): st.session_state.menu = "CABINA"
    if st.button("🏹 DIRECCIONAL"): st.info("Módulo Direccional V7 activo")
    if st.button("🧪 LABORATORIO"): st.info("Módulo Fluidos V7 activo")
    st.divider()
    st.write(f"** Rig Status:** DRILLING")
    st.write(f"** Depth:** {st.session_state.md} m")

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN DE PANTALLA TIPO CYBERBASE ---
st.set_page_config(page_title="MENFA WELL SIM V8.5", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050505; }
    .stMetric { background-color: #111; border: 2px solid #333; padding: 15px; }
    div[data-testid="stMetricValue"] { color: #00FF00; font-family: 'Courier New'; }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO DE LA CABINA ---
if "rig_state" not in st.session_state:
    st.session_state.update({
        "md": 3000.0, "mw": 10.5, "gpm": 600, "rpm": 80, "wob": 0.0,
        "on_bottom": False, "pump_running": False,
        "history": pd.DataFrame(columns=["MD", "ROP", "HKLD", "SPP"])
    })

# --- LÓGICA TÉCNICA (Basada en Clase 3 y 4) ---
def calcular_simulacion():
    # 1. Factor de Flotación (FF)
    ff = 1 - (st.session_state.mw / 65.5)
    peso_aire = 120.0  # TN (Peso teórico de la sarta)
    peso_efectivo = peso_aire * ff
    
    # 2. Martin Decker (Hook Load)
    # Si está en el fondo, HKLD = Peso Efectivo - WOB. Si está fuera, HKLD = Peso Efectivo.
    if st.session_state.on_bottom:
        hkld = peso_efectivo - st.session_state.wob
    else:
        hkld = peso_efectivo
        
    # 3. Presión de Bomba (SPP) - Hidráulica
    if st.session_state.pump_running:
        spp = (st.session_state.mw * (st.session_state.gpm**1.8) * st.session_state.md) / 1600000 + 500
    else:
        spp = 0
        
    # 4. ROP (Velocidad de penetración)
    rop = (st.session_state.wob * 0.8) * (st.session_state.rpm / 100) if st.session_state.on_bottom else 0
    
    return round(hkld, 1), round(spp, 0), round(rop, 1)

# --- INSTRUMENTACIÓN REALISTA ---
hkld_val, spp_val, rop_val = calcular_simulacion()

st.title("🎮 SIMULADOR DE CABINA DE PERFORACIÓN V8.5")

# --- FILA 1: EL MARTIN DECKER Y MANÓMETROS ---
col1, col2, col3 = st.columns([2, 2, 2])

with col1:
    # Indicador de Peso (Martin-Decker)
    fig_md = go.Figure(go.Indicator(
        mode = "gauge+number", value = hkld_val,
        title = {'text': "HOOK LOAD (TN)", 'font': {'color': 'white'}},
        gauge = {
            'axis': {'range': [0, 200], 'tickcolor': "white"},
            'bar': {'color': "#00FF00" if st.session_state.on_bottom else "#FFFF00"},
            'steps': [{'range': [150, 200], 'color': "red"}]
        }
    ))
    fig_md.update_layout(paper_bgcolor="black", font={'color': "white"}, height=350)
    st.plotly_chart(fig_md, use_container_width=True)

with col2:
    # Manómetro de Presión de Lodo
    fig_spp = go.Figure(go.Indicator(
        mode = "gauge+number", value = spp_val,
        title = {'text': "STANDPIPE PRESSURE (PSI)", 'font': {'color': 'white'}},
        gauge = {
            'axis': {'range': [0, 5000], 'tickcolor': "white"},
            'bar': {'color': "#3399FF"},
            'steps': [{'range': [4000, 5000], 'color': "red"}]
        }
    ))
    fig_spp.update_layout(paper_bgcolor="black", font={'color': "white"}, height=350)
    st.plotly_chart(fig_spp, use_container_width=True)

with col3:
    # Monitor de Torque / RPM
    st.metric("RATE OF PENETRATION", f"{rop_val} m/h")
    st.metric("BIT DEPTH (MD)", f"{st.session_state.md} m")
    st.metric("SURFACE TORQUE", f"{st.session_state.rpm * 150} ft-lbs")

# --- FILA 2: CONSOLA DE MANDOS (JOYSTICKS) ---
st.markdown("### 🎛️ PANEL DE CONTROL DEL PERFORADOR")
ctrl1, ctrl2, ctrl3, ctrl4 = st.columns(4)

with ctrl1:
    st.write("**PESO (WOB)**")
    st.session_state.wob = st.slider("Cargar Peso (TN)", 0, 50, int(st.session_state.wob))
    st.session_state.on_bottom = st.toggle("¿TOCANDO FONDO?", value=st.session_state.on_bottom)

with ctrl2:
    st.write("**ROTACIÓN (RPM)**")
    st.session_state.rpm = st.number_input("Set RPM", 0, 150, st.session_state.rpm)

with ctrl3:
    st.write("**BOMBAS DE LODO**")
    st.session_state.gpm = st.select_slider("Caudal (GPM)", options=[0, 200, 400, 600, 800], value=st.session_state.gpm)
    if st.button("ON/OFF BOMBAS"):
        st.session_state.pump_running = not st.session_state.pump_running

with ctrl4:
    st.write("**ACCIÓN**")
    if st.button("🚀 PERFORAR (AVANCE 1m)", use_container_width=True):
        if st.session_state.on_bottom and st.session_state.pump_running and st.session_state.rpm > 0:
            st.session_state.md += 1.0
            st.success("Perforando...")
        else:
            st.error("Verifique: Fondo + Bombas + Rotación")

# --- FOOTER INFORMATIVO ---
st.info(f"Estado Actual: {'PERFORANDO' if st.session_state.on_bottom else 'EN MANIOBRA'} | Densidad del Lodo: {st.session_state.mw} PPG")
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random

# --- CONFIGURACIÓN ESTILO CYBERBASE ---
st.set_page_config(page_title="MENFA RIG V9 - FULL CONSOLE", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050505; color: white; }
    .stMetric { background-color: #111; border: 1px solid #333; }
    [data-testid="stMetricValue"] { color: #00FFCC; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN DE VARIABLES ---
if "rig" not in st.session_state:
    st.session_state.update({
        "md": 3200.0, "wob": 0.0, "rpm": 0, "gpm": 0,
        "pump_on": False, "pit_level": 450, # Barriles
        "gas_unit": 15, # Unidades de gas
        "history": []
    })

# --- LÓGICA DE CÁLCULO (Clase 3 y 4) ---
def update_physics():
    # Martin Decker: Peso efectivo aprox 110 TN (Clase 3)
    hkld = 110.0 - st.session_state.wob
    
    # Hidráulica (Clase 4): Presión depende de GPM y Profundidad
    if st.session_state.pump_on:
        spp = (st.session_state.gpm**1.8 * st.session_state.md) / 1800000 + 400
    else:
        spp = 0
        
    # Simulación de Gas y Nivel de Tanques (Detección de Kicks)
    gas = st.session_state.gas_unit + random.uniform(-1, 1)
    pit = st.session_state.pit_level
    
    return round(hkld, 1), round(spp, 0), round(gas, 1), round(pit, 1)

hkld, spp, gas, pit = update_physics()

# --- INTERFAZ DE CABINA ---
st.title("📟 CONSOLA INTEGRADA DE PERFORACIÓN - V9.0")

# FILA 1: INSTRUMENTACIÓN PRINCIPAL (Martin Decker y SPP)
col1, col2, col3 = st.columns([2, 2, 2])

with col1:
    fig_md = go.Figure(go.Indicator(
        mode="gauge+number", value=hkld,
        title={'text': "HOOK LOAD (TN)", 'font': {'color': 'white'}},
        gauge={'axis': {'range': [0, 150]}, 'bar': {'color': "#00FFCC"}}
    ))
    fig_md.update_layout(paper_bgcolor="black", height=300, margin=dict(t=30, b=0))
    st.plotly_chart(fig_md, use_container_width=True)

with col2:
    fig_spp = go.Figure(go.Indicator(
        mode="gauge+number", value=spp,
        title={'text': "PUMP PRESS (PSI)", 'font': {'color': 'white'}},
        gauge={'axis': {'range': [0, 5000]}, 'bar': {'color': "#3399FF"}}
    ))
    fig_spp.update_layout(paper_bgcolor="black", height=300, margin=dict(t=30, b=0))
    st.plotly_chart(fig_spp, use_container_width=True)

with col3:
    st.markdown("### 🧬 MONITOREO DE GAS")
    st.metric("GAS TOTAL (units)", f"{gas}")
    # Mini gráfico de tendencia de gas
    st.line_chart([gas + random.uniform(-2, 5) for _ in range(10)], height=150)

# FILA 2: PARÁMETROS DE OPERACIÓN
st.divider()
c1, c2, c3, c4 = st.columns(4)
c1.metric("WOB", f"{st.session_state.wob} TN")
c2.metric("ROTARY", f"{st.session_state.rpm} RPM")
c3.metric("FLOW", f"{st.session_state.gpm} GPM")
c4.metric("PIT VOLUME", f"{pit} BBLS")

# FILA 3: CONTROLES (Mesa de Trabajo)
st.markdown("### 🕹️ MANDOS DEL PERFORADOR")
ctrl1, ctrl2, ctrl3 = st.columns(3)

with ctrl1:
    st.write("**TOP DRIVE / BRAKE**")
    st.session_state.wob = st.slider("Cargar Peso (WOB)", 0, 45, int(st.session_state.wob))
    st.session_state.rpm = st.slider("Ajustar RPM", 0, 160, st.session_state.rpm)

with ctrl2:
    st.write("**MUD PUMPS (BOMBAS)**")
    st.session_state.gpm = st.select_slider("Pump Output (GPM)", options=[0, 300, 550, 750, 900], value=st.session_state.gpm)
    if st.button("START/STOP BOMBAS", use_container_width=True):
        st.session_state.pump_on = not st.session_state.pump_on

with ctrl3:
    st.write("**PERFORACIÓN**")
    if st.button("🔨 AVANZAR PERFORACIÓN (10m)", type="primary", use_container_width=True):
        if st.session_state.pump_on and st.session_state.rpm > 40:
            st.session_state.md += 10
            # Simular aumento de gas al perforar nueva formación
            st.session_state.gas_unit = random.randint(10, 30)
            st.success(f"Profundidad alcanzada: {st.session_state.md} m")
        else:
            st.warning("ERROR: Se requiere circulación y rotación para avanzar.")

# --- ALERTAS DE SEGURIDAD ---
if gas > 50:
    st.error("⚠️ ALTA CONCENTRACIÓN DE GAS DETECTADA")
if spp > 4500:
    st.error("🚨 SOBREPRESIÓN EN STANDPIPE")
     import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="MENFA WELL SIM V9.5 - EMERGENCY OPS", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050505; color: #E0E0E0; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    .stMetric { background-color: #111; border: 1px solid #333; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO DEL SISTEMA ---
if "emergency" not in st.session_state:
    st.session_state.update({
        "bop_closed": False, "pit_volume": 500.0, "gain_loss": 0.0,
        "shut_in_cas_press": 0, "shut_in_dp_press": 0, "alarm": False
    })

# --- LÓGICA DE CONTROL DE POZO (Clase 4) ---
def simular_evento():
    # Si estamos perforando y no hay suficiente densidad, el volumen en tanques sube (Kick)
    if st.session_state.get('on_bottom', False) and not st.session_state.bop_closed:
        inc = np.random.choice([0, 0, 0.5, 2.0]) # Probabilidad de surgencia
        st.session_state.pit_volume += inc
        st.session_state.gain_loss = inc
        if inc > 0: st.session_state.alarm = True
    
    # Si cerramos el BOP, las presiones se estabilizan
    if st.session_state.bop_closed:
        st.session_state.shut_in_dp_press = 450
        st.session_state.shut_in_cas_press = 650
        st.session_state.alarm = False
    else:
        st.session_state.shut_in_dp_press = 0
        st.session_state.shut_in_cas_press = 0

simular_evento()

# --- INTERFAZ: CABINA DE CONTROL DE EMERGENCIA ---
st.title("🚨 PANEL DE CONTROL DE POZO Y BOP")

col_gauge, col_bop = st.columns([3, 1])

with col_gauge:
    # Manómetros de Cierre (SIDPP y SICP)
    c1, c2 = st.columns(2)
    with c1:
        fig1 = go.Figure(go.Indicator(
            mode="gauge+number", value=st.session_state.shut_in_dp_press,
            title={'text': "SIDP PRESS (PSI)"},
            gauge={'axis': {'range': [0, 2000]}, 'bar': {'color': "yellow"}}
        ))
        fig1.update_layout(paper_bgcolor="black", height=250, margin=dict(t=50, b=0))
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        fig2 = go.Figure(go.Indicator(
            mode="gauge+number", value=st.session_state.shut_in_cas_press,
            title={'text': "CASING PRESS (PSI)"},
            gauge={'axis': {'range': [0, 2000]}, 'bar': {'color': "orange"}}
        ))
        fig2.update_layout(paper_bgcolor="black", height=250, margin=dict(t=50, b=0))
        st.plotly_chart(fig2, use_container_width=True)

with col_bop:
    st.markdown("### 🕹️ BOP STACK")
    if st.button("🔴 CLOSE ANNULAR", type="secondary" if not st.session_state.bop_closed else "primary"):
        st.session_state.bop_closed = True
    st.divider()
    if st.button("🟢 OPEN BOP"):
        st.session_state.bop_closed = False
    
    status_color = "🔴 CERRADO" if st.session_state.bop_closed else "🟢 ABIERTO"
    st.write(f"ESTADO: **{status_color}**")

# --- MONITOREO DE TANQUES (PIT ROOM) ---
st.markdown("---")
st.subheader("📊 MONITOREO DE TANQUES (MUD PITS)")
m1, m2, m3 = st.columns(3)

with m1:
    st.metric("VOLUMEN TOTAL", f"{st.session_state.pit_volume} BBL", 
              delta=f"{st.session_state.gain_loss} BBL/min", delta_color="inverse")
with m2:
    flow_out = 100 if not st.session_state.bop_closed else 0
    st.metric("FLOW OUT %", f"{flow_out} %")
with m3:
    if st.session_state.alarm:
        st.error("⚠️ ¡GANANCIA EN TANQUES DETECTADA!")
    else:
        st.success("✅ NIVELES ESTABLES")

# Instrucciones para el alumno
with st.expander("ℹ️ Instrucciones de Seguridad (Clase 4)"):
    st.write("""
    1. Si el **Volumen Total** aumenta sin razón, es un 'Kick'.
    2. ¡Detenga la rotación y las bombas inmediatamente!
    3. Presione **CLOSE ANNULAR** para cerrar el pozo.
    4. Lea las presiones **SIDPP** y **SICP** para calcular el peso de lodo de ahogo.
    """)
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="MENFA WELL SIM V9.5 - EMERGENCY OPS", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050505; color: #E0E0E0; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    .stMetric { background-color: #111; border: 1px solid #333; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO DEL SISTEMA ---
if "emergency" not in st.session_state:
    st.session_state.update({
        "bop_closed": False, "pit_volume": 500.0, "gain_loss": 0.0,
        "shut_in_cas_press": 0, "shut_in_dp_press": 0, "alarm": False
    })

# --- LÓGICA DE CONTROL DE POZO (Clase 4) ---
def simular_evento():
    # Si el pozo está abierto y estamos simulando avance, hay chance de surgencia
    if not st.session_state.bop_closed:
        # Probabilidad de que entre un "influjo" (Kick)
        inc = np.random.choice([0, 0, 0, 0.5, 2.0]) 
        st.session_state.pit_volume += inc
        st.session_state.gain_loss = inc
        if inc > 0: st.session_state.alarm = True
    
    # Si cerramos el BOP, las presiones se estabilizan (SIDPP y SICP)
    if st.session_state.bop_closed:
        st.session_state.shut_in_dp_press = 450
        st.session_state.shut_in_cas_press = 650
        st.session_state.alarm = False
        st.session_state.gain_loss = 0
    else:
        st.session_state.shut_in_dp_press = 0
        st.session_state.shut_in_cas_press = 0

simular_evento()

# --- INTERFAZ: CABINA DE CONTROL DE EMERGENCIA ---
st.title("🚨 PANEL DE CONTROL DE POZO Y BOP")

col_gauge, col_bop = st.columns([3, 1])

with col_gauge:
    # Manómetros de Cierre (SIDPP y SICP)
    c1, c2 = st.columns(2)
    with c1:
        fig1 = go.Figure(go.Indicator(
            mode="gauge+number", value=st.session_state.shut_in_dp_press,
            title={'text': "SIDP PRESS (PSI)"},
            gauge={'axis': {'range': [0, 2000]}, 'bar': {'color': "yellow"}}
        ))
        fig1.update_layout(paper_bgcolor="black", height=250, margin=dict(t=50, b=0))
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        fig2 = go.Figure(go.Indicator(
            mode="gauge+number", value=st.session_state.shut_in_cas_press,
            title={'text': "CASING PRESS (PSI)"},
            gauge={'axis': {'range': [0, 2000]}, 'bar': {'color': "orange"}}
        ))
        fig2.update_layout(paper_bgcolor="black", height=250, margin=dict(t=50, b=0))
        st.plotly_chart(fig2, use_container_width=True)

with col_bop:
    st.markdown("### 🕹️ CONTROL DE BOP")
    if st.button("🔴 CLOSE ANNULAR", type="secondary" if not st.session_state.bop_closed else "primary"):
        st.session_state.bop_closed = True
    st.divider()
    if st.button("🟢 OPEN BOP"):
        st.session_state.bop_closed = False
    
    status_text = "CERRADO" if st.session_state.bop_closed else "ABIERTO"
    st.write(f"ESTADO: **{status_text}**")

# --- MONITOREO DE TANQUES (PIT ROOM) ---
st.markdown("---")
st.subheader("📊 MONITOREO DE TANQUES (MUD PITS)")
m1, m2, m3 = st.columns(3)

with m1:
    st.metric("VOLUMEN TOTAL", f"{st.session_state.pit_volume} BBL", 
              delta=f"{st.session_state.gain_loss} BBL/min", delta_color="inverse")
with m2:
    # Si el BOP está cerrado, el flujo de retorno debe ser 0
    flow_out = 100 if not st.session_state.bop_closed else 0
    st.metric("FLOW OUT %", f"{flow_out} %")
with m3:
    if st.session_state.alarm:
        st.error("⚠️ ¡GANANCIA EN TANQUES DETECTADA!")
    else:
        st.success("✅ NIVELES ESTABLES")
        import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PANTALLA ---
st.set_page_config(page_title="MENFA WELL SIM V10 - IADC REPORTING", layout="wide")

# --- ESTADO DEL REPORTE ---
if "log_data" not in st.session_state:
    st.session_state.update({
        "log_data": [],
        "current_depth": 3500.0,
        "supervisor": "Fabricio"
    })

# --- FUNCIÓN PARA REGISTRAR ACTIVIDAD (Clase 8: Sarta y Tiempos) ---
def registrar_evento(actividad):
    nuevo_registro = {
        "Hora": datetime.now().strftime("%H:%M:%S"),
        "Profundidad (m)": st.session_state.current_depth,
        "Actividad": actividad,
        "WOB (TN)": st.session_state.get('wob', 0),
        "SPP (PSI)": st.session_state.get('spp', 0)
    }
    st.session_state.log_data.append(nuevo_registro)

# --- INTERFAZ DE OPERACIONES Y REPORTE ---
st.title("📋 SISTEMA DE REPORTABILIDAD IADC - V10.0")

tab1, tab2 = st.tabs(["🕹️ CONSOLA OPERATIVA", "📄 REPORTE DIARIO (DDR)"])

with tab1:
    st.subheader("Control de Operaciones en Tiempo Real")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.session_state.wob = st.number_input("Peso sobre Trépano (WOB)", 0, 50, 15)
        if st.button("📝 REGISTRAR PESO"):
            registrar_evento(f"Perforando con {st.session_state.wob} TN")
            st.toast("Grabado en el log")

    with c2:
        if st.button("🚀 AVANZAR 10m"):
            st.session_state.current_depth += 10
            registrar_evento("Perforación de sección")
            st.success("Progreso registrado")

    with c3:
        operacion = st.selectbox("Cambio de Estado", ["Circulando", "En Maniobra", "Perfilaje", "Cementación"])
        if st.button("✅ REGISTRAR ESTADO"):
            registrar_evento(operacion)

with tab2:
    st.subheader("Daily Drilling Report (DDR)")
    
    if st.session_state.log_data:
        df_reporte = pd.DataFrame(st.session_state.log_data)
        
        # Mostrar tabla profesional
        st.table(df_reporte)
        
        # Botón para descargar reporte (CSV para Excel)
        csv = df_reporte.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 DESCARGAR REPORTE IADC (.CSV)",
            data=csv,
            file_name=f"Reporte_Pozo_{datetime.now().strftime('%Y%m%d')}.csv",
            mime='text/csv',
        )
    else:
        st.info("No hay datos registrados para el reporte de hoy.")

# --- RESUMEN TÉCNICO ---
st.sidebar.header("DATOS DEL POZO")
st.sidebar.write(f"**Supervisor:** {st.session_state.supervisor}")
st.sidebar.write(f"**Profundidad Actual:** {st.session_state.current_depth} m")
st.sidebar.divider()
st.sidebar.caption("Basado en normas IADC y procedimientos de las clases 3, 4 y 5.")
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# --- CONFIGURACIÓN DE INTERFAZ PROFESIONAL ---
st.set_page_config(page_title="MENFA WELL SIM V11", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050505; color: #E0E0E0; }
    .stMetric { background-color: #111; border: 1px solid #00FFCC; padding: 15px; border-radius: 10px; }
    .stButton>button { width: 100%; font-weight: bold; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO GLOBAL DEL SIMULADOR ---
if "v11_state" not in st.session_state:
    st.session_state.update({
        "md": 2800.0, "wob": 15, "log_events": [],
        "casing_diam": 9.625, "hole_diam": 12.25
    })

# --- FUNCIONES DE CÁLCULO (Clase 5 y 7) ---
def calcular_cemento(profundidad, diam_hoyo, diam_cas):
    # Cálculo de volumen en el espacio anular (Barriles)
    # Fórmula simplificada: (Dh^2 - Dp^2) / 314 * Longitud
    vol_anular_bbl = ((diam_hoyo**2 - diam_cas**2) / 314.5) * (profundidad * 3.28) # profundidad a pies
    # Rendimiento promedio: 1.18 cuft/sk (aprox 4.5 sacos por bbl)
    sacos_necesarios = vol_anular_bbl * 4.5 * 1.15 # 15% de exceso de seguridad
    return round(vol_anular_bbl, 1), int(sacos_necesarios)

def registrar_log(msg):
    st.session_state.log_events.append({
        "Hora": datetime.now().strftime("%H:%M"),
        "Prof": f"{st.session_state.md} m",
        "Evento": msg
    })

# --- DISEÑO DE LA CABINA V11 ---
st.title("🏗️ PLATAFORMA INTEGRADA DE PERFORACIÓN Y CEMENTACIÓN")

tab_ops, tab_cem, tab_iadc = st.tabs(["🕹️ OPERACIONES", "🧪 CEMENTACIÓN", "📊 REPORTE IADC"])

# --- TAB 1: OPERACIONES ---
with tab_ops:
    st.subheader("Control de Fondo y Superficie")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("PROFUNDIDAD (MD)", f"{st.session_state.md} m")
        if st.button("🚀 PERFORAR 15m"):
            st.session_state.md += 15
            registrar_log(f"Perforación rotaria con {st.session_state.wob} TN")
            st.toast("Avanzando...")
            
    with col2:
        st.session_state.wob = st.slider("PESO (WOB) - TN", 0, 40, st.session_state.wob)
        if st.button("📝 REGISTRAR PARÁMETROS"):
            registrar_log(f"Ajuste de parámetros: WOB {st.session_state.wob} TN")

    with col3:
        if st.button("⚠️ SIMULAR SURGENCIA (KICK)", type="secondary"):
            registrar_log("ALERTA: Ganancia en tanques detectada.")
            st.error("¡SURGENCIA DETECTADA! Proceder a cierre de pozo.")

# --- TAB 2: CEMENTACIÓN (CLASE 5) ---
with tab_cem:
    st.subheader("Calculador de Lechada para Cañería de Revestimiento")
    ce1, ce2 = st.columns(2)
    
    with ce1:
        st.info("Parámetros del Pozo para Entubado")
        h_diam = st.number_input("Diámetro del Hoyo (pulg)", value=12.25)
        c_diam = st.number_input("Diámetro del Casing (pulg)", value=9.625)
        exceso = st.slider("Exceso de Seguridad (%)", 0, 50, 15)
        
    with ce2:
        vol, sacos = calcular_cemento(st.session_state.md, h_diam, c_diam)
        st.metric("VOLUMEN ANULAR EST.", f"{vol} BBL")
        st.metric("SACOS DE CEMENTO (Est.)", f"{sacos} SK")
        
        if st.button("📋 CARGAR A REPORTE DE CEMENTACIÓN"):
            registrar_log(f"Cálculo Cementación: {sacos} sacos para etapa de {c_diam}\"")

# --- TAB 3: REPORTE IADC ---
with tab_iadc:
    st.subheader("Daily Drilling Report (DDR) / Parte Diario")
    if st.session_state.log_events:
        df = pd.DataFrame(st.session_state.log_events)
        st.table(df)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 DESCARGAR REPORTE IADC", csv, "IADC_Report.csv", "text/csv")
    else:
        st.write("No hay actividad registrada en este turno.")

import streamlit as st
import random

# --- CONFIGURACIÓN DE PANTALLA ---
st.set_page_config(page_title="MENFA WELL SIM V12 - EXAM MODE", layout="wide")

# --- BANCO DE PREGUNTAS (Basado en tus clases) ---
def generar_trivia():
    preguntas = [
        {
            "id": 1,
            "q": "¿Qué sucede con el Martin-Decker (Hook Load) cuando apoyas peso (WOB) en el fondo?",
            "options": ["Aumenta la carga", "Disminuye la carga", "Se mantiene igual"],
            "correct": "Disminuye la carga",
            "ref": "Clase 3: El peso se transfiere de la sarta al trépano."
        },
        {
            "id": 2,
            "q": "Si el volumen en los tanques (Pit Level) aumenta sin bombear, ¿qué indica?",
            "options": ["Pérdida de circulación", "Un Kick o Surgencia", "Falla en las zarandas"],
            "correct": "Un Kick o Surgencia",
            "ref": "Clase 4: Entrada de fluidos de formación al pozo."
        },
        {
            "id": 3,
            "q": "Para calcular el volumen de cemento, ¿qué diámetro es el más crítico?",
            "options": ["Diámetro Interno (ID) del Casing", "Espacio Anular (Hoyo vs OD Casing)", "Diámetro del Drill Pipe"],
            "correct": "Espacio Anular (Hoyo vs OD Casing)",
            "ref": "Clase 5: El cemento debe llenar el espacio tras el Casing."
        }
    ]
    return preguntas

# --- INTERFAZ DEL EXAMEN ---
st.title("🎓 EVALUACIÓN DE COMPETENCIAS TÉCNICAS")

if "score" not in st.session_state:
    st.session_state.score = 0
    st.session_state.answered = []

tab_sim, tab_exam = st.tabs(["🕹️ SIMULADOR ACTIVO", "📝 EXAMEN FINAL"])

with tab_sim:
    st.info("Continúa operando para recolectar datos...")
    st.metric("Profundidad Actual", f"{st.session_state.get('md', 3500)} m")
    st.warning("Recuerda: El reporte IADC es la base de tu evaluación.")

with tab_exam:
    st.subheader("Cuestionario de Certificación MENFA")
    
    preguntas = generar_trivia()
    
    for p in preguntas:
        st.write(f"**{p['id']}. {p['q']}**")
        ans = st.radio(f"Seleccione una opción para la preg. {p['id']}:", p['options'], key=f"q_{p['id']}")
        
        if st.button(f"Validar Respuesta {p['id']}"):
            if ans == p['correct']:
                st.success(f"¡Correcto! {p['ref']}")
                if p['id'] not in st.session_state.answered:
                    st.session_state.score += 1
                    st.session_state.answered.append(p['id'])
            else:
                st.error("Incorrecto. Revisa el material de la clase.")

    st.divider()
    st.metric("Puntaje Total", f"{st.session_state.score} / {len(preguntas)}")
    
    if st.session_state.score == len(preguntas):
        st.balloons()
        st.success("🎉 ¡Certificación MENFA Aprobada! Estás listo para el Rig Floor.")


import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime
import os

# --- 1. CONFIGURACIÓN E IDENTIDAD ---
st.set_page_config(page_title="IPCL MENFA V13 - SISTEMA INTEGRAL", layout="wide")

# Estilo para emular una cabina de perforación
st.markdown("""
    <style>
    .main { background-color: #050505; color: #E0E0E0; }
    .stMetric { background-color: #111; border: 1px solid #00FFCC; padding: 10px; border-radius: 10px; }
    [data-testid="stMetricValue"] { color: #00FFCC; font-family: 'Courier New'; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. INICIALIZACIÓN DE ESTADOS ---
if "auth" not in st.session_state:
    st.session_state.update({
        "auth": False, "usuario": "", "legajo": "", "kick_alert": False,
        "vida_sarta": 100.0, "pesca_activa": False, "densidad_lodo": 1.15,
        "presion_anular": 0, "score": 0, "finalizado": False,
        "history": pd.DataFrame([{
            "DEPTH": 2500.0, "WOB": 20.0, "RPM": 100, "ROP": 0.0, "GR": 110, "TANQUES": 1200, "DENS": 1.15
        }])
    })

# --- 3. FUNCIÓN DE CERTIFICADO PDF ---
def generar_pdf(nombre, dni, profundidad):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(2)
    pdf.rect(10, 10, 277, 190)
    
    pdf.set_font('Arial', 'B', 30)
    pdf.cell(0, 40, 'CERTIFICADO DE COMPETENCIA', ln=True, align='C')
    pdf.set_font('Arial', '', 18)
    pdf.cell(0, 10, 'El proyecto educativo MENFA (Mendoza) certifica a:', ln=True, align='C')
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 25)
    pdf.cell(0, 20, nombre.upper(), ln=True, align='C')
    pdf.set_font('Arial', '', 14)
    pdf.cell(0, 10, f'DNI/Legajo: {dni}', ln=True, align='C')
    pdf.ln(10)
    pdf.set_font('Arial', '', 16)
    cuerpo = f"Ha operado con éxito el simulador MENFA V13, alcanzando una profundidad de {profundidad}m y demostrando habilidades en Control de Pozos, Geología y Operaciones de Perforación."
    pdf.multi_cell(0, 10, cuerpo, align='C')
    pdf.ln(20)
    pdf.set_font('Arial', 'I', 12)
    pdf.cell(0, 10, f"Emitido el {datetime.now().strftime('%d/%m/%Y')} - Mendoza, Argentina", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1')

# --- 4. ACCESO (LOGIN) ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #00FFCC;'>🛡️ IPCL MENFA - CONTROL DE ACCESO</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        u_reg = st.text_input("Nombre y Apellido:")
        l_reg = st.text_input("DNI / Legajo:")
        if st.button("INGRESAR A CABINA", use_container_width=True):
            if u_reg and l_reg:
                st.session_state.usuario, st.session_state.legajo, st.session_state.auth = u_reg, l_reg, True
                st.rerun()
    st.stop()

# --- 5. LÓGICA DE SIMULACIÓN (SIDEBAR) ---
curr = st.session_state.history.iloc[-1]
with st.sidebar:
    st.header(f"Op: {st.session_state.usuario}")
    st.divider()
    wob = st.slider("WOB (klbs)", 0, 60, int(curr['WOB']))
    rpm = st.slider("RPM", 0, 180, int(curr['RPM']))
    
    if st.button("⏩ AVANZAR PERFORACIÓN", use_container_width=True):
        if not st.session_state.pesca_activa and not st.session_state.kick_alert:
            st.session_state.vida_sarta -= (wob * 0.15)
            if st.session_state.vida_sarta <= 0: st.session_state.pesca_activa = True
            
            n_prof = curr['DEPTH'] + random.randint(5, 15)
            # Lógica de Gamma Ray: Reservorio en 2850-2950m
            gr = random.randint(20, 40) if 2850 < n_prof < 2950 else random.randint(80, 130)
            
            # Lógica de Kick (Surgencia)
            tanques = curr['TANQUES']
            if random.random() < 0.10: # 10% de probabilidad
                st.session_state.kick_alert = True
                tanques += 40
                st.session_state.presion_anular = random.randint(350, 750)

            nueva_fila = {
                "DEPTH": n_prof, "WOB": wob, "RPM": rpm,
                "ROP": (wob * rpm) / 400, "GR": gr, 
                "TANQUES": tanques, "DENS": st.session_state.densidad_lodo
            }
            st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([nueva_fila])], ignore_index=True)
            st.rerun()

# --- 6. PANELES OPERATIVOS (TABS) ---
if st.session_state.kick_alert:
    st.error("🚨 KICK DETECTADO: ¡GANANCIA EN TANQUES! CIERRE EL BOP DE INMEDIATO.")

tabs = st.tabs(["📊 SCADA", "🛡️ WELL CONTROL", "🔩 SARTA & PESCA", "📈 GEOLOGÍA", "📖 MANUAL & EXAMEN"])

with tabs[0]: # SCADA MODERNO
    c1, c2, c3 = st.columns(3)
    c1.metric("BIT DEPTH", f"{curr['DEPTH']} m")
    c2.metric("WEIGHT ON BIT", f"{curr['WOB']} klbs")
    c3.metric("ROP", f"{round(curr['ROP'], 1)} m/h")
    
    # Gráfico de Martin-Decker
    fig_md = go.Figure(go.Indicator(
        mode="gauge+number", value=120 - curr['WOB'],
        title={'text': "HOOK LOAD (TN)"},
        gauge={'axis': {'range': [0, 150]}, 'bar': {'color': "#00FFCC"}}
    ))
    fig_md.update_layout(paper_bgcolor="black", height=250, margin=dict(t=30, b=0))
    st.plotly_chart(fig_md, use_container_width=True)

with tabs[1]: # WELL CONTROL
    st.subheader("Sistema de Prevención de Reventones")
    if st.session_state.kick_alert:
        st.metric("SICP (Presión Anular)", f"{st.session_state.presion_anular} psi")
        if st.button("🔒 CERRAR BOP ANULAR", type="primary"):
            st.session_state.kick_alert = False
            st.success("Pozo Controlado. Aumente la densidad del lodo.")
    else:
        st.success("Presiones equilibradas.")

with tabs[2]: # SARTA Y PESCA
    st.subheader("Vida útil de la herramienta")
    vida = max(0, st.session_state.vida_sarta)
    st.progress(vida / 100)
    if st.session_state.pesca_activa:
        st.warning("⚠️ SARTA CORTADA POR EXCESO DE PESO.")
        if st.button("🎣 OPERACIÓN DE PESCA"):
            st.session_state.vida_sarta, st.session_state.pesca_activa = 100.0, False
            st.rerun()

with tabs[3]: # GEOLOGÍA
    fig_gr = go.Figure()
    fig_gr.add_trace(go.Scatter(x=st.session_state.history['GR'], y=st.session_state.history['DEPTH'], name="Gamma Ray"))
    fig_gr.update_layout(yaxis=dict(autorange="reversed", title="Profundidad (m)"), xaxis=dict(title="GR (API)"))
    # Resaltar zona de interés
    fig_gr.add_hrect(y0=2850, y1=2950, fillcolor="green", opacity=0.2, annotation_text="POTENCIAL RESERVORIO")
    st.plotly_chart(fig_gr, use_container_width=True)

with tabs[4]: # EXAMEN Y CERTIFICADO
    st.header("Evaluación Técnica IPCL")
    q1 = st.radio("1. Si apoyas más peso (WOB), ¿qué ocurre con el Martin Decker (Hook Load)?", ["Sube", "Baja", "No cambia"])
    q2 = st.radio("2. ¿Cuál es el protocolo inmediato ante un Kick?", ["Aumentar RPM", "Cerrar BOP", "Perforar más rápido"])
    
    if st.button("🏁 FINALIZAR Y CALIFICAR"):
        aciertos = 0
        if q1 == "Baja": aciertos += 1
        if q2 == "Cerrar BOP": aciertos += 1
        
        if aciertos == 2:
            st.balloons()
            st.success("¡EXAMEN APROBADO 100%!")
            pdf_out = generar_pdf(st.session_state.usuario, st.session_state.legajo, curr['DEPTH'])
            st.download_button("🎓 DESCARGAR CERTIFICADO OFICIAL (PDF)", pdf_out, f"Certificado_{st.session_state.usuario}.pdf", "application/pdf")
        else:
            st.error(f"Aciertos: {aciertos}/2. Revisa el manual y reintenta.")

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="MENFA WELL ENGINEERING SIM v8", layout="wide")

# Inicialización de estados (Session State)
if "certificado" not in st.session_state:
    st.session_state.update({
        "certificado": False,
        "md": 2000.0,
        "tvd": 2000.0,
        "inc": 0.0,
        "vs": 0.0,
        "mw": 10.5,
        "wob": 0.0,
        "kop": 1800.0,
        "bur": 3.0,
        "well_type": "CONVENCIONAL",
        "total_cost": 500000.0
    })

# --- 2. MOTOR DE CÁLCULO TÉCNICO ---
def calcular_avance(md_nuevo):
    d_md = md_nuevo - st.session_state.md
    
    # Lógica de Construcción de Ángulo (Clase 7)
    if md_nuevo > st.session_state.kop:
        st.session_state.inc += (st.session_state.bur * (d_md / 30))
    
    rad = np.radians(st.session_state.inc)
    st.session_state.tvd += d_md * np.cos(rad)
    st.session_state.vs += d_md * np.sin(rad)
    st.session_state.md = md_nuevo
    
    # Lógica Económica (Clase 6)
    rig_rate = 45000 if st.session_state.well_type == "SHALE" else 35000
    costo_tramo = (d_md * 150) + (rig_rate / 24) 
    st.session_state.total_cost += costo_tramo

# --- 3. MÓDULO DE EXAMEN ---
def render_examen():
    st.title("🔒 CERTIFICACIÓN TÉCNICA OBLIGATORIA")
    st.warning("Debe aprobar con 16/20 (80%) para desbloquear la consola de perforación.")
    
    # Banco de preguntas resumido para esta versión
    preguntas = [
        {"id": 1, "p": "¿Método con 0% error? (Clase 1)", "o": ["Tangencial", "Mínima Curvatura"], "r": "Mínima Curvatura"},
        {"id": 2, "p": "¿Espera para reset MWD? (Clase 1)", "o": ["30s", "90s"], "r": "90s"},
        {"id": 3, "p": "¿Qué es MWD? (Clase 2)", "o": ["Measuring While Drilling", "Mechanical Weight"], "r": "Measuring While Drilling"},
        {"id": 4, "p": "¿Cómo transmite el MWD? (Clase 2)", "o": ["Cable", "Pulsos de lodo"], "r": "Pulsos de lodo"},
        {"id": 5, "p": "Fórmula HKLD (Clase 3):", "o": ["Peso Efectivo - WOB", "Peso Aire + WOB"], "r": "Peso Efectivo - WOB"},
        {"id": 6, "p": "¿Ubicación del Punto Neutro? (Clase 3)", "o": ["DP", "DC (Portamechas)"], "r": "DC (Portamechas)"},
        {"id": 7, "p": "¿Función de las toberas? (Clase 3)", "o": ["Fuerza hidráulica y limpieza", "Enfriar solamente"], "r": "Fuerza hidráulica y limpieza"},
        {"id": 8, "p": "Densidad del agua (ppg) (Clase 4):", "o": ["8.33", "1.0"], "r": "8.33"},
        {"id": 9, "p": "¿Qué evita el asentamiento? (Clase 4)", "o": ["Gel", "Filtrado"], "r": "Gel"},
        {"id": 10, "p": "Fórmula Factor Flotación (Clase 4):", "o": ["1 - (MW/65.5)", "MW * 0.052"], "r": "1 - (MW/65.5)"},
        {"id": 11, "p": "¿Zapato Flotador? (Clase 5)", "o": ["Válvula check y flotación", "Corte de roca"], "r": "Válvula check y flotación"},
        {"id": 12, "p": "¿Maniobra antes de TR? (Clase 5)", "o": ["Calibrar e inyectar tapón", "Aumentar GPM"], "r": "Calibrar e inyectar tapón"},
        {"id": 13, "p": "Permeabilidad Tight (Clase 6):", "o": [">10 mD", "<0.1 mD"], "r": "<0.1 mD"},
        {"id": 14, "p": "¿Técnica Shale? (Clase 6)", "o": ["Perf & Plug", "Open Hole"], "r": "Perf & Plug"},
        {"id": 15, "p": "¿Qué es el Flow Back? (Clase 6)", "o": ["Fluido retorno post-fractura", "Lodo nuevo"], "r": "Fluido retorno post-fractura"},
        {"id": 16, "p": "¿Qué es KOP? (Clase 7)", "o": ["Inicio de desvío", "Fin de pozo"], "r": "Inicio de desvío"},
        {"id": 17, "p": "Si Inc=0, ¿MD es igual a TVD?", "o": ["Sí", "No"], "r": "Sí"},
        {"id": 18, "p": "División de la sarta (Clase 8):", "o": ["BHA y DP", "Bomba y Motor"], "r": "BHA y DP"},
        {"id": 19, "p": "¿Función Drill Collars? (Clase 8)", "o": ["Dar peso al trépano", "Medir"], "r": "Dar peso al trépano"},
        {"id": 20, "p": "¿Qué afecta el Torque? (Clase 8)", "o": ["Geometría y fricción", "Color lodo"], "r": "Geometría y fricción"}
    ]
    
    score = 0
    for q in preguntas:
        res = st.radio(q['p'], q['o'], key=f"ex_{q['id']}")
        if res == q['r']: score += 1
    
    if st.button("FINALIZAR EXAMEN"):
        if score >= 16:
            st.session_state.certificado = True
            st.success(f"🏆 ¡APROBADO! {score}/20. Acceso concedido.")
            st.rerun()
        else:
            st.error(f"❌ REPROBADO ({score}/20). Revise los fundamentos técnicos.")

# --- 4. INTERFAZ DEL SIMULADOR ---
def render_simulador():
    st.sidebar.title("🎮 PANEL DE CONTROL")
    st.session_state.well_type = st.sidebar.selectbox("TIPO DE POZO", ["CONVENCIONAL", "SHALE"])
    st.session_state.mw = st.sidebar.number_input("DENSIDAD LODO (ppg)", 8.3, 18.0, 10.5)
    st.session_state.wob = st.sidebar.slider("WOB (TN)", 0, 40, 10)
    
    if st.sidebar.button("▶️ PERFORAR 30 METROS"):
        calcular_avance(st.session_state.md + 30)
        st.toast("Avanzando trayectoria...")

    # KPIs Principales
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("MD (Profundidad)", f"{st.session_state.md:.1f} m")
    c2.metric("TVD (Vertical)", f"{st.session_state.tvd:.1f} m")
    c3.metric("Inclinación", f"{st.session_state.inc:.2f} °")
    c4.metric("Costo Total", f"USD {st.session_state.total_cost:,.0f}")

    t1, t2, t3 = st.tabs(["🏗️ INGENIERÍA", "💰 ECONOMÍA", "📊 TRAYECTORIA"])
    
    with t1:
        st.subheader("Configuración de Sarta (BHA)")
        st.write(f"**Punto Neutro estimado:** En sección de Drill Collars.")
        st.info(f"Factor de Flotación (FF): {1 - (st.session_state.mw / 65.5):.3f}")
        
    with t2:
        st.subheader("Análisis de Costos")
        st.write(f"Tarifa del Equipo: {'USD 45,000/día' if st.session_state.well_type == 'SHALE' else 'USD 35,000/día'}")
        if st.session_state.well_type == "SHALE":
            st.warning("Escenario Shale detectado: Se requiere logística de Fractura Hidráulica.")

    with t3:
        # Gráfico simple de trayectoria
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[0, st.session_state.vs], y=[0, -st.session_state.tvd], mode='lines+markers', name='Pozo'))
        fig.update_layout(title="Perfil del Pozo (Vista Lateral)", xaxis_title="Sección Vertical (m)", yaxis_title="TVD (m)")
        st.plotly_chart(fig)

# --- EJECUCIÓN PRINCIPAL ---
if not st.session_state.certificado:
    render_examen()
else:
    render_simulador()
    if st.button("Cerrar Sesión"):
        st.session_state.certificado = False
        st.rerun()
