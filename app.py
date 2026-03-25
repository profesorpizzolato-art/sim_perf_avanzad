import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random

# --- 1. CONFIGURACIÓN DE NORMAS Y FÓRMULAS ---
# Normas Referenciadas: API RP 59 (Well Control), API RP 7G (Sartas)
def calc_torque_drag(depth, inc, mud_weight):
    """Simulación de arrastre (Drag) basada en fricción y geometría."""
    ff = 0.25 # Coeficiente de fricción promedio
    drag = depth * 0.15 * np.sin(np.radians(inc)) * ff
    torque = depth * 0.08 * ff
    return drag, torque

def formula_hidraulica(flow_rate, mw, bit_size):
    """Cálculo de HSI (Horsepower per Square Inch) en el trépano."""
    hsi = (flow_rate**3 * mw) / (10000 * bit_size**2)
    return hsi

# --- 2. BASE DE DATOS GEOLÓGICA PREVIA (PROGNOSIS) ---
prognosis = {
    "Formación": ["Post-Cuyo", "Lajas", "Punta Rosada", "Vaca Muerta"],
    "Tope (m)": [0, 1500, 2200, 2800],
    "Presión Poro (ppg)": [8.5, 9.2, 10.5, 12.5],
    "Litología": ["Areniscas", "Arcillas", "Arenas compactas", "Black Shale"]
}

# --- 3. INTERFAZ PRINCIPAL ---
st.set_page_config(page_title="MENFA - Simulador Integral", layout="wide")

# Inicialización de la sarta y trépano
if "sarta" not in st.session_state:
    st.session_state.sarta = {"tipo_bit": "PDC 8-1/2", "n_jets": 3, "tfa": 0.44}

# --- 4. CABINA DEL PERFORADOR (SCADA REAL-TIME) ---
with st.sidebar:
    st.title("🕹️ MANDOS DE CABINA")
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Logo_UTN.svg/1200px-Logo_UTN.svg.png", width=100)
    
    modo = st.radio("MODO DE TRABAJO:", ["PROGNOSIS", "PERFORACIÓN", "GEONAVEGACIÓN", "WELL CONTROL", "MANUAL & EVALUACIÓN"])
    
    st.divider()
    wob = st.slider("WOB (klbs)", 0, 60, 25)
    rpm = st.slider("RPM", 0, 150, 90)
    flow = st.slider("Flow Rate (GPM)", 300, 1200, 500)
    mw = st.number_input("Densidad Lodo (ppg)", 8.3, 18.0, 10.2)

# --- 5. LÓGICA POR MÓDULOS ---

if modo == "PROGNOSIS":
    st.header("🔍 Perfil Geológico Pre-Perforación")
    col1, col2 = st.columns(2)
    col1.table(pd.DataFrame(prognosis))
    
    # Gráfico de Ventana Operativa
    fig_win = go.Figure()
    depths = np.linspace(0, 3500, 50)
    fig_win.add_trace(go.Scatter(x=[8.5]*50, y=depths, name="Poro", fill='toself'))
    fig_win.add_trace(go.Scatter(x=[14.0]*50, y=depths, name="Fractura"))
    fig_win.update_yaxes(autorange="reversed", title="Profundidad (m)")
    st.plotly_chart(fig_win)

elif modo == "PERFORACIÓN":
    st.header("🏗️ Cabina de Operaciones - SCADA")
    
    # Métricas Críticas (Identical a un panel Martin-Decker)
    c1, c2, c3, c4 = st.columns(4)
    drag, torque = calc_torque_drag(3000, 45, mw)
    
    c1.metric("HOOK LOAD (klbs)", f"{180 - drag:.1f}", delta=f"-{drag:.1f} Drag")
    c2.metric("TORQUE (ft-lb)", f"{torque:.0f}")
    c3.metric("ROP (m/h)", f"{(wob * rpm / 500):.1f}")
    c4.metric("HSI (Toberas)", f"{formula_hidraulica(flow, mw, 8.5):.2f}")

    # Gauge de Presión de Bombas
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number", value = flow * 3.5,
        title = {'text': "SPP (Standpipe Pressure) psi"},
        gauge = {'axis': {'range': [0, 5000]}, 'steps': [{'range': [0, 3500], 'color': "green"}, {'range': [3500, 5000], 'color': "red"}]}
    ))
    st.plotly_chart(fig_gauge, use_container_width=True)

elif modo == "GEONAVEGACIÓN":
    st.header("🧭 Control de Trayectoria y Geosteering")
    # Gráfico de Target vs Real
    t_depth = np.linspace(2500, 3000, 20)
    target = np.sin(t_depth/100) * 50
    actual = np.sin(t_depth/105) * 45
    
    fig_geo = go.Figure()
    fig_geo.add_trace(go.Scatter(x=target, y=t_depth, name="Target Window", line=dict(dash='dash')))
    fig_geo.add_trace(go.Scatter(x=actual, y=t_depth, name="Bit Path", line=dict(color='lime', width=4)))
    fig_geo.update_yaxes(autorange="reversed")
    st.plotly_chart(fig_geo, use_container_width=True)

elif modo == "WELL CONTROL":
    st.header("🚨 Panel de Control de Pozos (BOP Stack)")
    st.error("SITUACIÓN: Aumento en volumen de tanques detectado (+15 bbl)")
    
    col1, col2 = st.columns(2)
    sidpp = col1.number_input("SIDPP (psi)", 0, 2000, 450)
    sicp = col2.number_input("SICP (psi)", 0, 2000, 620)
    
    if st.button("CALCULAR HOJA DE MATAR"):
        kill_mw = mw + (sidpp / (0.052 * 3000 * 3.28))
        st.write(f"### 🧪 Nueva Densidad de Ahogo: {kill_mw:.2f} ppg")
        st.info("Fórmula aplicada: KMW = Current MW + [SIDPP / (0.052 * TVD_ft)]")

elif modo == "MANUAL & EVALUACIÓN":
    st.header("📚 Manual Normativo y Examen Final")
    
    with st.expander("📖 Ver Manual de Procedimientos (Normas API)"):
        st.write("""
        * **API RP 59:** Prácticas recomendadas para el control de pozos.
        * **Normas IRAM:** Seguridad en equipos de perforación terrestre.
        * **Cálculo de Torque:** $T = K \cdot WOB \cdot D_{bit}$
        """)
        
    st.divider()
    st.subheader("📝 Evaluación Integradora IPCL MENFA")
    p1 = st.radio("1. ¿Qué parámetro indica una falla inminente en la sarta?", ["Aumento repentino de Torque", "Baja de ROP", "Cambio de color en el lodo"])
    p2 = st.radio("2. Si el SIDPP es > 0, ¿qué significa?", ["Pozo en equilibrio", "Presión de fondo < Presión de formación", "Sarta cortada"])
    
    if st.button("ENVIAR Y GENERAR CERTIFICADO"):
        if p1 == "Aumento repentino de Torque" and p2 == "Presión de fondo < Presión de formación":
            st.success(f"Excelente Fabricio. Certificado UTN/MENFA disponible para descarga.")
        else:
            st.error("Revisar conceptos de Well Control.")
