import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.graph_objects as go
from datetime import datetime
import time
st.set_page_config(page_title="IPCL MENFA V5", layout="wide")
def mostrar_imagen_segura(nombre_archivo, ancho=None, subtitulo=""):
    if os.path.exists(nombre_archivo):
        st.image(nombre_archivo, width=ancho, caption=subtitulo)
    else:
        st.info(f"ℹ️ Sistema: {nombre_archivo} no detectado.")

# Inicialización de variables de sesión
if "auth" not in st.session_state: st.session_state.auth = False
if "menu" not in st.session_state: st.session_state.menu = "HOME"
# --- INICIALIZACIÓN DE ESTADO (Pegar después de los imports) ---
if "auth" not in st.session_state: 
    st.session_state.auth = False
if "menu" not in st.session_state: 
    st.session_state.menu = "HOME"
if "usuario" not in st.session_state: 
    st.session_state.usuario = "Invitado"
# IMPORTACIÓN DE TUS MÓDULOS SUBIDOS (Asegúrate que estén en la misma carpeta)
try:
    from motor_calculos_avanzados import calcular_fisica_perforacion
    from mud_pumps import dashboard_bombas
except ImportError:
    st.error("⚠️ Algunos módulos secundarios no se encuentran. Usando lógica interna de respaldo.")
def login_screen():
    st.title("INGRESO AL SISTEMA")
    mostrar_imagen_segura("logo_menfa.png", ancho=200) # Aquí ya no fallará
    with st.form("login"):
        user = st.text_input("Alumno:")
        if st.form_submit_button("Entrar"):
            st.session_state.auth = True
            st.session_state.usuario = user
            st.rerun()

def render_home():
    # ... código que te pasé de los botones ...
    pass
# --- 1. CONFIGURACIÓN DE PÁGINA ESTILO ROC ---
st.set_page_config(page_title="IPCL MENFA WELL SIM V5", layout="wide", initial_sidebar_state="collapsed")

# Estilo CSS Personalizado (Dark Mode + SCADA Cards)
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
    .status-active { color: #2ecc71; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. INICIALIZACIÓN DE ESTADO ---
if "menu" not in st.session_state: st.session_state.menu = "HOME"
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame([{
        "DEPTH": 2850.0, "WOB": 25.0, "RPM": 120, "TORQUE": 18500, 
        "SPP": 3200, "ROP": 15.0, "MSE": 35.0, "GR": 140
    }])

# Datos actuales para métricas rápidas
curr = st.session_state.history.iloc[-1]

# --- 3. MÓDULOS DE INTERFAZ ---

def render_home():
    # Header con Logo
    col_l, col_r = st.columns([1, 4])
    with col_l: st.image("logo_menfa.png", width=180)
    with col_r:
        st.title("🖥️ IPCL MENFA WELL SIM V5.0")
        st.subheader("Unidad de Control Operativo | Vaca Muerta, Mendoza")
    
    st.divider()
    
    # Grilla de Iconos Grandes (Selector de Módulos)
    st.markdown("### 🕹️ SELECCIONAR UNIDAD DE MANDO")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="module-card"><h1>📊</h1><h3>SCADA & MSE</h3><p class="status-active">ONLINE</p></div>', unsafe_allow_html=True)
        if st.button("ABRIR MONITOR", use_container_width=True): st.session_state.menu = "SCADA"
    with c2:
        st.markdown('<div class="module-card"><h1>💺</h1><h3>CABINA CHAIR</h3><p class="status-active">CONNECTED</p></div>', unsafe_allow_html=True)
        if st.button("TOMAR MANDOS", use_container_width=True): st.session_state.menu = "CABINA"
    with c3:
        st.markdown('<div class="module-card"><h1>📡</h1><h3>LWD / MWD</h3><p class="status-active">SYNCED</p></div>', unsafe_allow_html=True)
        if st.button("GEONAVEGACIÓN", use_container_width=True): st.session_state.menu = "LWD"

    st.write("")
    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown('<div class="module-card"><h1>🛡️</h1><h3>SEGURIDAD BOP</h3><p style="color:#e74c3c;">STANDBY</p></div>', unsafe_allow_html=True)
        if st.button("CONTROL POZOS", use_container_width=True): st.session_state.menu = "BOP"
    with c5:
        st.markdown('<div class="module-card"><h1>🌀</h1><h3>SARTA & VIB</h3><p class="status-active">MONITORING</p></div>', unsafe_allow_html=True)
        if st.button("VER VIBRACIONES", use_container_width=True): st.session_state.menu = "SARTA"
    with c6:
        st.markdown('<div class="module-card"><h1>🏆</h1><h3>EVALUACIÓN</h3><p>IADC CERTIFIED</p></div>', unsafe_allow_html=True)
        if st.button("GENERAR REPORTE", use_container_width=True): st.session_state.menu = "REPORTE"
def render_home():
    st.title(f"👷 BIENVENIDO, {st.session_state.usuario}")
    st.markdown(f"**Yacimiento Asignado:** {st.session_state.get('yacimiento_activo', 'Mendoza General')}")
    st.divider()

    st.subheader("Seleccione el Módulo de Operación:")
    
    # Grilla de Navegación
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📊 MONITOR SCADA", use_container_width=True): 
            st.session_state.menu = "SCADA"
            st.rerun()
    with c2:
        if st.button("🛡️ CONTROL DE POZOS (BOP)", use_container_width=True): 
            st.session_state.menu = "BOP"
            st.rerun()
    with c3:
        if st.button("📡 GEONAVEGACIÓN LWD", use_container_width=True): 
            st.session_state.menu = "LWD"
            st.rerun()

    st.write("") # Espacio
    c4, c5, c6 = st.columns(3)
    with c4:
        if st.button("📉 GESTIÓN DE PÉRDIDAS", use_container_width=True): 
            st.session_state.menu = "PERDIDA"
            st.rerun()
    with c5:
        if st.button("🔩 DISEÑO DE SARTA (API)", use_container_width=True): 
            st.session_state.menu = "SARTAS"
            st.rerun()
    with c6:
        if st.button("🏆 REPORTE Y DIPLOMA", use_container_width=True): 
            st.session_state.menu = "REPORTE"
            st.rerun()
            
def render_scada():
    st.button("🔙 VOLVER AL INICIO", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("🖥️ MONITOR SCADA - MÉTRICAS EN TIEMPO REAL")
    
    # KPI Row
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("WOB (klbs)", f"{curr['WOB']}", delta="Normal")
    m2.metric("RPM", f"{curr['RPM']}")
    m3.metric("Torque", f"{curr['TORQUE']}")
    m4.metric("MSE (kpsi)", f"{curr['MSE']}")
    m5.metric("TVD (m)", f"{curr['DEPTH']}")

    # Charts
    col_chart, col_img = st.columns([2, 1])
    with col_chart:
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=st.session_state.history['SPP'], name="Presión SPP", line=dict(color='#3498db', width=3)))
        fig.add_trace(go.Scatter(y=st.session_state.history['TORQUE']/100, name="Torque / 100", line=dict(color='#f39c12', width=3)))
        fig.update_layout(template="plotly_dark", height=400, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    with col_img:
        st.image("Gemini_Generated_Image_rgblymrgblymrgbl.png", caption="Cabina SCADA Proyectada")

def render_bop():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("🛡️ PANEL DE SEGURIDAD BOP (WELL CONTROL)")
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.image("Gemini_Generated_Image_dn7zasdn7zasdn7z.png", width=450)
    with col_b:
        st.metric("Presión Acumulador", "2850 psi")
        if st.button("🔥 CIERRE TOTAL DE EMERGENCIA", type="primary"):
            st.error("¡CIERRE DE RAMS ACTIVADO!")
            st.toast("Pozo Asegurado")

def render_lwd():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("📡 GEONAVEGACIÓN LWD / MWD")
    
    # Lógica de Alarma LWD
    if curr['GR'] < 100:
        st.error(f"🚨 ALERTA LWD: GAMMA RAY BAJO ({curr['GR']} API) - ¡SALIENDO DE CAPA!")
    else:
        st.success(f"🎯 DENTRO DE TARGET: GAMMA RAY ({curr['GR']} API)")
    
    # Gráfico 3D
    z = np.linspace(0, curr['DEPTH'], 100)
    x = np.where(z < 2200, 0, (z - 2200)**1.6 / 60)
    fig = go.Figure(data=[go.Scatter3d(x=x, y=np.zeros(100), z=z, mode='lines', line=dict(color='#2ecc71', width=6))])
    fig.update_layout(scene=dict(zaxis=dict(autorange="reversed")), template="plotly_dark", height=600)
    st.plotly_chart(fig, use_container_width=True)

# --- 4. NAVEGACIÓN Y CONTROL LATERAL ---
with st.sidebar:
    st.image("logo_menfa.png", width=100)
    st.header("🎮 INSTRUCTOR")
    new_wob = st.slider("Ajustar WOB (klbs)", 0, 60, int(curr['WOB']))
    new_rpm = st.slider("Ajustar RPM", 0, 200, int(curr['RPM']))
    new_gr = st.slider("Simular Gamma Ray (LWD)", 50, 180, 140)
    
    if st.button("ACTUALIZAR SIMULACIÓN"):
        # Cálculo de nuevas métricas usando tu motor_calculos_avanzados (si existe) o lógica base
        new_depth = curr['DEPTH'] + 1.5
        new_torque = (new_wob * 450) + (new_rpm * 12)
        new_rop = (new_rpm * 0.12) + (new_wob * 0.35)
        # MSE Simplificado
        new_mse = round(((new_wob / 56) + (480 * new_torque * new_rpm) / (56 * new_rop * 3.28)) / 1000, 2) if new_rop > 0 else 0
        
        new_row = {"DEPTH": new_depth, "WOB": new_wob, "RPM": new_rpm, "TORQUE": new_torque, 
                   "SPP": 3200 + (new_depth*0.2), "ROP": new_rop, "MSE": new_mse, "GR": new_gr}
        st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([new_row])], ignore_index=True)
        st.rerun()

# --- 5. RENDERIZADO SEGÚN MENÚ ---
if st.session_state.menu == "HOME": render_home()
elif st.session_state.menu == "SCADA": render_scada()
elif st.session_state.menu == "BOP": render_bop()
elif st.session_state.menu == "LWD": render_lwd()
elif st.session_state.menu == "CABINA":
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("💺 CABINA CHAIR - VISTA DEL PERFORADOR")
    st.image("Gemini_Generated_Image_jl30d0jl30d0jl30.png", use_container_width=True)
elif st.session_state.menu == "REPORTE":
    st.title("🏆 REPORTE FINAL DE OPERACIÓN")
    st.table(st.session_state.history.tail(10))
    st.download_button("📥 DESCARGAR LOG CSV", st.session_state.history.to_csv().encode('utf-8'), "reporte_menfa.csv", "text/csv")
# En el selector de menú:
if st.session_state.menu == "T&D":
    modulo_torque_drag(curr['DEPTH'], 89.5, 11.5)
elif st.session_state.menu == "GEOFI":
    modulo_geofisica()
elif st.session_state.menu == "GEONAV":
    modulo_geonavegacion()
# Dentro de tu lógica de perforación en app.py
if st.button("AVANZAR PERFORACIÓN"):
    # ... cálculos normales ...
    
    # Probabilidad de evento (10% de chance de pérdida en zonas fracturadas)
    if random.random() < 0.10:
        st.session_state.tasa_perdida = random.randint(5, 20)
        st.session_state.menu = "PERDIDA" # Salta automáticamente al módulo de alerta
        st.warning("⚠️ ¡CAÍDA REPENTINA DE NIVEL EN TANQUES!")
def login_screen():
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    mostrar_imagen_segura("logo_menfa.png", ancho=250)
    st.title("SISTEMA DE ENTRENAMIENTO MENFA V5.0")
    st.subheader("Cátedra de Perforación - UTN Mendoza")
    st.markdown('</div>', unsafe_allow_html=True)

    with st.form("login_form"):
        nombre = st.text_input("Nombre Completo del Alumno:")
        legajo = st.text_input("Número de Legajo:")
        yacimiento = st.selectbox("Asignación de Yacimiento:", 
                                 ["Barrancas", "Cruz de Piedra", "Malargüe (V VM)", "Vizcacheral"])
        
        btn_ingresar = st.form_submit_state = st.form_submit_button("INICIAR GUARDIA DE PERFORACIÓN")

        if btn_ingresar:
            if nombre and legajo:
                st.session_state.usuario = nombre
                st.session_state.legajo = legajo
                st.session_state.yacimiento_activo = yacimiento
                st.session_state.auth = True
                st.session_state.menu = "HOME"
                st.rerun()
            else:
                st.error("Por favor, complete sus datos para ingresar.")

def generar_diploma():
    st.title("🏆 EVALUACIÓN FINAL DE COMPETENCIAS")
    
    # Cálculos de desempeño
    mse_promedio = st.session_state.history['MSE'].mean()
    seguridad = "APROBADO" if st.session_state.get('bop_cerrada', False) == False else "CRÍTICO (Pozo Cerrado)"
    
    st.markdown(f"""
    ---
    ### CERTIFICADO DE SIMULACIÓN
    **Operador:** {st.session_state.usuario}  
    **Legajo:** {st.session_state.legajo}  
    **Yacimiento:** {st.session_state.yacimiento_activo}
    
    **RESULTADOS TÉCNICOS:**
    * **Eficiencia de Perforación (MSE):** {round(mse_promedio, 2)} kpsi
    * **Estado de Seguridad:** {seguridad}
    * **Metros Perforados:** {len(st.session_state.history)} m
    
    ---
    """)
    
    if st.button("📥 DESCARGAR REPORTE PARA PROFESOR PIZZOLATO"):
        csv = st.session_state.history.to_csv(index=False).encode('utf-8')
        st.download_button("Click aquí para descargar .CSV", csv, f"Reporte_{st.session_state.usuario}.csv", "text/csv")
# --- LÓGICA DE NAVEGACIÓN PRINCIPAL ---
# --- LÓGICA DE NAVEGACIÓN FINAL ---

if not st.session_state.auth:
    login_screen() # Primero el Login
else:
    # Si ya se logueó, mostramos el Sidebar con info del Alumno
    with st.sidebar:
        mostrar_imagen_segura("logo_menfa.png", ancho=100)
        st.write(f"👤 **Alumno:** {st.session_state.usuario}")
        st.write(f"📍 **Pozo:** {st.session_state.yacimiento_activo}")
        st.divider()
        if st.button("🚪 CERRAR SESIÓN"):
            st.session_state.auth = False
            st.rerun()

    # RUTEADOR DE PÁGINAS
    if st.session_state.menu == "HOME":
        render_home()
    elif st.session_state.menu == "SCADA":
        render_scada() # Asegurate que esta función esté definida arriba
    elif st.session_state.menu == "BOP":
        render_bop()   # Asegurate que esta función esté definida arriba
    elif st.session_state.menu == "LWD":
        modulo_geonavegacion() 
    elif st.session_state.menu == "PERDIDA":
        modulo_perdida_circulacion()
    elif st.session_state.menu == "SARTAS":
        modulo_sartas_api()
    elif st.session_state.menu == "REPORTE":
        generar_diploma()
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    login_screen()
else:
    # Una vez logueado, mostramos el menú elegido
    if st.session_state.menu == "HOME":
        render_home()
    elif st.session_state.menu == "SCADA":
        render_scada()
    elif st.session_state.menu == "BOP":
        render_bop()
    elif st.session_state.menu == "LWD":
        render_lwd()
    elif st.session_state.menu == "PERDIDA":
        modulo_perdida_circulacion()
    elif st.session_state.menu == "REPORTE":
        generar_diploma()

    # Botón para cerrar sesión
    if st.sidebar.button("Cerrar Guardia (Logout)"):
        st.session_state.auth = False
        st.rerun()
def modulo_sartas_api():
    st.title("🔩 Módulo en Construcción")
    if st.button("Volver"): st.session_state.menu = "HOME"; st.rerun()
# --- ESTO VA AL FINAL DEL ARCHIVO ---
if not st.session_state.auth:
    login_screen()
else:
    if st.session_state.menu == "HOME":
        render_home()
    elif st.session_state.menu == "SCADA":
        # llamar a tu función de scada
        pass
    # ... resto de elif ...
