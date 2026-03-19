import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.graph_objects as go
from datetime import datetime
import time
import os

# --- 1. CONFIGURACIÓN ÚNICA DE PÁGINA ---
st.set_page_config(page_title="IPCL MENFA WELL SIM V5", layout="wide", initial_sidebar_state="collapsed")

# --- 2. ESTILO CSS PARA TARJETAS Y MÉTRICAS ---
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; background-color: #0e1117;}
    .stMetric {background-color: #1c222d; border: 1px solid #34495e; border-radius: 8px; padding: 15px;}
    [data-testid="stMetricValue"] {color: #f39c12; font-size: 1.8rem; font-weight: bold;}
    .module-card {
        text-align: center; padding: 25px; border-radius: 15px; 
        background-color: #161b22; border: 2px solid #34495e;
        transition: 0.3s; height: 200px;
    }
    .module-card:hover { border-color: #f39c12; background-color: #1c222d; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNCIONES DE UTILIDAD Y MOTOR ---
def mostrar_imagen_segura(nombre_archivo, ancho=None, subtitulo=""):
    if os.path.exists(nombre_archivo):
        st.image(nombre_archivo, width=ancho, caption=subtitulo)
    else:
        st.info(f"ℹ️ Sistema: {nombre_archivo} no detectado (Modo técnico).")

# Inicialización de variables de sesión (Singleton)
if "auth" not in st.session_state: st.session_state.auth = False
if "menu" not in st.session_state: st.session_state.menu = "HOME"
if "usuario" not in st.session_state: st.session_state.usuario = "Invitado"
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame([{
        "DEPTH": 2850.0, "WOB": 25.0, "RPM": 120, "TORQUE": 18500, 
        "SPP": 3200, "ROP": 15.0, "MSE": 35.0, "GR": 140, "TANQUES": 1000
    }])

# Datos actuales para cálculos rápidos
curr = st.session_state.history.iloc[-1]

# Intentar importar módulos externos
try:
    from motor_calculos_avanzados import calcular_fisica_perforacion
except ImportError:
    def calcular_fisica_perforacion(wob, rpm, torque, rop, depth, flow_rate):
        return {"MSE": round(35.0, 2), "AV": 120.0, "KMW": 11.5, "HOOK_LOAD": 250.0}

# --- 4. DEFINICIÓN DE PANTALLAS (MÓDULOS) ---

def login_screen():
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    mostrar_imagen_segura("logo_menfa.png", ancho=250)
    st.title("SISTEMA DE ENTRENAMIENTO MENFA V5.0")
    st.subheader("Cátedra de Perforación - UTN Mendoza")
    st.markdown('</div>', unsafe_allow_html=True)
    with st.form("login_form"):
        nombre = st.text_input("Nombre Completo del Alumno:")
        legajo = st.text_input("Número de Legajo:")
        yacimiento = st.selectbox("Asignación de Yacimiento:", ["Barrancas", "Cruz de Piedra", "Malargüe", "Vizcacheral"])
        if st.form_submit_button("INICIAR GUARDIA DE PERFORACIÓN"):
            if nombre and legajo:
                st.session_state.usuario = nombre
                st.session_state.legajo = legajo
                st.session_state.yacimiento_activo = yacimiento
                st.session_state.auth = True
                st.session_state.menu = "HOME"
                st.rerun()
            else:
                st.error("Complete sus datos.")

def render_home():
    st.title(f"👷 BIENVENIDO, {st.session_state.usuario}")
    st.write(f"📍 Pozo: {st.session_state.yacimiento_activo} | UTN FRM")
    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="module-card"><h1>📊</h1><h3>MONITOR SCADA</h3></div>', unsafe_allow_html=True)
        if st.button("ABRIR MONITOR", use_container_width=True): st.session_state.menu = "SCADA"; st.rerun()
    with c2:
        st.markdown('<div class="module-card"><h1>🛡️</h1><h3>SEGURIDAD BOP</h3></div>', unsafe_allow_html=True)
        if st.button("CONTROL POZOS", use_container_width=True): st.session_state.menu = "BOP"; st.rerun()
    with c3:
        st.markdown('<div class="module-card"><h1>📡</h1><h3>LWD / MWD</h3></div>', unsafe_allow_html=True)
        if st.button("GEONAVEGACIÓN", use_container_width=True): st.session_state.menu = "LWD"; st.rerun()
    
    st.write("")
    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown('<div class="module-card"><h1>📉</h1><h3>GESTIÓN PÉRDIDAS</h3></div>', unsafe_allow_html=True)
        if st.button("MANEJAR PÉRDIDAS", use_container_width=True): st.session_state.menu = "PERDIDA"; st.rerun()
    with c5:
        st.markdown('<div class="module-card"><h1>🔩</h1><h3>DISEÑO SARTA</h3></div>', unsafe_allow_html=True)
        if st.button("SARTAS API", use_container_width=True): st.session_state.menu = "SARTAS"; st.rerun()
    with c6:
        st.markdown('<div class="module-card"><h1>🏆</h1><h3>EVALUACIÓN</h3></div>', unsafe_allow_html=True)
        if st.button("REPORTE FINAL", use_container_width=True): st.session_state.menu = "REPORTE"; st.rerun()

def render_scada():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("🖥️ MONITOR SCADA - MÉTRICAS")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("WOB (klbs)", f"{curr['WOB']}")
    m2.metric("RPM", f"{curr['RPM']}")
    m3.metric("Torque", f"{curr['TORQUE']}")
    m4.metric("MSE (kpsi)", f"{curr['MSE']}")
    m5.metric("TVD (m)", f"{curr['DEPTH']}")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=st.session_state.history['SPP'], name="Presión SPP", line=dict(color='#3498db', width=3)))
    fig.update_layout(template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)

def render_bop():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("🛡️ PANEL DE SEGURIDAD BOP (API S53)")
    col_a, col_b = st.columns(2)
    with col_a: mostrar_imagen_segura("Gemini_Generated_Image_dn7zasdn7zasdn7z.png", ancho=450)
    with col_b:
        st.metric("Presión Acumulador", "2850 psi")
        if st.button("🔥 CIERRE DE EMERGENCIA", type="primary"):
            st.error("¡CIERRE ACTIVADO!")

def render_lwd():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("📡 GEONAVEGACIÓN LWD / MWD")
    if curr['GR'] < 100: st.error(f"🚨 ALERTA LWD: GAMMA RAY BAJO ({curr['GR']})")
    else: st.success(f"🎯 EN CAPA: GAMMA RAY ({curr['GR']})")
    
    z = np.linspace(0, curr['DEPTH'], 100)
    x = np.where(z < 2200, 0, (z - 2200)**1.6 / 60)
    fig = go.Figure(data=[go.Scatter3d(x=x, y=np.zeros(100), z=z, mode='lines', line=dict(color='#2ecc71', width=6))])
    fig.update_layout(scene=dict(zaxis=dict(autorange="reversed")), template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

def modulo_perdida_circulacion():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("📉 GESTIÓN DE PÉRDIDAS")
    st.warning(f"Nivel de Tanques: {int(curr['TANQUES'])} bbl")
    if st.button("BOMBEAR LCM"): st.success("Píldora bombeada.")

def modulo_sartas_api():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("🔩 DISEÑO DE SARTA (API 5DP)")
    st.info("Módulo de cálculo de tensión y torque máximo.")

def generar_diploma():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("🏆 REPORTE FINAL")
    st.write(f"Operador: {st.session_state.usuario} | Legajo: {st.session_state.legajo}")
    st.table(st.session_state.history.tail(5))
    st.download_button("📥 DESCARGAR CSV", st.session_state.history.to_csv().encode('utf-8'), "reporte.csv")

# --- 5. LÓGICA DE NAVEGACIÓN Y SIDEBAR ---

if not st.session_state.auth:
    login_screen()
else:
    with st.sidebar:
        mostrar_imagen_segura("logo_menfa.png", width=100)
        st.header(f"🕹️ {st.session_state.usuario}")
        new_wob = st.slider("WOB (klbs)", 0, 60, int(curr['WOB']))
        new_rpm = st.slider("RPM", 0, 200, int(curr['RPM']))
        if st.button("ACTUALIZAR SIMULACIÓN"):
            # Lógica de cálculo y evento aleatorio
            new_depth = curr['DEPTH'] + 1.5
            if random.random() < 0.10:
                st.session_state.menu = "PERDIDA"
                st.warning("⚠️ ¡PÉRDIDA DE LODO!")
            
            new_row = {"DEPTH": new_depth, "WOB": new_wob, "RPM": new_rpm, "TORQUE": (new_wob*400), 
                       "SPP": 3200 + (new_depth*0.1), "ROP": 15, "MSE": 35, "GR": random.randint(80,160), 
                       "TANQUES": curr['TANQUES'] - (random.randint(0,5))}
            st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([new_row])], ignore_index=True)
            st.rerun()
        if st.button("🚪 LOGOUT"):
            st.session_state.auth = False
            st.rerun()

    # Ruteador Final
    if st.session_state.menu == "HOME": render_home()
    elif st.session_state.menu == "SCADA": render_scada()
    elif st.session_state.menu == "BOP": render_bop()
    elif st.session_state.menu == "LWD": render_lwd()
    elif st.session_state.menu == "PERDIDA": modulo_perdida_circulacion()
    elif st.session_state.menu == "SARTAS": modulo_sartas_api()
    elif st.session_state.menu == "REPORTE": generar_diploma()
