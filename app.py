import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.graph_objects as go
import os
from datetime import datetime

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="SIMULADOR MENFA V5", layout="wide", initial_sidebar_state="collapsed")

# --- 2. FUNCIONES DE INTERFAZ ---
def mostrar_imagen(archivo, ancho=None):
    if os.path.exists(archivo):
        st.image(archivo, width=ancho)

# --- 3. ESTADO DEL SISTEMA ---
if "auth" not in st.session_state: st.session_state.auth = False
if "menu" not in st.session_state: st.session_state.menu = "HOME"
if "kick_alert" not in st.session_state: st.session_state.kick_alert = False
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame([{
        "DEPTH": 2500.0, "WOB": 20.0, "RPM": 100, "TORQUE": 15000, 
        "SPP": 2800, "ROP": 10.0, "MSE": 30.0, "GR": 120, "TANQUES": 1000
    }])

curr = st.session_state.history.iloc[-1]

# --- 4. DEFINICIÓN DE MÓDULOS ---

def login_menfa():
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    mostrar_imagen("logo_menfa.png", ancho=300)
    st.title("SISTEMA DE ENTRENAMIENTO PETROLERO")
    st.subheader("IPCL MENFA - MENDOZA")
    st.markdown('</div>', unsafe_allow_html=True)
    with st.form("acceso_operador"):
        nombre = st.text_input("Operador:")
        legajo = st.text_input("Legajo:")
        yacimiento = st.selectbox("Yacimiento:", ["Barrancas", "Vizcacheral", "Malargüe", "Puesto Pozo Cercado"])
        if st.form_submit_button("INGRESAR A CABINA"):
            if nombre:
                st.session_state.usuario = nombre
                st.session_state.legajo = legajo
                st.session_state.yacimiento = yacimiento
                st.session_state.auth = True
                st.rerun()

def render_home():
    if st.session_state.kick_alert:
        st.error("⚠️ ¡ALERTA DE ARREMETIDA! FLUJO POSITIVO EN TANQUES. ¡CIERRE BOP!")
    
    st.title(f"🕹️ CONTROL DE OPERACIONES - {st.session_state.yacimiento}")
    st.write(f"Operador: {st.session_state.usuario} | Legajo: {st.session_state.legajo}")
    st.divider()
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📊 MONITOR SCADA", use_container_width=True): st.session_state.menu = "SCADA"; st.rerun()
    with c2:
        tipo = "primary" if st.session_state.kick_alert else "secondary"
        if st.button("🛡️ PANEL BOP", use_container_width=True, type=tipo): st.session_state.menu = "BOP"; st.rerun()
    with c3:
        if st.button("📡 GEONAVEGACIÓN LWD", use_container_width=True): st.session_state.menu = "LWD"; st.rerun()
    
    st.write("")
    c4, c5, c6 = st.columns(3)
    with c4:
        if st.button("🧪 CÁLCULO DE LODOS", use_container_width=True): st.session_state.menu = "LODOS"; st.rerun()
    with c5:
        if st.button("🔩 TORQUE Y DRAG", use_container_width=True): st.session_state.menu = "SARTAS"; st.rerun()
    with c6:
        if st.button("🏆 REPORTE FINAL", use_container_width=True): st.session_state.menu = "REPORTE"; st.rerun()

def vista_scada():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.header("MONITOR DE TIEMPO REAL")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Profundidad (m)", f"{curr['DEPTH']}")
    m2.metric("WOB (klbs)", f"{curr['WOB']}")
    m3.metric("RPM", f"{curr['RPM']}")
    m4.metric("Tanques (bbl)", f"{int(curr['TANQUES'])}")
    
    fig = go.Figure(go.Scatter(y=st.session_state.history['SPP'], name="SPP", line=dict(color='#00ff00')))
    fig.update_layout(template="plotly_dark", title="Presión de Bomba (PSI)")
    st.plotly_chart(fig, use_container_width=True)

def panel_bop():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("🛡️ PANEL DE CONTROL DE POZO")
    mostrar_imagen("bop_panel.png", ancho=500)
    if st.button("CERRAR RAMS / ANULAR", type="primary"):
        st.session_state.kick_alert = False
        st.success("¡POZO CERRADO Y SEGURO!")

def modulo_lodos():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("🧪 INGENIERÍA DE FLUIDOS")
    densidad = st.number_input("Densidad (ppg):", value=9.5)
    tvd_ft = curr['DEPTH'] * 3.28
    presion = 0.052 * densidad * tvd_ft
    st.metric("Presión Hidrostática", f"{round(presion, 2)} psi")

def modulo_sartas():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("🔩 ANÁLISIS DE TORQUE Y DRAG")
    # Lógica de T&D
    tension_gancho = (curr['DEPTH'] * 12.5) + (curr['WOB'] * 1000)
    st.metric("Tensión en el Gancho (Hook Load)", f"{round(tension_gancho, 0)} lbs")
    st.metric("Torque de Rotación", f"{curr['TORQUE']} ft-lb")
    
    if curr['TORQUE'] > 22000:
        st.warning("⚠️ ALTO TORQUE: Riesgo de aprisionamiento o fatiga de materiales.")

def generar_reporte():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("🏆 REPORTE DE GUARDIA")
    st.table(st.session_state.history.tail(10))
    csv = st.session_state.history.to_csv(index=False).encode('utf-8')
    st.download_button("📥 DESCARGAR LOG", csv, f"Guardia_{st.session_state.usuario}.csv")

# --- 5. LÓGICA DE NAVEGACIÓN ---

if not st.session_state.auth:
    login_menfa()
else:
    with st.sidebar:
        mostrar_imagen("logo_menfa.png", ancho=150)
        st.write(f"Operador: {st.session_state.usuario}")
        st.divider()
        wob = st.slider("WOB (klbs)", 0, 50, int(curr['WOB']))
        rpm = st.slider("RPM", 0, 180, int(curr['RPM']))
        
        if st.button("AVANZAR PERFORACIÓN"):
            # Probabilidad de Kick (Arremetida)
            kick_evento = 0
            if random.random() < 0.10:
                st.session_state.kick_alert = True
                kick_evento = random.randint(10, 30)
            
            nueva_fila = {
                "DEPTH": curr['DEPTH'] + 1.0, 
                "WOB": wob, 
                "RPM": rpm, 
                "TORQUE": (wob * 350) + (curr['DEPTH'] * 0.1), 
                "SPP": 2800 + (curr['DEPTH'] * 0.02),
                "ROP": (rpm * 0.12) + (wob * 0.05), 
                "MSE": 30.0, 
                "GR": random.randint(80, 150), 
                "TANQUES": curr['TANQUES'] + kick_evento
            }
            st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([nueva_fila])], ignore_index=True)
            st.rerun()
            
        if st.button("LOGOUT"):
            st.session_state.auth = False
            st.rerun()

    # Ruteador
    if st.session_state.menu == "HOME": render_home()
    elif st.session_state.menu == "SCADA": vista_scada()
    elif st.session_state.menu == "BOP": panel_bop()
    elif st.session_state.menu == "LWD": 
        st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
        st.title("📡 GEONAVEGACIÓN LWD")
        st.write(f"Gamma Ray: {curr['GR']} API")
    elif st.session_state.menu == "LODOS": modulo_lodos()
    elif st.session_state.menu == "SARTAS": modulo_sartas()
    elif st.session_state.menu == "REPORTE": generar_reporte()
