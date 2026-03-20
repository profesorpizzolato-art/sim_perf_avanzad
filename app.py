import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.graph_objects as go
import time

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="SIMULADOR MENFA V6 - FULL", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #f4ecd8; color: #5d4037; }
    @keyframes blinker { 50% { opacity: 0; } }
    .alarm-kick { background-color: #d32f2f; padding: 20px; border-radius: 10px; border: 5px solid #fff; text-align: center; animation: blinker 1s linear infinite; color: white; margin-bottom: 20px; }
    .warning-pesca { background-color: #610000; padding: 15px; border-radius: 10px; text-align: center; color: #ffaa00; font-weight: bold; }
    .manual-box { background-color: #eaddca; padding: 15px; border-left: 5px solid #8b4513; font-family: 'Courier New', monospace; font-size: 0.9em; }
    .target-reached { background-color: #2e7d32; padding: 30px; border-radius: 15px; text-align: center; color: white; border: 4px double #ffd700; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. INICIALIZACIÓN DE VARIABLES ---
if "auth" not in st.session_state: st.session_state.auth = False
if "kick_alert" not in st.session_state: st.session_state.kick_alert = False
if "vida_sarta" not in st.session_state: st.session_state.vida_sarta = 100.0 
if "pesca_activa" not in st.session_state: st.session_state.pesca_activa = False
if "target_met" not in st.session_state: st.session_state.target_met = False
if "densidad_lodo" not in st.session_state: st.session_state.densidad_lodo = 1.15
if "presion_anular" not in st.session_state: st.session_state.presion_anular = 0
if "kicks_recibidos" not in st.session_state: st.session_state.kicks_recibidos = 0
if "sartas_rotas" not in st.session_state: st.session_state.sartas_rotas = 0

TARGET_DEPTH = 3000.0

if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame([{
        "DEPTH": 2500.0, "WOB": 20.0, "RPM": 100, "TORQUE": 8000, 
        "SPP": 2800, "ROP": 12.0, "GR": 110, "TANQUES": 1200, "DENS": 1.15
    }])

# --- 3. LOGIN ---
if not st.session_state.auth:
    st.title("🛡️ IPCL MENFA - MENDOZA")
    st.subheader("Simulador Técnico de Perforación v6.0")
    with st.form("login_form"):
        u = st.text_input("Nombre del Operador:")
        l = st.text_input("Legajo:")
        if st.form_submit_button("INGRESAR A CABINA"):
            if u:
                st.session_state.usuario = u
                st.session_state.auth = True
                st.rerun()
    st.stop()

# --- 4. LÓGICA DE SIMULACIÓN (SIDEBAR) ---
curr = st.session_state.history.iloc[-1]

with st.sidebar:
    st.header(f"Op: {st.session_state.usuario}")
    st.divider()
    wob = st.slider("WOB (klbs)", 0, 60, int(curr['WOB']))
    rpm = st.slider("RPM", 0, 180, int(curr['RPM']))
    
    if st.button("⏩ AVANZAR 200 METROS", use_container_width=True):
        if not st.session_state.pesca_activa and not st.session_state.target_met:
            # Desgaste
            st.session_state.vida_sarta -= (wob * 0.22)
            if st.session_state.vida_sarta <= 0:
                st.session_state.pesca_activa = True
                st.session_state.sartas_rotas += 1
                st.session_state.vida_sarta = 0
            
            # Profundidad
            n_prof = curr['DEPTH'] + 1.0
            if n_prof >= TARGET_DEPTH: st.session_state.target_met = True
            
            # Gamma Ray (Lógica de reservorio)
            gr = random.randint(25, 45) if 2850 < n_prof < 2950 else random.randint(85, 125)
            
            # Lógica de Kick
            tanques = curr['TANQUES']
            if random.random() < 0.08 and not st.session_state.kick_alert:
                st.session_state.kick_alert = True
                st.session_state.kicks_recibidos += 1
                tanques += 45
                st.session_state.presion_anular = random.randint(400, 850)

            nueva_fila = {
                "DEPTH": n_prof, "WOB": wob, "RPM": rpm,
                "TORQUE": (wob * 310) + random.randint(-50, 50),
                "SPP": 2800 + (wob * 2), "ROP": (wob * rpm) / 450, 
                "GR": gr, "TANQUES": tanques, "DENS": st.session_state.densidad_lodo
            }
            st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([nueva_fila])], ignore_index=True)
            st.rerun()
    
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.clear()
        st.rerun()

# --- 5. CUERPO PRINCIPAL ---

# Alertas Críticas
if st.session_state.kick_alert:
    st.markdown('<div class="alarm-kick"><h1>🚨 KICK ACTIVO</h1><p>SURGENCIA EN TANQUES - CIERRE BOP</p></div>', unsafe_allow_html=True)
if st.session_state.pesca_activa:
    st.markdown('<div class="warning-pesca">⚠️ SARTA ROTA POR SOBREPESO. REALICE MANIOBRA DE PESCA.</div>', unsafe_allow_html=True)
if st.session_state.target_met:
    st.markdown('<div class="target-reached"><h1>🎯 OBJETIVO LOGRADO</h1><p>Pozo terminado a 3000m. Genere el reporte.</p></div>', unsafe_allow_html=True)

tabs = st.tabs(["📊 SCADA", "🧪 LODOS", "🛡️ WELL CONTROL", "🔩 SARTA & PESCA", "📈 GEOLOGÍA", "📖 MANUAL & EVAL"])

with tabs[0]: # SCADA
    st.title("Monitor en Tiempo Real")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Profundidad", f"{curr['DEPTH']} m")
    c2.metric("WOB", f"{curr['WOB']} klbs")
    c3.metric("ROP", f"{round(curr['ROP'], 1)} m/h")
    c4.metric("DENSIDAD", f"{curr['DENS']} SG")
    st.subheader("Historial de Perforación")
    st.dataframe(st.session_state.history.tail(10), use_container_width=True)

with tabs[1]: # LODOS
    st.title("🧪 Sistema de Lodos")
    st.info(f"Presión Hidrostática Estimada: {round(curr['DEPTH'] * 1.422 * st.session_state.densidad_lodo / 10, 0)} psi")
    st.write("Ajuste de Densidad para controlar el pozo:")
    nueva_dens = st.number_input("Densidad (SG)", 1.0, 2.0, st.session_state.densidad_lodo, step=0.01)
    if st.button("Aplicar Nuevo Lodo"):
        st.session_state.densidad_lodo = nueva_dens
        st.success("Lodo pesado en circulación...")

with tabs[2]: # WELL CONTROL
    st.title("🛡️ Panel BOP")
    if st.session_state.kick_alert:
        col_b1, col_b2 = st.columns(2)
        col_b1.metric("SIDP (Presión Interna)", "420 psi")
        col_b2.metric("SICP (Presión Anular)", f"{st.session_state.presion_anular} psi")
        if st.button("🔒 CERRAR BOP ANULAR", type="primary", use_container_width=True):
            st.session_state.kick_alert = False
            st.session_state.presion_anular = 0
            st.balloons()
            st.success("Surgencia controlada.")
    else:
        st.success("Presiones estables. No se detecta flujo.")

with tabs[3]: # SARTA & PESCA
    st.title("🔩 Integridad Mecánica")
    st.metric("Vida Útil Sarta", f"{round(st.session_state.vida_sarta, 1)}%")
    st.progress(max(0.0, st.session_state.vida_sarta / 100))
    if st.session_state.pesca_activa:
        tension = st.number_input("Tensión de Overshot (klbs)", 0, 300, 100)
        if st.button("🎣 INTENTAR PESCA"):
            if tension > 220:
                st.session_state.pesca_activa = False
                st.session_state.vida_sarta = 100
                st.success("¡Pez recuperado! Sarta nueva instalada.")
                st.rerun()
            else: st.warning("Tensión insuficiente para liberar el pez.")
    else:
        if st.button("Mantenimiento de BHA"):
            st.session_state.vida_sarta = 100
            st.rerun()

with tabs[4]: # GEOLOGÍA
    st.title("📈 Gráfico de Perforación (Gamma Ray)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=st.session_state.history['GR'], y=st.session_state.history['DEPTH'], mode='lines', line=dict(color='#8B4513')))
    fig.update_layout(yaxis=dict(autorange="reversed", title="Depth (m)"), xaxis=dict(title="GR (API)"), template="simple_white")
    st.plotly_chart(fig, use_container_width=True)

with tabs[5]: # MANUAL & EVALUACIÓN
    st.title("Evaluación del Operador")
    st.markdown("""
    <div class="manual-box">
    <b>REGLAS DEL SIMULADOR:</b><br>
    - No exceder los 45 klbs de WOB.<br>
    - El reservorio se encuentra por debajo de los 2850m.<br>
    - Si hay Kick, cerrar el pozo inmediatamente.
    </div>
    """, unsafe_allow_html=True)
    
    # Lógica de Puntaje
    score = 100 - (st.session_state.kicks_recibidos * 15) - (st.session_state.sartas_rotas * 30)
    st.metric("PUNTAJE FINAL", f"{max(0, score)}/100")
    
    st.download_button(
        label="📥 DESCARGAR REPORTE EXAMEN",
        data=st.session_state.history.to_csv(index=False),
        file_name=f"Evaluacion_{st.session_state.usuario}.csv",
        mime="text/csv"
    )
    import os

# --- FUNCIÓN DE AUTOGUARDADO EN CARPETA LOCAL ---
def guardar_examen_local(df_historial, nombre_alumno, nro_legajo):
    # Creamos la carpeta si no existe
    carpeta = "EXAMENES_MENFA"
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)
    
    # Nombre del archivo con Legajo y Fecha/Hora para que no se pisen
    timestamp = time.strftime("%Y%m%d-%H%M")
    nombre_archivo = f"{carpeta}/Examen_{nro_legajo}_{nombre_alumno}_{timestamp}.csv"
    
    # Guardamos el CSV
    df_historial.to_csv(nombre_archivo, index=False)
    return nombre_archivo

# --- DENTRO DE LA PESTAÑA DE EVALUACIÓN (TAB 5) ---
with tabs[5]:
    st.title("Finalizar y Entregar Evaluación")
    st.warning("Al presionar el botón, su desempeño se guardará en el servidor local de IPCL MENFA.")
    
    if st.button("🏁 FINALIZAR TURNO Y GUARDAR EXAMEN", type="primary", use_container_width=True):
        if not st.session_state.history.empty:
            ruta = guardar_examen_local(
                st.session_state.history, 
                st.session_state.usuario, 
                st.session_state.legajo
            )
            st.success(f"✅ ¡Examen Guardado! Archivo: {ruta}")
            st.balloons()
            # Bloqueamos para que no sigan tocando
            st.session_state.target_met = True 
        else:
            st.error("No hay datos de perforación para guardar.")

    st.divider()
    st.info("Nota: Una vez guardado, el instructor Fabricio revisará su ROP promedio y el control de Kicks.")
