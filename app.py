import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.graph_objects as go
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="SIMULADOR MENFA - NORMATIVA API", layout="wide", initial_sidebar_state="collapsed")

# --- 2. FUNCIONES DE INTERFAZ ---
def mostrar_imagen(archivo, ancho=None):
    if os.path.exists(archivo):
        st.image(archivo, width=ancho)

# --- 3. ESTADO DEL SISTEMA ---
if "auth" not in st.session_state: st.session_state.auth = False
if "menu" not in st.session_state: st.session_state.menu = "HOME"
if "kick_alert" not in st.session_state: st.session_state.kick_alert = False
if "vida_sarta" not in st.session_state: st.session_state.vida_sarta = 100.0 
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame([{
        "DEPTH": 2500.0, "WOB": 20.0, "RPM": 100, "TORQUE": 15000, 
        "SPP": 2800, "ROP": 10.0, "MSE": 30.0, "GR": 120, "TANQUES": 1000
    }])

curr = st.session_state.history.iloc[-1]

# --- 4. MÓDULOS BAJO NORMATIVA API ---

def render_home():
    if st.session_state.kick_alert:
        st.error("⚠️ ALERTA DE ARREMETIDA (API S53): FLUJO POSITIVO DETECTADO. PROCEDER A CIERRE.")
    
    st.title(f"🕹️ CONTROL DE OPERACIONES - {st.session_state.yacimiento}")
    st.subheader(f"OPERADOR: {st.session_state.usuario} | NORMATIVA API ACTIVA")
    st.divider()
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📊 MONITOR SCADA", use_container_width=True): st.session_state.menu = "SCADA"; st.rerun()
    with c2:
        tipo = "primary" if st.session_state.kick_alert else "secondary"
        if st.button("🛡️ PANEL BOP (API S53)", use_container_width=True, type=tipo): st.session_state.menu = "BOP"; st.rerun()
    with c3:
        if st.button("📡 LWD / MWD", use_container_width=True): st.session_state.menu = "LWD"; st.rerun()
    
    st.write("")
    c4, c5, c6 = st.columns(3)
    with c4:
        if st.button("🧪 FLUIDOS (API RP 13B)", use_container_width=True): st.session_state.menu = "LODOS"; st.rerun()
    with c5:
        if st.button("🔩 SARTAS (API 5DP)", use_container_width=True): st.session_state.menu = "SARTAS"; st.rerun()
    with c6:
        if st.button("🏆 REPORTE FINAL", use_container_width=True): st.session_state.menu = "REPORTE"; st.rerun()

def modulo_lodos():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("🧪 FLUIDOS DE PERFORACIÓN (API RP 13B-1)")
    
    col_a, col_b = st.columns(2)
    with col_a:
        densidad = st.number_input("Densidad (ppg):", value=9.5)
        tvd_ft = curr['DEPTH'] * 3.28
        # Constante API 0.052
        presion_hidro = 0.052 * densidad * tvd_ft
        st.metric("Presión Hidrostática", f"{round(presion_hidro, 2)} psi")
    with col_b:
        st.info("De acuerdo a API RP 13B-1, la densidad debe medirse con balanza de lodos calibrada.")
        if presion_hidro < (0.465 * tvd_ft):
            st.warning("RIESGO: Presión Hidrostática por debajo del gradiente de formación (0.465 psi/ft).")

def modulo_sartas():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("🔩 TUBULARES Y SARTA (API 5DP / API RP 7G)")
    
    # Cálculo de Tensión con Factor de Flotabilidad
    densidad_lodo = 9.5
    factor_flot = 1 - (densidad_lodo / 65.5) # Acero = 65.5 ppg
    peso_aire = curr['DEPTH'] * 15 # lb/m aprox
    tension_gancho = (peso_aire * factor_flot) + (curr['WOB'] * 1000)
    
    st.metric("Hook Load (API Flotado)", f"{round(tension_gancho, 0)} lbs")
    
    st.divider()
    st.subheader("Estado de Fatiga (API RP 7G)")
    st.progress(st.session_state.vida_sarta / 100)
    if st.session_state.vida_sarta < 30:
        st.error("RECOMENDACIÓN API: Inspección de Ensayos No Destructivos (NDT) requerida.")

def panel_bop():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("🛡️ CONTROL DE POZO (API S53)")
    st.write("Configuración: Diverter + Anular + Rams de Tubería + Rams Ciegos")
    mostrar_imagen("bop_panel.png", ancho=500)
    
    if st.button("CERRAR ANULAR (HARD SHUT-IN)", type="primary"):
        st.session_state.kick_alert = False
        st.success("POZO CERRADO SEGÚN PROTOCOLO API S53.")

# --- 5. LÓGICA DE PERFORACIÓN ---

def login_menfa():
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    mostrar_imagen("logo_menfa.png", ancho=300)
    st.title("IPCL MENFA - MENDOZA")
    st.subheader("SIMULADOR TÉCNICO BAJO NORMAS API")
    st.markdown('</div>', unsafe_allow_html=True)
    with st.form("login"):
        u = st.text_input("Operador:")
        l = st.text_input("Legajo:")
        y = st.selectbox("Yacimiento:", ["Barrancas", "Vizcacheral", "Malargüe"])
        if st.form_submit_button("CONECTAR A CABINA"):
            st.session_state.usuario, st.session_state.legajo, st.session_state.yacimiento, st.session_state.auth = u, l, y, True
            st.rerun()

if not st.session_state.auth:
    login_menfa()
else:
    with st.sidebar:
        mostrar_imagen("logo_menfa.png", ancho=150)
        st.divider()
        st.write(f"Ref: API 5DP Grade G-105")
        wob = st.slider("WOB (klbs)", 0, 60, int(curr['WOB']))
        rpm = st.slider("RPM", 0, 200, int(curr['RPM']))
        
        if st.button("AVANZAR PERFORACIÓN"):
            # Lógica de Fatiga API
            desgaste = (wob * 0.02) + (rpm * 0.008)
            st.session_state.vida_sarta -= desgaste
            
            # Arremetida (Kick) aleatoria
            kick = 0
            if random.random() < 0.07:
                st.session_state.kick_alert = True
                kick = random.randint(10, 25)
            
            nueva_fila = {
                "DEPTH": curr['DEPTH'] + 1.0, "WOB": wob, "RPM": rpm, 
                "TORQUE": (wob * 380) + (curr['DEPTH'] * 0.15), 
                "SPP": 2800 + (curr['DEPTH'] * 0.025),
                "ROP": (rpm * 0.11) + (wob * 0.045), "MSE": 30.0, 
                "GR": random.randint(80, 150), "TANQUES": curr['TANQUES'] + kick
            }
            st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([nueva_fila])], ignore_index=True)
            st.rerun()

    # Ruteo Final
    if st.session_state.menu == "HOME": render_home()
    elif st.session_state.menu == "SCADA":
        st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
        st.metric("Profundidad Actual", f"{curr['DEPTH']} m")
        st.metric("MSE (Mechanical Specific Energy)", f"{curr['MSE']} kpsi")
    elif st.session_state.menu == "BOP": panel_bop()
    elif st.session_state.menu == "SARTAS": modulo_sartas()
    elif st.session_state.menu == "LODOS": modulo_lodos()
    elif st.session_state.menu == "LWD":
        st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
        st.title("MWD / LWD DATA")
        st.write(f"Gamma Ray: {curr['GR']} API Units")
    elif st.session_state.menu == "REPORTE":
        st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
        st.write("REPORTE DE OPERACIONES API")
        st.table(st.session_state.history.tail())
