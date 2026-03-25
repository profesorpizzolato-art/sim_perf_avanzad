import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- CONFIGURACIÓN DE PANTALLA INDUSTRIAL ---
st.set_page_config(page_title="MENFA CYBERBASE V16", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #05070a; color: #00ffcc; }
    .stMetric { background-color: #10141b; border: 2px solid #1f2937; border-radius: 10px; padding: 20px; }
    [data-testid="stMetricValue"] { color: #ffffff; font-family: 'Segment7', 'Courier New'; font-size: 2.5rem; }
    .stSlider { color: #00ffcc; }
    .stButton>button { background: linear-gradient(135deg, #00ffcc 0%, #008b8b 100%); color: black; font-weight: bold; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE CÁLCULO (FÍSICA DE PERFORACIÓN) ---
def simular_parametros(wob, rpm, flow, mw, depth):
    # Relaciones matemáticas reales (Torque, Drag, ROP)
    torque = (wob * 0.15) + (rpm * 0.05) + (depth * 0.001)
    drag = depth * 0.02 # Arrastre por fricción
    hook_load = 250 - drag - wob
    spp = (flow**1.8) * 0.02 # Stand Pipe Pressure (psi)
    rop = (wob * rpm) / 400
    return hook_load, torque, spp, rop

# --- ESTADO INICIAL ---
if "log" not in st.session_state:
    st.session_state.log = pd.DataFrame(columns=["MD", "HKLD", "TORQUE", "SPP", "ROP"])

# --- INTERFAZ: CABINA DEL PERFORADOR ---
st.title("📟 PANEL DE CONTROL INTEGRAL - IPCL MENFA")

# FILA 1: INDICADORES ANÁLOGOS (Gauges estilo Martin-Decker)
col_g1, col_g2, col_g3 = st.columns(3)

# Inputs de control (Sliders simulando palancas de la cabina)
with st.sidebar:
    st.header("🎛️ MANDOS DE LA TORRE")
    wob_in = st.slider("WOB (klbs) - Peso sobre trépano", 0, 80, 25)
    rpm_in = st.slider("RPM - Mesa Rotaria / Top Drive", 0, 200, 100)
    st.divider()
    st.header("💧 CONTROL DE LODOS")
    flow_in = st.slider("GPM - Caudal de Bombas", 200, 1200, 600)
    mw_in = st.number_input("MW (ppg) - Densidad", 8.3, 18.0, 10.5)
    
    st.divider()
    if st.button("🚀 INICIAR PERFORACIÓN (TRAMO 30m)"):
        st.toast("Perforando... monitorear presiones.")

# Lógica de cálculo
hkld, torq, spp, rop = simular_parametros(wob_in, rpm_in, flow_in, mw_in, 3200)

with col_g1:
    fig_hkld = go.Figure(go.Indicator(
        mode = "gauge+number", value = hkld,
        title = {'text': "HOOK LOAD (klbs)", 'font': {'size': 20, 'color': "#00ffcc"}},
        gauge = {'axis': {'range': [0, 300], 'tickwidth': 2}, 'bar': {'color': "#00ffcc"},
                 'steps': [{'range': [0, 50], 'color': "red"}, {'range': [250, 300], 'color': "red"}]}
    ))
    fig_hkld.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=350)
    st.plotly_chart(fig_hkld, use_container_width=True)

with col_g2:
    fig_torq = go.Figure(go.Indicator(
        mode = "gauge+number", value = torq,
        title = {'text': "TORQUE (ft-lb)", 'font': {'size': 20, 'color': "#ffff00"}},
        gauge = {'axis': {'range': [0, 50], 'tickwidth': 2}, 'bar': {'color': "#ffff00"},
                 'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 45}}
    ))
    fig_torq.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=350)
    st.plotly_chart(fig_torq, use_container_width=True)

with col_g3:
    fig_spp = go.Figure(go.Indicator(
        mode = "gauge+number", value = spp,
        title = {'text': "SPP (psi) - Bombas", 'font': {'size': 20, 'color': "#00ffff"}},
        gauge = {'axis': {'range': [0, 5000], 'tickwidth': 2}, 'bar': {'color': "#00ffff"}}
    ))
    fig_spp.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=350)
    st.plotly_chart(fig_spp, use_container_width=True)

# FILA 2: MÉTRICAS DIGITALES Y GEONAVEGACIÓN
st.divider()
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("ROP (m/h)", f"{rop:.1f}")
c2.metric("BIT DEPTH (m)", "3240.5")
c3.metric("TVD (m)", "3180.2")
c4.metric("D-EXPONENT", "1.24")
c5.metric("PUMP STROKES", f"{flow_in/8:.0f} SPM")

# FILA 3: GEOLOGÍA Y CONTROL DE POZOS
col_l, col_r = st.columns([2, 1])

with col_l:
    st.subheader("📈 Registros de Perforación (Real-Time Logs)")
    # Simulación de curvas geofísicas
    t = np.linspace(3200, 3240, 40)
    gr = 100 + np.random.randn(40) * 10
    res = 10** (np.random.rand(40) * 2)
    
    fig_logs = make_subplots(rows=1, cols=2, shared_yaxes=True)
    fig_logs.add_trace(go.Scatter(x=gr, y=t, name="Gamma Ray", line=dict(color="green")), 1, 1)
    fig_logs.add_trace(go.Scatter(x=res, y=t, name="Resistividad", line=dict(color="red")), 1, 2)
    fig_logs.update_yaxes(autorange="reversed")
    fig_logs.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)')
    st.plotly_chart(fig_logs, use_container_width=True)

with col_r:
    st.subheader("🚨 Panel de Seguridad")
    st.error("Nivel de Tanques: +5 bbl (Alerta)")
    if st.button("🔴 EMERGENCY SHUT DOWN"):
        st.warning("BOP Cerrado. Sistema Bloqueado.")
    
    with st.expander("🛠️ Detalles de la Sarta"):
        st.write("- **Trépano:** PDC 8-1/2' (Mendoza High-Impact)")
        st.write("- **BHA:** Motor de Fondo + MWD + LWD")
        st.write("- **Portamechas:** 6-1/4' x 90m")

# PIE DE PÁGINA PROFESIONAL
st.markdown("---")
st.caption("IPCL MENFA - Entrenamiento Técnico en Petróleo | UTN Mendoza 2026")
def render_martin_decker(hkld, torque, spp):
    col1, col2, col3 = st.columns(3)
    
    # Gauge de Peso en el Gancho
    fig_hk = go.Figure(go.Indicator(
        mode = "gauge+number", value = hkld,
        title = {'text': "HOOK LOAD (Klbs)"},
        gauge = {'axis': {'range': [0, 300]}, 'bar': {'color': "#00ffcc"}}))
    col1.plotly_chart(fig_hk, use_container_width=True)

    # Gauge de Torque (Crítico para evitar roturas)
    fig_tq = go.Figure(go.Indicator(
        mode = "gauge+number", value = torque,
        title = {'text': "TORQUE (ft-lb)"},
        gauge = {'axis': {'range': [0, 50]}, 'bar': {'color': "#ffff00"}}))
    col2.plotly_chart(fig_tq, use_container_width=True)

    # Gauge de Presión de Bombas (Standpipe)
    fig_sp = go.Figure(go.Indicator(
        mode = "gauge+number", value = spp,
        title = {'text': "SPP (PSI)"},
        gauge = {'axis': {'range': [0, 5000]}, 'bar': {'color': "#00ffff"}}))
    col3.plotly_chart(fig_sp, use_container_width=True)

with st.expander("💧 SISTEMA DE CIRCULACIÓN Y LODOS"):
    st.info("Parámetros de entrada de Bombas")
    st.number_input("Densidad Entrada (ppg)", 8.3, 18.0, 10.5, key="mw_in")
    st.number_input("Viscosidad Marsh (seg)", 30, 80, 45, key="visco")
    st.progress(0.65, text="Nivel de Tanques: 650 bbl")

def graficar_geonavegacion(profundidad, desviacion):
    st.subheader("🧭 Panel de Geonavegación")
    # Genera una ventana de target (límites de la formación)
    target_top = [20, 22, 18, 25, 23]
    target_base = [-20, -18, -22, -15, -17]
    pos_trepano = [desviacion] * 5
    
    fig_nav = go.Figure()
    fig_nav.add_trace(go.Scatter(y=target_top, name="Tope Formación", line=dict(color='gray', dash='dash')))
    fig_nav.add_trace(go.Scatter(y=target_base, name="Base Formación", fill='tonexty', fillcolor='rgba(0,255,0,0.1)'))
    fig_nav.add_trace(go.Scatter(y=pos_trepano, name="Trépano", mode='markers+lines', line=dict(color='red', width=4)))
    st.plotly_chart(fig_nav, use_container_width=True)

def calcular_t_and_d(prof, inc, wob):
    # Factor de fricción (FF) típico 0.25 - 0.30
    ff = 0.28 
    drag_total = (prof * 0.15) * np.cos(np.radians(inc)) * ff
    peso_efectivo = (prof * 18) - drag_total # 18 lbs/ft promedio
    torque_real = (wob * 0.5) + (prof * 0.02)
    return peso_efectivo, torque_real

def modulo_evaluacion_final():
    st.divider()
    st.header("🏁 Examen Final de Competencias")
    p1 = st.selectbox("Si el SPP cae repentinamente, ¿qué puede estar pasando?", ["Tobera lavada", "Aumento de densidad", "Falla en motor"])
    p2 = st.radio("¿Norma API para control de pozos?", ["RP 59", "RP 7G", "Spec 10"])
    
    if st.button("Finalizar y Certificar"):
        if p1 == "Tobera lavada" and p2 == "RP 59":
            st.balloons()
            st.success("¡Habilitado para operar en IPCL MENFA!")

# Al final de tu código principal:
if choice == "Cabina":
    # 1. Calculamos la física
    hk, tq = calcular_t_and_d(s["md"], s["inc"], wob_in)
    # 2. Renderizamos los relojes
    render_martin_decker(hk, tq, flow_in * 3.5)
    # 3. Mostramos la navegación
    graficar_geonavegacion(s["md"], s["inc"])

def render_manual_tecnico():
    st.divider()
    st.header("📖 Manual de Referencia y Normativa (API / IRAM)")
    
    with st.expander("📝 1. Control de Pozos (API RP 59)"):
        st.write("""
        **Procedimiento de Cierre (Shut-in):**
        1. **Espaciar:** Levantar la sarta para que el Kelly o junta no esté en el BOP.
        2. **Parar:** Detener bombas y rotación.
        3. **Cerrar:** Cerrar el Preventor Anular o Ram Superior.
        4. **Notificar:** Avisar al Company Man y registrar presiones (SIDPP/SICP).
        """)
        st.latex(r"KMW = MW + \frac{SIDPP}{0.052 \cdot TVD_{ft}}")

    with st.expander("🔧 2. Diseño de Sartas (API RP 7G)"):
        st.write("""
        * **Punto Neutro:** Debe mantenerse siempre dentro de los Drill Collars (DC) para evitar fallas por fatiga en los Heavy Weight (HWDP).
        * **Margen de Overpull:** Capacidad excedente de la sarta antes de llegar al límite elástico del acero.
        """)
        st.info("💡 Tip MENFA: En Mendoza, por la dureza de las formaciones, el control de vibraciones (vibración axial y stick-slip) es crítico.")

    with st.expander("🛠️ 3. Tipos de Trépanos y Selección"):
        col_t1, col_t2 = st.columns(2)
        col_t1.write("**PDC (Polycrystalline Diamond Compact):**")
        col_t1.write("- Ideal para formaciones blandas a medias (Shale).")
        col_t1.write("- Alta ROP, pero sensible al impacto.")
        
        col_t2.write("**Tricónicos (Dientes de Acero/Insertos):**")
        col_t2.write("- Para formaciones duras o abrasivas.")
        col_t2.write("- Acción de trituración y paleo.")

    with st.expander("⚖️ 4. Normas Regulatorias Argentinas"):
        st.write("""
        * **Resolución 25/04:** Normas de seguridad para la industria del petróleo.
        * **Normas IRAM 3500:** Protección contra incendios en equipos de perforación.
        * **Gestión de Residuos:** Disposición final de lodos base aceite (OBM) según leyes ambientales vigentes.
        """)

# --- LLAMADA FINAL EN EL CUERPO PRINCIPAL ---
# Agregá esto donde querés que aparezca el manual
render_manual_tecnico()

import csv
import os

def guardar_resultado_menfa(nombre, legajo, nota):
    archivo = "registro_alumnos_menfa.csv"
    # Si el archivo no existe, lo creamos con cabeceras
    existe = os.path.isfile(archivo)
    
    with open(archivo, mode='a', newline='', encoding='utf-8') as f:
        escritor = csv.writer(f)
        if not existe:
            escritor.writerow(["Fecha", "Operador", "DNI/Legajo", "Nota", "Estado"])
        
        estado = "APROBADO" if nota >= 16 else "REPROBADO"
        fecha_act = datetime.now().strftime("%Y-%m-%d %H:%M")
        escritor.writerow([fecha_act, nombre, legajo, nota, estado])

def modulo_administracion():
    st.sidebar.divider()
    if st.sidebar.button("📊 DESCARGAR REGISTRO EXCEL (CSV)"):
        if os.path.exists("registro_alumnos_menfa.csv"):
            with open("registro_alumnos_menfa.csv", "rb") as file:
                st.sidebar.download_button(
                    label="Confirmar Descarga",
                    data=file,
                    file_name="Reporte_Alumnos_MENFA_2026.csv",
                    mime="text/csv"
                )
        else:
            st.sidebar.error("No hay datos registrados aún.")

def generar_geologia_dinamica(profundidad):
    """Varía la dureza y radiactividad según la profundidad real."""
    # Simulación de capas: Arcilla (High GR), Arena (Low GR), Carbonato (Hard)
    seed = int(profundidad // 10) 
    np.random.seed(seed)
    
    if 2800 <= profundidad <= 3100: # Zona Objetivo (Vaca Muerta)
        gr = np.random.normal(120, 15) # Shale muy radiactivo
        dureza = 1.8 # Más difícil de perforar
    elif 2100 <= profundidad < 2800: # Punta Rosada
        gr = np.random.normal(45, 10)  # Arenas limpias
        dureza = 1.2
    else:
        gr = np.random.normal(80, 20)
        dureza = 1.0
        
    return gr, dureza

if "bit_health" not in st.session_state:
    st.session_state.bit_health = 100.0

def calcular_desgaste(wob, rpm, dureza_roca):
    # El desgaste aumenta con el peso, la velocidad y la dureza
    desgaste = (wob * 0.01) + (rpm * 0.005) * dureza_roca
    st.session_state.bit_health -= desgaste
    # Factor de eficiencia (1.0 al inicio, baja a 0.3 cuando está destruido)
    return max(0.3, st.session_state.bit_health / 100)

def check_eventos_aleatorios():
    evento = random.random()
    if evento < 0.05: # 5% de probabilidad de pérdida de circulación
        st.error("⚠️ ALERTA: Pérdida parcial de retorno detectada (10 bbl/h).")
        return "Pérdida"
    elif 0.05 <= evento < 0.10: # 5% de probabilidad de Torque Excesivo (Stick-Slip)
        st.warning("⚠️ VIBRACIÓN: Stick-Slip detectado. Reduzca WOB inmediatamente.")
        return "Vibración"
    return "Normal"

def calcular_ecd(mw, flow, depth):
    # Pérdida de carga por fricción simplificada en el espacio anular
    annular_loss = (flow**1.8 * depth) / 500000 
    # ECD = Densidad estática + Presión por fricción convertida a ppg
    ecd = mw + (annular_loss / (0.052 * depth * 3.28))
    return ecd

# --- DENTRO DEL BOTÓN DE PERFORAR ---
gr_actual, dureza = generar_geologia_dinamica(s["md"])
eficiencia_bit = calcular_desgaste(wob_in, rpm_in, dureza)
evento = check_eventos_aleatorios()

# La ROP ahora depende de la dureza, el desgaste y el peso
rop_real = (wob_in * rpm_in / (500 * dureza)) * eficiencia_bit

# La ECD se muestra en el panel para evitar fracturar la formación
ecd_actual = calcular_ecd(mw_in, flow_in, s["md"])

# Actualizar métricas con variabilidad
st.metric("ECD (ppg)", f"{ecd_actual:.2f}", delta=f"{ecd_actual - mw_in:.2f} frict")
st.metric("BIT HEALTH", f"{st.session_state.bit_health:.1f}%")

# --- DENTRO DEL BOTÓN DE PERFORAR ---
gr_actual, dureza = generar_geologia_dinamica(s["md"])
eficiencia_bit = calcular_desgaste(wob_in, rpm_in, dureza)
evento = check_eventos_aleatorios()

# La ROP ahora depende de la dureza, el desgaste y el peso
rop_real = (wob_in * rpm_in / (500 * dureza)) * eficiencia_bit

# La ECD se muestra en el panel para evitar fracturar la formación
ecd_actual = calcular_ecd(mw_in, flow_in, s["md"])

# Actualizar métricas con variabilidad
st.metric("ECD (ppg)", f"{ecd_actual:.2f}", delta=f"{ecd_actual - mw_in:.2f} frict")
st.metric("BIT HEALTH", f"{st.session_state.bit_health:.1f}%")
# --- RENDERIZADO DE CONSOLA ---
def mostrar_cabina_scada(hkld, torque, spp, ecd, bit_health):
    render_martin_decker(hkld, torque, spp) # Los relojes analógicos
    
    # Métricas digitales de alta visibilidad
    c1, c2, c3 = st.columns(3)
    c1.metric("ECD (Presión Real)", f"{ecd:.2f} ppg")
    c2.metric("VIDA DEL TRÉPANO", f"{bit_health*100:.1f} %")
    c3.metric("D-EXPONENT (Geomecánica)", f"{1.2 + (0.1 * np.random.rand()):.2f}")

# --- VISUALIZACIÓN 3D Y LOGS ---
def mostrar_geosteering(prof, inc):
    graficar_geonavegacion(prof, inc) # Gráfico de ventana productora
    # Aquí podés llamar a la función de perfiles LWD (Gamma Ray vs Profundidad)

# --- BLOQUE ADMINISTRATIVO FINAL ---
render_manual_tecnico() # Las normas API pegadas al final
modulo_evaluacion_final() # El examen que habilita al alumno
modulo_administracion() # El botón para que vos descargues el Excel/CSV

