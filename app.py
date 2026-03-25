import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from fpdf import FPDF
from datetime import datetime
import time
import random

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="IPCL MENFA V13 - SISTEMA INTEGRAL", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050505; color: #E0E0E0; }
    .stMetric { background-color: #111; border: 1px solid #00FFCC; padding: 15px; border-radius: 10px; border-left: 5px solid #00FFCC; }
    [data-testid="stMetricValue"] { color: #00FFCC; font-family: 'Courier New'; font-weight: bold; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #00FFCC; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. INICIALIZACIÓN DE ESTADOS (SESSION STATE) ---
if "auth" not in st.session_state:
    st.session_state.update({
        "auth": False, "usuario": "", "legajo": "", "aprobado": False,
        "md": 2500.0, "tvd": 2500.0, "inc": 0.0, "vs": 0.0,
        "vida_sarta": 100.0, "kick_alert": False, "pesca_activa": False,
        "history": pd.DataFrame([{
            "DEPTH": 2500.0, "WOB": 20.0, "RPM": 100, "ROP": 0.0, "GR": 110, "ILD": 2.0, "RHOB": 2.4, "MW": 10.5
        }]),
        "eventos": []
    })

# --- 3. FUNCIONES DE SOPORTE ---

def generar_pdf(nombre, dni, prof, historia_eventos):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.rect(10, 10, 277, 190)
    pdf.set_font('Arial', 'B', 30)
    pdf.cell(0, 40, 'CERTIFICADO DE COMPETENCIA OPERATIVA', ln=True, align='C')
    pdf.set_font('Arial', '', 18)
    pdf.cell(0, 10, f'IPCL MENFA Mendoza certifica que el profesional:', ln=True, align='C')
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 25)
    pdf.cell(0, 20, nombre.upper(), ln=True, align='C')
    pdf.set_font('Arial', '', 14)
    pdf.cell(0, 10, f'DNI/Legajo: {dni} | Profundidad Final: {prof} m', ln=True, align='C')
    pdf.ln(10)
    pdf.set_font('Arial', 'I', 12)
    cuerpo = "Aprobó el examen técnico y operó exitosamente el Simulador MENFA V13 (Drilling & Well Control)."
    pdf.multi_cell(0, 10, cuerpo, align='C')
    pdf.cell(0, 20, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1')

def calcular_perforacion(wob, rpm, mw):
    curr = st.session_state.history.iloc[-1]
    n_md = curr['DEPTH'] + random.uniform(5, 15)
    
    # Lógica de Inclinación (KOP a los 2800m)
    inc_nueva = st.session_state.inc
    if n_md > 2800:
        inc_nueva += (3.0 * (n_md - curr['DEPTH']) / 30) # Build up rate
    
    rad = np.radians(inc_nueva)
    st.session_state.tvd += (n_md - curr['DEPTH']) * np.cos(rad)
    st.session_state.vs += (n_md - curr['DEPTH']) * np.sin(rad)
    st.session_state.inc = inc_nueva
    st.session_state.md = n_md

    # Geofísica Sintética
    gr = random.randint(20, 45) if 2850 < n_md < 2950 else random.randint(80, 130)
    ild = random.uniform(50, 200) if gr < 50 else random.uniform(1, 5)
    rhob = random.uniform(2.1, 2.3) if gr < 50 else random.uniform(2.4, 2.6)

    # Lógica de Alarmas
    if random.random() < 0.12: st.session_state.kick_alert = True
    
    nueva_data = {
        "DEPTH": n_md, "WOB": wob, "RPM": rpm, "ROP": (wob * rpm) / 450,
        "GR": gr, "ILD": ild, "RHOB": rhob, "MW": mw
    }
    st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([nueva_data])], ignore_index=True)

# --- 4. FLUJO DE PANTALLAS ---

# PANTALLA A: LOGIN
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #00FFCC;'>🛡️ IPCL MENFA - ACCESO AL SISTEMA</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1, 1])
    with col:
        u = st.text_input("Nombre del Operador:")
        l = st.text_input("DNI / Legajo:")
        if st.button("INICIAR SESIÓN"):
            if u and l:
                st.session_state.usuario, st.session_state.legajo, st.session_state.auth = u, l, True
                st.rerun()
    st.stop()

# PANTALLA B: EXAMEN TÉCNICO (Solo si no está aprobado)
if not st.session_state.aprobado:
    st.header(f"📝 Examen de Certificación - Operador: {st.session_state.usuario}")
    st.info("Debe responder correctamente al menos 16 de 20 preguntas (80%).")
    
    preguntas = [
        ("¿Método de cálculo direccional con 0% error?", ["Tangencial", "Mínima Curvatura"], "Mínima Curvatura"),
        ("¿Espera recomendada para reset de MWD?", ["30s", "90s"], "90s"),
        ("¿Qué significan las siglas MWD?", ["Measuring While Drilling", "Mechanical Weight"], "Measuring While Drilling"),
        ("¿Ubicación del Punto Neutro en la sarta?", ["DP", "DC (Portamechas)"], "DC (Portamechas)"),
        ("¿Fórmula del Factor de Flotación?", ["1 - (MW/65.5)", "MW * 0.052"], "1 - (MW/65.5)"),
        ("¿Función principal del Zapato Flotador?", ["Válvula check y flotación", "Corte de roca"], "Válvula check y flotación"),
        ("¿Qué es el KOP?", ["Inicio de desvío", "Fin de pozo"], "Inicio de desvío"),
        ("¿Protocolo inmediato ante un Kick?", ["Aumentar RPM", "Cerrar BOP"], "Cerrar BOP"),
        ("¿Densidad del agua dulce en ppg?", ["8.33", "1.0"], "8.33"),
        ("¿Qué propiedad evita el asentamiento de recortes?", ["Gel", "Filtrado"], "Gel")
    ] # (Se pueden añadir las 20 siguiendo este formato)
    
    score = 0
    for i, (p, opts, r) in enumerate(preguntas):
        res = st.radio(f"{i+1}. {p}", opts, key=f"q{i}")
        if res == r: score += 1

    if st.button("VALIDAR COMPETENCIAS"):
        if score >= 8: # Ajustado para el ejemplo de 10 preguntas
            st.session_state.aprobado = True
            st.success(f"Aprobado con {score} aciertos. Desbloqueando Consola...")
            time.sleep(1)
            st.rerun()
        else:
            st.error(f"Puntaje insuficiente ({score}). Repase el material de IPCL MENFA.")
    st.stop()

# PANTALLA C: SIMULADOR SCADA (Principal)
curr = st.session_state.history.iloc[-1]

# Sidebar de Control
with st.sidebar:
    st.title("🕹️ CONSOLA")
    st.write(f"Operador: **{st.session_state.usuario}**")
    wob_in = st.slider("WOB (klbs)", 0, 60, int(curr['WOB']))
    rpm_in = st.slider("RPM", 0, 180, int(curr['RPM']))
    mw_in = st.number_input("Mud Weight (ppg)", 8.3, 16.0, float(curr['MW']))
    
    if st.button("⏩ AVANZAR PERFORACIÓN"):
        if not st.session_state.kick_alert:
            calcular_perforacion(wob_in, rpm_in, mw_in)
            st.rerun()

    st.divider()
    if st.button("🚪 CERRAR SESIÓN"):
        st.session_state.clear()
        st.rerun()

# Layout Principal
if st.session_state.kick_alert:
    st.error("🚨 KICK DETECTADO: ¡GANANCIA EN TANQUES! CIERRE EL BOP DE INMEDIATO.")

t1, t2, t3, t4 = st.tabs(["📊 SCADA & KPI", "📈 GEOFÍSICA (LAS)", "🛡️ WELL CONTROL", "📄 REPORTES"])

with t1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("DEPTH (MD)", f"{curr['DEPTH']:.1f} m")
    c2.metric("INC", f"{st.session_state.inc:.2f} °")
    c3.metric("ROP", f"{curr['ROP']:.1f} m/h")
    c4.metric("MW", f"{curr['MW']} ppg")

    # Gráfico Trayectoria 3D
    fig_3d = go.Figure(data=[go.Scatter3d(
        x=st.session_state.history.index, y=[0]*len(st.session_state.history), z=-st.session_state.history['DEPTH'],
        mode='lines+markers', line=dict(color='#00FFCC', width=4)
    )])
    fig_3d.update_layout(title="Trayectoria del Pozo", height=500, template="plotly_dark")
    st.plotly_chart(fig_3d, use_container_width=True)

with t2:
    st.subheader("Visualizador de Perfiles (Log Tracks)")
    df = st.session_state.history
    fig_logs = make_subplots(rows=1, cols=3, shared_yaxes=True, subplot_titles=('Litología (GR)', 'Resistividad', 'Densidad'))
    
    fig_logs.add_trace(go.Scatter(x=df['GR'], y=df['DEPTH'], name='GR', line=dict(color='green')), row=1, col=1)
    fig_logs.add_trace(go.Scatter(x=df['ILD'], y=df['DEPTH'], name='Res', line=dict(color='red')), row=1, col=2)
    fig_logs.add_trace(go.Scatter(x=df['RHOB'], y=df['DEPTH'], name='Dens', line=dict(color='black')), row=1, col=3)
    
    fig_logs.update_yaxes(autorange="reversed", title="Profundidad (m)")
    fig_logs.update_xaxes(row=1, col=2, type="log")
    fig_logs.update_layout(height=600, template="plotly_white")
    st.plotly_chart(fig_logs, use_container_width=True)

with t3:
    st.subheader("Panel de Preventores (BOP)")
    if st.session_state.kick_alert:
        st.warning("⚠️ Presión en el Anular detectada.")
        if st.button("🔒 ACTIVAR CIERRE DE EMERGENCIA (BOP)"):
            st.session_state.kick_alert = False
            st.session_state.eventos.append(f"{datetime.now().strftime('%H:%M')} - Kick controlado exitosamente.")
            st.success("Pozo Cerrado. Presiones estabilizadas.")
    else:
        st.success("Presión de fondo en equilibrio hidrostático.")

with t4:
    st.subheader("Generación de Documentación IPCL")
    if st.button("🎓 FINALIZAR Y GENERAR CERTIFICADO"):
        pdf_bytes = generar_pdf(st.session_state.usuario, st.session_state.legajo, curr['DEPTH'], st.session_state.eventos)
        st.download_button("⬇️ DESCARGAR PDF OFICIAL", pdf_bytes, f"Certificado_{st.session_state.legajo}.pdf", "application/pdf")
        st.balloons()

