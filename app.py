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
