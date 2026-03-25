import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import random
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL (ESTILO CYBERBASE) ---
st.set_page_config(page_title="IPCL MENFA - Simulador Integral V16", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #05070a; color: #00ffcc; }
    .stMetric { background-color: #10141b; border: 1px solid #1f2937; border-left: 5px solid #00ffcc; border-radius: 10px; padding: 15px; }
    [data-testid="stMetricValue"] { color: #ffffff; font-family: 'Courier New'; font-weight: bold; }
    .stButton>button { background: linear-gradient(135deg, #00ffcc 0%, #008b8b 100%); color: black; font-weight: bold; border: none; width: 100%; }
    .stExpander { background-color: #0b0d10; border: 1px solid #1f2937; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTOR TÉCNICO: FÍSICA, GEOLOGÍA Y EVENTOS ---
def generar_geologia_dinamica(prof):
    # Simula cambios de formación (Mendoza/Vaca Muerta)
    if 2850 <= prof <= 3050: # Payzone
        gr, dureza = np.random.normal(130, 10), 1.7
    elif 2100 <= prof < 2850:
        gr, dureza = np.random.normal(40, 8), 1.2
    else:
        gr, dureza = np.random.normal(85, 15), 1.0
    return gr, dureza

def calcular_fisica_cabina(prof, inc, wob, rpm, flow, mw, health):
    # Torque & Drag
    drag = (prof * 0.12) * np.cos(np.radians(inc)) * 0.28
    hkld = 220 - drag - (wob * 0.8)
    torque = (wob * 0.4) + (prof * 0.01) + (rpm * 0.05)
    
    # Hidráulica (SPP y ECD)
    spp = (flow**1.8 * 0.015) 
    annular_loss = (flow**1.7 * prof) / 450000
    ecd = mw + (annular_loss / (0.052 * prof * 3.28))
    
    # ROP y Desgaste
    desgaste = (wob * 0.005) + (rpm * 0.002)
    new_health = max(10, health - desgaste)
    rop = (wob * rpm / (450 * (1.1 if prof > 2800 else 1.0))) * (new_health/100)
    
    return hkld, torque, spp, ecd, rop, new_health

# --- 3. PERSISTENCIA Y REGISTRO (DB LOCAL) ---
def guardar_registro(nombre, legajo, nota):
    archivo = "registro_alumnos_menfa.csv"
    existe = os.path.isfile(archivo)
    with open(archivo, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not existe: writer.writerow(["Fecha", "Operador", "DNI", "Nota", "Estado"])
        estado = "APROBADO" if nota >= 16 else "REPROBADO"
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), nombre, legajo, nota, estado])

# --- 4. ESTADO DE SESIÓN ---
if "s" not in st.session_state:
    st.session_state.s = {
        "auth": False, "user": "", "dni": "", "md": 2500.0, "inc": 0.0,
        "health": 100.0, "history": pd.DataFrame(columns=["MD", "GR", "ROP", "ECD"]),
        "score": 0, "exam_done": False
    }
s = st.session_state.s

# --- 5. INTERFAZ: LOGIN Y CABINA ---
if not s["auth"]:
    st.title("🛡️ ACCESO SISTEMA IPCL MENFA")
    u = st.text_input("Nombre del Operador:")
    d = st.text_input("DNI / Legajo:")
    if st.button("INGRESAR A CABINA") and u and d:
        s["user"], s["dni"], s["auth"] = u, d, True
        st.rerun()
    st.stop()

# --- SIDEBAR: MANDOS DE LA TORRE ---
with st.sidebar:
    st.header(f"👤 {s['user']}")
    st.divider()
    wob = st.slider("WOB (Klbs) - Peso sobre Trépano", 0, 70, 25)
    rpm = st.slider("RPM - Rotación", 0, 160, 95)
    flow = st.slider("GPM - Caudal Bombas", 300, 1100, 600)
    mw = st.number_input("MW (ppg) - Lodo", 8.3, 16.5, 10.8)
    
    if st.button("▶️ PERFORAR TRAMO (30m)"):
        gr, dur = generar_geologia_dinamica(s["md"])
        hk, tq, sp, ec, rp, hl = calcular_fisica_cabina(s["md"], s["inc"], wob, rpm, flow, mw, s["health"])
        
        s["md"] += 30
        s["inc"] += (2.0 if s["md"] > 2800 else 0)
        s["health"] = hl
        
        new_data = pd.DataFrame([{"MD": s["md"], "GR": gr, "ROP": rp, "ECD": ec}])
        s["history"] = pd.concat([s["history"], new_data], ignore_index=True)
        st.rerun()

# --- PANTALLA PRINCIPAL: CABINA SCADA ---
t1, t2, t3, t4 = st.tabs(["📟 CABINA", "🧭 GEONAVEGACIÓN", "📚 MANUAL API", "🏁 EVALUACIÓN"])

with t1:
    # Gauges Estilo Martin-Decker
    hk, tq, sp, ec, rp, hl = calcular_fisica_cabina(s["md"], s["inc"], wob, rpm, flow, mw, s["health"])
    
    col_g1, col_g2, col_g3 = st.columns(3)
    
    # Peso (HKLD)
    fig_hk = go.Figure(go.Indicator(mode="gauge+number", value=hk, title={'text': "HOOK LOAD (Klbs)"},
                                   gauge={'axis': {'range': [0, 300]}, 'bar': {'color': "#00ffcc"}}))
    col_g1.plotly_chart(fig_hk, use_container_width=True)
    
    # Torque
    fig_tq = go.Figure(go.Indicator(mode="gauge+number", value=tq, title={'text': "TORQUE (ft-lb)"},
                                   gauge={'axis': {'range': [0, 50]}, 'bar': {'color': "#ffff00"}}))
    col_g2.plotly_chart(fig_tq, use_container_width=True)
    
    # Bombas (SPP)
    fig_sp = go.Figure(go.Indicator(mode="gauge+number", value=sp, title={'text': "SPP (PSI)"},
                                   gauge={'axis': {'range': [0, 5000]}, 'bar': {'color': "#00ffff"}}))
    col_g3.plotly_chart(fig_sp, use_container_width=True)

    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("BIT DEPTH", f"{s['md']:.1f} m")
    m2.metric("ROP", f"{rp:.1f} m/h")
    m3.metric("ECD", f"{ec:.2f} ppg")
    m4.metric("BIT HEALTH", f"{hl:.1f} %", delta=f"{hl-100:.1f}%")

with t2:
    st.subheader("🧭 Control de Geosteering (Trayectoria 3D)")
    if not s["history"].empty:
        fig_geo = make_subplots(rows=1, cols=2)
        fig_geo.add_trace(go.Scatter(x=s["history"]["GR"], y=s["history"]["MD"], name="Gamma Ray", line=dict(color="green")), 1, 1)
        fig_geo.add_trace(go.Scatter(x=s["history"]["ROP"], y=s["history"]["MD"], name="ROP", line=dict(color="orange")), 1, 2)
        fig_geo.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_geo, use_container_width=True)

with t3:
    st.header("📖 Biblioteca Técnica MENFA")
    with st.expander("📝 API RP 59: CONTROL DE POZOS"):
        st.write("Procedimiento de cierre rápido: 1. Espaciar, 2. Parar, 3. Cerrar, 4. Notificar.")
        st.latex(r"KMW = MW + \frac{SIDPP}{0.052 \cdot TVD}")
    with st.expander("🔧 API RP 7G: DISEÑO DE SARTAS"):
        st.write("Criterios de tracción, torque y fatiga en Drill Collars y HWDP.")

with t4:
    st.header("🏁 EXAMEN FINAL UTN")
    q1 = st.radio("¿Qué indica un aumento súbito de torque?", ["Falla de trépano o formación", "Falta de lodo"])
    q2 = st.radio("¿Fórmula de Presión Hidrostática?", ["0.052 * MW * TVD", "MW / 10"])
    
    if st.button("FINALIZAR Y GUARDAR"):
        nota = 20 if (q1.startswith("Falla") and q2.startswith("0.052")) else 0
        st.success(f"Nota registrada: {nota}/20")
        # Aquí llamarías a guardar_registro(s["user"], s["dni"], nota)
