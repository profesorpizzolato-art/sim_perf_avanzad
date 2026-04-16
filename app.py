import streamlit as st
import pandas as pd
import numpy as np
import time
import base64
import os
from datetime import datetime
from fpdf import FPDF
from streamlit_autorefresh import st_autorefresh
import io
# --- IMPORTACIÓN DE TUS MÓDULOS TÉCNICOS (FILES) ---
import motor_calculos_avanzados as motor
import geonavegacion_pro as geo
import torque_and_drag as td
import bombas_de_lodo as bombas
import sartas_perforacion as sartas
import sys
import os
import plotly.graph_objects as go
import streamlit.components.v1 as components
# --- 1. INICIALIZACIÓN BLINDADA (Colocar justo después de los imports) ---
import time
import random
import streamlit as st
from streamlit_autorefresh import st_autorefresh
# --- 1. MEMORIA COMPARTIDA ÚNICA (SERVIDOR) ---
@st.cache_resource
def conectar_pizarra_maestra():
    return {
        "profundidad_actual": 2500.0,
        "caudal_maestro": 500.0,
        "wob_maestro": 0.0,
        "rpm_maestro": 0.0,
        "torque_maestro": 0.0,# --- 1. MEMORIA COMPARTIDA ÚNICA (SERVIDOR) ---
        "presion_base": 1200.0,
        "densidad_maestra": 10.2,
        "evento_activo": None,
        "alarma_activa": False,
        "bop_cerrado": False,
        "mensaje_evento": "Operación Normal"
    }

# ESTO CONECTA A TODOS AL MISMO CABLE
piz = conectar_pizarra_maestra()
pizarra = piz
USUARIOS_ALUMNOS = {
    "Florencia Usubiaga": "8651",
    "Agustin Flores ": "8652",
    "Moya Lila ": "8653",
    "Jonathan Emmanuel Perez ": "8654",
    "Jonatan Sebastian Paredes ": "8655",
    "Pilar Suárez Casanueva ": "8656",
    "Renzo Pizzolato ": "8657",
    "Abrahan Fermín Omar Villalba ":"8658"
}
# Lista de variables necesarias para que la app no explote
variables_necesarias = {
    "pizarra": {
        "wob_maestro": 0.0, "rpm_maestro": 0.0, "caudal_maestro": 500.0,
        "densidad_maestra": 10.2, "presion_base": 1200.0,
        "profundidad_actual": 2500.0, "evento_activo": None,
        "piletas_nivel": 500.0, "bop_cerrado": False
    },
    "ultima_falla": time.time(),
    "inicio_falla": None,
    "tiempo_respuesta": 0,
    "mensaje_alerta": "Operación Normal"
}

# Creamos las variables si no existen
for clave, valor_defecto in variables_necesarias.items():
    if clave not in st.session_state:
        st.session_state[clave] = valor_defecto

# Acceso directo para facilitar el código
piz = st.session_state.pizarra
# Esto le dice a Python que busque módulos en la carpeta donde está app.py
sys.path.append(os.path.dirname(__file__))

import streamlit as st
import bombas_de_lodo as bombas  # Ahora debería encontrarlo
# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="MENFA 3.0 - Mendoza Oil Industry", layout="wide", page_icon="🏗️")
st.set_page_config(page_title="Simulador IPCL MENFA", layout="wide")


st_autorefresh(interval=1000, key="f5_simulador")

import streamlit.components.v1 as components

def disparar_alarma_sonora():
    # Ajustá 'assets/alarma.mp3' según el nombre exacto de tu carpeta
    ruta_audio = "assets/alarma.mp3" 
    
    if os.path.exists(ruta_audio):
        with open(ruta_audio, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            # Creamos el HTML para reproducir el archivo local
            html_audio = f"""
                <audio autoplay loop>
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
            """
            components.html(html_audio, height=0, width=0)
    else:
        st.error(f"⚠️ No se encontró el archivo en {ruta_audio}")
# --- 3. LÓGICA DE AUDIO (ALARMAS) ---
def reproducir_alarma_critica():
    if os.path.exists("assets/alarma.mp3"):
        with open("assets/alarma.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            html = f'<audio autoplay loop><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.components.v1.html(html, height=0)

# --- 4. CONTROL DE ACCESO (FABRICIO VS ALUMNOS) ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.image("logo.menfa.png", use_container_width=True)
        st.markdown("<h2 style='text-align: center;'>SISTEMA DE ENTRENAMIENTO v3.0</h2>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🎓 Acceso Alumnos", "👨‍🏫 Instructor"])
        with tab1:
            with st.form("alumno_login"):
                u = st.text_input("Nombre y Apellido (Tal cual figura en lista)")
                c = st.text_input("Contraseña Individual", type="password")
                if st.form_submit_button("Ingresar"):
                    # Verificamos si el nombre existe y la clave coincide
                    if u in USUARIOS_ALUMNOS and USUARIOS_ALUMNOS[u] == c:
                        st.session_state.autenticado = True
                        st.session_state.usuario = u
                        st.session_state.rol = "alumno"
                        st.rerun()
                    else:
                        st.error("❌ Nombre o Clave incorrectos. Contacte al instructor.")
        with tab2:
            with st.form("profe_login"):
                cp = st.text_input("Clave Maestro", type="password")
                if st.form_submit_button("Acceso Administrativo"):
                    if cp == "menfa2026":
                        st.session_state.autenticado, st.session_state.usuario, st.session_state.rol = True, "Inst. Fabricio Pizzolato", "instructor"
                        st.rerun()
    st.stop()

# --- 5. INTERFAZ PRINCIPAL (SIDEBAR UNIFICADO) ---
with st.sidebar:
    st.image("logo.menfa.png", use_container_width=True)
    st.title(f"👤 {st.session_state.usuario}")
    st.write(f"Rol: {st.session_state.rol.capitalize()}")

    # --- INICIO DEL FILTRO DE SEGURIDAD PARA INSTRUCTOR ---
    if st.session_state.rol == "instructor":
        st.divider()
        st.header("👨‍🏫 Panel del Instructor")
        # Dentro del if st.session_state.rol == "instructor":
# SLIDERS GLOBALES
piz["caudal_maestro"] = st.slider("Caudal (GPM)", 0, 1200, int(piz["caudal_maestro"]))
piz["wob_maestro"] = st.slider("WOB (klbs)", 0, 100, int(piz["wob_maestro"]))
piz["rpm_maestro"] = st.slider("RPM", 0, 200, int(piz["rpm_maestro"]))
        # 1. HERRAMIENTAS DE SISTEMA
        if st.button("🧹 Limpiar Memoria y Reiniciar"):
            st.session_state.clear()
            st.rerun()
        
        if st.button("🔄 Resetear Eventos"):
            st.session_state.evento_activo = None
            pizarra["alarma_activa"] = False
            st.rerun()

        st.divider()
        st.write(f"📍 Profundidad actual: {pizarra.get('profundidad_actual', 0):.2f} 
 if st.button("🚨 Provocar Kick"):
    piz["evento_activo"] = "KICK"
    piz["alarma_activa"] = True
    piz["mensaje_evento"] = "¡SURGENCIA DETECTADA!"
    st.rerun()

if st.button("✅ Normalizar Pozo"):
    piz["evento_activo"] = None
    piz["alarma_activa"] = False
    piz["mensaje_evento"] = "Operación Normal"
    st.rerun()

        # 2. CONTROLES OPERATIVOS (SLIDERS)
        # Caudal
        val_c = int(pizarra.get("caudal_maestro", 500))
        nuevo_caudal = st.slider("Caudal (GPM)", 0, 1200, val_c, step=10)
        pizarra["caudal_maestro"] = float(nuevo_caudal)

        # WOB
        val_w = int(pizarra.get("wob_maestro", 0))
        nuevo_wob = st.slider("WOB (klbs)", 0, 100, val_w, step=1)
        pizarra["wob_maestro"] = float(nuevo_wob)

        # RPM
        val_r = int(pizarra.get("rpm_maestro", 0))
        nuevo_rpm = st.slider("RPM", 0, 200, val_r, step=1)
        pizarra["rpm_maestro"] = float(nuevo_rpm)

        st.divider()
        
        # 3. SISTEMA DE AUDIO
        st.subheader("🔊 Sistema de Audio")
        st.session_state.alarma_activa = st.toggle("Activar Sirena de Emergencia", value=True)
        if st.button("🔊 Probar Sonido"):
            disparar_alarma_sonora()

        st.divider()

        # 4. SIMULACIÓN DE FALLAS (LOS BOTONES QUE NO DEBEN FALTAR)
        st.subheader("🕹️ Simulación de Fallas")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            if st.button("🚨 Provocar Kick"):
                pizarra["evento_activo"] = "KICK"
                pizarra["alarma_activa"] = True
                st.rerun()
            
            if st.button("⚙️ Falla Bomba 1"):
                st.session_state.evento_activo = "FALLA_BOMBA"
                st.rerun()

        with col_f2:
            if st.button("📉 Provocar Pérdida"):
                st.session_state.evento_activo = "PERDIDA"
                st.rerun()

            if st.button("✅ Normalizar Pozo"):
                st.session_state.evento_activo = None
                pizarra["alarma_activa"] = False
                st.rerun()

    # --- VISTA PARA EL ALUMNO (SI NO ES INSTRUCTOR) ---
    else:
        st.divider()
        st.header("🎓 Panel del Alumno")
        st.info("Operación en curso. Los parámetros son controlados por el instructor.")
        st.metric("Profundidad", f"{pizarra.get('profundidad_actual', 0):.2f} m")
        st.write("Verifique los manómetros en la consola principal.")

    # --- SECCIÓN COMÚN (PARA AMBOS) ---
    st.divider()
    if st.button("📊 Generar Reporte Final"):
        # Tu lógica de PDF aquí
        st.success("Reporte generado con éxito.")
# --- MODO ALUMNO (VISUALIZACIÓN Y ACCIÓN) ---
st.title("📟 Panel Integral de Operaciones")

# Lógica de Alarma Sonora y Visual
# Si 'alarma_activa' no existe, devolverá False y la app seguirá funcionando
if pizarra.get("alarma_activa", False):
    st.error(f"🔥 {pizarra.get('mensaje_evento', 'Sistema Operativo Normal')}")
    reproducir_alarma_critica()
    
    # PANEL BOP PARA EL ALUMNO
    st.markdown("### 🛡️ PANEL DE EMERGENCIA (BOP)")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("🔴 CERRAR BOP ANULAR", type="primary", use_container_width=True):
            pizarra["bop_cerrado"] = True
            pizarra["alarma_activa"] = False
            st.success("POZO CERRADO. Presión controlada.")
    with col_b2:
        st.button("🔴 CERRAR RAMS CIEGOS", type="secondary", use_container_width=True)

# --- INTEGRACIÓN DE MÓDULOS TÉCNICOS (ALUMNO Y PROFE VEN ESTO) ---
col1, col2, col3 = st.columns(3)
# Cambiá tu línea 265 por esta forma más segura:
res_fisica = motor.calcular_fisica_perforacion(
    wob=pizarra.get("wob_maestro", 0.0),
    rpm=pizarra.get("rpm_maestro", 0.0),
    torque=pizarra.get("torque_maestro", 0.0), # Si no lo encuentra, usa 0.0
    profundidad=pizarra.get("profundidad_actual", 2500.0),
    flow_rate=pizarra.get("caudal_maestro", 500.0)
)

# 2. Extraemos los valores del diccionario para los manómetros
rop_actual = res_fisica.get("ROP", 0.0) if 'res_fisica' in locals() else 0.0
mse_actual = res_fisica["MSE"]
hk_actual = res_fisica["HOOK_LOAD"]
av_actual = res_fisica["AV"]
kmw_actual = res_fisica["KMW"]

# 3. (Opcional) Si necesitas HHP e Impact Force para otros gráficos:
hhp = (pizarra["presion_base"] * pizarra["caudal_maestro"]) / 1714
if_force = 0.0182 * pizarra["caudal_maestro"] * (pizarra["presion_base"] * pizarra["densidad_maestra"])**0.5

# --- GRÁFICOS DINÁMICOS DE TUS ARCHIVOS ---
st.divider()
c_gra1, c_gra2 = st.columns(2)

with c_gra1:
    st.subheader("📍 Geonavegación Pro")
    # Llamamos a tu archivo geonavegacion_pro.py
    fig_geo = geo.generar_grafico_trayectoria(pizarra["profundidad_actual"])
    st.plotly_chart(fig_geo, use_container_width=True)

with c_gra2:
    st.subheader("⚙️ Torque & Drag")
    # Llamamos a tu archivo torque_and_drag.py
    fig_td = td.calcular_curvas_esfuerzo(pizarra["wob_maestro"], pizarra["rpm_maestro"])
    st.plotly_chart(fig_td, use_container_width=True)

st.sidebar.divider()

# 1. Aseguramos que el estado del reporte exista
if "bytes_reporte_final" not in st.session_state:
    st.session_state.bytes_reporte_final = None

# 2. Botón para GENERAR el reporte
import io  # Asegurate de tener este import arriba de todo

st.sidebar.divider()

# --- DENTRO DEL BOTÓN DE INFORME ---
pdf_rep = FPDF()
pdf_rep.add_page()
pdf_rep.set_font("Arial", 'B', 16)

# USAR TEXTO PLANO (Sin tildes ni emojis como 📊 o 🚨)
pdf_rep.cell(200, 10, "MENFA IPCL - REPORTE DE ENTRENAMIENTO", 0, 1, 'C')
pdf_rep.ln(10)
pdf_rep.set_font("Arial", '', 12)
pdf_rep.cell(200, 10, f"Alumno: {st.session_state.get('usuario', 'Anonimo')}", 0, 1)
pdf_rep.cell(200, 10, "Instructor: Fabricio Pizzolato", 0, 1)

# Conversión final segura
pdf_str_rep = pdf_rep.output(dest='S')
if isinstance(pdf_str_rep, str):
    st.session_state.bytes_reporte_final = pdf_str_rep.encode('latin-1', 'ignore')
else:
    st.session_state.bytes_reporte_final = pdf_str_rep
    
# motor_calculos_avanzados.py
import numpy as np

def calcular_metricas(presion, caudal, densidad):
    # HHP: Potencia Hidráulica
    hhp = (presion * caudal) / 1714
    
    # IF: Fuerza de Impacto
    if_force = 0.0182 * caudal * np.sqrt(densidad * presion)
    
    return round(hhp, 2), round(if_force, 2)

def calcular_ecd(densidad_lodo, caudal, profundidad):
    # Simulación de pérdida por fricción anular
    perdida_friccion = (caudal * 0.1) / 100 
    ecd = densidad_lodo + perdida_friccion
    return round(ecd, 2)

# geonavegacion_pro.py
import plotly.graph_objects as go
import numpy as np

def generar_grafico_trayectoria(profundidad_actual):
    # Creamos una trayectoria ficticia basada en la profundidad real
    z = np.linspace(0, profundidad_actual, 100)
    x = np.sin(z/500) * 50 # Desvío lateral
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=z, name="Trayectoria Real", line=dict(color='lime', width=4)))
    
    fig.update_layout(
        title="Perfil de Pozo (Vaca Muerta)",
        yaxis=dict(autorange="reversed", title="Profundidad (m)"),
        xaxis=dict(title="Desplazamiento Lateral (m)"),
        template="plotly_dark"
    )
    return fig

# --- DENTRO DE LA VISTA DEL ALUMNO ---
st.header("📊 Monitor de Perforación en Tiempo Real")

# --- EN EL LÓGICA DEL ALUMNO ---

# 1. Llamamos al motor de física (asegúrate de tener 'import motor_calculos_avanzados as motor')
res = motor.calcular_fisica_perforacion(
    wob=pizarra["wob_maestro"],
    rpm=pizarra["rpm_maestro"],
    torque = pizarra.get("torque_maestro", 0.0),
    profundidad=pizarra["profundidad_actual"],
    flow_rate=pizarra["caudal_maestro"]
)
# --- 1. CÁLCULOS (Esto ya lo tenés) ---
res = motor.calcular_fisica_perforacion(
    wob=pizarra["wob_maestro"],
    rpm=pizarra["rpm_maestro"],
    torque=pizarra.get("torque_maestro", 0.0),
    profundidad=pizarra["profundidad_actual"],
    flow_rate=pizarra["caudal_maestro"]
)

# --- 2. DEFINICIÓN DE PESTAÑAS (Aquí va el código nuevo) ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🎮 Consola Principal", 
    "🛡️ BOP & Control", 
    "🧪 Lodos y Tanques", 
    "🛰️ Geonavegación"
])
import plotly.graph_objects as go

def crear_manometro(valor, titulo, unidad, max_val, color_linea):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = valor,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"<b>{titulo}</b><br><span style='font-size:0.8em;color:gray'>{unidad}</span>", 'font': {'size': 18}},
        gauge = {
            'axis': {'range': [None, max_val], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': color_linea},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "#555",
            'steps': [
                {'range': [0, max_val*0.8], 'color': 'rgba(0, 255, 0, 0.1)'},
                {'range': [max_val*0.8, max_val], 'color': 'rgba(255, 0, 0, 0.3)'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_val * 0.9
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=50, b=20),
        height=250,
        font={'color': "white", 'family': "Arial"}
    )
    return fig
# --- 3. CONTENIDO DE CADA PESTAÑA ---

with tab1:
    st.subheader("Tablero de Perforación en Tiempo Real")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.plotly_chart(crear_manometro(res["ROP"], "Velocidad ROP", "m/hr", 60, "lime"), use_container_width=True)
    with col2:
        st.plotly_chart(crear_manometro(res["MSE"], "Eficiencia MSE", "kpsi", 100, "orange"), use_container_width=True)
    with col3:
        st.plotly_chart(crear_manometro(res["HOOK_LOAD"], "Peso en Gancho", "klbs", 600, "white"), use_container_width=True)

with tab2:
    import bop_panel as bop # Importamos tu módulo de BOP
with tab2:
    import bop_panel as bop 
    st.header("🛡️ Sistema de Seguridad de Pozo")
    
    # Cambiamos 'mostrar_interfaz_bop' por 'render_bop_ui'
    bop.render_bop_ui(pizarra)   
with tab3:
    import gestion_perdidas as gp
    st.header("🧪 Control de Piletas y Lodos")
    # Aquí graficaremos los niveles de los tanques
    gp.render_tanques(pizarra)

with tab4:
    import geonavegacion_pro as geo
    st.header("🛰️ Trayectoria en Vaca Muerta")
    fig_geo = geo.generar_grafico_trayectoria(pizarra["profundidad_actual"])
    st.plotly_chart(fig_geo, use_container_width=True, key="grafico_geo_tab4")
    import plotly.graph_objects as go

def crear_reloj(valor, titulo, unidad, max_val, color_linea):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = valor,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"<b>{titulo}</b><br><span style='font-size:0.8em;color:gray'>{unidad}</span>"},
        gauge = {
            'axis': {'range': [None, max_val], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': color_linea},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "#444",
            'steps': [
                {'range': [0, max_val*0.8], 'color': 'rgba(0, 255, 0, 0.1)'},
                {'range': [max_val*0.8, max_val], 'color': 'rgba(255, 0, 0, 0.2)'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': valor
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=30, r=30, t=50, b=30),
        height=280,
        font={'color': "white", 'family': "Arial"}
    )
    return fig
# 2. Dibujamos los manómetros usando tu nueva función
col1, col2, col3 = st.columns(3)

with col1:
    st.plotly_chart(crear_manometro(res["ROP"], "ROP", "m/hr", 60, "lime"), use_container_width=True)

with col2:
    st.plotly_chart(crear_manometro(res["MSE"], "MSE", "kpsi", 100, "orange"), use_container_width=True)

with col3:
    st.plotly_chart(crear_manometro(res["HOOK_LOAD"], "Hook Load", "klbs", 600, "white"), use_container_width=True)
# --- CÁLCULOS DE POTENCIA HIDRÁULICA (Antes de los relojes) ---
# La fórmula es: (Presión * Caudal) / 1714
presion = pizarra.get("presion_base", 0)
caudal = pizarra.get("caudal_maestro", 0)

hhp_actual = (presion * caudal) / 1714

# Ahora sí, el reloj de la línea 433 va a funcionar:
st.plotly_chart(crear_reloj(hhp_actual, "Potencia", "HHP", 2000, "purple"))
# Actualizamos la profundidad en la pizarra automáticamente (Simulando el avance)
if not pizarra["bop_cerrado"] and res["ROP"] > 1:
    pizarra["profundidad_actual"] += (res["ROP"] / 3600) # Avance por segundo
# 2. Mostramos los Gauges (Relojes)
col1, col2, col3 = st.columns(3)
with col1:
    st.plotly_chart(crear_reloj(pizarra["presion_base"], "Presión SPP", "PSI", 5000, "red"), key="reloj_spp_tab")
with col2:
    st.plotly_chart(crear_reloj(hhp_actual, "Potencia", "HHP", 2000, "purple"), key="reloj_hhp_principal")
with col3:
    st.plotly_chart(crear_reloj(pizarra["rpm_maestro"], "Rotación", "RPM", 200, "green"), key="reloj_rpm_tab")

# --- ASÍ DEBE QUEDAR LA LÍNEA 535 ---
st.plotly_chart(
    geo.generar_grafico_trayectoria(pizarra["profundidad_actual"]), 
    key="grafico_trayectoria_direccional" # Este es el DNI único
)
# --- DENTRO DEL LÓGICA DEL ALUMNO EN app.py ---

st.markdown("### 📊 MONITOREO DE PARÁMETROS EN TIEMPO REAL")

fila1_col1, fila1_col2, fila1_col3 = st.columns(3)

with fila1_col1:
    # Manómetro de Presión (SPP)
    st.plotly_chart(crear_manometro(pizarra["presion_base"], "Presión Standpipe", "PSI", 5000, "#ff4b4b"), use_container_width=True)

with fila1_col2:
    # Manómetro de Caudal
    st.plotly_chart(crear_manometro(pizarra["caudal_maestro"], "Caudal de Bomba", "GPM", 1200, "#00d4ff"), use_container_width=True)

with fila1_col3:
    # Manómetro de Torque (Puedes traerlo de torque_and_drag.py)
   st.plotly_chart(
    crear_manometro(pizarra.get("torque_maestro", 0.0), "Torque en Mesa", "kft-lb", 40, "#ffcc00"), 
    use_container_width=True, 
    key="manometro_torque_principal"
)
fila2_col1, fila2_col2, fila2_col3 = st.columns(3)

with fila2_col1:
    st.plotly_chart(crear_manometro(pizarra["rpm_maestro"], "Rotación (RPM)", "rev/min", 200, "#00ff88"), use_container_width=True)

with fila2_col2:
    st.plotly_chart(crear_manometro(pizarra["wob_maestro"], "Peso (WOB)", "klbs", 60, "#a64dff"), use_container_width=True)

with fila2_col3:
    # Densidad del Lodo
    st.plotly_chart(crear_manometro(pizarra["densidad_maestra"], "Densidad Lodo", "ppg", 20, "#ffffff"), use_container_width=True)

# SI HAY ALERTA, MOSTRAR EL PANEL BOP ABAJO DE LOS RELOJES
if pizarra.get("alarma_activa", False):
    st.error("🚨 ¡ALERTA DE SEGURIDAD! Verifique los parámetros de presión.")
    # Si tenés el código del audio de la alarma, iría aquí debajo

import streamlit as st

def render_bop_ui(pizarra):
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #ff4b4b;'>🛡️ CONSOLA DE CONTROL DE SURGENCIAS (BOP)</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("⭕ CERRAR ANULAR", type="primary", use_container_width=True):
            pizarra["bop_cerrado"] = True
            pizarra["alarma_activa"] = False
            pizarra["mensaje_evento"] = f"✅ Pozo Cerrado (Anular) por {st.session_state.usuario}"
            st.success("Anular Cerrado")

    with col2:
        if st.button("🚫 PIPE RAMS", type="secondary", use_container_width=True):
            pizarra["bop_cerrado"] = True
            pizarra["alarma_activa"] = False
            pizarra["mensaje_evento"] = f"✅ Pozo Cerrado (Rams) por {st.session_state.usuario}"
            st.success("Pipe Rams Cerrados")

    with col3:
        if st.button("✂️ BLIND RAMS (Corte)", type="secondary", use_container_width=True):
            pizarra["bop_cerrado"] = True
            pizarra["alarma_activa"] = False
            pizarra["mensaje_evento"] = "❗ POZO SELLADO (CORTE DE SARTA)"
            st.warning("Sarta Cortada - Pozo Sellado")

import plotly.graph_objects as go

def crear_manometro(valor, titulo, unidad, max_val, color_linea):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = valor,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"<b>{titulo}</b><br><span style='font-size:0.8em;color:gray'>{unidad}</span>", 'font': {'size': 18}},
        gauge = {
            'axis': {'range': [None, max_val], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': color_linea},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "#333",
            'steps': [
                {'range': [0, max_val*0.8], 'color': 'rgba(0, 255, 0, 0.1)'},
                {'range': [max_val*0.8, max_val], 'color': 'rgba(255, 0, 0, 0.2)'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': valor
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=50, b=20),
        height=250,
        font={'color': "white", 'family': "Arial"}
    )
    return fig

import plotly.graph_objects as go
import streamlit as st
import plotly.graph_objects as go  # <-- IMPORTANTE
# ... otros imports ...

def crear_manometro(valor, titulo, unidad, max_val, color_linea):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = valor,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"<b>{titulo}</b><br><span style='font-size:0.8em;color:gray'>{unidad}</span>", 'font': {'size': 18}},
        gauge = {
            'axis': {'range': [None, max_val], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': color_linea},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "#555",
            'steps': [
                {'range': [0, max_val*0.8], 'color': 'rgba(0, 255, 0, 0.1)'},
                {'range': [max_val*0.8, max_val], 'color': 'rgba(255, 0, 0, 0.3)'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_val * 0.8
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=50, b=20),
        height=250,
        font={'color': "white", 'family': "Arial"}
    )
    return fig

# --- 2. DESPUÉS LA PIZARRA ---
@st.cache_resource
def obtener_pizarra():
    return {
        "wob_maestro": 0.0,
        "rpm_maestro": 0.0,
        "torque_maestro": 0.0,
        "caudal_maestro": 500.0,
        "profundidad_actual": 2500.0,
        "alarma_activa": False,
        "bop_cerrado": False
    }

pizarra = obtener_pizarra()
# --- SISTEMA DE EVENTOS CRÍTICOS ---

# 1. Lógica de Surgencia (Kick)
if st.sidebar.button("🚨 ACTIVAR KICK (SURGENCIA)"):
    pizarra["alarma_activa"] = True
    st.session_state.tipo_evento = "KICK"

if st.session_state.get("tipo_evento") == "KICK":
    # La presión sube 5 psi por segundo si no cierran el BOP
    if not pizarra["bop_cerrado"]:
        # ESTAS LÍNEAS AHORA TIENEN LA SANGRÍA CORRECTA
        pizarra["presion_base"] = pizarra.get("presion_base", 0) + 5
        st.error("⚠️ ¡AUMENTO DE PRESIÓN EN TUBING! ¡CERRAR BOP!")
    else:
        st.success("✅ POZO CERRADO. CALCULAR KILL MUD WEIGHT.")

# 2. Lógica de Pérdida de Circulación
if st.sidebar.button("📉 ACTIVAR PÉRDIDA DE RETORNO"):
    st.session_state.tipo_evento = "PERDIDA"

if st.session_state.get("tipo_evento") == "PERDIDA":
    # Asumiendo que 'res' es el diccionario de tus resultados de cálculo
    if "AV" in res:
        res["AV"] = res["AV"] * 0.4 
    st.warning("📉 PÉRDIDA DE CIRCULACIÓN DETECTADA EN FORMACIÓN")

# 3. Lógica de Falla de Bomba
if st.sidebar.button("⚙️ FALLA BOMBA 1"):
    st.session_state.tipo_evento = "FALLA_BOMBA"

if st.session_state.get("tipo_evento") == "FALLA_BOMBA":
    pizarra["caudal_maestro"] = pizarra.get("caudal_maestro", 0) * 0.5
    st.error("💥 FALLA EN VÁLVULA DE BOMBA 1. CAUDAL REDUCIDO AL 50%")
    
# --- LÓGICA DE DETECCIÓN DE KICK (Línea 689 Corregida) ---
umbral_alarma = 5000  

# Usamos .get() para que si no existe, devuelva 0 y no se rompa la app
presion_actual = piz.get("presion_base", 0) 

if presion_actual > umbral_alarma:
    st.error(f"🚨 ¡ALERTA! PRESIÓN CRÍTICA EN BOCA DE POZO: {presion_actual} PSI")
    
    # IMPORTANTE: Usamos la variable de la pizarra para disparar el sonido
    if piz.get('alarma_activa', False):
        disparar_alarma_sonora()
        
    # Visualmente podemos hacer que la pantalla "parpadee" usando markdown
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #440000;
            transition: background-color 0.5s;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    # Volver al color normal si la presión baja
    st.markdown(
        """
        <style>
        .stApp { background-color: transparent; }
        </style>
        """,
        unsafe_allow_html=True
    )
    
# --- 4. INTERFAZ DE USUARIO (TABS) ---
# Asegurate de que esto esté fuera de cualquier otro bloque 'with'
with tab4:
    st.subheader("🛰️ Navegación en el Target")
    
# --- 2. SEGUNDO: Asignamos la variable local (ESTO EVITA EL NAMEERROR) ---
# Usamos el mismo nombre que intentas llamar en la línea 174
pizarra = st.session_state.pizarra 
piz = st.session_state.pizarra  # Creamos 'piz' también por si lo usas más abajo
# 2. SEGUNDO: Creamos los tabs
tab1, tab2, tab3, tab4 = st.tabs(["🎮 Consola", "🛡️ BOP", "🧪 Lodos", "🛰️ Geo"])

with tab1:
    # Acá piz ya funciona
    st.write(f"Profundidad: {piz['profundidad_actual']}")

with tab4:
    st.subheader("🛰️ Navegación en el Target")
    # LÍNEA 674: Ahora sí, 'piz' existe y no va a tirar error
    actual = piz["profundidad_actual"] 
    limite_superior = 2510 
    limite_inferior = 2540
    # ... resto del código    
    # Definimos variables locales para este Tab
    actual = piz["profundidad_actual"]
    limite_superior = 2510 
    limite_inferior = 2540

    # Columnas alineadas perfectamente
    col_geo1, col_geo2 = st.columns(2) 
    
    with col_geo1:
        st.metric("Techo Formación", f"{limite_superior} m")
        st.metric("Piso Formación", f"{limite_inferior} m")
    
    with col_geo2:
        if actual > limite_inferior:
            st.error("🚨 SALIDA POR EL PISO - ¡CORREGIR INCLINACIÓN!")
        elif actual < limite_superior:
            st.warning("⚠️ CERCA DEL TECHO - AJUSTAR TRAYECTORIA")
        else:
            st.success("🎯 DENTRO DE LA VENTANA PRODUCTIVA")

# Cálculo físico para el simulador del MENFA
peso_lineal = 0.02 # klbs por metro
peso_sarta = piz["profundidad_actual"] * peso_lineal
hook_load_real = peso_sarta - piz["wob_maestro"]

import time

if 'inicio_falla' not in st.session_state:
    st.session_state.inicio_falla = None
if 'tiempo_respuesta' not in st.session_state:
    st.session_state.tiempo_respuesta = 0

if piz.get("evento_activo") and st.session_state.inicio_falla is None:
    st.session_state.inicio_falla = time.time()

if not piz.get("evento_activo"):
    st.session_state.inicio_falla = None
    
# Ahora podés usar 'hook_load_real' en cualquier reloj de la Tab 1
with st.sidebar:
    st.header("🎮 Controles del Perforador")
    st.info("Ajuste los parámetros de perforación en tiempo real.")

    # 1. SEGURIDAD Y BLINDAJE (Fuera de los sliders)
    # Obtenemos valores limpios y enteros
    rpm_val = int(max(0, min(200, piz.get("rpm_maestro", 0))))
    wob_val = int(max(0, min(50, piz.get("wob_maestro", 0))))
    gpm_val = int(max(0, min(1000, piz.get("caudal_maestro", 500))))

    # 2. SLIDERS ÚNICOS (Uno por cada parámetro)
    piz["rpm_maestro"] = st.slider("Rotación (RPM)", 0, 200, rpm_val)
    
    piz["wob_maestro"] = st.slider("Peso sobre Trépano (WOB klbs)", 0, 50, wob_val)
    
    piz["caudal_maestro"] = st.slider(
        label="Bomba (GPM)", 
        min_value=0, 
        max_value=1000, 
        value=gpm_val,
        step=10
    )

    st.divider()

    # 3. BOTÓN DE EMERGENCIA
if st.button("🚨 EMERGENCIA: PARADA TOTAL", width="stretch"):
        piz["caudal_maestro"] = 0
        st.warning("SISTEMA DETENIDO")
        st.rerun()

if st.button("🚨 EMERGENCIA: PARADA TOTAL"):
    piz["rpm_maestro"] = 0
    piz["caudal_maestro"] = 0
    st.warning("SISTEMA DETENIDO")

# --- PESTAÑAS INTERACTIVAS ---
with tab2:
    st.header("🛡️ Unidad de Cierre BOP")
    
    # Verificamos el estado actual en la pizarra
    bop_cerrado = pizarra.get("bop_cerrado", False)
    
    if not bop_cerrado:
        # SI ESTÁ ABIERTO: Mostrar botón para cerrar
        if st.button("🔴 CERRAR RAMS (EMERGENCIA)", use_container_width=True):
            pizarra["bop_cerrado"] = True
            pizarra["alarma_activa"] = False  # Apagamos la sirena al cerrar
            st.success("✅ BOP Cerrado exitosamente")
            st.rerun()
    else:
        # SI ESTÁ CERRADO: Mostrar botón para abrir
        if st.button("🔓 ABRIR RAMS", use_container_width=True):
            pizarra["bop_cerrado"] = False
            st.warning("⚠️ BOP Abierto - Pozo en comunicación")
            st.rerun()

    # Indicador visual de estado
    if bop_cerrado:
        st.error("ESTADO: BLOQUEADO / CERRADO")
    else:
        st.success("ESTADO: ABIERTO / FLUJO LIBRE")

with tab3:
    st.header("🧪 Control de Densidad")
    # Usamos .get para evitar errores si la clave no existe aún
    dens_actual = piz.get("densidad_maestra", 10.0)
    nuevo_peso = st.number_input("Ajustar Densidad (ppg)", 8.0, 18.0, dens_actual)
    
    if st.button("⚗️ Tratar Lodo"):
        piz["densidad_maestra"] = nuevo_peso
        st.info(f"Densidad ajustada a {nuevo_peso} ppg. Recalculando ECD...")

with tab4:
    st.header("🛰️ Dirección de Pozo")
    inc_ajuste = st.select_slider("Corregir Inclinación", options=["Bajar (-)", "Mantener", "Subir (+)"], value="Mantener")
    
    if inc_ajuste == "Subir (+)":
        piz["profundidad_actual"] -= 0.5 # Sube hacia el techo (TVD menor)
    elif inc_ajuste == "Bajar (-)":
        piz["profundidad_actual"] += 0.5 # Baja hacia el piso (TVD mayor)
        
    st.metric("Posición Actual TVD", f"{piz['profundidad_actual']:.2f} m")

# --- 1. LÓGICA DE FALLAS Y TIEMPO ---
if 'inicio_falla' not in st.session_state:
    st.session_state.inicio_falla = None

ultima_falla_segura = st.session_state.get("ultima_falla", time.time())

if time.time() - ultima_falla_segura > 300:
    if random.random() < 0.3: 
        fallas = ["KICK", "PERDIDA", "FALLA BOMBA", "PEGAMIENTO"]
        piz["evento_activo"] = random.choice(fallas)
        st.session_state.ultima_falla = time.time()
        st.session_state.inicio_falla = time.time()
  
# --- 2. PANEL DE ALERTAS (VISIBLES EN TODA LA APP) ---
if piz.get("evento_activo"):
    # Si por algún motivo no se inició el tiempo, lo iniciamos ahora
    if st.session_state.inicio_falla is None:
        st.session_state.inicio_falla = time.time()
        
    tiempo_transcurrido = int(time.time() - st.session_state.inicio_falla)
    
    col_err1, col_err2 = st.columns([3, 1])
    with col_err1:
        st.error(f"🚨 ¡FALLA ACTIVA: {piz['evento_activo']}!")
        # Lógica dinámica de la falla
        if piz["evento_activo"] == "KICK":
            piz["presion_base"] += 0.5
            piz["piletas_nivel"] += 0.1
        elif piz["evento_activo"] == "PERDIDA":
            piz["piletas_nivel"] -= 0.1
            
    with col_err2:
        st.metric("⏱️ Tiempo Reacción", f"{tiempo_transcurrido} s")

    if tiempo_transcurrido > 45:
        st.error("💥 ¡DESCONTROL DEL POZO! Tardaste demasiado.")
        st.stop()

# --- 3. CONTENIDO DE LAS PESTAÑAS (TABS) ---
with tab1:
    st.subheader("📊 Panel de Control Principal")
    # ... tus otros gráficos ...
    st.divider()
    st.subheader("🏆 Ranking de Operadores (Top Mendoza)")
    data_ranking = {
        "Alumno": ["Fabricio", "Alumno A", "Alumno B"],
        "Reacción (s)": [12, 18, 25],
        "Costo (USD)": [15000, 18200, 22100]
    }
    st.table(data_ranking)

with tab2:
    st.header("🛡️ Seguridad de Pozo (BOP)")
    if piz["evento_activo"] == "KICK":
        if st.button("✅ CERRAR POZO (Driller's Method)", type="primary"):
            piz["evento_activo"] = None
            st.session_state.inicio_falla = None
            st.balloons()
            st.success("🎯 ¡KICK CONTROLADO!")

with tab3:
    st.header("🧪 Sistema de Circulación")
    # Consolidamos la métrica de piletas aquí
    st.metric("📦 Volumen en Piletas", f"{piz.get('piletas_nivel', 500):.1f} bbl")
    
    if piz["evento_activo"] == "PERDIDA":
        if st.button("🧪 Bombear Píldora LCM"):
            piz["evento_activo"] = None
            st.session_state.inicio_falla = None
            st.success("✅ Pérdida sellada exitosamente")
            
# --- SISTEMA DE EMISIÓN DE DOCUMENTOS MENFA (ESTILO INSTITUCIONAL NARANJA) ---
st.write("---") 
st.header("🎓 Gestión de Certificados y Reportes")

# 1. Aseguramos que existan las variables de memoria
if "pdf_cert_final" not in st.session_state:
    st.session_state.pdf_cert_final = None

# 2. SECCIÓN CERTIFICADO
col1, col2 = st.columns(2)

with col1:
    alumno = st.text_input("Nombre del Alumno:", key="input_cert_nombre", placeholder="Ej: JUAN PEREZ")
    
    if st.button("📌 1. Generar Certificado de Participación"):
        if alumno:
            try:
                import unicodedata
                from fpdf import FPDF
                from datetime import datetime
                
                # Limpieza de nombre (Mayúsculas y sin acentos para evitar errores de librería)
                n_limpio = ''.join(c for c in unicodedata.normalize('NFD', alumno) if unicodedata.category(c) != 'Mn').upper()
                
                # Configuración: Horizontal (L), A4
                f_pdf = FPDF(orientation='L', unit='mm', format='A4')
                f_pdf.add_page()
                
                # --- FONDO DE COLOR (Simulando el naranja de la imagen) ---
                f_pdf.set_fill_color(255, 120, 0)  # Naranja vibrante MENFA
                f_pdf.rect(0, 0, 297, 210, 'F')
                
                # --- DETALLES DE DISEÑO (Triángulos oscuros en las esquinas como el modelo) ---
                f_pdf.set_fill_color(10, 30, 60) # Azul muy oscuro
                f_pdf.polygon([(0,0), (80,0), (0,80)], fill=True) # Esquina sup izq
                f_pdf.polygon([(297,210), (217,210), (297,130)], fill=True) # Esquina inf der

                # --- ENCABEZADO ---
                f_pdf.ln(25)
                f_pdf.set_font("Arial", 'B', 24)
                f_pdf.set_text_color(255, 255, 255) # Texto Blanco
                f_pdf.cell(0, 10, "MENFA CAPACITACIONES", ln=True, align='C')
                
                # --- TÍTULO ---
                f_pdf.ln(15)
                f_pdf.set_font("Arial", '', 18)
                f_pdf.cell(0, 10, "Certificado de finalización", ln=True, align='C')
                f_pdf.set_font("Arial", 'B', 20)
                f_pdf.cell(0, 10, "Participación en el Simulador de Perforaciòn", ln=True, align='C')
                
                # --- NOMBRE DEL ALUMNO (Destacado en Blanco) ---
                f_pdf.ln(15)
                f_pdf.set_font("Arial", 'B', 45)
                f_pdf.cell(0, 30, n_limpio, ln=True, align='C')
                
                # --- TEXTO DESCRIPTIVO ---
                f_pdf.ln(10)
                f_pdf.set_font("Arial", '', 15)
                texto = "Entrenamiento práctico intensivo en el Simulador de Perforación Avanzada"
                f_pdf.cell(0, 10, texto, ln=True, align='C')
                
                # --- FECHA ---
                f_pdf.ln(5)
                fecha_texto = datetime.now().strftime("%B %d, %Y").capitalize()
                f_pdf.set_font("Arial", '', 12)
                f_pdf.cell(0, 10, fecha_texto, ln=True, align='C')
                
                # --- FIRMA (ESTILO FABRICIO PIZZOLATO) ---
                f_pdf.set_xy(0, 170)
                f_pdf.set_font("Arial", 'B', 16)
                f_pdf.cell(0, 10, "Fabricio Pizzolato", ln=True, align='C')
                f_pdf.set_font("Arial", '', 11)
                f_pdf.cell(0, 5, "Dirección General - MENFA", ln=True, align='C')

                # --- PROCESAMIENTO DE BYTES (Anti-error bytearray) ---
                pdf_out = f_pdf.output(dest='S')
                if isinstance(pdf_out, str):
                    st.session_state.pdf_cert_final = pdf_out.encode('latin-1', 'replace')
                else:
                    st.session_state.pdf_cert_final = bytes(pdf_out)
                
                st.success(f"✅ Certificado de {n_limpio} generado correctamente.")
                st.rerun() 

            except Exception as e:
                st.error(f"Error técnico al crear el PDF: {e}")
        else:
            st.warning("⚠️ Ingresá el nombre del alumno para habilitar la generación.")

with col2:
    if st.session_state.pdf_cert_final is not None:
        st.write("###") # Espaciador
        st.download_button(
            label="📥 DESCARGAR CERTIFICADO PDF",
            data=st.session_state.pdf_cert_final,
            file_name=f"Certificado_MENFA_{alumno.replace(' ', '_')}.pdf",
            mime="application/pdf",
            key="btn_descarga_final"  # <--- Asegurate que termine así
        )
# --- BOTÓN DE CIERRE DE SESIÓN / INSTRUCTOR ---
st.sidebar.divider()
with st.sidebar.expander("🔐 Panel del Instructor"):
    st.write("Uso exclusivo para finalizar la jornada de capacitación.")
    if st.button("🏁 DAR POR TERMINADA LA CLASE", use_container_width=True, type="secondary"):
        # 1. Limpiamos las variables críticas
        st.session_state.pizarra["evento_activo"] = None
        st.session_state.pizarra["rpm_maestro"] = 0
        st.session_state.pizarra["caudal_maestro"] = 0
        st.session_state.pizarra["piletas_nivel"] = 500.0
        st.session_state.pizarra["profundidad_actual"] = 2500.0
        
        # 2. Reseteamos cronómetros
        st.session_state.ultima_falla = time.time()
        st.session_state.inicio_falla = None
        st.session_state.tiempo_respuesta = 0
        
        # 3. Mensaje de despedida y reinicio
        st.success("✅ Clase finalizada. Sistema reseteado para el próximo turno.")
        time.sleep(2) # Pausa para que el instructor vea el mensaje
        st.rerun()

from weasyprint import HTML
import os

# Definición del contenido HTML para el manual técnico
html_content = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>
        @page {
            size: A4;
            margin: 20mm;
            background-color: #ffffff;
            @bottom-right {
                content: "Página " counter(page) " de " counter(pages);
                font-size: 9pt;
                color: #555;
            }
        }
        body {
            font-family: 'Helvetica', 'Arial', sans-serif;
            color: #333;
            line-height: 1.6;
            margin: 0;
            padding: 0;
        }
        .header-banner {
            background-color: #1a3c5e;
            color: white;
            padding: 30pt;
            text-align: center;
            margin-bottom: 30pt;
        }
        h1 { margin: 0; font-size: 24pt; text-transform: uppercase; letter-spacing: 2px; }
        h2 { 
            color: #1a3c5e; 
            border-left: 5px solid #1a3c5e; 
            padding-left: 10pt; 
            margin-top: 25pt;
            font-size: 16pt;
            page-break-after: avoid;
        }
        h3 { color: #2c5d8f; font-size: 13pt; margin-top: 15pt; }
        .info-box {
            background-color: #f4f7f9;
            border: 1px solid #d1d9e1;
            padding: 15pt;
            margin: 15pt 0;
            border-radius: 4px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15pt 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 10pt;
            text-align: left;
            font-size: 10pt;
        }
        th { background-color: #f2f2f2; color: #1a3c5e; }
        .formula {
            font-family: 'Courier New', monospace;
            background-color: #222;
            color: #00ff00;
            padding: 12pt;
            display: block;
            margin: 10pt 0;
            border-radius: 3px;
            font-weight: bold;
        }
        .footer {
            margin-top: 50pt;
            text-align: center;
            font-size: 10pt;
            color: #777;
            border-top: 1px solid #eee;
            padding-top: 20pt;
        }
        .logo-text {
            font-weight: bold;
            font-size: 18pt;
            color: #1a3c5e;
            margin-bottom: 5pt;
        }
    </style>
</head>
<body>
    <div class="header-banner">
        <div class="logo-text" style="color: white;">IPCL MENFA</div>
        <h1>Manual Técnico del Simulador</h1>
        <p>Normas, Fórmulas de Perforación y Control de Pozos</p>
    </div>

    <div class="info-box">
        <strong>Instructor:</strong> Fabricio<br>
        <strong>Institución:</strong> IPCL MENFA - Mendoza, Argentina<br>
        <strong>Materia:</strong> Simulación de Operaciones de Perforación y Control de Pozos
    </div>

    <h2>1. Marco Normativo Internacional</h2>
    <p>El simulador integra los procedimientos estandarizados por las organizaciones líderes de la industria petrolera mundial para garantizar operaciones seguras en yacimientos convencionales y no convencionales (Vaca Muerta).</p>
    <ul>
        <li><strong>API RP 59:</strong> Prácticas recomendadas para operaciones de control de pozos.</li>
        <li><strong>API Standard 53:</strong> Requisitos para sistemas de equipos de control de presión (BOP).</li>
        <li><strong>ISO 13533:</strong> Especificaciones para equipos de cabezal de pozo y árboles de navidad.</li>
        <li><strong>Estándares IADC:</strong> Protocolos de reporte y seguridad en el equipo de perforación.</li>
    </ul>

    <h2>2. Fórmulas de Perforación (Drilling)</h2>
    <p>Utilizadas para el cálculo de los parámetros operativos que el alumno debe ajustar en la consola.</p>
    
    <h3>Factor de Flotación (FF)</h3>
    <div class="formula">FF = (65.5 - Densidad Lodo ppg) / 65.5</div>
    
    <h3>Peso sobre el Trépano Real (WOB)</h3>
    <div class="formula">WOB_real = Peso_Sarta_Aire * FF</div>

    <h3>Caudal de Bomba Triplex (GPM)</h3>
    <div class="formula">GPM = 0.000243 * (ID_Camisa^2) * Carrera * Eficiencia * SPM</div>

    <h2>3. Control de Pozos (Well Control)</h2>
    <p>Cálculos críticos ante la detección de un ingreso de fluido de formación (Kick).</p>

    <h3>Presión Hidrostática (Ph)</h3>
    <div class="formula">Ph (psi) = Densidad (ppg) * 0.052 * TVD (ft)</div>

    <h3>Presión de Fondo de Pozo (BHP)</h3>
    <div class="formula">BHP = Ph + SIDPP (Presión de Cierre en TP)</div>

    <h3>Densidad de Matar (KMW)</h3>
    <div class="formula">KMW = (SIDPP / (0.052 * TVD)) + Densidad_Actual</div>

    <h2>4. Geonavegación (Geonav)</h2>
    <p>Cálculos para el mantenimiento de la trayectoria en la ventana productiva.</p>
    
    <h3>Severidad de Pata de Perro (DLS)</h3>
    <div class="formula">DLS = (Grados de Cambio / Longitud) * 100</div>

    <div class="footer">
        <p>Este documento es propiedad académica de IPCL MENFA.<br>
        Prohibida su reproducción total o parcial sin autorización del instructor.</p>
    </div>
</body>
</html>
"""

# Generación del PDF
output_filename = "manual_tecnico_simulador_menfa_v1.pdf"
HTML(string=html_content).write_pdf(output_filename)
