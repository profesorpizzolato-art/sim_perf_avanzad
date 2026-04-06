import streamlit as st
import pandas as pd
import numpy as np
import time
import base64
import os
from datetime import datetime
from fpdf import FPDF
from streamlit_autorefresh import st_autorefresh

# --- IMPORTACIÓN DE TUS MÓDULOS TÉCNICOS (FILES) ---
import motor_calculos_avanzados as motor
import geonavegacion_pro as geo
import torque_and_drag as td
import bombas_de_lodo as bombas
import sartas_perforacion as sartas
import sys
import os

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

pizarra = obtener_pizarra_maestra()

# Latido del sistema para que el alumno vea los cambios del instructor cada 1 seg
st_autorefresh(interval=1000, key="latido_sincro")

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
with st.sidebar:
    st.title("👨‍🏫 Panel del Instructor")
    st.write(f"Profundidad: {pizarra['profundidad_actual']:.2f} m")
    
    if st.button("🔄 Resetear Eventos"):
        st.session_state.tipo_evento = None
        pizarra["alarma_activa"] = False
        st.rerun()
# --- 5. INTERFAZ PRINCIPAL ---

# SIDEBAR COMÚN
st.sidebar.image("logo.menfa.png", use_container_width=True)
st.sidebar.title(f"Usuario: {st.session_state.usuario}")

# --- MODO INSTRUCTOR (TÚ MANEJAS LAS VARIABLES) ---
if st.session_state.rol == "instructor":
    st.sidebar.markdown("### 🎮 PANEL DE CONTROL MAESTRO")
nuevo_caudal = st.sidebar.slider("Caudal (GPM)", 0, 1200, float(pizarra["caudal_maestro"]))
nuevo_wob = st.sidebar.slider("WOB (klbs)", 0, 100, float(pizarra["wob_maestro"]))
nuevo_rpm = st.sidebar.slider("RPM", 0, 200, float(pizarra["rpm_maestro"]))

# Luego actualizamos la pizarra con esos nuevos valores
pizarra["caudal_maestro"] = nuevo_caudal
pizarra["wob_maestro"] = nuevo_wob
pizarra["rpm_maestro"] = nuevo_rpm
    st.sidebar.divider()
    if not pizarra["alarma_activa"]:
        if st.sidebar.button("🚨 ACTIVAR KICK / SURGENCIA", type="primary", use_container_width=True):
            pizarra["alarma_activa"] = True
            pizarra["bop_cerrado"] = False
            pizarra["mensaje_evento"] = "¡AMENAZA DE SURGENCIA DETECTADA! CIERRE EL POZO."
    else:
        if st.sidebar.button("✅ NORMALIZAR SISTEMA", use_container_width=True):
            pizarra["alarma_activa"] = False
            pizarra["bop_cerrado"] = False
            pizarra["mensaje_evento"] = "Operación Normal"

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

# --- 6. REPORTE FINAL (SIN IADC) ---
st.sidebar.divider()
if st.sidebar.button("📥 Generar Informe Final"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "MENFA IPCL - REPORTE DE ENTRENAMIENTO", 0, 1, 'C')
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, f"Alumno: {st.session_state.usuario}", 0, 1)
    pdf.cell(200, 10, f"Instructor: Fabricio Pizzolato", 0, 1)
    pdf.cell(200, 10, f"Resultado: {'Operación Exitosa' if pizarra['bop_cerrado'] else 'Finalizado'}", 0, 1)
    
    # Descarga directa
    reporte_bytes = pdf.output(dest='S').encode('latin-1')
    st.sidebar.download_button("Descargar PDF", data=reporte_bytes, file_name="Reporte_Final.pdf")

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

# 2. Dibujamos los manómetros usando tu nueva función
col1, col2, col3 = st.columns(3)

with col1:
    st.plotly_chart(crear_manometro(res["ROP"], "ROP", "m/hr", 60, "lime"), use_container_width=True)

with col2:
    st.plotly_chart(crear_manometro(res["MSE"], "MSE", "kpsi", 100, "orange"), use_container_width=True)

with col3:
    st.plotly_chart(crear_manometro(res["HOOK_LOAD"], "Hook Load", "klbs", 600, "white"), use_container_width=True)

# Actualizamos la profundidad en la pizarra automáticamente (Simulando el avance)
if not pizarra["bop_cerrado"] and res["ROP"] > 1:
    pizarra["profundidad_actual"] += (res["ROP"] / 3600) # Avance por segundo
# 2. Mostramos los Gauges (Relojes)
col1, col2, col3 = st.columns(3)
with col1:
    st.plotly_chart(crear_reloj(pizarra["presion_base"], "Presión SPP", "PSI", 5000, "red"))
with col2:
    st.plotly_chart(crear_reloj(hhp_actual, "Potencia", "HHP", 2000, "purple"))
with col3:
    st.plotly_chart(crear_reloj(pizarra["rpm_maestro"], "Rotación", "RPM", 200, "green"))

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

# --- 3. AL FINAL LA LÓGICA QUE LLAMA A LAS FUNCIONES ---
# Aquí es donde usas st.plotly_chart(crear_manometro(...))
# --- SISTEMA DE EVENTOS CRÍTICOS ---

# 1. Lógica de Surgencia (Kick)
if st.sidebar.button("🚨 ACTIVAR KICK (SURGENCIA)"):
    pizarra["alarma_activa"] = True
    st.session_state.tipo_evento = "KICK"

if st.session_state.get("tipo_evento") == "KICK":
    # La presión sube 5 psi por segundo si no cierran el BOP
    if not pizarra["bop_cerrado"]:
        pizarra["presion_base"] += 5
        st.error("⚠️ ¡AUMENTO DE PRESIÓN EN TUBING! ¡CERRAR BOP!")
    else:
        st.success("✅ POZO CERRADO. CALCULAR KILL MUD WEIGHT.")

# 2. Lógica de Pérdida de Circulación
if st.sidebar.button("📉 ACTIVAR PÉRDIDA DE RETORNO"):
    st.session_state.tipo_evento = "PERDIDA"

if st.session_state.get("tipo_evento") == "PERDIDA":
    res["AV"] = res["AV"] * 0.4 # Cae la velocidad anular
    st.warning("📉 PÉRDIDA DE CIRCULACIÓN DETECTADA EN FORMACIÓN")

# 3. Lógica de Falla de Bomba
if st.sidebar.button("⚙️ FALLA BOMBA 1"):
    st.session_state.tipo_evento = "FALLA_BOMBA"

if st.session_state.get("tipo_evento") == "FALLA_BOMBA":
    pizarra["caudal_maestro"] = pizarra["caudal_maestro"] * 0.5
    st.error("💥 FALLA EN VÁLVULA DE BOMBA 1. CAUDAL REDUCIDO AL 50%")

