import streamlit as st
import pandas as pd
import numpy as np
import time
import random
import plotly.graph_objects as go
import base64
import os
from datetime import datetime
from fpdf import FPDF
from streamlit_autorefresh import st_autorefresh

# --- 0. CONFIGURACIÓN DE PÁGINA (DEBE SER LA PRIMERA LÍNEA DE ST) ---
st.set_page_config(page_title="MENFA 3.0 - Simulador", layout="wide", page_icon="🏗️")

# --- 1. INICIALIZACIÓN DE VARIABLES DE SESIÓN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario = ""
    st.session_state.rol = None
if "penalizaciones" not in st.session_state:
    st.session_state.penalizaciones = []

# --- 2. CARÁTULA DE INGRESO ---
if not st.session_state.autenticado:
    # Contenedor para el logo y título principal
    col_izq, col_logo, col_der = st.columns([1, 2, 1])
    
    with col_logo:
        # LÓGICA DEL LOGO:
        if os.path.exists("logo_menfa.png"):
            st.image("logo_menfa.png", use_container_width=True)
        else:
            # Si no está el archivo, mostramos un título grande
            st.markdown("<h1 style='text-align: center;'>🏗️ MENFA</h1>", unsafe_allow_html=True)
        
        st.markdown("<h2 style='text-align: center; color: #004280;'>SISTEMA DE ENTRENAMIENTO v3.0</h2>", unsafe_allow_html=True)
        st.divider()

    # Tabs de acceso
    tab1, tab2 = st.tabs(["🎓 Acceso Alumnos", "👨‍🏫 Acceso Instructor"])
    
    with tab1:
        with st.form("login_alumno"):
            nombre_alumno = st.text_input("Nombre y Apellido")
            clave_alumno = st.text_input("Contraseña de Curso", type="password")
            if st.form_submit_button("Ingresar al Simulador", use_container_width=True):
                if nombre_alumno and clave_alumno == "alumno2026":
                    st.session_state.autenticado = True
                    st.session_state.usuario = nombre_alumno
                    st.session_state.rol = "alumno"
                    st.rerun()
                else:
                    st.error("Datos incorrectos")

    with tab2:
        with st.form("login_instructor"):
            clave_inst = st.text_input("Clave de Instructor", type="password")
            if st.form_submit_button("Acceso Administrativo", use_container_width=True):
                if clave_inst == "menfa2026":
                    st.session_state.autenticado = True
                    st.session_state.usuario = "Inst. Fabricio Pizzolato"
                    st.session_state.rol = "instructor"
                    st.rerun()
                else:
                    st.error("Clave incorrecta")
    
    # Detenemos la ejecución aquí para que no muestre el simulador si no está logueado
    st.stop()

# --- 3. DESDE AQUÍ EMPIEZA EL SIMULADOR (LOGUEADO) ---
# ... resto de tu código
# --- 1. INICIALIZACIÓN DE VARIABLES DE SESIÓN (OBLIGATORIO) ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario = ""
    st.session_state.rol = None
 # Inicializar banderas de error si no existen
if "error_cierre_activo" not in st.session_state:
    st.session_state.error_cierre_activo = False
if "error_geo_activo" not in st.session_state:
    st.session_state.error_geo_activo = False
if "error_tanques_activo" not in st.session_state:
    st.session_state.error_tanques_activo = False   
# AGREGÁ ESTA LÍNEA AQUÍ ARRIBA:# --- EJEMPLO: CONTROL DE CIERRE DE POZO ---
# --- DEFINICIÓN DE VARIABLES DE SEGURIDAD (Agregá esto arriba de la línea 87) ---

# 1. Obtenemos el valor del slider de tanques (asegurate que el nombre coincida)
ganancia_tanques = st.session_state.get('nivel_tanques', 0.0) 

# 2. Definimos el límite de seguridad (ejemplo: 10 barriles)
limite_seguridad = 10.0 

# 3. Estado del BOP (podes usar un checkbox o un botón)
bop_cerrado = st.session_state.get('bop_cerrado', False)

# --- AHORA SÍ, TU LÓGICA DE LA LÍNEA 87 NO FALLARÁ ---
if ganancia_tanques > limite_seguridad and not bop_cerrado:
    if not st.session_state.get('error_cierre_activo', False):
        st.session_state.penalizaciones.append({
            "Hora": datetime.now().strftime("%H:%M:%S"),
            "Infracción": "No detectó el cierre de pozo a tiempo (Kick)",
            "Gravedad": "CRÍTICA"
        })
        st.session_state.error_cierre_activo = True
# --- VARIABLES DE TRAYECTORIA (Agregá esto arriba de la línea 107) ---
# 1. Calculamos la desviación (ejemplo: diferencia entre profundidad real y objetivo)
# Si tenés un slider de profundidad, usalo aquí:
profundidad_objetivo = 2500.0 
profundidad_actual = st.session_state.get('profundidad', 0.0)

# La desviación es la resta de ambas
desviacion_vertical = profundidad_actual - profundidad_objetivo

# 2. Margen de tolerancia (ejemplo: 5 metros para no salir de la formación)
margen_formacion = 5.0
# --- AHORA SÍ, LA LÍNEA 107 FUNCIONARÁ ---
if abs(desviacion_vertical) > margen_formacion:
    if not st.session_state.get('error_geo_activo', False):
        st.session_state.penalizaciones.append({
            "Hora": datetime.now().strftime("%H:%M:%S"),
            "Infracción": "Error de Geonavegación: Salida de zona productiva",
            "Gravedad": "CRÍTICA"
        })
        st.session_state.error_geo_activo = True
else:
    st.session_state.error_geo_activo = False        
# --- EJEMPLO: GEONAVEGACIÓN ---
if abs(desviacion_vertical) > margen_formacion:
    if not st.session_state.error_geo_activo:
        st.session_state.penalizaciones.append({
            "Hora": datetime.now().strftime("%H:%M:%S"),
            "Infracción": "Error de Geonavegación: Fuera de formación",
            "Gravedad": "CRÍTICA"
        })
        st.session_state.error_geo_activo = True
else:
    st.session_state.error_geo_activo = False
if "penalizaciones" not in st.session_state:
    st.session_state.penalizaciones = []
def generar_certificado_final(nombre, puntaje, nivel, fecha):
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Marco y Estilo
        pdf.set_draw_color(0, 66, 128)
        pdf.rect(5, 5, 200, 287)
        
        pdf.set_font("Arial", 'B', 24)
        pdf.set_text_color(0, 66, 128)
        pdf.cell(0, 30, "MENFA CAPACITACIONES", 0, 1, 'C')
        
        pdf.set_font("Arial", 'B', 18)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 15, "CERTIFICADO DE COMPETENCIA", 0, 1, 'C')
        pdf.ln(10)
        
        # Eliminamos tildes para evitar errores de encoding en FPDF
        nombre_limpio = nombre.replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u").upper()
        
        pdf.set_font("Arial", '', 14)
        texto_cuerpo = f"Se hace entrega del presente a {nombre_limpio}, por haber completado el entrenamiento en el Simulador de Perforacion Avanzada 3.0."
        pdf.multi_cell(0, 10, texto_cuerpo, align='C')
        
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"Resultado: {puntaje}/100", 0, 1, 'C')
        pdf.cell(0, 10, f"Calificacion: {nivel}", 0, 1, 'C')
        
        pdf.ln(20)
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, f"Fecha de emision: {fecha}", 0, 1, 'C')
        pdf.cell(0, 10, "Firma del Instructor: Fabricio Pizzolato", 0, 1, 'C')
        
        # --- CORRECCIÓN DEL ERROR DE ENCODING ---
        resultado = pdf.output(dest='S')
        
        # Si el resultado ya son bytes (o bytearray), lo devolvemos directo
        if isinstance(resultado, (bytes, bytearray)):
            return bytes(resultado)
        # Si es un string, lo codificamos
        return resultado.encode('latin-1')
        
    except Exception as e:
        return f"Error interno: {str(e)}"
# --- 1. DEFINICIÓN DE FUNCIONES (DEBE IR ARRIBA DE TODO) ---
def reproducir_alarma_local():
    archivo_audio = "assets/alarma.mp3"
    if os.path.exists(archivo_audio):
        with open(archivo_audio, "rb") as f:
            data = f.read()
            base64_audio = base64.b64encode(data).decode()
            html_audio = f"""
                <audio autoplay loop>
                    <source src="data:audio/mp3;base64,{base64_audio}" type="audio/mp3">
                </audio>
            """
            st.components.v1.html(html_audio, height=0)
    else:
        # Esto te avisará si el archivo no está en GitHub
        st.sidebar.error("⚠️ No se encontró 'assets/alarma.mp3'")

# --- 2. EL RESTO DE TU LÓGICA (PIZARRA, LOGIN, ETC.) ---
@st.cache_resource
def obtener_pizarra():
    return {
        "alarma_activa": False,
        "presion_base": 2500,
        "incremento_kick": 0,
        "mensaje_inst": "Operación Normal"
    }

pizarra = obtener_pizarra()

# ... (Aquí sigue tu código de Login y la línea 96 que ahora sí va a funcionar)
# 1. LA PIZARRA (Base de datos compartida en el servidor)
@st.cache_resource
def obtener_pizarra():
    return {
        "alarma_activa": False,
        "presion_base": 2500,
        "incremento_kick": 0,
        "mensaje_inst": "Operación Normal",
        "formacion": "Cacheuta"
    }

pizarra = obtener_pizarra()
# --- 8. CARÁTULA DE INGRESO CON CONTRASEÑA DOBLE ---
if not st.session_state.autenticado:
    # Centramos el logo y el título
    col_izq, col_logo, col_der = st.columns([1, 2, 1])
    
    with col_logo:
        # Buscamos el logo en las rutas posibles
        if os.path.exists("logo_menfa.png"):
            st.image("logo_menfa.png", use_container_width=True)
        elif os.path.exists("assets/logo_menfa.png"):
            st.image("assets/logo_menfa.png", use_container_width=True)
        else:
            st.markdown("<h1 style='text-align: center;'>🏗️</h1>", unsafe_allow_html=True)
        
        st.markdown("<h2 style='text-align: center; color: #004280;'>MENFA 3.0 - ACCESO AL SISTEMA</h2>", unsafe_allow_html=True)
        st.write("<br>", unsafe_allow_html=True)

    # Tabs de acceso
    tab1, tab2 = st.tabs(["🎓 Acceso Alumnos", "👨‍🏫 Acceso Instructor"])
    
    with tab1:
        with st.form("login_alumno"):
            st.subheader("Ingreso de Estudiante")
            nombre_alumno = st.text_input("Nombre y Apellido")
            clave_alumno = st.text_input("Contraseña de Curso", type="password", help="Solicite la clave al instructor")
            
            if st.form_submit_button("Validar e Ingresar", use_container_width=True):
                # Podés cambiar 'alumno2026' por la clave que prefieras
                if nombre_alumno and clave_alumno == "alumno2026":
                    st.session_state.autenticado = True
                    st.session_state.usuario = nombre_alumno
                    st.session_state.rol = "alumno"
                    st.success(f"Bienvenido {nombre_alumno}")
                    st.rerun()
                elif not nombre_alumno:
                    st.error("Por favor, ingrese su nombre para el certificado.")
                else:
                    st.error("Contraseña de alumno incorrecta.")

    with tab2:
        with st.form("login_instructor"):
            st.subheader("Panel de Control Maestro")
            clave_inst = st.text_input("Clave de Instructor", type="password")
            
            if st.form_submit_button("Acceder al Sistema", use_container_width=True):
                if clave_inst == "menfa2026":
                    st.session_state.autenticado = True
                    st.session_state.usuario = "Inst. Fabricio Pizzolato"
                    st.session_state.rol = "instructor"
                    st.success("Acceso concedido, Fabricio.")
                    st.rerun()
                else:
                    st.error("Clave de instructor incorrecta.")

    # IMPORTANTE: Detener ejecución aquí para bloquear el simulador
    st.stop()

# 3. SINCRONIZACIÓN (1 segundo para máxima velocidad)
st_autorefresh(interval=1000, key="latido_menfa")

# --- 4. PROCEDIMIENTO COMÚN (Lo que ven ambos después del Login) ---

st.sidebar.title(f"Sesión: {st.session_state.usuario}")
st.sidebar.write(f"Rol: **{st.session_state.rol.upper()}**")

# PANEL DEL INSTRUCTOR (Solo Fabricio puede modificar datos)
if st.session_state.rol == "instructor":
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎮 PANEL DE MODIFICACIÓN")
    
    # Modificar presión base del alumno en tiempo real
    pizarra["presion_base"] = st.sidebar.number_input("Presión Base (PSI)", value=pizarra["presion_base"], step=100)
    
    # Liberar o Activar Alertas
    if not pizarra["alarma_activa"]:
        if st.sidebar.button("🚨 LANZAR ALERTA", type="primary"):
            pizarra["alarma_activa"] = True
            pizarra["mensaje_inst"] = "¡KICK DETECTADO! CIERRE BOP."
    else:
        if st.sidebar.button("✅ LIBERAR ALERTA"):
            pizarra["alarma_activa"] = False
            pizarra["incremento_kick"] = 0
            pizarra["mensaje_inst"] = "Operación Normal"
# --- DENTRO DE LA VISTA DEL ALUMNO ---
if pizarra["alarma_activa"]:
    st.error(f"🔥 {pizarra['mensaje_inst']}")
    
    # Llamamos a la alarma sonora de tu carpeta assets
    reproducir_alarma_local()
    
    # EL BOTÓN CLAVE: Este botón afecta a la PIZARRA global
    if st.button("🔴 CERRAR BOP Y ESTABILIZAR", type="primary", use_container_width=True):
        pizarra["alarma_activa"] = False  # Esto apaga la luz roja para TODOS
        pizarra["mensaje_inst"] = f"✅ Pozo controlado por: {st.session_state.usuario}"
        pizarra["incremento_kick"] = 0    # Resetea la presión
        st.success("¡Operación exitosa! Pozo bajo control.")
        st.rerun() # Refresca para que deje de sonar la alarma
    else:
       st.success(f"✅ Estado: {pizarra['mensaje_inst']}")
       st.title("Simulador de Perforación en Tiempo Real")

# Lógica de incremento si hay Kick
if pizarra["alarma_activa"]:
    pizarra["incremento_kick"] += 10 # La presión sube sola mientras no se libere

presion_total = pizarra["presion_base"] + pizarra["incremento_kick"]

col1, col2 = st.columns(2)
col1.metric("SIDP (Tubería)", f"{presion_total} PSI", delta=f"+{pizarra['incremento_kick']}" if pizarra["alarma_activa"] else None)
col2.metric("SICP (Anular)", f"{presion_total + 200} PSI")

if pizarra["alarma_activa"]:
    st.error(f"⚠️ {pizarra['mensaje_inst']}")
    # Aquí puedes agregar el código de la sirena que vimos antes
else:
    st.success("✅ Sistema Estable - Esperando parámetros del Instructor")


import base64
import os

# 1. FUNCIÓN PARA LEER EL ARCHIVO LOCAL Y GENERAR EL AUDIO
def reproducir_alarma_local():
    archivo_audio = "assets/alarma.mp3"
    
    if os.path.exists(archivo_audio):
        with open(archivo_audio, "rb") as f:
            data = f.read()
            # Convertimos el audio a base64 para que Streamlit lo "inyecte" en el navegador
            base64_audio = base64.b64encode(data).decode()
            
            html_audio = f"""
                <audio autoplay loop>
                    <source src="data:audio/mp3;base64,{base64_audio}" type="audio/mp3">
                </audio>
            """
            st.components.v1.html(html_audio, height=0)
    else:
        # Si el archivo no está, te avisa en la consola de Streamlit para que no explote
        st.error("Archivo 'assets/alarma.mp3' no encontrado en GitHub.")

# 2. APLICACIÓN EN LA VISTA DEL ALUMNO
# Buscá la parte donde el alumno reacciona al Kick:

if pizarra["alarma_activa"]:
    st.error(f"🔥 {pizarra['mensaje_inst']}")
    
    # ¡Aquí llamamos a tu archivo de assets!
    reproducir_alarma_local()
    
    st.toast("🚨 ¡Surgencia en progreso!", icon="⚠️")

# --- INICIALIZACIÓN DE ESTADOS DE SEGURIDAD ---
if 'evento_activo' not in st.session_state:
    st.session_state.evento_activo = None
if 'presion_vibracion' not in st.session_state:
    st.session_state.presion_vibracion = 0.0
if 'vibracion_reloj' not in st.session_state:
    st.session_state.vibracion_reloj = time.time()
# Inicialización de seguridad al inicio del script
# Inicialización de seguridad (Línea 10 aprox.)
profundidad_actual = 0 
temp_fondo = 20 # Temperatura de superficie por defecto
rpm_actual = 0
wob = 0
rop_actual = 0
vibracion_axial = 0
# --- INICIALIZACIÓN GLOBAL ---
if 'vibracion_axial' not in st.session_state:
    vibracion_axial = 0.1
if 'd_exp_norm' not in st.session_state:
    d_exp_norm = 0.0
if 'errores_iadc' not in st.session_state:
    st.session_state.errores_iadc = []
# --- 1. ACCESO RÁPIDO AL ESTADO DE LA SESIÓN ---
# Esto le dice a Python que 's' es lo mismo que 'st.session_state'
s = st.session_state

# --- 2. INICIALIZACIÓN DE VARIABLES (Si no existen) ---
if "depth" not in s:
    s["depth"] = 2500.0  # Profundidad inicial de ejemplo
    # --- EN LA BARRA LATERAL (Sidebar) ---
profundidad_actual = st.sidebar.slider("Profundidad Actual (m)", 0, 5000, 1000)

# --- AHORA SÍ, REALIZÁS EL CÁLCULO ---
# Pegá esto justo después del slider:
temp_fondo = 20 + (0.03 * profundidad_actual)
# --- INICIALIZACIÓN DE VARIABLES DE LODO Y PARÁMETROS ---
variables_iniciales = {
    'retorno_lodo': 100.0,      # El retorno normal es 100%
    'nivel_cajones': 500.0,     # Nivel inicial en bbl o m3
    'presion_bombeo': 0.0,
    'presion_anular': 0.0,
    'profundidad_actual': 0.0,
    'evento_activo': None,
    'vibracion_reloj': time.time(),
    'presion_vibracion': 0.0
}

for clave, valor in variables_iniciales.items():
    if clave not in st.session_state:
        st.session_state[clave] = valor
# --- MOTOR DE CÁLCULOS INTEGRADO (Reemplaza al archivo externo) ---
def calcular_presiones_fondo(mw, depth_m, flow_gpm):
    """
    Calcula la Presión de Fondo (BHP) y la ECD.
    Fórmula: P(psi) = 0.052 * Densidad(ppg) * Profundidad(ft)
    """
    tvd_ft = depth_m * 3.28084  # Conversión de metros a pies
    
    # 1. Presión Hidrostática Estática
    p_hidro = 0.052 * mw * tvd_ft
    
    # 2. Pérdida por Fricción Anular (Simplificada para simulación)
    # A mayor caudal y profundidad, mayor es la fricción
    p_friccion = (flow_gpm**1.8 * depth_m) / 450000
    
    bhp_total = p_hidro + p_friccion
    
    # 3. Cálculo de ECD (Equivalent Circulating Density)
    # Es la densidad que "siente" el pozo debido a la fricción
    ecd = mw + (p_friccion / (0.052 * tvd_ft))
    
    return bhp_total, ecd
# Configuración de la cabina
st.set_page_config(page_title="Simulador Perf. Avanzada v3.0", layout="wide")
# Definir todo lo que falta antes de mostrarlo
vibracion_axial = (wob / 5) * (rpm_actual / 100) if rpm_actual > 0 else 0.1
d_exp_norm = (np.log10(rop_actual/(60*rpm_actual)) / np.log10(12*wob/(10**6*5.875))) * (9/densidad_lodo) if rpm_actual > 0 else 0
temp_fondo = 20 + (0.03 * profundidad_actual)
# ... cualquier otro cálculo (CCI, ECD) ...

# --- LÓGICA DE CÁLCULOS ---
def calcular_metricas(presion, caudal, densidad):
    # Potencia Hidráulica (HHP)
    hhp = (presion * caudal) / 1714
    # Fuerza de Impacto (Impact Force - Aproximada)
    # IF = (Densidad * Caudal * Velocidad) / 1930 -> Simplificado para simulador
    if_force = (densidad * caudal * 0.05) * (caudal / 100) 
    return round(hhp, 2), round(if_force, 2)
# --- LOGO EN LA PARTE SUPERIOR IZQUIERDA (SIDEBAR) ---
try:
    # 'use_container_width=True' hace que el logo se ajuste al ancho de la barra lateral
    st.sidebar.image("assets/logo_menfa.png", use_container_width=True)
except Exception as e:
    # Si el logo falla, ponemos un texto elegante para que no quede vacío
    st.sidebar.markdown("<h2 style='text-align: center; color: #004280;'>🏗️ MENFA 3.0</h2>", unsafe_allow_html=True)

st.sidebar.markdown("---") # Una línea divisoria para separar el logo de los mandos
# --- SIDEBAR (CONTROLES) ---
st.sidebar.header("🕹️ Mandos de la Cabina")
densidad = st.sidebar.slider("Densidad del Lodo (ppg)", 8.0, 19.0, 10.5)
caudal = st.sidebar.slider("Caudal de Bomba (GPM)", 100, 1200, 500)
presion = st.sidebar.number_input("Presión de Standpipe (PSI)", 500, 5000, 3200)
rpm_actual = st.sidebar.slider("Velocidad de Rotación (RPM)", 0, 150, 60)
wob = st.sidebar.slider("Peso sobre la Mecha (WOB - klbs)", 0, 50, 15)
rop_actual = st.sidebar.slider("Tasa de Penetración (ROP - m/h)", 0, 40, 10)
densidad_lodo = st.sidebar.number_input("Densidad del Lodo (ppg)", 8.33, 18.0, 9.5)

hhp_val, if_val = calcular_metricas(presion, caudal, densidad)

# --- INTERFAZ GRÁFICA (GAUGES) ---
st.title("📟 Panel Integral de Perforación")
st.markdown("---")

def crear_reloj(valor, titulo, unidad, max_val, color):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = valor,
        title = {'text': f"<b>{titulo}</b><br><span style='font-size:0.7em'>{unidad}</span>"},
        gauge = {'axis': {'range': [0, max_val]}, 'bar': {'color': color}}
    ))
    fig.update_layout(height=220, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='rgba(0,0,0,0)')
    return fig

# Fila 1: Parámetros Mecánicos
col1, col2, col3 = st.columns(3)
with col1: st.plotly_chart(crear_reloj(18.5, "WOB", "Tons", 50, "#00d4ff"), use_container_width=True)
with col2: st.plotly_chart(crear_reloj(90, "RPM", "rev/min", 200, "#00ff88"), use_container_width=True)
with col3: st.plotly_chart(crear_reloj(12, "Torque", "kft-lb", 30, "#ffcc00"), use_container_width=True)

# Fila 2: Parámetros Hidráulicos
st.subheader("💧 Sistema de Circulación e Hidráulica")
col4, col5, col6 = st.columns(3)
with col4: st.plotly_chart(crear_reloj(presion, "Presión", "PSI", 5000, "#ff4b4b"), use_container_width=True)
with col5: st.plotly_chart(crear_reloj(hhp_val, "Potencia (HHP)", "hp", 2000, "#a64dff"), use_container_width=True)
with col6: st.plotly_chart(crear_reloj(if_val, "Impact Force", "lbs", 1500, "#ff8c00"), use_container_width=True)

# --- GRÁFICA DE TENDENCIA ---
st.divider()
st.subheader("📊 Historial de Limpieza y Penetración")
# Simulación de datos de tendencia
t = np.linspace(0, 20, 50)
rop = 10 + 5*np.sin(t/3) + (hhp_val/200) # La ROP sube si hay más HHP
fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(x=t, y=rop, name="ROP (m/h)", line=dict(color="#00ff88", width=3)))
fig_trend.update_layout(template="plotly_dark", height=300)
st.plotly_chart(fig_trend, use_container_width=True)

st.caption(f"Configuración guardada por @profesorpizzolato-art | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
# --- SECCIÓN DE CÁLCULOS AVANZADOS (Hidráulica y Seguridad) ---
def calcular_hidraulica(p, q, rho):
    # HHP: Potencia Hidráulica
    hhp = (p * q) / 1714
    # IF: Fuerza de Impacto (Libras fuerza)
    # Basado en una aproximación de boquillas estándar
    impact_force = 0.0182 * q * np.sqrt(rho * p)
    return round(hhp, 2), round(impact_force, 2)

# Interfaz de entrada en Sidebar para estos cálculos
st.sidebar.divider()
st.sidebar.subheader("🛡️ Límites de Seguridad")
p_max = st.sidebar.number_input("Presión Máxima (PSI)", value=4500)
q_caudal = st.sidebar.slider("Caudal Actual (GPM)", 100, 1000, 550)
lodo_rho = st.sidebar.number_input("Densidad Lodo (ppg)", value=10.5)

# Ejecutar cálculos
hhp_actual, if_actual = calcular_hidraulica(presion, q_caudal, lodo_rho)

# --- VISUALIZACIÓN DE HIDRÁULICA (6 INDICADORES) ---
st.header("📊 Monitoreo de Cabina en Tiempo Real")
fila1 = st.columns(3)
fila2 = st.columns(3)

# ... (Aquí irían tus gauges de WOB, RPM y Torque en fila1) ...

with fila2[0]:
    st.plotly_chart(crear_reloj(presion, "Presión Standpipe", "PSI", 5000, "#ff4b4b"), use_container_width=True)
with fila2[1]:
    st.plotly_chart(crear_reloj(hhp_actual, "Potencia (HHP)", "hp", 2000, "#a64dff"), use_container_width=True)
with fila2[2]:
    st.plotly_chart(crear_reloj(if_actual, "Impact Force", "lbs", 1500, "#ff8c00"), use_container_width=True)

# --- SISTEMA DE ALARMAS (Lógica al final) ---
st.divider()
st.subheader("🚨 Panel de Alarmas del Sistema")

col_a1, col_a2, col_a3 = st.columns(3)

with col_a1:
    if presion > p_max:
        st.error(f"⚠️ SOBREPRESIÓN: {presion} PSI (Límite: {p_max})")
    else:
        st.success("✅ Presión de Bomba Estable")

with col_a2:
    if hhp_actual < 500:
        st.warning("⚠️ BAJA POTENCIA: Limpieza de pozo ineficiente")
    else:
        st.success("✅ Hidráulica Óptima")

with col_a3:
    # Simulación de Torque excesivo
    torque_actual = 12 # Este valor vendría de tus datos
    if torque_actual > 25:
        st.error("🛑 ALTO TORQUE: Riesgo de pega de tubería")
    else:
        st.success("✅ Rotación Libre")

# --- RESUMEN DE OPERACIÓN ---
st.info(f"**Estado General:** Perforando a {q_caudal} GPM con una Fuerza de Impacto de {if_actual} lbs. El sistema está operando dentro de los márgenes de seguridad establecidos por @profesorpizzolato-art.")
# --- SECCIÓN DE ECONOMÍA Y EFICIENCIA ---
st.sidebar.divider()
st.sidebar.subheader("💰 Economía de Perforación")
costo_equipo = st.sidebar.number_input("Costo Rig (USD/hr)", value=1500)
costo_mecha = st.sidebar.number_input("Costo Mecha (USD)", value=15000)

# --- VALIDACIÓN DE SEGURIDAD ---
# Nos aseguramos de que rop sea un número y no una lista
rop_valor = float(rop[0]) if isinstance(rop, (list, np.ndarray)) else float(rop)

if rop_valor > 0:
    st.success(f"🚀 Perforando a {rop_valor:.2f} m/h")
    # Aquí va tu lógica de avance de metros
else:
    st.warning("⚠️ Sin avance. Verifique WOB y RPM.")

# --- BOTÓN DE REPORTE FINAL ---
st.divider()
col_rep1, col_rep2 = st.columns([3, 1])

with col_rep1:
    st.write("### 📝 Registro de Operaciones")
    data_log = pd.DataFrame({
        "Parámetro": ["WOB Máximo", "RPM Promedio", "HHP Final", "Impact Force"],
        "Valor": [f"25 Tons", f"95", f"{hhp_actual} hp", f"{if_actual} lbs"]
    })
    st.table(data_log)

with col_rep2:
    st.write("### Acciones")
    if st.button("📥 Descargar Reporte"):
        st.success("Reporte generado con éxito (Sim_Perf_v3)")
# --- SECCIÓN: SEGURIDAD Y VENTANA DE LODOS ---
st.divider()
st.header("🛡️ Seguridad Geomecánica: Ventana de Lodo")

col_geo1, col_geo2 = st.columns([1, 2])

with col_geo1:
    st.write("### Parámetros de Formación")
    profundidad_actual = st.number_input("Profundidad de Interés (m)", value=3500)
    presion_poro = st.slider("Gradiente Poro (ppg e)", 8.5, 12.0, 9.8)
    presion_fractura = st.slider("Gradiente Fractura (ppg e)", 12.5, 18.0, 15.5)
    
    # Métrica de Seguridad
    densidad_lodo = 12.2 # Este valor viene de tu sidebar anterior
    
    if densidad_lodo < presion_poro:
        st.error(f"🚨 ¡RIESGO DE BROTE (KICK)! Densidad < {presion_poro} ppg")
    elif densidad_lodo > presion_fractura:
        st.error(f"🚨 ¡RIESGO DE FRACTURA! Densidad > {presion_fractura} ppg")
    else:
        st.success("✅ Operando dentro de la Ventana de Lodo")

with col_geo2:
    # Generar Gráfica de Ventana de Lodos (Profundidad vs Densidad)
    z = np.linspace(0, 5000, 100)
    linea_poro = 8.5 + (z/5000) * 2
    linea_frac = 14 + (z/5000) * 3
    
    fig_window = go.Figure()
    
    # Área Segura (Ventana)
    fig_window.add_trace(go.Scatter(x=linea_poro, y=z, name="P. Poro", line=dict(color='red', dash='dash')))
    fig_window.add_trace(go.Scatter(x=linea_frac, y=z, name="P. Fractura", line=dict(color='orange')))
    
    # Punto Actual (Tu lodo)
    fig_window.add_trace(go.Scatter(x=[densidad_lodo], y=[profundidad_actual], 
                                    mode="markers+text", name="Estado Actual",
                                    text=["BIT"], textposition="top center",
                                    marker=dict(color='lime', size=15, symbol='star')))

    fig_window.update_layout(
        title="Gráfico de Ventana de Perforación",
        xaxis_title="Densidad Equivalente (ppg)",
        yaxis_title="Profundidad (m)",
        yaxis=dict(autorange="reversed"), # Las gráficas de pozo se ven de arriba hacia abajo
        template="plotly_dark",
        height=500
    )
    st.plotly_chart(fig_window, use_container_width=True)

# --- SECCIÓN: DINÁMICA DE FLUIDOS (ECD) ---
st.divider()
st.header("🌊 Dinámica de Circulación (ECD)")

col_ecd1, col_ecd2 = st.columns(2)

with col_ecd1:
    st.write("### Cálculo de Densidad Equivalente")
    # Parámetros para fricción (Simplificado para el simulador)
    viscosidad = st.slider("Viscosidad Plástica (cP)", 10, 60, 25)
    longitud_pozo = profundidad_actual # Tomado de la sección anterior
   
    # Fórmula simplificada de pérdida de carga anular (APL) en ppg
    # APL = (0.000077 * Densidad * Velocidad^2) / (D_hoyo - D_tuberia)
    # Aquí usamos una aproximación directa basada en Caudal y Viscosidad
    apl = (viscosidad * caudal / 2000) / 10 
    ecd = densidad_lodo + apl

    st.metric(label="ECD (Densidad Circulante)", value=f"{round(ecd, 2)} ppg", 
              delta=f"+{round(apl, 2)} ppg por fricción", delta_color="inverse")

with col_ecd2:
    # Indicador Visual de Seguridad del ECD
    fig_ecd = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = ecd,
        delta = {'reference': presion_fractura, 'position': "top"},
        title = {'text': "<b>ECD vs Fractura</b>"},
        gauge = {
            'axis': {'range': [8, 20]},
            'steps': [
                {'range': [0, presion_poro], 'color': "rgba(255, 0, 0, 0.3)"},
                {'range': [presion_poro, presion_fractura], 'color': "rgba(0, 255, 0, 0.2)"},
                {'range': [presion_fractura, 20], 'color': "rgba(255, 0, 0, 0.6)"}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': ecd
            }
        }
    ))
    fig_ecd.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
    st.plotly_chart(fig_ecd, use_container_width=True)

# --- ALERTA CRÍTICA DE ECD ---
if ecd >= presion_fractura:
    st.error(f"🛑 ¡FRACTURA INMINENTE! El ECD ({round(ecd,2)}) ha superado el límite de formación ({presion_fractura}). Reduzca el caudal o la viscosidad inmediatamente.")
elif ecd <= presion_poro:
    st.warning(f"⚠️ RIESGO DE SURGENCIA: El ECD es demasiado bajo para controlar la presión de poro.")

import random

# --- MOTOR DE EVENTOS Y FALLAS ---
st.sidebar.divider()
st.sidebar.subheader("🎲 Centro de Entrenamiento")
activar_fallas = st.sidebar.checkbox("Activar Fallas Aleatorias")

# Inicializar estados de falla
if 'falla_activa' not in st.session_state:
    st.session_state.falla_activa = "Normal"

if activar_fallas:
    if st.sidebar.button("Generar Evento Crítico"):
        fallas = ["Stuck Pipe", "Washout", "Worn Bit", "Normal"]
        st.session_state.falla_activa = random.choice(fallas)
    
    if st.sidebar.button("Resetear Sistema"):
        st.session_state.falla_activa = "Normal"

# --- LÓGICA DE IMPACTO DE FALLAS ---
msg_falla = ""
color_falla = "gray"

if st.session_state.falla_activa == "Stuck Pipe":
    torque_actual = 28.5 # Valor alto
    rpm_actual = 15 # Caída de rotación
    msg_falla = "⚠️ ALERTA: Torque excesivo detectado. ¡Posible Pega de Tubería!"
    color_falla = "red"
elif st.session_state.falla_activa == "Washout":
    presion = presion * 0.6 # Caída del 40% de presión
    msg_falla = "⚠️ ALERTA: Caída de presión súbita. ¡Posible lavado en la sarta!"
    color_falla = "orange"
elif st.session_state.falla_activa == "Worn Bit":
    rop = 1.5 # ROP mínima
    msg_falla = "ℹ️ INFO: ROP extremadamente baja. Verifique estado de la mecha."
    color_falla = "blue"
else:
    msg_falla = "✅ Operación Normal: Formación Estable"
    color_falla = "green"

# --- MOSTRAR ESTADO EN PANTALLA ---
st.markdown(f"""
    <div style="background-color:{color_falla}; padding:10px; border-radius:10px; text-align:center;">
        <h3 style="color:white; margin:0;">MODO: {st.session_state.falla_activa}</h3>
        <p style="color:white; margin:0;">{msg_falla}</p>
    </div>
    """, unsafe_allow_html=True)
st.write("") # Espaciado

# --- SECCIÓN: INGENIERÍA DE DETALLE (MSE & REOLOGÍA) ---
st.divider()
st.header("🔬 Análisis de Eficiencia y Reología")

col_tec1, col_tec2 = st.columns(2)

with col_tec1:
    st.subheader("⚙️ Optimización Mecánica (MSE)")
    diametro_mecha = st.number_input("Diámetro de Mecha (in)", value=8.5)
    
# --- 1. INICIALIZACIÓN (Evita el NameError) ---
mse = 0 

# --- 2. CÁLCULO DE EFICIENCIA (Solo si hay avance) ---
# Asegurate de que 'val_rop', 'torque_actual' y 'rpm_actual' estén definidos arriba
if 'val_rop' in locals() and val_rop > 0:
    diametro = 8.5  # Pulgadas
    # Fórmula simplificada de MSE
    term_rot = (480 * torque_actual * rpm_actual) / (diametro**2 * val_rop)
    term_axl = (4 * wob) / (np.pi * diametro**2)
    mse = term_rot + term_axl
else:
    mse = 0

# --- 3. VISUALIZACIÓN (Línea 373 corregida) ---
st.metric("MSE (psi)", f"{int(mse)}", help="Energía Mecánica Específica (Eficiencia)")
# --- CÁLCULO DE VELOCIDAD CRÍTICA (HIDRÁULICA) ---
# Asegurate de que no haya espacios extra al inicio de estas líneas
pv = st.session_state.get('pv', 15) # Viscosidad Plástica
yp = st.session_state.get('yp', 20) # Punto Cedente
densidad = st.session_state.get('mw', 10.5)

# Cálculo de la velocidad crítica (Fórmula de Walker simplificada)
vel_critica = (97 * pv + 97 * np.sqrt(pv**2 + 6.2 * (8.5 - 5) * yp * densidad)) / (densidad * (8.5 - 5))

# Visualización para el alumno
st.metric("Velocidad Crítica (ft/min)", f"{vel_critica:.2f}")

# --- GRÁFICA DE LIMPIEZA DE HOYO ---
st.subheader("🧹 Capacidad de Transporte de Recortes (Cutting Transport)")
v_anular = (24.5 * caudal) / (8.5**2 - 5**2) # ft/min aprox
v_deslizamiento = 0.45 * (yp / densidad)**0.5 * 60 # ft/min aprox

eficiencia_limpieza = ((v_anular - v_deslizamiento) / v_anular) * 100

st.progress(min(max(eficiencia_limpieza/100, 0.0), 1.0), 
            text=f"Eficiencia de Limpieza: {round(eficiencia_limpieza, 1)}%")

if eficiencia_limpieza < 70:
    st.error("🚨 ¡PELIGRO DE EMBOCAMIENTO! Los recortes están cayendo al fondo.")

# --- SECCIÓN: CONTROL DE POZOS (HOJA DE MATAR) ---
st.divider()
st.header("📋 Hoja de Matar (Kill Sheet) - Método del Perforador")

with st.expander("Abrir Procedimiento de Control de Pozos"):
    col_k1, col_k2 = st.columns(2)
    
    with col_k1:
        st.subheader("📝 Datos del Brote")
        sidpp = st.number_input("SIDPP (Presión Tubería) [PSI]", value=500)
        sicp = st.number_input("SICP (Presión Anular) [PSI]", value=750)
        ganancia_tanque = st.number_input("Ganancia en Tanques [bbl]", value=15)
        
    with col_k2:
        st.subheader("🧮 Cálculos de Control")
        # Cálculo de la Nueva Densidad (Kill Mud Weight)
        # 0.1703 es el factor de conversión para metros a PSI/ppg
        kmw = densidad_lodo + (sidpp / (0.1703 * profundidad_actual))
        
        st.metric("Kill Mud Weight (KMW)", f"{round(kmw, 2)} ppg", 
                  delta=f"+{round(kmw - densidad_lodo, 2)} ppg")
        
        # Presión Inicial de Circulación (ICP)
        # ICP = SIDPP + Presión de Circulación a Velocidad Reducida (SCR)
        scr = 400 # Presión a baja velocidad simulada
        icp = sidpp + scr
        st.write(f"**ICP (Presión Inicial):** {icp} PSI")

    st.divider()
    st.info("💡 **Instrucción para el Alumno:** Para controlar el pozo, debe bombear el lodo pesado (KMW) manteniendo la presión en el anular constante hasta que el lodo llegue a la mecha.")

    # Gráfico de la Línea de Presión (Schedule)
    st.subheader("📉 Plan de Presión en Tubería")
    strokes = np.linspace(0, 1500, 100) # Emboladas de la bomba
    p_line = np.linspace(icp, scr + (kmw-densidad_lodo)*10, 100) # Caída teórica
    
    fig_kill = go.Figure()
    fig_kill.add_trace(go.Scatter(x=strokes, y=p_line, name="Presión de Control", line=dict(color='yellow', width=3)))
    fig_kill.update_layout(
        title="Gráfico de Presión vs Emboladas (Pump Strokes)",
        xaxis_title="Emboladas (Strokes)",
        yaxis_title="Presión en Tubería (PSI)",
        template="plotly_dark",
        height=300
    )
    st.plotly_chart(fig_kill, use_container_width=True)
# --- SECCIÓN: SISTEMA DE TANQUES (PVT - Pit Volume Totalizer) ---
st.divider()
st.header("🛢️ Sistema de Tanques y Volumen (PVT)")

# Simulación de volumen total
volumen_inicial = 1200 # Barriles (bbl)
if 'volumen_actual' not in st.session_state:
    st.session_state.volumen_actual = volumen_inicial

col_t1, col_t2, col_t3 = st.columns([1, 1, 2])

with col_t1:
    st.subheader("📊 Niveles")
    # Lógica de cambio de volumen basada en el estado del pozo
    cambio_flujo = 0
    if st.session_state.falla_activa == "Washout":
        cambio_flujo = -2.5 # Perdiendo lodo
    elif sidpp > 0: 
        cambio_flujo = 1.8 # Ganando fluido (Brote)
    
    st.session_state.volumen_actual += cambio_flujo
    
    st.metric("Volumen Total", f"{round(st.session_state.volumen_actual, 1)} bbl", 
              delta=f"{cambio_flujo} bbl/min", delta_color="inverse")

with col_t2:
    # Gráfico de Barra Vertical (Tanque)
    fig_tank = go.Figure(go.Bar(
        x=["Tanque Activo"],
        y=[st.session_state.volumen_actual],
        marker_color='#00d4ff',
        width=0.5
    ))
    fig_tank.update_layout(
        yaxis=dict(range=[0, 2000]),
        height=300,
        template="plotly_dark",
        title="Nivel de Presas"
    )
    st.plotly_chart(fig_tank, use_container_width=True)

with col_t3:
    st.subheader("📈 Tendencia de Ganancia/Pérdida")
    # Simulación de línea de tendencia
    tiempos = np.linspace(0, 10, 20)
    tendencia = volumen_inicial + (cambio_flujo * tiempos)
    
    fig_pvt = go.Figure()
    fig_pvt.add_trace(go.Scatter(x=tiempos, y=tendencia, mode='lines+markers', 
                                 line=dict(color='#ffcc00' if cambio_flujo != 0 else '#00ff88')))
    fig_pvt.update_layout(height=300, template="plotly_dark", xaxis_title="Minutos", yaxis_title="Barriles")
    st.plotly_chart(fig_pvt, use_container_width=True)

# Alerta de Tanques
if st.session_state.volumen_actual > volumen_inicial + 20:
    st.error("🚨 ¡GANANCIA EN TANQUES! Posible entrada de fluido de formación.")
elif st.session_state.volumen_actual < volumen_inicial - 20:
    st.warning("⚠️ PÉRDIDA DE CIRCULACIÓN: El lodo se está filtrando a la formación.")
# --- SECCIÓN: PROTOCOLO IADC WELLSHARP ---
st.divider()
st.header("🏆 Evaluación de Control de Pozos (Estándar IADC)")

# Parámetros de la Zapata (Casing Shoe) para el MAASP
st.sidebar.subheader("🏗️ Integridad del Pozo")
zapata_tvd = st.sidebar.number_input("Profundidad de Zapata (m)", value=1500)
gradiente_leak_off = st.sidebar.slider("LOT (Leak-off Test) [ppg]", 13.0, 18.0, 15.5)

# Cálculo del MAASP (Maximum Allowable Annular Surface Pressure)
# Presión máxima que puede aguantar el pozo en superficie sin romper la zapata
maasp = (gradiente_leak_off - densidad_lodo) * 0.1703 * zapata_tvd

st.sidebar.metric("MAASP (Límite de Presión)", f"{round(maasp, 0)} PSI")

col_iadc1, col_iadc2 = st.columns(2)

with col_iadc1:
    st.subheader("🛑 Procedimiento de Detección")
    if st.button("Realizar FLOW CHECK"):
        with st.status("Deteniendo bombas y observando..."):
            time.sleep(2)
            if sidpp > 0 or cambio_flujo > 0:
                st.error("🚨 ¡EL POZO FLUYE! Proceda a cerrar el pozo (Hard Shut-in).")
            else:
                st.success("✅ El pozo está estático. Continúe perforando.")

with col_iadc2:
    st.subheader("📉 Monitor de Seguridad IADC")
    # Gráfico de presión actual vs MAASP
    fig_maasp = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = sicp,
        title = {'text': "SICP vs MAASP (Límite)"},
        gauge = {
            'axis': {'range': [0, maasp*1.2]},
            'threshold': {
                'line': {'color': "red", 'width': 5},
                'thickness': 0.75,
                'value': maasp
            },
            'bar': {'color': "yellow" if sicp < maasp else "red"}
        }
    ))
    fig_maasp.update_layout(height=250, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_maasp, use_container_width=True)

# Lógica de fracaso IADC
if sicp > maasp:
    st.markdown("""
        <div style="background-color:maroon; padding:20px; border-radius:10px; border: 5px solid red;">
            <h1 style="color:white; text-align:center;">💥 ¡FALLA DE INTEGRIDAD!</h1>
            <p style="color:white; text-align:center;">Has superado el MAASP. La formación en la zapata se ha fracturado. El pozo está perdido.</p>
        </div>
    """, unsafe_allow_html=True)

# --- SECCIÓN: EVALUADOR DE COMPETENCIAS IADC ---
st.divider()
st.header("📝 Registro de Evaluación (Auditoría IADC)")

# Inicializar lista de errores si no existe
if 'errores_iadc' not in st.session_state:
    st.session_state.errores_iadc = []

# Lógica de detección de infracciones (Checkpoints)
def registrar_error(descripcion):
    if descripcion not in st.session_state.errores_iadc:
        st.session_state.errores_iadc.append({
            "Hora": datetime.now().strftime("%H:%M:%S"),
            "Infracción": descripcion,
            "Gravedad": "CRÍTICA"
        })

# Verificación automática de errores en tiempo real
if sicp > maasp:
    registrar_error("Excedió el MAASP (Riesgo de Fractura en Zapata)")
if sidpp > 0 and st.session_state.falla_activa == "Normal" and not activar_fallas:
    registrar_error("No detectó el cierre de pozo a tiempo")
if ecd > presion_fractura:
    registrar_error("ECD por encima del Gradiente de Fractura")
if st.session_state.volumen_actual > volumen_inicial + 50:
    registrar_error("Ganancia excesiva en tanques sin acción correctiva")

# Mostrar Tabla de Errores
if st.session_state.errores_iadc:
    df_errores = pd.DataFrame(st.session_state.errores_iadc)
    st.table(df_errores)
    
    # Cálculo de Nota (Empieza en 100 y resta 25 por cada error crítico)
    nota_final = max(0, 100 - (len(st.session_state.errores_iadc) * 25))
    
    col_score1, col_score2 = st.columns(2)
    with col_score1:
        st.metric("Puntaje de Seguridad", f"{nota_final}/100")
    with col_score2:
        if nota_final >= 75:
            st.success("🎯 ESTADO: APROBADO PARA CERTIFICACIÓN")
        else:
            st.error("❌ ESTADO: REQUIERE RE-ENTRENAMIENTO")
else:
    st.balloons()
    st.success("🌟 ¡PERFORMANCE PERFECTA! No se detectaron violaciones de seguridad.")

# Botón para limpiar el expediente del alumno
if st.button("Reiniciar Evaluación"):
    st.session_state.errores_iadc = []
    st.session_state.volumen_actual = volumen_inicial
    st.rerun()

st.sidebar.divider()
st.sidebar.write("📌 **Nota IADC:** El cumplimiento del MAASP y el reconocimiento de señales de advertencia son obligatorios para la certificación WellSharp.")

# --- MÓDULO DE INGENIERÍA AVANZADA (Menfa Tech) ---
st.divider()
st.header("🔬 Diagnóstico Técnico de Perforación")

col_t1, col_t2 = st.columns(2)

with col_t1:
    st.subheader("📉 Detección de Presiones (d-exponent)")
    # Cálculo del Exponente d normalizado (d-exp)
    # Evitamos logaritmos de cero o negativos
    try:
        n_rpm = max(rpm_actual, 1)
        w_wob = max(wob * 2204.62, 1) # Convertir Tons a Libras
        r_rop = max(rop * 3.28, 1)    # Convertir m/h a ft/h
        
        d_exp = np.log10(r_rop / (60 * n_rpm)) / np.log10((12 * w_wob) / (10**6 * diametro_mecha))
        # Normalización por densidad de lodo
        d_exp_norm = d_exp * (9.0 / densidad_lodo) 
        
        st.metric("Exponente 'd' Normalizado", round(d_exp_norm, 3))
        
        if d_exp_norm < 1.2:
            st.warning("⚠️ TENDENCIA REVERSA: Posible zona de transición de presión detectada.")
    except:
        st.write("Esperando datos estables para cálculo de d-exp...")

with col_t2:
    st.subheader("🌪️ Hidráulica de Partículas")
    # Cálculo de la capacidad de acarreo (Transport Ratio)
    # Ft = Velocidad Anular / (Velocidad Anular + Velocidad Deslizamiento)
    v_anular = (24.5 * caudal) / (diametro_mecha**2 - 5**2) # ft/min
    v_slip = 0.45 * (yp / densidad_lodo)**0.5 * 60         # ft/min (Moore correlation)
    
    transport_ratio = v_anular / (v_anular + v_slip)
    
    fig_limpieza = go.Figure(go.Indicator(
        mode = "number+gauge",
        value = transport_ratio * 100,
        number = {'suffix': "%"},
        title = {'text': "Transport Ratio (Eficiencia)"},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "lime" if transport_ratio > 0.7 else "red"},
            'steps': [{'range': [0, 70], 'color': "rgba(255,0,0,0.2)"}]
        }
    ))
    fig_limpieza.update_layout(height=250, margin=dict(t=50, b=0), paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_limpieza, use_container_width=True)

# --- PANEL DE ACCIÓN TÉCNICA ---
st.info(f"""
**Análisis Menfa Capacitaciones:** Actualmente el pozo presenta un **Transport Ratio** de {round(transport_ratio, 2)}. 
Para mejorar la limpieza, considere {'aumentar el caudal' if transport_ratio < 0.7 else 'mantener los parámetros actuales'}.
""")

# --- MÓDULO DE GEONAVEGACIÓN (GEOSTEERING) ---
st.divider()
st.header("🎯 Geonavegación y Control de Trayectoria")

col_geo1, col_geo2 = st.columns([1, 2])

with col_geo1:
    st.subheader("📡 Sensores LWD")
    # Simulación de Rayos Gamma (Gamma Ray)
    gr_valor = 30 + 10 * np.sin(profundidad_actual / 10) + random.uniform(-5, 5)
    
    st.metric("Rayos Gamma (API)", f"{round(gr_valor, 1)} units")
    
    if gr_valor < 40:
        st.success("💎 ZONA PRODUCTIVA (Arena)")
    else:
        st.warning("🪨 ZONA DE CIERRE (Arcilla/Lutita)")

    st.subheader("🕹️ Control de Dirección")
    inc_deseada = st.slider("Ajustar Inclinación (deg)", 80.0, 100.0, 90.0)
    st.info(f"Objetivo: Mantener GR < 40 API")

with col_geo2:
    # Gráfico de Geosteering (Sección Lateral)
    distancia = np.linspace(0, 500, 50)
    # Perfil del reservorio (Ondulado)
    techo_res = 2500 + 15 * np.sin(distancia / 100)
    piso_res = techo_res + 10 # Espesor de 10 metros
    
    # Trayectoria del pozo basada en la inclinación
    trayectoria = 2505 + (distancia * np.tan(np.radians(90 - inc_deseada)))

    fig_geo = go.Figure()
    # Dibujar Reservorio
    fig_geo.add_trace(go.Scatter(x=distancia, y=techo_res, name="Techo Reservorio", line=dict(color='gray', dash='dash')))
    fig_geo.add_trace(go.Scatter(x=distancia, y=piso_res, name="Piso Reservorio", fill='tonexty', fillcolor='rgba(255, 255, 0, 0.2)', line=dict(color='gray')))
    
    # Dibujar Pozo
    fig_geo.add_trace(go.Scatter(x=distancia, y=trayectoria, name="Trayectoria Pozo", line=dict(color='lime', width=4)))

    fig_geo.update_layout(
        title="Visualización de Geonavegación (Corte Lateral)",
        xaxis_title="Desplazamiento Horizontal (m)",
        yaxis_title="TVD (m)",
        yaxis=dict(range=[2530, 2480], autorange=False), # Zoom en la zona del reservorio
        template="plotly_dark",
        height=400
    )
    st.plotly_chart(fig_geo, use_container_width=True)

# Lógica de Evaluación de Geonavegación
error_dist = abs(trayectoria[-1] - (techo_res[-1] + 5))
if error_dist > 5:
    st.error("🚨 ¡FUERA DE VENTANA! El pozo ha salido del reservorio productivo.")
    registrar_error("Error de Geonavegación: Salida de zona productiva")

# --- MÓDULO DE TORTUOSIDAD Y DLS (DOGLEG SEVERITY) ---
st.divider()
st.header("🔄 Análisis de Tortuosidad y Dogleg (DLS)")

col_tor1, col_tor2 = st.columns([1, 2])

with col_tor1:
    st.subheader("📐 Parámetros de Curvatura")
    # Simulación de cambio de inclinación entre estaciones
    inc_anterior = 89.5 
    delta_inc = abs(inc_deseada - inc_anterior)
    distancia_estacion = 30 # metros estándar
    
    # Cálculo de DLS (°/30m)
    dls = (delta_inc / distancia_estacion) * 30
    
    st.metric("Dogleg Severity (DLS)", f"{round(dls, 2)} °/30m")
    
    if dls > 3.0:
        st.error("🚨 DLS EXCESIVO: Riesgo de fatiga y dificultad en entubación.")
        registrar_error(f"Tortuosidad alta detectada: {round(dls,2)} DLS")
    elif dls > 1.5:
        st.warning("⚠️ CURVATURA MODERADA: Monitorear torque y arrastre.")
    else:
        st.success("✅ TRAYECTORIA SUAVE: Óptimo para terminación.")

with col_tor2:
    st.subheader("📈 Mapa de Tortuosidad Acumulada")
    # Generar una trayectoria con "ruido" para visualizar tortuosidad
    puntos = np.linspace(0, 100, 20)
    ideal = 90 + 0 * puntos
    real = ideal + (dls * np.sin(puntos/5) * 0.5) # Simula la sinuosidad
    
    fig_tor = go.Figure()
    fig_tor.add_trace(go.Scatter(x=puntos, y=ideal, name="Plan Ideal", line=dict(color='gray', dash='dot')))
    fig_tor.add_trace(go.Scatter(x=puntos, y=real, name="Trayectoria Real", line=dict(color='#00d4ff', width=3)))
    
    fig_tor.update_layout(
        title="Desviación de la Micro-Trayectoria",
        xaxis_title="Profundidad Medida (m)",
        yaxis_title="Inclinación (°)",
        template="plotly_dark",
        height=300
    )
    st.plotly_chart(fig_tor, use_container_width=True)

# --- CÁLCULO DE CARGA EN EL GANCHO (HOOK LOAD) ---

# 1. Recuperamos el WOB del estado de la sesión o del slider
# (Usamos .get para que si no existe, devuelva 0 y no explote)
wob_valor = st.session_state.get('wob', 0.0) 

# 2. Variables de fricción (asegurate que estén definidas arriba)
hook_load_estatico = s.get('peso_sarta', 150.0) # Valor base en klbs
drag_friccion = s.get('drag', 5.0)

# 3. Cálculo corregido (Línea 779)
hook_load_real = hook_load_estatico - drag_friccion - (wob_valor * 0.8)

# --- ANÁLISIS DE RIESGO DIRECCIONAL ---
dls = s.get('dls_actual', 0.0)
wob = s.get('wob', 0.0)

# Asegurate de que no haya espacios extra al inicio de este 'if'
if dls > 2.5 and wob > 20:
    st.error("⚠️ RIESGO DE FATIGA: DLS excesivo con alto WOB.")
    st.warning("Reduzca el peso sobre el trépano para evitar rotura de sarta.")
    st.subheader("🌡️ Efecto Térmico en el Lodo")
    temp_superficie = 20 # °C
    gradiente_termico = 0.03 # °C/m
    temp_fondo = temp_superficie + (gradiente_termico * profundidad_actual)
    
    # La densidad cae aprox 0.01 ppg por cada 15°C de aumento
    reduccion_densidad = (temp_fondo - 20) / 15 * 0.01
    densidad_fondo_real = densidad_lodo - reduccion_densidad

    st.write(f"**Temperatura de Fondo:** {round(temp_fondo, 1)} °C")
    st.metric("Densidad Real en Fondo", f"{round(densidad_fondo_real, 2)} ppg", 
              delta=f"-{round(reduccion_densidad, 3)} por expansión térmica", delta_color="inverse")

# --- GRÁFICA DE ESFUERZOS ACUMULADOS ---
st.subheader("📊 Gráfico de Cargas Críticas")
depth_array = np.linspace(0, profundidad_actual, 50)
carga_limite = 200 - (depth_array * 0.01) # Límite de tensión de la tubería
carga_actual = hook_load_real + (depth_array * 0.005)

fig_esf = go.Figure()
fig_esf.add_trace(go.Scatter(x=depth_array, y=carga_limite, name="Límite de Cedencia", line=dict(color='red', dash='dash')))
fig_esf.add_trace(go.Scatter(x=depth_array, y=carga_actual, name="Carga en la Sarta", fill='tonexty', fillcolor='rgba(0, 255, 0, 0.1)'))
fig_esf.update_layout(title="Margen de Tensión (Overpull Capability)", template="plotly_dark", height=300)
st.plotly_chart(fig_esf, use_container_width=True)

# --- MÓDULO DE REOLOGÍA AVANZADA Y TELEMETRÍA ---
st.divider()
st.header("🧬 Física de Fluidos y Telemetría MWD")

col_adv_t1, col_adv_t2 = st.columns(2)

with col_adv_t1:
    st.subheader("🧪 Modelo de Herschel-Bulkley")
    # Entradas de laboratorio (Fann 35)
    r600 = st.number_input("Lectura 600 RPM", value=50)
    r300 = st.number_input("Lectura 300 RPM", value=30)
    r3 = st.number_input("Lectura 3 RPM (Gel)", value=5)
    
    # Cálculo de índices n, k y Tau0
    n_index = 3.32 * np.log10(r600 / r300)
    k_index = (0.511 * r300) / (511**n_index)
    tau0 = r3 # Aproximación simple del Yield Stress real
    
    st.write(f"**Índice de Flujo (n):** {round(n_index, 3)}")
    st.write(f"**Consistencia (k):** {round(k_index, 3)}")
    
    if n_index < 0.5:
        st.info("💡 Lodo altamente pseudoplástico: Excelente para limpieza con bajo caudal.")

with col_adv_t2:
    st.subheader("📡 Calidad de Señal MWD")
    # La compresibilidad del lodo afecta la velocidad del pulso
    # v = sqrt(K / rho)
    modulo_bulk = 220000 # PSI aprox para lodo base agua
    velocidad_pulso = np.sqrt((modulo_bulk * 144) / (densidad_lodo * 0.00149)) # ft/s
    
    # Atenuación (Simplificada: aumenta con profundidad y viscosidad)
    atenuacion = (profundidad_actual * 0.01) + (pv * 0.5)
    fuerza_senal = max(0, 100 - atenuacion)
    
    fig_signal = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = fuerza_senal,
        title = {'text': "Fuerza de Señal MWD (%)"},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "cyan" if fuerza_senal > 40 else "darkred"},
            'steps': [{'range': [0, 30], 'color': "rgba(255, 0, 0, 0.3)"}]
        }
    ))
    fig_signal.update_layout(height=280, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_signal, use_container_width=True)

# --- DIAGNÓSTICO DE PRECISIÓN ---
if fuerza_senal < 20:
    st.error("🚨 PERDIDA DE TELEMETRÍA: La viscosidad o profundidad impiden recibir datos LWD. ¡Geonavegación a ciegas!")
# --- MÓDULO DE DINÁMICA DE TRANSITORIOS (SURGE/SWAB & STICK-SLIP) ---
st.divider()
st.header("🫨 Dinámica de Transitorios y Vibraciones")

col_dyn1, col_dyn2 = st.columns(2)

with col_dyn1:
    st.subheader("🚀 Efecto de Pistoneo (Surge & Swab)")
    v_tubería = st.slider("Velocidad de Maniobra (ft/min)", -200, 200, 0) # Positivo es bajar, negativo es subir
    
    # Cálculo simplificado del cambio de presión por pistoneo (Clave técnica IADC)
    # DeltaP = (Viscosidad * Velocidad) / (Diametro_hoyo - Diametro_tubería)
    delta_p_pistoneo = (pv * v_tubería) / (1000 * (diametro_mecha - 5))
    presion_fondo_dinamica = (densidad_lodo * 0.1703 * profundidad_actual) + delta_p_pistoneo
    ecd_dinamico = presion_fondo_dinamica / (0.1703 * profundidad_actual)

    st.metric("ECD Dinámico", f"{round(ecd_dinamico, 2)} ppg", 
              delta=f"{round(delta_p_pistoneo, 1)} PSI (Efecto Pistoneo)")
    
    if ecd_dinamico > presion_fractura:
        st.error("🚨 CRÍTICO: ¡Fractura por SURGE! Reduzca velocidad de bajada.")
    elif ecd_dinamico < presion_poro:
        st.error("🚨 CRÍTICO: ¡Brote por SWAB! Reduzca velocidad de sacada.")

with col_dyn2:
    st.subheader("🎸 Análisis de Vibraciones (Stick-Slip)")
    # ==========================================
# BLOQUE DE CÁLCULOS TÉCNICOS (EL MOTOR)
# ==========================================

# 1. Cálculo de Vibraciones (Bit Bounce)
if rpm_actual > 0 and wob > 0:
    vibracion_axial = (wob / 5) * (rpm_actual / 100) * random.uniform(0.8, 1.2)
else:
    vibracion_axial = 0.1

# 2. Cálculo del Exponente d (Predicción de Presión)
if rpm_actual > 0 and wob > 0 and rop_actual > 0:
    d_exp = np.log10(rop_actual / (60 * rpm_actual)) / np.log10(12 * wob / (10**6 * diametro_mecha))
    d_exp_norm = d_exp * (9.0 / densidad_lodo)
else:
    d_exp_norm = 0.0

# 3. Otros KPIs que podrías necesitar (MAASP, CCI, etc.)
# ... (asegurate que todos se calculen aquí) ...
# --- SIMULACIÓN DE DINÁMICA DE ROTACIÓN ---

# 1. Recuperamos las RPM del slider (asegurate que el key coincida)
rpm_actual = s.get('rpm', 0.0) 

# 2. Factor de variación (esto simula vibraciones torsionales)
# Si no tenés 'variacion_torque' definida, usamos un valor base de 1.0
variacion_torque = s.get('var_torque', 1.0)

# 3. Cálculo corregido (Línea 887)
rpm_bit_real = rpm_actual * variacion_torque

# 4. Mostramos el efecto visual para el alumno de la UTN
if variacion_torque < 0.8:
    st.warning("⚠️ ALERTA: Stick-Slip detectado en el trépano.")
    # Simulación de onda de torsión
    t_v = np.linspace(0, 10, 50)
    wave = rpm_actual + (rpm_actual * (variacion_torque - 1) * np.sin(t_v * 2))
    
    fig_vib.add_trace(go.Scatter(x=t_v, y=wave, name="RPM en la Mecha", line=dict(color='orange')))
    fig_vib.update_layout(title="Vibración Torsional (Stick-Slip)", template="plotly_dark", height=250)
    st.plotly_chart(fig_vib, use_container_width=True)

    if variacion_torque > 1.8:
        st.warning("⚠️ STICK-SLIP DETECTADO: Energía torsional acumulada liberándose peligrosamente.")


# --- CÁLCULO DE LIMPIEZA DE POZO (CCI) ---

# 1. Recuperamos las variables del estado de la sesión (usando 's')
# Asegurate de que 'caudal_gpm', 'id_hoyo' y 'od_dp' estén definidos arriba
caudal = s.get('caudal_gpm', 0.0)
diam_hoyo = 8.5   # Pulgadas
diam_dp = 5.0     # Pulgadas (Drill Pipe)
densidad_lodo = s.get('mw', 10.0)
k_index = s.get('k_index', 0.5) # Índice de consistencia del lodo

# 2. Calculamos la Velocidad Anular (v_actual_anular) en ft/min
# Fórmula: GPM / (Capacidad Anular en bbl/ft * 42) o simplificada:
if (diam_hoyo**2 - diam_dp**2) > 0:
    v_actual_anular = (24.5 * caudal) / (diam_hoyo**2 - diam_dp**2)
else:
    v_actual_anular = 0

# 3. Cálculo corregido del CCI (Línea 937)
if v_actual_anular > 0:
    cci = (k_index * densidad_lodo * v_actual_anular) / 400000
else:
    cci = 0
# ==========================================
# PANEL DE TELEMETRÍA (VISUALIZACIÓN)
# ==========================================
st.metric("Vib. Axial", f"{round(vibracion_axial, 1)}G", delta="ALTA" if vibracion_axial > 3 else "OK")
st.metric("d-exp", f"{round(d_exp_norm, 2)}", help="Exponente d Normalizado")
# 4. Visualización para la UTN
st.metric("Índice de Limpieza (CCI)", f"{cci:.2f}", help="Cuttings Carrying Index")
# --- ANÁLISIS TÉCNICO DE LIMPIEZA ---
if cci < 1.0:
    st.markdown(f"""
    > **Ingeniería Menfa:** El CCI actual de **{round(cci,2)}** indica que el lodo no tiene suficiente 'capacidad de transporte'. 
    > Aumente el **Yield Point (YP)** o incremente el **Caudal** para evitar el enterramiento de la sarta.
    """)

# --- PANEL DE TELEMETRÍA MAESTRA (KPI CONSOLIDATED VIEW) ---
st.divider()
st.header("📡 Centro de Control y Telemetría de Alta Fidelidad")
# --- CÁLCULO DE VIBRACIONES (Pegar antes de la línea 960) ---
# Simulamos la vibración axial (Bit Bounce) basada en WOB y RPM
# Si no hay rotación o peso, la vibración es mínima (0.1)
if rpm_actual > 0 and wob > 0:
    vibracion_axial = (wob / 5) * (rpm_actual / 100) * random.uniform(0.8, 1.2)
else:
    vibracion_axial = 0.1

# Ahora la línea 960 podrá leer la variable sin errores
st.metric("Vib. Axial", f"{round(vibracion_axial, 1)}G", delta="ALTA" if vibracion_axial > 3 else "OK", delta_color="inverse")
# Creamos una matriz de KPIs para una lectura rápida tipo "Glass Cockpit"
kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)

with kpi_col1:
    st.metric("DLS", f"{round(dls, 1)}°", delta="Crítico" if dls > 3 else "Normal", delta_color="inverse")
    st.metric("MSE", f"{round(mse/1000, 1)}k", help="Mechanical Specific Energy en ksi")

with kpi_col2:
    st.metric("ECD", f"{round(ecd_dinamico, 2)}", delta=f"{round(ecd_dinamico - densidad_lodo, 2)}", help="Densidad Circulante con Efecto Surge/Swab")
    st.metric("CCI", f"{round(cci, 2)}", delta="Bajo" if cci < 1.0 else "Óptimo")

with kpi_col3:
    st.metric("Vib. Axial", f"{round(vibracion_axial, 1)}G", delta="ALTA" if vibracion_axial > 3 else "OK", delta_color="inverse")
    st.metric("d-exp", f"{round(d_exp_norm, 2)}", help="Exponente d Normalizado")

with kpi_col4:
    st.metric("MAASP Margin", f"{round(maasp - sicp, 0)} PSI", delta="Seguro" if sicp < maasp else "PELIGRO")
    st.metric("TR", f"{round(transport_ratio * 100, 0)}%", help="Transport Ratio de recortes")

with kpi_col5:
    st.metric("Stick-Slip", f"{round(variacion_torque, 2)}", delta="Inestable" if variacion_torque > 1.5 else "Estable", delta_color="inverse")
    st.metric("Temp Fondo", f"{round(temp_fondo, 0)}°C")
# --- CÁLCULO DE TEMPERATURA DE FONDO (Gradiente Geotérmico) ---
# Supuestos para Mendoza/Cuenca Cuyana: 
# Temp Superficie: 20°C | Gradiente: 3°C por cada 100m
temp_superficie = 20 
gradiente_geotermico = 0.03 # °C/metro
# 2. La lógica de alerta (PEGAR AQUÍ)
if temp_fondo > 120:
    st.sidebar.error(f"🌡️ ALTA TEMPERATURA: {round(temp_fondo, 1)}°C")
    st.sidebar.caption("⚠️ Riesgo de falla en sellos de motor de fondo y telemetría MWD.")
elif temp_fondo > 100:
    st.sidebar.warning(f"💡 Temperatura elevada: {round(temp_fondo, 1)}°C")
# Cálculo dinámico
temp_fondo = temp_superficie + (gradiente_geotermico * profundidad_actual)

# Ahora la línea 1019 funcionará correctamente
st.metric("Temp Fondo", f"{round(temp_fondo, 0)}°C")
# --- GRÁFICO RADAR DE PERFORMANCE TÉCNICA ---
st.subheader("🕸️ Análisis Multivariable de Operación")

categories = ['Limpieza', 'Estabilidad', 'Eficiencia ROP', 'Integridad Zapata', 'Mecánica Sarta']
# Normalización de valores para el radar (0 a 1)
values = [
    min(cci, 1.5)/1.5, 
    1 - (abs(ecd_dinamico - (presion_poro + 0.5)) / 2), 
    min(40000/mse if mse > 0 else 1, 1),
    max(0, (maasp - sicp) / maasp),
    1 - (min(vibracion_axial, 10) / 10)
]

fig_radar = go.Figure()
fig_radar.add_trace(go.Scatterpolar(
      r=values,
      theta=categories,
      fill='toself',
      name='Estado Actual',
      line=dict(color='lime')
))

fig_radar.update_layout(
  polar=dict(
    radialaxis=dict(visible=True, range=[0, 1])),
  showlegend=False,
  template="plotly_dark",
  height=450
)
st.plotly_chart(fig_radar, use_container_width=True)

# Mensaje Final de Certificación Menfa
st.caption(f"© 2026 Menfa Capacitaciones - Mendoza, Argentina. Sistema de Simulación de Perforación v4.0 - IADC & Geonavegación Compliant.")

# --- MÓDULO DE RESONANCIA ESTRUCTURAL Y RIGIDEZ (Advanced Physics) ---
st.divider()
st.header("🎻 Análisis de Resonancia y Rigidez de Sarta")

col_phys1, col_phys2 = st.columns(2)

with col_phys1:
    st.subheader("🎵 Frecuencias Críticas (RPM)")
    # Cálculo simplificado de la primera frecuencia natural del BHA
    # f = (1 / 2pi) * sqrt(E*I / m*L^4)
    longitud_bha = 120 # metros
    diametro_interior = 3.0 # in
    # Frecuencia crítica en RPM
    rpm_critica_1 = 60 * ( (10.2 / longitud_bha**2) * np.sqrt( (29e6 * (diametro_mecha**4 - diametro_interior**4)) / 490) )
    
    st.write(f"**1ra Velocidad Crítica Teórica:** {round(rpm_critica_1, 1)} RPM")
    
    # Proximidad a la resonancia
    proximidad = abs(rpm_actual - rpm_critica_1) / rpm_critica_1
    
    if proximidad < 0.1:
        st.error(f"🚨 RESONANCIA DETECTADA: Operando al {round((1-proximidad)*100,1)}% de la frecuencia crítica. ¡Cambie RPM inmediatamente!")
    else:
        st.success("✅ Frecuencia de Rotación Segura")

with col_phys2:
    st.subheader("🦾 Rigidez a la Flexión (Stiff-String)")
    # Momento de Inercia de la tubería (I)
    i_moment = (np.pi / 64) * (diametro_mecha**4 - diametro_interior**4)
    # Esfuerzo de flexión inducido por el DLS
    # Sigma = (E * d/2) / Radio_curvatura
    radio_curvatura = 1718 / max(dls, 0.01) # pies
    esfuerzo_flexion = (29e6 * (diametro_mecha / 2)) / (radio_curvatura * 12)
    
    st.metric("Esfuerzo de Flexión", f"{round(esfuerzo_flexion / 1000, 1)} ksi")
    
    # Límite de Fatiga (Aproximación para Acero Grado S-135)
    limite_fatiga = 45 # ksi
    st.progress(min(esfuerzo_flexion / (limite_fatiga * 1000), 1.0), 
                text=f"Consumo de Vida Útil por Ciclo: {round((esfuerzo_flexion/(limite_fatiga*1000))*100, 2)}%")

# --- MÓDULO DE CINÉTICA DE FONDO Y TRANSPORTE DE SÓLIDOS (Advanced THM) ---
st.divider()
st.header("🧬 Cinética de Fondo y Transporte de Sólidos")

col_kin1, col_kin2 = st.columns(2)

with col_kin1:
    st.subheader("⚡ Dinámica Axial (Bit Bounce)")
    # Simulación de aceleración G en la mecha
    vibracion_axial = (wob / 5) * (rpm_actual / 100) * 1.5 # Valor base simulado
    
    st.metric("Vibración Axial (G-RMS)", f"{round(vibracion_axial, 2)} G")
    
    if vibracion_axial > 4.5:
        st.error("🚨 BIT BOUNCE CRÍTICO: Riesgo de rotura de cortadores PDC.")
    elif vibracion_axial > 2.5:
        st.warning("⚠️ VIBRACIÓN MODERADA: Optimice parámetros de perforación.")

with col_kin2:
    st.subheader("🧪 Eficiencia de Acarreo (CCI - Cuttings Carrying Index)")
    # El CCI es el estándar para asegurar que el pozo esté limpio
    # CCI = (K * Densidad * Caudal) / (577 * Diametro)
    # k_index es el Consistency Index de Herschel-Bulkley calculado previamente
    
    cci = (k_index * densidad_lodo * v_actual_anular) / 400000 # Simplificación de campo
    
    fig_cci = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = cci,
        title = {'text': "Cuttings Carrying Index (CCI)"},
        gauge = {
            'axis': {'range': [0, 2.0]},
            'steps': [
                {'range': [0, 0.5], 'color': "maroon"},
                {'range': [0.5, 1.0], 'color': "orange"},
                {'range': [1.0, 2.0], 'color': "lime"}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'value': 1.0
            }
        }
    ))
    fig_cci.update_layout(height=280, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_cci, use_container_width=True)

# --- ANÁLISIS TÉCNICO DE LIMPIEZA ---
if cci < 1.0:
    st.markdown(f"""
    > **Ingeniería Menfa:** El CCI actual de **{round(cci,2)}** indica que el lodo no tiene suficiente 'capacidad de transporte'. 
    > Aumente el **Yield Point (YP)** o incremente el **Caudal** para evitar el enterramiento de la sarta.
    """)




# --- PANEL DE TELEMETRÍA MAESTRA (KPI CONSOLIDATED VIEW) ---
st.divider()
st.header("📡 Centro de Control y Telemetría de Alta Fidelidad")

# Matriz de KPIs para lectura rápida tipo "Glass Cockpit"
kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)

with kpi_col1:
    st.metric("DLS", f"{round(dls, 1)}°", delta="Crítico" if dls > 3 else "Normal", delta_color="inverse")
    st.metric("MSE", f"{round(mse/1000, 1)}k", help="Mechanical Specific Energy en ksi")

with kpi_col2:
    st.metric("ECD", f"{round(ecd_dinamico, 2)}", delta=f"{round(ecd_dinamico - densidad_lodo, 2)}", help="Densidad Circulante con Efecto Surge/Swab")
    st.metric("CCI", f"{round(cci, 2)}", delta="Bajo" if cci < 1.0 else "Óptimo")

with kpi_col3:
    st.metric("Vib. Axial", f"{round(vibracion_axial, 1)}G", delta="ALTA" if vibracion_axial > 3 else "OK", delta_color="inverse")
    st.metric("d-exp", f"{round(d_exp_norm, 2)}", help="Exponente d Normalizado")

with kpi_col4:
    st.metric("MAASP Margin", f"{round(maasp - sicp, 0)} PSI", delta="Seguro" if sicp < maasp else "PELIGRO")
    st.metric("TR", f"{round(transport_ratio * 100, 0)}%", help="Transport Ratio de recortes")

with kpi_col5:
    st.metric("Stick-Slip", f"{round(variacion_torque, 2)}", delta="Inestable" if variacion_torque > 1.5 else "Estable", delta_color="inverse")
    st.metric("Temp Fondo", f"{round(temp_fondo, 0)}°C")

# --- GRÁFICO RADAR DE PERFORMANCE TÉCNICA ---
st.subheader("🕸️ Análisis Multivariable de Operación")

categories = ['Limpieza (CCI)', 'Estabilidad (ECD)', 'Eficiencia (MSE)', 'Integridad (MAASP)', 'Mecánica (Vib)']
# Normalización de valores para el radar (escala 0 a 1)
values = [
    min(cci, 1.5)/1.5, 
    1 - (abs(ecd_dinamico - (presion_poro + 0.5)) / 2), 
    min(40000/mse if mse > 0 else 1, 1),
    max(0, (maasp - sicp) / maasp),
    1 - (min(vibracion_axial, 10) / 10)
]

fig_radar = go.Figure()
fig_radar.add_trace(go.Scatterpolar(
      r=values,
      theta=categories,
      fill='toself',
      name='Estado Actual',
      line=dict(color='lime')
))

fig_radar.update_layout(
  polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
  showlegend=False,
  template="plotly_dark",
  height=450
)
st.plotly_chart(fig_radar, use_container_width=True)

st.caption("© 2026 Menfa Capacitaciones - Mendoza. Sistema v4.0 - IADC & Geonavegación Compliant.")

import streamlit as st
from fpdf import FPDF
from datetime import datetime

# --- FUNCION UNICA Y LIMPIA ---
# =========================================================
# 📄 SECCIÓN FINAL: EXPORTACIÓN Y CERTIFICADO (PEGAR AL FINAL)
# =========================================================
st.sidebar.divider()
st.sidebar.subheader("🎓 Panel de Certificación Menfa")

# 1. Inputs del Alumno
nombre_alumno = st.sidebar.text_input("Nombre del Alumno:", value="Fabricio")
dni_alumno = st.sidebar.text_input("DNI / ID:", value="")
curso_tipo = st.sidebar.selectbox("Módulo:", ["Perforación IADC", "Geonavegación", "Lodos"])

# --- SECCIÓN DE REPORTES Y CERTIFICADOS ---
if st.sidebar.button("🛠️ Generar Reporte Técnico"):
    try:
        # 1. Intentamos generar el reporte principal
        pdf_bytes = generar_reporte_tecnico()
        datos_errores = st.session_state.get('errores_iadc', [])
        
        if datos_errores:
            st.sidebar.info(f"Registrados {len(datos_errores)} eventos de control.")
        
        st.sidebar.success("✅ Reporte listo")
        st.sidebar.download_button(
            label="Descargar Reporte PDF",
            data=pdf_bytes,
            file_name="Reporte_Menfa_Simulador.pdf",
            mime="application/pdf"
        )
        
        # 2. Generamos el Certificado de Alumno automáticamente debajo
        nombre_alumno = st.session_state.get('nombre_alumno', 'Alumno Menfa')
        dni_alumno = st.session_state.get('dni_alumno', '00.000.000')
        curso_tipo = "Perforación y Control de Pozos"
        
        pdf_final = generar_reporte_tecnico_certificado(
            nombre_alumno, 
            dni_alumno, 
            curso_tipo, 
            datos_errores
        )
        
        st.sidebar.success("✅ Certificado procesado con éxito")
        st.sidebar.download_button(
            label="📥 DESCARGAR CERTIFICADO",
            data=pdf_final,
            file_name=f"Certificado_Menfa_{nombre_alumno.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
        
    except Exception as e:
        st.sidebar.error(f"Falta información de simulación: {e}")
        st.sidebar.info("Asegúrese de haber iniciado la perforación para capturar datos técnicos.")

# --- PANEL DE CONTROL DE POZO (BOP) ---
st.sidebar.markdown("### 🕹️ Panel de Emergencia")
if st.sidebar.button("🔒 CERRAR BOP (Shut-in)"):
    if st.session_state.get('cronometro_activo'):
        st.session_state.tiempo_reaccion = round(time.time() - st.session_state.tiempo_inicio_evento, 2)
        st.session_state.cronometro_activo = False
        st.session_state.evento_activo = None
        st.sidebar.success(f"Pozo Cerrado en {st.session_state.tiempo_reaccion} segundos")

# --- PANEL DE INSTRUCTOR ---
with st.expander("🛠️ CONSOLA DE INSTRUCTOR", expanded=False):
    st.markdown("### Generar Eventos en Tiempo Real")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚨 Simular Amago de Surgencia (Kick)"):
            st.session_state.cronometro_activo = True
            st.session_state.tiempo_inicio_evento = time.time()
            st.session_state.evento_activo = "KICK"
            st.session_state.presion_anular += 200
            st.warning("⚠️ Evento de Control de Pozo Iniciado")
            
        if st.button("📉 Simular Pérdida de Circulación"):
            st.session_state.evento_activo = "LOST_CIRC"
            st.session_state.retorno_lodo -= 30
            
    with col2:
        if st.button("⚙️ Falla en Bomba 1"):
            st.session_state.falla_bomba = True
            st.session_state.presion_bombeo = 0
            
    if st.button("✅ Limpiar Eventos"):
        st.session_state.evento_activo = None
        st.session_state.falla_bomba = False
        st.session_state.cronometro_activo = False
# --- EJEMPLO: CONTROL DE CIERRE DE POZO ---
# (Suponiendo que tenés variables como 'ganancia_tanques' o 'kick_detectado')
if ganancia_tanques > limite_seguridad and not bop_cerrado:
    if not st.session_state.error_cierre_activo:
        st.session_state.penalizaciones.append({
            "Hora": datetime.now().strftime("%H:%M:%S"),
            "Infracción": "No detectó el cierre de pozo a tiempo (Kick)",
            "Gravedad": "CRÍTICA"
        })
        st.session_state.error_cierre_activo = True  # Bloquea repeticiones
else:
    # IMPORTANTE: Solo se resetea si el alumno cerró el BOP
    if bop_cerrado:
        st.session_state.error_cierre_activo = False

# --- EJEMPLO: GEONAVEGACIÓN ---
if abs(desviacion_vertical) > margen_formacion:
    if not st.session_state.error_geo_activo:
        st.session_state.penalizaciones.append({
            "Hora": datetime.now().strftime("%H:%M:%S"),
            "Infracción": "Error de Geonavegación: Fuera de formación",
            "Gravedad": "CRÍTICA"
        })
        st.session_state.error_geo_activo = True
else:
    st.session_state.error_geo_activo = False
# --- EN EL PANEL DEL INSTRUCTOR ---
if st.session_state.rol == "instructor":
    st.sidebar.subheader("🏢 Selección de Escenario Industrial")
    escenario = st.sidebar.selectbox("Elegir Ejercicio", [
        "Normal: Perforación Estándar",
        "Escenario 1: Turno de Perforador (Leve aumento)",
        "Escenario 2: Evento Crítico (Kick rápido)",
        "Escenario 3: Presión de Producción (ROP al límite)",
        "Escenario 4: Company Man (Toma de decisiones)"
    ])
    
    if st.sidebar.button("🚀 Lanzar Escenario Seleccionado"):
        pizarra["escenario_actual"] = escenario
        pizarra["alarma_activa"] = True
        # Aquí podés variar la velocidad del incremento_kick según el escenario
        if "Crítico" in escenario:
            pizarra["velocidad_presion"] = 50 
        else:
            pizarra["velocidad_presion"] = 10

import plotly.graph_objects as go

def graficar_geologia_y_pozo(profundidad):
    import plotly.graph_objects as go
    
    # 1. Creamos la figura explícitamente
    fig = go.Figure()

    # 2. Dibujamos las capas geológicas (usando tus topes de Mendoza/Neuquén)
    for capa in topes_reales:
        fig.add_shape(
            type="rect", x0=0, x1=1, y0=capa["top"], y1=capa["base"],
            fillcolor=capa["color"], opacity=0.5, layer="below", line_width=0
        )
        # Etiqueta de la formación
        fig.add_annotation(
            x=0.5, y=(capa["top"] + capa["base"]) / 2,
            text=capa["nombre"], showarrow=False, font=dict(color="white")
        )

    # 3. Dibujamos el pozo (una línea que baja con la profundidad actual)
    fig.add_trace(go.Scatter(
        x=[0.5, 0.5], y=[0, profundidad],
        mode="lines+markers",
        line=dict(color="black", width=4),
        name="Pozo en Perforación"
    ))

    # 4. Configuramos los ejes (AQUÍ ESTABA EL ERROR)
    fig.update_layout(
        title="Perfil Geológico y Estado del Pozo",
        xaxis=dict(showticklabels=False, range=[0, 1]),
        yaxis=dict(autorange="reversed", title="Profundidad (m)"), # Invertido para que baje
        template="plotly_white",
        height=600
    )
    
    return fig
# --- Aseguramos la existencia de la variable ---
profundidad_actual = st.session_state.get('profundidad', 0)

# 1. Definimos la lista (asegurando el nombre que usa la función)
formaciones = [
    {"nombre": "Grupo Neuquén", "top": 0, "base": 1200, "fp": 1.2, "color": "#f1c40f"},
    {"nombre": "Fm. Quintuco", "top": 1200, "base": 2100, "fp": 0.9, "color": "#bdc3c7"},
    {"nombre": "Fm. Vaca Muerta ⭐", "top": 2100, "base": 2500, "fp": 0.5, "color": "#2c3e50"},
    {"nombre": "Fm. Lajas", "top": 2500, "base": 3500, "fp": 0.8, "color": "#d35400"}
]

def obtener_formacion_actual(prof):
    for f in formaciones:
        if f["top"] <= prof < f["base"]:
            return f
    return formaciones[-1]

# =========================================================
# 🛠️ MOTOR DE PERFORACIÓN Y REACCIÓN (MENFA 3.0)
# =========================================================

# 1. Aseguramos que existan las variables de vibración en el session_state
if 'vibracion_reloj' not in st.session_state:
    st.session_state.vibracion_reloj = time.time()
if 'presion_vibracion' not in st.session_state:
    st.session_state.presion_vibracion = 0.0

def obtener_formacion_actual(prof):
    # Asegúrate que la lista 'formaciones' esté definida antes de llamar a esta función
    for f in formaciones:
        if f["top"] <= prof < f["base"]:
            return f
    return formaciones[-1]

# Ejecutamos el cálculo de formación
f_actual = obtener_formacion_actual(st.session_state.get('profundidad_actual', 0))
factor_dureza = f_actual["fp"]

# --- CAPTURA ÚNICA DE VARIABLES (Evitamos redundancia) ---
wob = st.session_state.get('wob_actual', 0) 
rpm = st.session_state.get('rpm_actual', 0)
# Buscamos el diámetro; si no existe en la UI, usamos 8.5 por defecto
diam_m = st.session_state.get('diam_mecha', st.session_state.get('diametro_mecha', 8.5))

# --- CÁLCULO DE ROP ---
rop_base = (wob * rpm) / (diam_m ** 2) if diam_m > 0 else 0
rop_final = rop_base * factor_dureza

# Aplicar desgaste de mecha si existe el evento
if st.session_state.get('mecha_gastada', False):
    rop_final *= 0.6

# =========================================================
# ⚙️ MOTOR DINÁMICO DE KICK (CAOS VISUAL)
# =========================================================

# Reacción AGRESIVA si hay un KICK activo
if st.session_state.get('evento_activo') == "KICK":
    # Incrementos por cada refresco de pantalla
    st.session_state.presion_bombeo += 15.0  # Ajustado para que no explote en 1 segundo
    st.session_state.presion_anular += 10.0
    st.session_state.nivel_cajones += 5.0    
    st.session_state.retorno_lodo = 115.0 

    # Motor de Vibración (Pánico Visual)
    # np.random.normal requiere 'import numpy as np'
    ahora = time.time()
    if ahora - st.session_state.vibracion_reloj > 0.05: 
        st.session_state.presion_vibracion = np.random.normal(0, 40.0) 
        st.session_state.vibracion_reloj = ahora
else:
    # Si no hay kick, la vibración se apaga suavemente
    st.session_state.presion_vibracion *= 0.5

# Aplicamos la vibración SOLO para las agujas de los manómetros
presion_bombeo_gauge = max(0, st.session_state.get('presion_bombeo', 0) + st.session_state.presion_vibracion)
presion_anular_gauge = max(0, st.session_state.get('presion_anular', 0) + st.session_state.presion_vibracion)
nivel_cajones_gauge = max(0, st.session_state.get('nivel_cajones', 0) + (st.session_state.presion_vibracion / 10.0))

# --- DIBUJAR MANÓMETRO SPP ---
fig_bombeo = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = presion_bombeo_gauge,
    title = {'text': "Presión Bombeo (SPP) psi", 'font': {'size': 18}},
    gauge = {
        'axis': {'range': [0, 5000]},
        'bar': {'color': "darkblue"},
        'steps' : [
            {'range': [0, 3000], 'color': "lightgray"},
            {'range': [3000, 4500], 'color': "orange"}],
        'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.8, 'value': 4500}
    }
))
fig_bombeo.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
st.plotly_chart(fig_bombeo, use_container_width=True)

import base64

# Función para cargar audio y convertirlo a base64 (para que no falle el navegador)
import base64
import os

def reproducir_audio_local(nombre_archivo, loop=False):
    # 1. Construimos la ruta a tu carpeta assets
    ruta_audio = os.path.join("assets", nombre_archivo)
    
    if os.path.exists(ruta_audio):
        with open(ruta_audio, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            
            # 2. Creamos el HTML con el audio incrustado
            loop_attr = "loop" if loop else ""
            audio_html = f"""
                <audio autoplay {loop_attr}>
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
            """
            st.components.v1.html(audio_html, height=0)
    else:
        st.error(f"No se encontró el archivo: {ruta_audio}")

# --- CÓMO USARLO EN EL KICK ---
if st.session_state.get('evento_activo') == "KICK":
    st.error("🚨 !!! ALERTA: KICK EN PROGRESO !!! 🚨")
    # Cambiá 'alarma.mp3' por el nombre exacto de tu archivo en assets
    reproducir_audio_local("alarma.mp3", loop=True)

# --- CÓMO USARLO EN EL BOTÓN DE CIERRE ---
if st.sidebar.button("🔒 CERRAR BOP (Shut-in)", key="btn_bop_final"):
    reproducir_audio_local("cierre.mp3") # Sonido seco de válvula
    # ... resto de tu lógica ...

if st.button("🔔 Probar Audio de Assets"):
    reproducir_audio_local("alarma.mp3")
def generar_reporte_menfa_v3(nombre_alumno, tiempo, formacion):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 25)
    pdf.cell(0, 20, "MENFA CAPACITACIONES", ln=True, align='C')
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 10, "Simulador de Perforacion y Control de Pozos", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 12)
    
    contenido = f"""
    Este documento certifica el desempeño tecnico en el simulador.
    
    DETALLES DE LA OPERACION:
    --------------------------------------------------
    Alumno: {nombre_alumno}
    Formacion Geologica: {formacion}
    Evento Detectado: KICK (Surgencia de Fluido)
    Tiempo de Reaccion: {tiempo} segundos
    --------------------------------------------------
    """
    pdf.multi_cell(0, 10, contenido)
    
    calificacion = "EXCELENTE" if tiempo < 15 else "SATISFACTORIO" if tiempo < 30 else "RIESGO OPERATIVO"
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, f"CALIFICACION FINAL: {calificacion}", ln=True, align='L')
    
    return pdf.output()
# --- SECCIÓN DE BIBLIOTECA ---
st.sidebar.divider()
st.sidebar.subheader("📚 Biblioteca Técnica")

# 1. Definimos la función con limpieza de caracteres para fpdf2
def generar_manual_tecnico_descargable():
    from fpdf import FPDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- PORTADA TIPO LIBRO ---
    pdf.add_page()
    pdf.set_fill_color(30, 41, 59) # Azul Menfa
    pdf.rect(0, 0, 210, 297, 'F')
    pdf.set_text_color(255, 255, 255)
    
    pdf.ln(80)
    pdf.set_font("Helvetica", 'B', 35) # Cambiado a Helvetica para mayor compatibilidad
    pdf.cell(0, 20, "MENFA 3.0", ln=True, align='C')
    pdf.set_font("Helvetica", 'B', 18)
    pdf.cell(0, 10, "MANUAL DE OPERACIONES Y GUIA TECNICA", ln=True, align='C')
    
    pdf.ln(100)
    pdf.set_font("Helvetica", 'I', 12)
    pdf.cell(0, 10, "Instructor: Fabricio | Cuenca Neuquina & Cuyana", ln=True, align='C')
    pdf.cell(0, 10, "Mendoza, Argentina - 2026", ln=True, align='C')

    # --- PÁGINA 1: INTRODUCCIÓN ---
    pdf.add_page()
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 15, "1. Introduccion al Simulador", ln=True)
    pdf.set_font("Helvetica", '', 11)
    
    intro = ("El Simulador Menfa 3.0 es una herramienta de precision diseñada para el entrenamiento "
             "de personal en operaciones de perforacion. Integra modelos de hidraulica y control de pozos.")
    pdf.multi_cell(0, 7, intro.encode('latin-1', 'ignore').decode('latin-1'))

    # --- PÁGINA 2: GLOSARIO ---
    pdf.ln(10)
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 15, "2. Glosario de Formulas", ln=True)
    
    formulas = [
        ("ROP (Rate of Penetration)", "Velocidad de avance de la mecha (m/h)."),
        ("WOB (Weight on Bit)", "Peso aplicado sobre el trepano."),
        ("MSE (Mechanical Specific Energy)", "Energia requerida para destruir roca."),
        ("ECD (Equivalent Circulating Density)", "Presion real en circulacion.")
    ]

    for tit, desc in formulas:
        pdf.set_font("Helvetica", 'B', 11)
        pdf.cell(0, 8, f"- {tit}:", ln=True)
        pdf.set_font("Helvetica", '', 10)
        pdf.multi_cell(0, 6, desc.encode('latin-1', 'ignore').decode('latin-1'))
        pdf.ln(2)

    # --- PÁGINA 3: EJERCICIOS ---
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 15, "3. Plan de Entrenamiento", ln=True)
    
    ejercicios = [
        "Ejercicio 1: Optimizacion de MSE. Ajustar WOB/RPM.",
        "Ejercicio 2: Navegacion Geologica. Detectar cambios de ROP.",
        "Ejercicio 3: Control de Pozo. Realizar un Shut-in eficaz."
    ]
    
    pdf.set_font("Helvetica", '', 11)
    for ej in ejercicios:
        texto_limpio = f"* {ej}".encode('latin-1', 'ignore').decode('latin-1')
        pdf.multi_cell(0, 10, texto_limpio)
        pdf.ln(2)

    return pdf.output() # fpdf2 entrega bytes/bytearray aquí

# 2. LÓGICA DE COMPILACIÓN Y BOTÓN
try:
    # Generamos el contenido
    resultado_binario = generar_manual_tecnico_descargable()
    
    # CONVERSIÓN CRÍTICA: Forzamos a bytes para que Streamlit no de error de formato
    libro_bytes = bytes(resultado_binario)
    
    st.sidebar.download_button(
        label="📖 Descargar Manual Técnico (Libro)",
        data=libro_bytes,
        file_name="Manual_Tecnico_Menfa_3.pdf",
        mime="application/pdf",
        key="btn_descarga_manual_menfa_vFinal"
    )
    st.sidebar.success("✅ Manual disponible")

except Exception as e:
    st.sidebar.error(f"❌ Error al compilar el libro: {e}")
def mostrar_evaluacion(puntos):
    st.markdown("---")
    st.header("🧾 Planilla de Evaluación Final")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Puntaje Total", f"{puntos}/100")
        if puntos >= 90:
            st.success("🏆 Nivel: EXCELENTE (Operativo Real)")
            nivel = "Nivel 3: Avanzado / Criterio Operativo"
        elif puntos >= 70:
            st.info("🥈 Nivel: APROBADO (Competente)")
            nivel = "Nivel 2: Operador Competente"
        else:
            st.warning("⚠️ Nivel: A MEJORAR")
            nivel = "Nivel 1: Operador en Entrenamiento"
            
    with col2:
        st.write("**Desglose de Competencias:**")
        st.write("- Monitoreo de variables: 20/20 pts")
        st.write("- Toma de decisiones: 30/30 pts")
        st.write("- Control del evento: 20/20 pts")

    if puntaje_final >= 70:
       pdf_bytes = generar_certificado_final(st.session_state.usuario, puntaje_final, nivel_cert, fecha_hoy)
    
    if isinstance(pdf_bytes, bytes):
        st.download_button(
            label="📥 Descargar Certificado Oficial",
            data=pdf_bytes,
            file_name=f"Certificado_MENFA_{st.session_state.usuario}.pdf",
            mime="application/pdf"
        )
    else:
        st.error(f"Error técnico: {pdf_bytes}")

def agregar_falla(msg):
    if msg not in [p['error'] for p in st.session_state.penalizaciones]:
        st.session_state.penalizaciones.append({"hora": datetime.now().strftime("%H:%M"), "error": msg})

# Verificaciones en tiempo real
if sicp > maasp:
    agregar_falla("⚠️ Violación de MAASP: Fractura de Zapata")
if ecd > presion_fractura:
    agregar_falla("🚨 Exceso de ECD: Pérdida de lodo por fractura")

st.divider()
tab_sim, tab_eval = st.tabs(["🎮 Simulador Activo", "📊 Reporte de Competencias"])
# Usamos .get() para dar una lista vacía si 'penalizaciones' no existe
lista_errores = st.session_state.get('penalizaciones', [])
score = max(0, 100 - (len(lista_errores) * 20))

with tab_eval:
    st.header("Resultados de la Maniobra")
    col_e1, col_e2, col_e3 = st.columns(3)
    
    with col_e1:
        # Nota dinámica basada en errores
        score = max(0, 100 - (len(st.session_state.penalizaciones) * 20))
        st.metric("Puntaje Final", f"{score}/100", delta=f"-{len(st.session_state.penalizaciones)} errores")
    
    with col_e2:
        st.write("**Infracciones Detectadas:**")
        for p in st.session_state.penalizaciones:
            st.write(f"- {p['hora']}: {p['error']}")

def generar_certificado(nombre, nota):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "CERTIFICADO DE ENTRENAMIENTO - MENFA", 0, 1, 'C')
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, f"Se certifica que el alumno: {nombre}", 0, 1, 'L')
    pdf.cell(200, 10, f"Ha completado la simulación con una nota de: {nota}/100", 0, 1, 'L')
    return pdf.output(dest='S').encode('latin-1')

# Botón de descarga en la pestaña de evaluación
if st.button("🎓 Descargar Certificado de Competencia"):
    pdf_bytes = generar_certificado(st.session_state.usuario, score)
    st.download_button("Click aquí para guardar PDF", data=pdf_bytes, file_name="certificado_menfa.pdf")

# ==========================================
# --- MÓDULO FINAL: CIERRE DE OPERACIONES ---
# ==========================================
st.write("<br><br>", unsafe_allow_html=True)
st.divider()

# Creamos un contenedor especial para el final
with st.container():
    col_final1, col_final2 = st.columns([2, 1])

    with col_final1:
        st.title("🏁 Fin de la Simulación")
        st.subheader(f"Operador: {st.session_state.usuario}")
        st.write("Has completado el módulo de perforación avanzada. A continuación, se presenta tu registro visual y técnico.")

    with col_final2:
        # Aquí integramos el sonido que mencionaste (beep de finalización)
        # Asegurate de que el archivo esté en la carpeta raíz o 'assets'
        if os.path.exists("freesound_community-exposure-unit-beep-sound-2-97240 (1).mp3"):
            with open("freesound_community-exposure-unit-beep-sound-2-97240 (1).mp3", "rb") as f:
                data = f.read()
                b64 = base64.b64encode(data).decode()
                st.components.v1.html(f"""
                    <audio autoplay>
                        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                    </audio>
                """, height=0)
# ==========================================
# --- 10. MÓDULO FINAL Y CERTIFICACIÓN ---
# ==========================================
st.write("<br><br>", unsafe_allow_html=True)
st.divider()

# --- PASO A: CÁLCULO DE PUNTAJE SEGURO ---
try:
    # Usamos .get para evitar NameError si la variable no existe
    puntos_raw = st.session_state.get('puntos', 0)
    if isinstance(puntos_raw, (list, np.ndarray)):
        puntaje_final = int(puntos_raw[0]) 
    else:
        puntaje_final = int(puntos_raw)
except:
    puntaje_final = 0

# Definición del nivel para el diploma
if puntaje_final >= 90: 
    nivel_cert = "Excelente - Operativo Real"
elif puntaje_final >= 70: 
    nivel_cert = "Aprobado - Competente"
else: 
    nivel_cert = "En Entrenamiento"

# ==========================================
# --- 10. CIERRE DE SESIÓN Y EVALUACIÓN ---
# ==========================================

# --- PASO A: REGISTRO VISUAL ---
st.write("### 📸 Registro Visual de la Jornada")
img_col1, img_col2, img_col3 = st.columns(3)

with img_col1:
    if os.path.exists("Imagen generada por Gemini_dn7zasdn7zasdn7z.png"):
        st.image("Imagen generada por Gemini_dn7zasdn7zasdn7z.png", caption="Análisis de Formación", use_container_width=True)
with img_col2:
    if os.path.exists("Imagen generada por Géminis_i9vg9ti9vg9ti9vg.png"):
        st.image("Imagen generada por Géminis_i9vg9ti9vg9ti9vg.png", caption="Estado del Trépano", use_container_width=True)
with img_col3:
    if os.path.exists("Imagen generada por Gemini_jl30d0jl30d0jl30.png"):
        st.image("Imagen generada por Gemini_jl30d0jl30d0jl30.png", caption="Perfil del Pozo", use_container_width=True)

st.write("---")

# --- PASO B: EVALUACIÓN FINAL DE SEGURIDAD ---
try:
    # 1. Recuperamos las penalizaciones
    penalizaciones_lista = st.session_state.get('penalizaciones', [])
    eventos_criticos = len(penalizaciones_lista)
    
    # 2. Cálculo de puntos
    puntaje_final = max(0, 100 - (eventos_criticos * 20))
    
    # 3. Definición del rango
    if puntaje_final >= 90:
        nivel_cert = "Excelente - Operativo Real"
    elif puntaje_final >= 70:
        nivel_cert = "Aprobado - Competente"
    else:
        nivel_cert = "En Entrenamiento"

except Exception as e:
    puntaje_final = 0
    nivel_cert = "Error de Sistema"
    st.error(f"Error en motor de evaluación: {e}")

# --- PASO C: REPORTE VISUAL ---
st.markdown("### 📊 Reporte de Seguridad Operacional")

if st.session_state.get('penalizaciones'):
    df_reporte = pd.DataFrame(st.session_state.penalizaciones)
    st.dataframe(df_reporte, use_container_width=True)
    st.warning(f"Atención: Se registraron {len(st.session_state.penalizaciones)} infracciones.")
else:
    st.success("✅ Operación segura: Sin infracciones detectadas.")

st.info(f"**Resultado Final:** {puntaje_final}/100 - **Nivel:** {nivel_cert}")

# --- PASO D: BOTONES DE ACCIÓN ---
st.write("---")
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if puntaje_final >= 70:
        try:
            # Ahora sí, generamos el PDF con los datos calculados arriba
            pdf_bytes = generar_certificado_final(
                st.session_state.usuario, 
                puntaje_final, 
                nivel_cert, 
                datetime.now().strftime("%d/%m/%Y")
            )
            
            st.download_button(
                label="🎓 Descargar Certificado Oficial",
                data=pdf_bytes,
                file_name=f"Certificado_MENFA_{st.session_state.usuario}.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="descarga_final_cert"
            )
        except Exception as e:
            st.error(f"Error al preparar el PDF: {e}")
    else:
        st.info("Puntaje insuficiente para la certificación oficial.")

with col_btn2:
    if st.button("💾 Finalizar y Salir", type="primary", use_container_width=True, key="btn_salir_sistema"):
        st.balloons()
        st.success("Sesión enviada a la base de datos de MENFA.")
        time.sleep(2)
        st.session_state.autenticado = False
        st.rerun()

# --- PASO E: SIDEBAR FINAL ---
st.sidebar.markdown("---")
st.sidebar.caption(f"ID Sesión: {random.randint(1000, 9999)} | MENFA 3.0")
