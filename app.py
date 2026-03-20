import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.graph_objects as go
from fpdf import FPDF
import datetime
import os
import time

# --- 1. CONFIGURACIÓN E IDENTIDAD ---
st.set_page_config(page_title="SIMULADOR MENFA V7.6 - FULL ESTRENO", layout="wide")

# --- 2. INICIALIZACIÓN CRÍTICA (Evita el AttributeError) ---
if "auth" not in st.session_state: st.session_state.auth = False
if "usuario" not in st.session_state: st.session_state.usuario = ""
if "legajo" not in st.session_state: st.session_state.legajo = ""
if "kick_alert" not in st.session_state: st.session_state.kick_alert = False
if "vida_sarta" not in st.session_state: st.session_state.vida_sarta = 100.0
if "pesca_activa" not in st.session_state: st.session_state.pesca_activa = False
if "densidad_lodo" not in st.session_state: st.session_state.densidad_lodo = 1.15
if "presion_anular" not in st.session_state: st.session_state.presion_anular = 0

if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame([{
        "DEPTH": 2500.0, "WOB": 20.0, "RPM": 100, "ROP": 0.0, "GR": 110, "TANQUES": 1200, "DENS": 1.15
    }])

# --- 3. LOGIN DE ESTRENO (DNI LIBRE) ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #003366;'>🛡️ IPCL MENFA - MENDOZA</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Ingreso a Examen de Perforación</h3>", unsafe_allow_html=True)
    with st.container():
        c1, c2, c3 = st.columns([1,1.5,1])
        with c2:
            st.info("⚠️ Complete sus datos para el Certificado Oficial.")
            u_reg = st.text_input("Nombre y Apellido del Alumno:")
            l_reg = st.text_input("DNI o Legajo:")
            if st.button("INGRESAR A CABINA", use_container_width=True):
                if u_reg and l_reg:
                    st.session_state.usuario = u_reg
                    st.session_state.legajo = l_reg
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.warning("Complete ambos campos.")
    st.stop()

# --- 4. LÓGICA DE SIMULACIÓN (SIDEBAR) ---
curr = st.session_state.history.iloc[-1]
with st.sidebar:
    st.header(f"Op: {st.session_state.usuario}")
    st.divider()
    wob = st.slider("WOB (klbs)", 0, 60, int(curr['WOB']))
    rpm = st.slider("RPM", 0, 180, int(curr['RPM']))
    
    if st.button("⏩ PERFORAR 500 METROS", use_container_width=True):
        if not st.session_state.pesca_activa:
            # Desgaste y Profundidad
            st.session_state.vida_sarta -= (wob * 0.2)
            if st.session_state.vida_sarta <= 0: st.session_state.pesca_activa = True
            
            n_prof = curr['DEPTH'] + 1.0
            gr = random.randint(25, 45) if 2850 < n_prof < 2950 else random.randint(85, 125)
            
            # Lógica de Kick
            tanques = curr['TANQUES']
            if random.random() < 0.07 and not st.session_state.kick_alert:
                st.session_state.kick_alert = True
                tanques += 50
                st.session_state.presion_anular = random.randint(400, 800)

            nueva_fila = {
                "DEPTH": n_prof, "WOB": wob, "RPM": rpm,
                "ROP": (wob * rpm) / 450, "GR": gr, 
                "TANQUES": tanques, "DENS": st.session_state.densidad_lodo
            }
            st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([nueva_fila])], ignore_index=True)
            st.rerun()

# --- 5. CUERPO PRINCIPAL (TABS) ---
if st.session_state.kick_alert:
    st.error("🚨 ¡KICK DETECTADO! SURGENCIA EN TANQUES. CIERRE BOP.")

tabs = st.tabs(["📊 SCADA", "🧪 LODOS", "🛡️ WELL CONTROL", "🔩 SARTA & PESCA", "📈 GEOLOGÍA", "📖 EVALUACIÓN"])

with tabs[0]: # SCADA
    c1, c2, c3 = st.columns(3)
    c1.metric("Profundidad", f"{curr['DEPTH']} m")
    c2.metric("WOB", f"{curr['WOB']} klbs")
    c3.metric("ROP", f"{round(curr['ROP'], 1)} m/h")
    st.dataframe(st.session_state.history.tail(5), use_container_width=True)

with tabs[1]: # LODOS
    st.subheader("Sistema de Circulación")
    n_dens = st.number_input("Ajustar Densidad (SG)", 1.0, 2.0, st.session_state.densidad_lodo, step=0.01)
    if st.button("Bombear Lodo Nuevo"):
        st.session_state.densidad_lodo = n_dens
        st.success("Densidad actualizada en el pozo.")

with tabs[2]: # WELL CONTROL
    st.subheader("Panel de Control de Surgencias")
    if st.session_state.kick_alert:
        st.metric("SICP (Anular)", f"{st.session_state.presion_anular} psi")
        if st.button("🔒 CERRAR BOP ANULAR", type="primary"):
            st.session_state.kick_alert = False
            st.success("Pozo Cerrado y Controlado.")
    else:
        st.success("Presiones en equilibrio.")

with tabs[3]: # SARTA & PESCA
    st.subheader("Estado de la Herramienta")
    st.progress(max(0.0, st.session_state.vida_sarta / 100))
    if st.session_state.pesca_activa:
        st.warning("SARTA CORTADA. Realice maniobra de pesca.")
        if st.button("🎣 BAJAR OVERSHOT"):
            st.session_state.pesca_activa = False
            st.session_state.vida_sarta = 100
            st.rerun()

with tabs[4]: # GEOLOGÍA
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=st.session_state.history['GR'], y=st.session_state.history['DEPTH']))
    fig.update_layout(yaxis=dict(autorange="reversed", title="Profundidad"), xaxis=dict(title="Gamma Ray (API)"))
    st.plotly_chart(fig, use_container_width=True)
with tabs[4]: # MANUAL DE OPERACIONES (Antes de Evaluación)
    st.header("📖 Manual de Procedimientos - IPCL MENFA")
    
    col_m1, col_m2 = st.columns(2)
    
    with col_m1:
        st.subheader("🛠️ Parámetros de Perforación")
        st.write("""
        * **WOB (Weight on Bit):** Es el peso que aplicás al trépano. 
            * *Rango Seguro:* 10 a 40 klbs.
            * *Peligro:* Superar los 50 klbs puede producir fatiga y **Corte de Sarta**.
        * **RPM (Revoluciones):** Velocidad de rotación.
            * *Rango Óptimo:* 60 a 120 RPM.
        * **ROP (Rate of Penetration):** Velocidad de avance. Se calcula automáticamente según tu eficiencia.
        """)
        
    with col_m2:
        st.subheader("🛡️ Control de Pozos (Well Control)")
        st.warning("**Protocolo ante KICK (Surgencia):**")
        st.write("""
        1. **Detección:** Si el volumen de los tanques sube repentinamente o el pozo fluye con bombas apagadas.
        2. **Acción:** Ir a la pestaña **WELL CONTROL**.
        3. **Cierre:** Presionar el botón **CERRAR BOP**. 
        4. **Estabilización:** Ajustar la densidad del lodo en la pestaña **LODOS** antes de reabrir.
        """)

    st.divider()
    
    st.subheader("📉 Interpretación Geológica (Gamma Ray)")
    st.info("El gráfico de Gamma Ray te indica qué formación estás atravesando.")
    st.write("""
    * **Valores Altos (>80 API):** Arcillas (Shales). Formaciones impermeables.
    * **Valores Bajos (<40 API):** Areniscas (Sandstones). ¡Posible reservorio! Prestá atención cuando la profundidad supere los 2800 metros.
    """)
    
    st.success("💡 **Consejo del Instructor Fabricio:** No perfores " + 
               "a ciegas. Mirá siempre los tanques; el pozo te habla a través de los niveles.")
with tabs[5]: # EVALUACIÓN
    st.subheader("Finalizar Capacitación")
    if st.button("🏁 GUARDAR Y FINALIZAR"):
        if not os.path.exists("EXAMENES_MENFA"): os.makedirs("EXAMENES_MENFA")
        st.session_state.history.to_csv(f"EXAMENES_MENFA/Examen_{st.session_state.legajo}.csv", index=False)
        st.balloons()
        st.success("Examen guardado. Solicite su certificado al Inst. Fabricio.")
