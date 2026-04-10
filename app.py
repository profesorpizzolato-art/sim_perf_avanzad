import streamlit as st
import pandas as pd
import numpy as np
import time
import base64
import os
from datetime import datetime
from fpdf import FPDF
from streamlit_autorefresh import st_autorefresh
import io
# --- IMPORTACIÓN DE TUS MÓDULOS TÉCNICOS (FILES) ---
import motor_calculos_avanzados as motor
import geonavegacion_pro as geo
import torque_and_drag as td
import bombas_de_lodo as bombas
import sartas_perforacion as sartas
import sys
import os
import plotly.graph_objects as go
import streamlit.components.v1 as components
# --- 1. INICIALIZACIÓN BLINDADA (Colocar justo después de los imports) ---
import time
import random

# Lista de variables necesarias para que la app no explote
variables_necesarias = {
    "pizarra": {
        "wob_maestro": 0.0, "rpm_maestro": 0.0, "caudal_maestro": 500.0,
        "densidad_maestra": 10.2, "presion_base": 1200.0,
        "profundidad_actual": 2500.0, "evento_activo": None,
        "piletas_nivel": 500.0, "bop_cerrado": False
    },
    "ultima_falla": time.time(),
    "inicio_falla": None,
    "tiempo_respuesta": 0,
    "mensaje_alerta": "Operación Normal"
}

# Creamos las variables si no existen
for clave, valor_defecto in variables_necesarias.items():
    if clave not in st.session_state:
        st.session_state[clave] = valor_defecto

# Acceso directo para facilitar el código
piz = st.session_state.pizarra
# Esto le dice a Python que busque módulos en la carpeta donde está app.py
sys.path.append(os.path.dirname(__file__))

import streamlit as st
import bombas_de_lodo as bombas  # Ahora debería encontrarlo
# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="MENFA 3.0 - Mendoza Oil Industry", layout="wide", page_icon="🏗️")

# --- 2. PIZARRA GLOBAL (SINCRONIZACIÓN MAESTRO-ALUMNO) ---
@st.cache_resource
def obtener_pizarra_maestra():
    return {
        "alarma_activa": False,
        "mensaje_evento": "Operación Normal",
        "presion_base": 2500.0,
        "caudal_maestro": 550.0,
        "densidad_maestra": 10.2,
        "profundidad_actual": 2800.0,
        "bop_cerrado": False,
        "torque_maestro": 12.0,
        "wob_maestro": 15.0,
        "rpm_maestro": 60.0
    }

import streamlit.components.v1 as components

def disparar_alarma_sonora():
    # Ajustá 'assets/alarma.mp3' según el nombre exacto de tu carpeta
    ruta_audio = "assets/alarma.mp3" 
    
    if os.path.exists(ruta_audio):
        with open(ruta_audio, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            # Creamos el HTML para reproducir el archivo local
            html_audio = f"""
                <audio autoplay loop>
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
            """
            components.html(html_audio, height=0, width=0)
    else:
        st.error(f"⚠️ No se encontró el archivo en {ruta_audio}")
# --- 3. LÓGICA DE AUDIO (ALARMAS) ---
def reproducir_alarma_critica():
    if os.path.exists("assets/alarma.mp3"):
        with open("assets/alarma.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            html = f'<audio autoplay loop><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.components.v1.html(html, height=0)

# --- 4. CONTROL DE ACCESO (FABRICIO VS ALUMNOS) ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.image("logo.menfa.png", use_container_width=True)
        st.markdown("<h2 style='text-align: center;'>SISTEMA DE ENTRENAMIENTO v3.0</h2>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🎓 Acceso Alumnos", "👨‍🏫 Instructor"])
        with tab1:
            with st.form("alumno_login"):
                u = st.text_input("Nombre y Apellido")
                c = st.text_input("Clave de Curso", type="password")
                if st.form_submit_button("Ingresar"):
                    if c == "alumno2026":
                        st.session_state.autenticado, st.session_state.usuario, st.session_state.rol = True, u, "alumno"
                        st.rerun()
        with tab2:
            with st.form("profe_login"):
                cp = st.text_input("Clave Maestro", type="password")
                if st.form_submit_button("Acceso Administrativo"):
                    if cp == "menfa2026":
                        st.session_state.autenticado, st.session_state.usuario, st.session_state.rol = True, "Inst. Fabricio Pizzolato", "instructor"
                        st.rerun()
    st.stop()
# 1. PRIMERO reparamos la variable (AFUERA del sidebar)
if 'pizarra' in st.session_state:
    pizarra = st.session_state.pizarra 
else:
    st.session_state.pizarra = {
        "profundidad_actual": 2500.0,
        "presion_base": 1200.0,
        "alarma_activa": False,
        "evento_activo": None
    }
    pizarra = st.session_state.pizarra

# 2. AHORA entramos al sidebar con todo alineado
with st.sidebar:
    st.title("👨‍🏫 Panel del Instructor")
    
    # Esta línea ahora tiene 4 espacios de sangría
    st.write(f"Profundidad: {pizarra['profundidad_actual']:.2f} m")
    
    # El botón también tiene 4 espacios de sangría
    if st.button("🔄 Resetear Eventos"):
        st.session_state.evento_activo = None
        pizarra["alarma_activa"] = False
        st.rerun()
# --- 5. INTERFAZ PRINCIPAL ---

# SIDEBAR COMÚN
st.sidebar.image("logo.menfa.png", use_container_width=True)
st.sidebar.title(f"Usuario: {st.session_state.usuario}")

# --- PANEL DEL INSTRUCTOR (Aproximadamente línea 100) ---
# --- PANEL DEL INSTRUCTOR (Línea 100 en adelante) ---
with st.sidebar:
    st.title("👨‍🏫 Panel del Instructor")
    
    # 1. CAUDAL: Forzamos a que todo sea número entero
    try:
        val_c = int(float(pizarra.get("caudal_maestro", 500)))
    except:
        val_c = 500
    
    # Aseguramos rango 0-1200 y que sea INT
    val_c = max(0, min(1200, val_c))
    nuevo_caudal = st.slider("Caudal (GPM)", 0, 1200, val_c, step=1)
    pizarra["caudal_maestro"] = float(nuevo_caudal)

    # 2. WOB: Rango 0-100
    try:
        val_w = int(float(pizarra.get("wob_maestro", 0)))
    except:
        val_w = 0
        
    val_w = max(0, min(100, val_w))
    nuevo_wob = st.slider("WOB (klbs)", 0, 100, val_w, step=1)
    pizarra["wob_maestro"] = float(nuevo_wob)

    # 3. RPM: Rango 0-200
    try:
        val_r = int(float(pizarra.get("rpm_maestro", 0)))
    except:
        val_r = 0
        
    val_r = max(0, min(200, val_r))
    nuevo_rpm = st.slider("RPM", 0, 200, val_r, step=1)
    pizarra["rpm_maestro"] = float(nuevo_rpm)
    
st.sidebar.divider()
st.sidebar.subheader("🔊 Sistema de Audio")
st.session_state.alarma_activa = st.sidebar.toggle("Activar Sirena de Emergencia", value=True)

if st.sidebar.button("🔊 Probar Sonido"):
    disparar_alarma_sonora()
st.sidebar.subheader("🕹️ Simulación de Fallas")

if st.sidebar.button("🚨 Provocar Kick"):
    st.session_state.evento_activo = "KICK"
    
if st.sidebar.button("📉 Provocar Pérdida"):
    st.session_state.evento_activo = "PERDIDA"

st.sidebar.divider()

if st.sidebar.button("✅ Normalizar Pozo"):
    st.session_state.evento_activo = None
    st.rerun()
# Luego actualizamos la pizarra con esos nuevos valores
pizarra["caudal_maestro"] = nuevo_caudal
pizarra["wob_maestro"] = nuevo_wob
pizarra["rpm_maestro"] = nuevo_rpm
st.sidebar.divider()

if st.session_state.get("evento_activo") == "KICK":
    # Acción obligatoria: La presión sube si el pozo no está cerrado
    if not piz.get("bop_cerrado", False):
        piz["presion_base"] = piz.get("presion_base", 1200.0) + 2.5 
        piz["alarma_activa"] = True # Esto activa el sonido y el fondo rojo
        st.error("🚨 ¡ALERTA DE KICK! PRESIÓN EN AUMENTO")
    else:
        piz["alarma_activa"] = False # Apaga el sonido si cerraron el BOP
        st.success("✅ POZO CERRADO BAJO PRESIÓN")

elif st.session_state.get("evento_activo") == "PERDIDA":
    # Acción obligatoria: Bajamos el caudal de retorno simulado
    st.warning("📉 PÉRDIDA DE CIRCULACIÓN DETECTADA")
    pizarra["caudal_maestro"] *= 0.9

elif st.session_state.get("evento_activo") == "FALLA_BOMBA":
    # Acción obligatoria: Reducimos la potencia de bombeo
    st.error("💥 FALLA EN VÁLVULA DE BOMBA 1")
    pizarra["caudal_maestro"] = 250.0

# --- MODO ALUMNO (VISUALIZACIÓN Y ACCIÓN) ---
st.title("📟 Panel Integral de Operaciones")

# Lógica de Alarma Sonora y Visual
if pizarra["alarma_activa"]:
    st.error(f"🔥 {pizarra['mensaje_evento']}")
    reproducir_alarma_critica()
    
    # PANEL BOP PARA EL ALUMNO
    st.markdown("### 🛡️ PANEL DE EMERGENCIA (BOP)")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("🔴 CERRAR BOP ANULAR", type="primary", use_container_width=True):
            pizarra["bop_cerrado"] = True
            pizarra["alarma_activa"] = False
            st.success("POZO CERRADO. Presión controlada.")
    with col_b2:
        st.button("🔴 CERRAR RAMS CIEGOS", type="secondary", use_container_width=True)

# --- INTEGRACIÓN DE MÓDULOS TÉCNICOS (ALUMNO Y PROFE VEN ESTO) ---
col1, col2, col3 = st.columns(3)

# Datos calculados por tus otros archivos .py
# 1. Llamamos a la función real del motor con sus 5 parámetros requeridos
res_fisica = motor.calcular_fisica_perforacion(
    wob=pizarra["wob_maestro"],
    rpm=pizarra["rpm_maestro"],
    torque=pizarra["torque_maestro"],
    profundidad=pizarra["profundidad_actual"],
    flow_rate=pizarra["caudal_maestro"]
)

# 2. Extraemos los valores del diccionario para los manómetros
rop_actual = res_fisica["ROP"]
mse_actual = res_fisica["MSE"]
hk_actual = res_fisica["HOOK_LOAD"]
av_actual = res_fisica["AV"]
kmw_actual = res_fisica["KMW"]

# 3. (Opcional) Si necesitas HHP e Impact Force para otros gráficos:
hhp = (pizarra["presion_base"] * pizarra["caudal_maestro"]) / 1714
if_force = 0.0182 * pizarra["caudal_maestro"] * (pizarra["presion_base"] * pizarra["densidad_maestra"])**0.5

# --- GRÁFICOS DINÁMICOS DE TUS ARCHIVOS ---
st.divider()
c_gra1, c_gra2 = st.columns(2)

with c_gra1:
    st.subheader("📍 Geonavegación Pro")
    # Llamamos a tu archivo geonavegacion_pro.py
    fig_geo = geo.generar_grafico_trayectoria(pizarra["profundidad_actual"])
    st.plotly_chart(fig_geo, use_container_width=True)

with c_gra2:
    st.subheader("⚙️ Torque & Drag")
    # Llamamos a tu archivo torque_and_drag.py
    fig_td = td.calcular_curvas_esfuerzo(pizarra["wob_maestro"], pizarra["rpm_maestro"])
    st.plotly_chart(fig_td, use_container_width=True)

st.sidebar.divider()

# 1. Aseguramos que el estado del reporte exista
if "bytes_reporte_final" not in st.session_state:
    st.session_state.bytes_reporte_final = None

# 2. Botón para GENERAR el reporte
import io  # Asegurate de tener este import arriba de todo

st.sidebar.divider()

# --- DENTRO DEL BOTÓN DE INFORME ---
pdf_rep = FPDF()
pdf_rep.add_page()
pdf_rep.set_font("Arial", 'B', 16)

# USAR TEXTO PLANO (Sin tildes ni emojis como 📊 o 🚨)
pdf_rep.cell(200, 10, "MENFA IPCL - REPORTE DE ENTRENAMIENTO", 0, 1, 'C')
pdf_rep.ln(10)
pdf_rep.set_font("Arial", '', 12)
pdf_rep.cell(200, 10, f"Alumno: {st.session_state.get('usuario', 'Anonimo')}", 0, 1)
pdf_rep.cell(200, 10, "Instructor: Fabricio Pizzolato", 0, 1)

# Conversión final segura
pdf_str_rep = pdf_rep.output(dest='S')
if isinstance(pdf_str_rep, str):
    st.session_state.bytes_reporte_final = pdf_str_rep.encode('latin-1', 'ignore')
else:
    st.session_state.bytes_reporte_final = pdf_str_rep
    
# motor_calculos_avanzados.py
import numpy as np

def calcular_metricas(presion, caudal, densidad):
    # HHP: Potencia Hidráulica
    hhp = (presion * caudal) / 1714
    
    # IF: Fuerza de Impacto
    if_force = 0.0182 * caudal * np.sqrt(densidad * presion)
    
    return round(hhp, 2), round(if_force, 2)

def calcular_ecd(densidad_lodo, caudal, profundidad):
    # Simulación de pérdida por fricción anular
    perdida_friccion = (caudal * 0.1) / 100 
    ecd = densidad_lodo + perdida_friccion
    return round(ecd, 2)

# geonavegacion_pro.py
import plotly.graph_objects as go
import numpy as np

def generar_grafico_trayectoria(profundidad_actual):
    # Creamos una trayectoria ficticia basada en la profundidad real
    z = np.linspace(0, profundidad_actual, 100)
    x = np.sin(z/500) * 50 # Desvío lateral
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=z, name="Trayectoria Real", line=dict(color='lime', width=4)))
    
    fig.update_layout(
        title="Perfil de Pozo (Vaca Muerta)",
        yaxis=dict(autorange="reversed", title="Profundidad (m)"),
        xaxis=dict(title="Desplazamiento Lateral (m)"),
        template="plotly_dark"
    )
    return fig

# --- DENTRO DE LA VISTA DEL ALUMNO ---
st.header("📊 Monitor de Perforación en Tiempo Real")

# --- EN EL LÓGICA DEL ALUMNO ---
# --- Lógica de renderizado en app.py ---

# 1. Llamamos al motor de física (asegúrate de tener 'import motor_calculos_avanzados as motor')
res = motor.calcular_fisica_perforacion(
    wob=pizarra["wob_maestro"],
    rpm=pizarra["rpm_maestro"],
    torque=pizarra["torque_maestro"],
    profundidad=pizarra["profundidad_actual"],
    flow_rate=pizarra["caudal_maestro"]
)
# --- 1. CÁLCULOS (Esto ya lo tenés) ---
res = motor.calcular_fisica_perforacion(
    wob=pizarra["wob_maestro"],
    rpm=pizarra["rpm_maestro"],
    torque=pizarra["torque_maestro"],
    profundidad=pizarra["profundidad_actual"],
    flow_rate=pizarra["caudal_maestro"]
)

# --- 2. DEFINICIÓN DE PESTAÑAS (Aquí va el código nuevo) ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🎮 Consola Principal", 
    "🛡️ BOP & Control", 
    "🧪 Lodos y Tanques", 
    "🛰️ Geonavegación"
])
import plotly.graph_objects as go

def crear_manometro(valor, titulo, unidad, max_val, color_linea):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = valor,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"<b>{titulo}</b><br><span style='font-size:0.8em;color:gray'>{unidad}</span>", 'font': {'size': 18}},
        gauge = {
            'axis': {'range': [None, max_val], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': color_linea},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "#555",
            'steps': [
                {'range': [0, max_val*0.8], 'color': 'rgba(0, 255, 0, 0.1)'},
                {'range': [max_val*0.8, max_val], 'color': 'rgba(255, 0, 0, 0.3)'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_val * 0.9
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=50, b=20),
        height=250,
        font={'color': "white", 'family': "Arial"}
    )
    return fig
# --- 3. CONTENIDO DE CADA PESTAÑA ---

with tab1:
    st.subheader("Tablero de Perforación en Tiempo Real")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.plotly_chart(crear_manometro(res["ROP"], "Velocidad ROP", "m/hr", 60, "lime"), use_container_width=True)
    with col2:
        st.plotly_chart(crear_manometro(res["MSE"], "Eficiencia MSE", "kpsi", 100, "orange"), use_container_width=True)
    with col3:
        st.plotly_chart(crear_manometro(res["HOOK_LOAD"], "Peso en Gancho", "klbs", 600, "white"), use_container_width=True)

with tab2:
    import bop_panel as bop # Importamos tu módulo de BOP
with tab2:
    import bop_panel as bop 
    st.header("🛡️ Sistema de Seguridad de Pozo")
    
    # Cambiamos 'mostrar_interfaz_bop' por 'render_bop_ui'
    bop.render_bop_ui(pizarra)   
with tab3:
    import gestion_perdidas as gp
    st.header("🧪 Control de Piletas y Lodos")
    # Aquí graficaremos los niveles de los tanques
    gp.render_tanques(pizarra)

with tab4:
    import geonavegacion_pro as geo
    st.header("🛰️ Trayectoria en Vaca Muerta")
    fig_geo = geo.generar_grafico_trayectoria(pizarra["profundidad_actual"])
    st.plotly_chart(fig_geo, use_container_width=True, key="grafico_geo_tab4")
    import plotly.graph_objects as go

def crear_reloj(valor, titulo, unidad, max_val, color_linea):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = valor,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"<b>{titulo}</b><br><span style='font-size:0.8em;color:gray'>{unidad}</span>"},
        gauge = {
            'axis': {'range': [None, max_val], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': color_linea},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "#444",
            'steps': [
                {'range': [0, max_val*0.8], 'color': 'rgba(0, 255, 0, 0.1)'},
                {'range': [max_val*0.8, max_val], 'color': 'rgba(255, 0, 0, 0.2)'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': valor
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=30, r=30, t=50, b=30),
        height=280,
        font={'color': "white", 'family': "Arial"}
    )
    return fig
# 2. Dibujamos los manómetros usando tu nueva función
col1, col2, col3 = st.columns(3)

with col1:
    st.plotly_chart(crear_manometro(res["ROP"], "ROP", "m/hr", 60, "lime"), use_container_width=True)

with col2:
    st.plotly_chart(crear_manometro(res["MSE"], "MSE", "kpsi", 100, "orange"), use_container_width=True)

with col3:
    st.plotly_chart(crear_manometro(res["HOOK_LOAD"], "Hook Load", "klbs", 600, "white"), use_container_width=True)
# --- CÁLCULOS DE POTENCIA HIDRÁULICA (Antes de los relojes) ---
# La fórmula es: (Presión * Caudal) / 1714
presion = pizarra.get("presion_base", 0)
caudal = pizarra.get("caudal_maestro", 0)

hhp_actual = (presion * caudal) / 1714

# Ahora sí, el reloj de la línea 433 va a funcionar:
st.plotly_chart(crear_reloj(hhp_actual, "Potencia", "HHP", 2000, "purple"))
# Actualizamos la profundidad en la pizarra automáticamente (Simulando el avance)
if not pizarra["bop_cerrado"] and res["ROP"] > 1:
    pizarra["profundidad_actual"] += (res["ROP"] / 3600) # Avance por segundo
# 2. Mostramos los Gauges (Relojes)
col1, col2, col3 = st.columns(3)
with col1:
    st.plotly_chart(crear_reloj(pizarra["presion_base"], "Presión SPP", "PSI", 5000, "red"), key="reloj_spp_tab")
with col2:
    st.plotly_chart(crear_reloj(hhp_actual, "Potencia", "HHP", 2000, "purple"), key="reloj_hhp_principal")
with col3:
    st.plotly_chart(crear_reloj(pizarra["rpm_maestro"], "Rotación", "RPM", 200, "green"), key="reloj_rpm_tab")

# 3. Gráfico de Geonavegación sincronizado
st.plotly_chart(geo.generar_grafico_trayectoria(pizarra["profundidad_actual"]))
# --- DENTRO DEL LÓGICA DEL ALUMNO EN app.py ---

st.markdown("### 📊 MONITOREO DE PARÁMETROS EN TIEMPO REAL")

fila1_col1, fila1_col2, fila1_col3 = st.columns(3)

with fila1_col1:
    # Manómetro de Presión (SPP)
    st.plotly_chart(crear_manometro(pizarra["presion_base"], "Presión Standpipe", "PSI", 5000, "#ff4b4b"), use_container_width=True)

with fila1_col2:
    # Manómetro de Caudal
    st.plotly_chart(crear_manometro(pizarra["caudal_maestro"], "Caudal de Bomba", "GPM", 1200, "#00d4ff"), use_container_width=True)

with fila1_col3:
    # Manómetro de Torque (Puedes traerlo de torque_and_drag.py)
    st.plotly_chart(crear_manometro(pizarra["torque_maestro"], "Torque en Mesa", "kft-lb", 40, "#ffcc00"), use_container_width=True)

fila2_col1, fila2_col2, fila2_col3 = st.columns(3)

with fila2_col1:
    st.plotly_chart(crear_manometro(pizarra["rpm_maestro"], "Rotación (RPM)", "rev/min", 200, "#00ff88"), use_container_width=True)

with fila2_col2:
    st.plotly_chart(crear_manometro(pizarra["wob_maestro"], "Peso (WOB)", "klbs", 60, "#a64dff"), use_container_width=True)

with fila2_col3:
    # Densidad del Lodo
    st.plotly_chart(crear_manometro(pizarra["densidad_maestra"], "Densidad Lodo", "ppg", 20, "#ffffff"), use_container_width=True)

# SI HAY ALERTA, MOSTRAR EL PANEL BOP ABAJO DE LOS RELOJES
if pizarra["alarma_activa"]:
    from bop_panel import render_bop_ui
    render_bop_ui(pizarra)

import streamlit as st

def render_bop_ui(pizarra):
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #ff4b4b;'>🛡️ CONSOLA DE CONTROL DE SURGENCIAS (BOP)</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("⭕ CERRAR ANULAR", type="primary", use_container_width=True):
            pizarra["bop_cerrado"] = True
            pizarra["alarma_activa"] = False
            pizarra["mensaje_evento"] = f"✅ Pozo Cerrado (Anular) por {st.session_state.usuario}"
            st.success("Anular Cerrado")

    with col2:
        if st.button("🚫 PIPE RAMS", type="secondary", use_container_width=True):
            pizarra["bop_cerrado"] = True
            pizarra["alarma_activa"] = False
            pizarra["mensaje_evento"] = f"✅ Pozo Cerrado (Rams) por {st.session_state.usuario}"
            st.success("Pipe Rams Cerrados")

    with col3:
        if st.button("✂️ BLIND RAMS (Corte)", type="secondary", use_container_width=True):
            pizarra["bop_cerrado"] = True
            pizarra["alarma_activa"] = False
            pizarra["mensaje_evento"] = "❗ POZO SELLADO (CORTE DE SARTA)"
            st.warning("Sarta Cortada - Pozo Sellado")

import plotly.graph_objects as go

def crear_manometro(valor, titulo, unidad, max_val, color_linea):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = valor,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"<b>{titulo}</b><br><span style='font-size:0.8em;color:gray'>{unidad}</span>", 'font': {'size': 18}},
        gauge = {
            'axis': {'range': [None, max_val], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': color_linea},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "#333",
            'steps': [
                {'range': [0, max_val*0.8], 'color': 'rgba(0, 255, 0, 0.1)'},
                {'range': [max_val*0.8, max_val], 'color': 'rgba(255, 0, 0, 0.2)'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': valor
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=50, b=20),
        height=250,
        font={'color': "white", 'family': "Arial"}
    )
    return fig

import plotly.graph_objects as go
import streamlit as st
import plotly.graph_objects as go  # <-- IMPORTANTE
# ... otros imports ...

def crear_manometro(valor, titulo, unidad, max_val, color_linea):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = valor,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"<b>{titulo}</b><br><span style='font-size:0.8em;color:gray'>{unidad}</span>", 'font': {'size': 18}},
        gauge = {
            'axis': {'range': [None, max_val], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': color_linea},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "#555",
            'steps': [
                {'range': [0, max_val*0.8], 'color': 'rgba(0, 255, 0, 0.1)'},
                {'range': [max_val*0.8, max_val], 'color': 'rgba(255, 0, 0, 0.3)'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_val * 0.8
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=50, b=20),
        height=250,
        font={'color': "white", 'family': "Arial"}
    )
    return fig

# --- 2. DESPUÉS LA PIZARRA ---
@st.cache_resource
def obtener_pizarra():
    return {
        "wob_maestro": 0.0,
        "rpm_maestro": 0.0,
        "torque_maestro": 0.0,
        "caudal_maestro": 500.0,
        "profundidad_actual": 2500.0,
        "alarma_activa": False,
        "bop_cerrado": False
    }

pizarra = obtener_pizarra()
# --- SISTEMA DE EVENTOS CRÍTICOS ---

# 1. Lógica de Surgencia (Kick)
if st.sidebar.button("🚨 ACTIVAR KICK (SURGENCIA)"):
    pizarra["alarma_activa"] = True
    st.session_state.tipo_evento = "KICK"

if st.session_state.get("tipo_evento") == "KICK":
    # La presión sube 5 psi por segundo si no cierran el BOP
    if not pizarra["bop_cerrado"]:
        # ESTAS LÍNEAS AHORA TIENEN LA SANGRÍA CORRECTA
        pizarra["presion_base"] = pizarra.get("presion_base", 0) + 5
        st.error("⚠️ ¡AUMENTO DE PRESIÓN EN TUBING! ¡CERRAR BOP!")
    else:
        st.success("✅ POZO CERRADO. CALCULAR KILL MUD WEIGHT.")

# 2. Lógica de Pérdida de Circulación
if st.sidebar.button("📉 ACTIVAR PÉRDIDA DE RETORNO"):
    st.session_state.tipo_evento = "PERDIDA"

if st.session_state.get("tipo_evento") == "PERDIDA":
    # Asumiendo que 'res' es el diccionario de tus resultados de cálculo
    if "AV" in res:
        res["AV"] = res["AV"] * 0.4 
    st.warning("📉 PÉRDIDA DE CIRCULACIÓN DETECTADA EN FORMACIÓN")

# 3. Lógica de Falla de Bomba
if st.sidebar.button("⚙️ FALLA BOMBA 1"):
    st.session_state.tipo_evento = "FALLA_BOMBA"

if st.session_state.get("tipo_evento") == "FALLA_BOMBA":
    pizarra["caudal_maestro"] = pizarra.get("caudal_maestro", 0) * 0.5
    st.error("💥 FALLA EN VÁLVULA DE BOMBA 1. CAUDAL REDUCIDO AL 50%")
    
# --- LÓGICA DE DETECCIÓN DE KICK (Línea 689 Corregida) ---
umbral_alarma = 5000  

# Usamos .get() para que si no existe, devuelva 0 y no se rompa la app
presion_actual = piz.get("presion_base", 0) 

if presion_actual > umbral_alarma:
    st.error(f"🚨 ¡ALERTA! PRESIÓN CRÍTICA EN BOCA DE POZO: {presion_actual} PSI")
    
    # IMPORTANTE: Usamos la variable de la pizarra para disparar el sonido
    if piz.get('alarma_activa', False):
        disparar_alarma_sonora()
        
    # Visualmente podemos hacer que la pantalla "parpadee" usando markdown
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #440000;
            transition: background-color 0.5s;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    # Volver al color normal si la presión baja
    st.markdown(
        """
        <style>
        .stApp { background-color: transparent; }
        </style>
        """,
        unsafe_allow_html=True
    )
    
# --- 4. INTERFAZ DE USUARIO (TABS) ---
# Asegurate de que esto esté fuera de cualquier otro bloque 'with'
with tab4:
    st.subheader("🛰️ Navegación en el Target")
    
if 'pizarra' not in st.session_state:
    st.session_state.pizarra = {
        "wob_maestro": 0.0,
        "rpm_maestro": 0.0,
        "caudal_maestro": 500.0,
        "densidad_maestra": 10.2,
        "presion_base": 1200.0,
        "profundidad_actual": 2500.0,
        "evento_activo": None,     # <-- ACÁ TIENE QUE HABER UNA COMA
        "piletas_nivel": 500.0,    # <-- ACÁ TAMBIÉN TIENE QUE HABER UNA COMA
        "bop_cerrado": False       # Esta puede quedar sin coma porque es la última
    }
piz = st.session_state.pizarra
# 1. PRIMERO: Definimos la variable global para todos los tabs
piz = st.session_state.pizarra
# 2. SEGUNDO: Creamos los tabs
tab1, tab2, tab3, tab4 = st.tabs(["🎮 Consola", "🛡️ BOP", "🧪 Lodos", "🛰️ Geo"])

with tab1:
    # Acá piz ya funciona
    st.write(f"Profundidad: {piz['profundidad_actual']}")

with tab4:
    st.subheader("🛰️ Navegación en el Target")
    # LÍNEA 674: Ahora sí, 'piz' existe y no va a tirar error
    actual = piz["profundidad_actual"] 
    limite_superior = 2510 
    limite_inferior = 2540
    # ... resto del código    
    # Definimos variables locales para este Tab
    actual = piz["profundidad_actual"]
    limite_superior = 2510 
    limite_inferior = 2540

    # Columnas alineadas perfectamente
    col_geo1, col_geo2 = st.columns(2) 
    
    with col_geo1:
        st.metric("Techo Formación", f"{limite_superior} m")
        st.metric("Piso Formación", f"{limite_inferior} m")
    
    with col_geo2:
        if actual > limite_inferior:
            st.error("🚨 SALIDA POR EL PISO - ¡CORREGIR INCLINACIÓN!")
        elif actual < limite_superior:
            st.warning("⚠️ CERCA DEL TECHO - AJUSTAR TRAYECTORIA")
        else:
            st.success("🎯 DENTRO DE LA VENTANA PRODUCTIVA")

# Cálculo físico para el simulador del MENFA
peso_lineal = 0.02 # klbs por metro
peso_sarta = piz["profundidad_actual"] * peso_lineal
hook_load_real = peso_sarta - piz["wob_maestro"]

import time

if 'inicio_falla' not in st.session_state:
    st.session_state.inicio_falla = None
if 'tiempo_respuesta' not in st.session_state:
    st.session_state.tiempo_respuesta = 0

if piz.get("evento_activo") and st.session_state.inicio_falla is None:
    st.session_state.inicio_falla = time.time()

if not piz.get("evento_activo"):
    st.session_state.inicio_falla = None
    
# Ahora podés usar 'hook_load_real' en cualquier reloj de la Tab 1
with st.sidebar:
    st.header("🎮 Controles del Perforador")
    st.info("Ajuste los parámetros de perforación en tiempo real.")

    # 1. SEGURIDAD Y BLINDAJE (Fuera de los sliders)
    # Obtenemos valores limpios y enteros
    rpm_val = int(max(0, min(200, piz.get("rpm_maestro", 0))))
    wob_val = int(max(0, min(50, piz.get("wob_maestro", 0))))
    gpm_val = int(max(0, min(1000, piz.get("caudal_maestro", 500))))

    # 2. SLIDERS ÚNICOS (Uno por cada parámetro)
    piz["rpm_maestro"] = st.slider("Rotación (RPM)", 0, 200, rpm_val)
    
    piz["wob_maestro"] = st.slider("Peso sobre Trépano (WOB klbs)", 0, 50, wob_val)
    
    piz["caudal_maestro"] = st.slider(
        label="Bomba (GPM)", 
        min_value=0, 
        max_value=1000, 
        value=gpm_val,
        step=10
    )

    st.divider()

    # 3. BOTÓN DE EMERGENCIA
if st.button("🚨 EMERGENCIA: PARADA TOTAL", width="stretch"):
        piz["caudal_maestro"] = 0
        st.warning("SISTEMA DETENIDO")
        st.rerun()

if st.button("🚨 EMERGENCIA: PARADA TOTAL"):
    piz["rpm_maestro"] = 0
    piz["caudal_maestro"] = 0
    st.warning("SISTEMA DETENIDO")

# --- PESTAÑAS INTERACTIVAS ---
with tab2:
    st.header("🛡️ Unidad de Cierre BOP")
    col_bop1, col_bop2 = st.columns(2)
    
   # --- Línea 810 y 811 corregidas ---
with st.container():  # O el 'with' que tengas en la línea 810
    try:
        st.image("assets/BoP.png", width="stretch")
    except:
        st.warning("⚠️ No se pudo cargar la imagen del BOP.")
        st.image("assest/BoP.png", width=100) 
        if st.button("🔒 CERRAR RAMS (Anular)", type="primary"):
            piz["bop_cerrado"] = True
            st.error("BOP CERRADO - Presión contenida")
            
    with col_bop2:
        if st.button("🔓 ABRIR RAMS"):
            piz["bop_cerrado"] = False
            st.success("BOP ABIERTO - Circulación libre")

with tab3:
    st.header("🧪 Control de Densidad")
    # Usamos .get para evitar errores si la clave no existe aún
    dens_actual = piz.get("densidad_maestra", 10.0)
    nuevo_peso = st.number_input("Ajustar Densidad (ppg)", 8.0, 18.0, dens_actual)
    
    if st.button("⚗️ Tratar Lodo"):
        piz["densidad_maestra"] = nuevo_peso
        st.info(f"Densidad ajustada a {nuevo_peso} ppg. Recalculando ECD...")

with tab4:
    st.header("🛰️ Dirección de Pozo")
    inc_ajuste = st.select_slider("Corregir Inclinación", options=["Bajar (-)", "Mantener", "Subir (+)"], value="Mantener")
    
    if inc_ajuste == "Subir (+)":
        piz["profundidad_actual"] -= 0.5 # Sube hacia el techo (TVD menor)
    elif inc_ajuste == "Bajar (-)":
        piz["profundidad_actual"] += 0.5 # Baja hacia el piso (TVD mayor)
        
    st.metric("Posición Actual TVD", f"{piz['profundidad_actual']:.2f} m")

# --- 1. LÓGICA DE FALLAS Y TIEMPO ---
if 'inicio_falla' not in st.session_state:
    st.session_state.inicio_falla = None

ultima_falla_segura = st.session_state.get("ultima_falla", time.time())

if time.time() - ultima_falla_segura > 300:
    if random.random() < 0.3: 
        fallas = ["KICK", "PERDIDA", "FALLA BOMBA", "PEGAMIENTO"]
        piz["evento_activo"] = random.choice(fallas)
        st.session_state.ultima_falla = time.time()
        st.session_state.inicio_falla = time.time()
  
# --- 2. PANEL DE ALERTAS (VISIBLES EN TODA LA APP) ---
if piz.get("evento_activo"):
    # Si por algún motivo no se inició el tiempo, lo iniciamos ahora
    if st.session_state.inicio_falla is None:
        st.session_state.inicio_falla = time.time()
        
    tiempo_transcurrido = int(time.time() - st.session_state.inicio_falla)
    
    col_err1, col_err2 = st.columns([3, 1])
    with col_err1:
        st.error(f"🚨 ¡FALLA ACTIVA: {piz['evento_activo']}!")
        # Lógica dinámica de la falla
        if piz["evento_activo"] == "KICK":
            piz["presion_base"] += 0.5
            piz["piletas_nivel"] += 0.1
        elif piz["evento_activo"] == "PERDIDA":
            piz["piletas_nivel"] -= 0.1
            
    with col_err2:
        st.metric("⏱️ Tiempo Reacción", f"{tiempo_transcurrido} s")

    if tiempo_transcurrido > 45:
        st.error("💥 ¡DESCONTROL DEL POZO! Tardaste demasiado.")
        st.stop()

# --- 3. CONTENIDO DE LAS PESTAÑAS (TABS) ---
with tab1:
    st.subheader("📊 Panel de Control Principal")
    # ... tus otros gráficos ...
    st.divider()
    st.subheader("🏆 Ranking de Operadores (Top Mendoza)")
    data_ranking = {
        "Alumno": ["Fabricio", "Alumno A", "Alumno B"],
        "Reacción (s)": [12, 18, 25],
        "Costo (USD)": [15000, 18200, 22100]
    }
    st.table(data_ranking)

with tab2:
    st.header("🛡️ Seguridad de Pozo (BOP)")
    if piz["evento_activo"] == "KICK":
        if st.button("✅ CERRAR POZO (Driller's Method)", type="primary"):
            piz["evento_activo"] = None
            st.session_state.inicio_falla = None
            st.balloons()
            st.success("🎯 ¡KICK CONTROLADO!")

with tab3:
    st.header("🧪 Sistema de Circulación")
    # Consolidamos la métrica de piletas aquí
    st.metric("📦 Volumen en Piletas", f"{piz.get('piletas_nivel', 500):.1f} bbl")
    
    if piz["evento_activo"] == "PERDIDA":
        if st.button("🧪 Bombear Píldora LCM"):
            piz["evento_activo"] = None
            st.session_state.inicio_falla = None
            st.success("✅ Pérdida sellada exitosamente")
# --- SISTEMA DE EMISIÓN DE DOCUMENTOS MENFA ---
st.write("---") # Esto crea una línea divisoria física
st.header("🎓 Gestión de Certificados y Reportes")

# 1. Aseguramos que existan las variables de memoria
if "pdf_cert_final" not in st.session_state:
    st.session_state.pdf_cert_final = None
if "pdf_repo_final" not in st.session_state:
    st.session_state.pdf_repo_final = None

# 2. SECCIÓN CERTIFICADO
col1, col2 = st.columns(2)

with col1:
    alumno = st.text_input("Nombre del Alumno para Certificado:", key="input_cert_nombre")
    if st.button("📌 1. Preparar Certificado"):
        if alumno:
            try:
                # Limpieza de nombre (sin tildes para evitar errores)
                import unicodedata
                n_limpio = ''.join(c for c in unicodedata.normalize('NFD', alumno) if unicodedata.category(c) != 'Mn').upper()
                
                f_pdf = FPDF()
                f_pdf.add_page()
                f_pdf.set_font("Arial", 'B', 20)
                f_pdf.cell(200, 20, "IPCL MENFA - CERTIFICADO", ln=True, align='C')
                f_pdf.ln(10)
                f_pdf.set_font("Arial", '', 16)
                f_pdf.cell(200, 10, f"Otorgado a: {n_limpio}", ln=True, align='C')
                
                # Conversión segura a bytes
                out_str = f_pdf.output(dest='S')
                st.session_state.pdf_cert_final = out_str.encode('latin-1', 'replace')
                st.success(f"Certificado de {n_limpio} listo")
            except Exception as e:
                st.error(f"Error en Certificado: {e}")

with col2:
    if st.session_state.pdf_cert_final is not None:
        st.download_button(
            label="📥 DESCARGAR CERTIFICADO",
            data=st.session_state.pdf_cert_final,
            file_name="Certificado_MENFA.pdf",
            mime="application/pdf",
            key="dl_cert_btn"
        )

# 3. SECCIÓN REPORTE (SIDEBAR)
st.sidebar.markdown("---")
st.sidebar.subheader("📄 Reporte de Entrenamiento")

if st.sidebar.button("⚙️ Preparar Reporte Final"):
    try:
        r_pdf = FPDF()
        r_pdf.add_page()
        r_pdf.set_font("Arial", 'B', 14)
        r_pdf.cell(200, 10, "REPORTE OPERATIVO - MENFA IPCL", ln=True, align='C')
        
        # Generación de bytes
        r_str = r_pdf.output(dest='S')
        st.session_state.pdf_repo_final = r_str.encode('latin-1', 'replace')
        st.sidebar.success("Reporte preparado")
    except Exception as e:
        st.sidebar.error(f"Error en Reporte: {e}")

if st.session_state.pdf_repo_final is not None:
    st.sidebar.download_button(
        label="📥 DESCARGAR INFORME",
        data=st.session_state.pdf_repo_final,
        file_name="Reporte_Final.pdf",
        mime="application/pdf",
        key="dl_repo_btn"
    )
# --- BOTÓN DE CIERRE DE SESIÓN / INSTRUCTOR ---
st.sidebar.divider()
with st.sidebar.expander("🔐 Panel del Instructor"):
    st.write("Uso exclusivo para finalizar la jornada de capacitación.")
    if st.button("🏁 DAR POR TERMINADA LA CLASE", use_container_width=True, type="secondary"):
        # 1. Limpiamos las variables críticas
        st.session_state.pizarra["evento_activo"] = None
        st.session_state.pizarra["rpm_maestro"] = 0
        st.session_state.pizarra["caudal_maestro"] = 0
        st.session_state.pizarra["piletas_nivel"] = 500.0
        st.session_state.pizarra["profundidad_actual"] = 2500.0
        
        # 2. Reseteamos cronómetros
        st.session_state.ultima_falla = time.time()
        st.session_state.inicio_falla = None
        st.session_state.tiempo_respuesta = 0
        
        # 3. Mensaje de despedida y reinicio
        st.success("✅ Clase finalizada. Sistema reseteado para el próximo turno.")
        time.sleep(2) # Pausa para que el instructor vea el mensaje
        st.rerun()
