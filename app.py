import streamlit as st
import time
import os
import json

# Importación de tus módulos técnicos
import pizarra_maestra as pm
import motor_perforacion as motor
import control_operativo as control
import visual_pro as vis
import sarta_pro as sarta

# 1. CONFIGURACIÓN E IDENTIDAD INSTITUCIONAL
st.set_page_config(
    layout="wide", 
    page_title="MENFA Drilling Sim 3.0", 
    page_icon="assets/logo_menfa.png"
)

# 2. CONSTANTES DE SEGURIDAD Y ACCESO
CLAVE_ALUMNO = "menfa2026"
CLAVE_INSTRUCTOR = "admin_mza"

if "auth" not in st.session_state:
    st.session_state.auth = False
    st.session_state.rol = None
    st.session_state.usuario = None

# Pantalla de Login
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color:#00ffcc;'>🛡️ MENFA 3.0 | ACCESO AL RIG</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        input_pass = st.text_input("Código de Seguridad:", type="password")
        if st.button("CONECTAR CON LA CABINA", use_container_width=True):
            if input_pass == CLAVE_INSTRUCTOR:
                st.session_state.auth, st.session_state.rol, st.session_state.usuario = True, "instructor", "Fabricio Pizzolato"
                st.rerun()
            elif input_pass == CLAVE_ALUMNO:
                st.session_state.auth, st.session_state.rol, st.session_state.usuario = True, "alumno", "Operador en Evaluación"
                st.rerun()
            else:
                st.error("Código inválido.")
    st.stop()

# 3. CONEXIÓN A LA PIZARRA (Blindada contra errores de archivo vacío)
try:
    piz = pm.conectar_pizarra()
except Exception:
    piz = {
        "configurado": False, 
        "profundidad_actual": 0.0, 
        "tvd_target": 3500.0, 
        "bop_cerrado": False, 
        "volumen_piletas": 500.0,
        "influjo_instructor": 0.0,
        "inclinacion": 0.0,
        "azimut": 0.0,
        "yacimiento": "No Definido"
    }
    st.sidebar.error("⚠️ Pizarra inicializada en modo seguro.")

# 4. FILTRO DE CONFIGURACIÓN DEL YACIMIENTO
# Corregido para asegurar que el alumno pase una vez que el instructor active
if not piz.get("configurado"):
    st.warning("⚠️ El sistema requiere configuración inicial del yacimiento.")
    
    if st.session_state.rol == "instructor":
        # Botón de arranque forzado con datos de Mendoza
        if st.button("🚀 ACTIVAR OPERACIONES (ARRANQUE RÁPIDO)"):
            piz["configurado"] = True
            piz["profundidad_actual"] = 1200.0  # Empezamos ya en profundidad
            piz["tvd_target"] = 3500.0
            piz["yacimiento"] = "Vaca Muerta - Mendoza"
            pm.actualizar_fichero(piz)
            st.rerun()
            
        pm.selector_yacimiento_mendoza(piz)
    else:
        st.info("Esperando que el instructor configure el pozo...")
        # Botón de refresco manual para el alumno
        if st.button("🔄 Verificar Estado del Pozo"):
            st.rerun()
        st.stop()

# 5. CÁLCULOS TÉCNICOS Y API 5DP
datos_fisica = motor.calcular_todo(piz)
resistencia = sarta.modulo_sartas_api(piz) 

datos_fisica["hook_load"] = resistencia.get("hook_load", 0)
datos_fisica["max_yield"] = resistencia.get("max_yield", 0)

# 6. LÓGICA DE AVANCE Y WELL CONTROL
if not piz.get("bop_cerrado"):
    rop_actual = datos_fisica.get("ROP", 0)
    if rop_actual > 0:
        avance = (rop_actual / 3600) * 10 
        piz["profundidad_actual"] = round(float(piz.get("profundidad_actual", 0)) + avance, 4) 
    
    influjo_rate = piz.get("influjo_instructor", 0) 
    piz["volumen_piletas"] = float(piz.get("volumen_piletas", 500.0)) + (influjo_rate * 0.1)
    datos_fisica["Influjo"] = influjo_rate 

# Guardar estado actual
pm.actualizar_fichero(piz) 

# 7. INTERFAZ DE USUARIO (DASHBOARD)
st.sidebar.title(f"👤 {st.session_state.usuario}")
st.sidebar.info(f"📍 Yacimiento: {piz.get('yacimiento', 'Mendoza')}")

# Barra de progreso - Con protección contra división por cero
meta = float(piz.get("tvd_target", 3500.0))
if meta <= 0: meta = 3500.0 # Valor de seguridad
prof_actual = float(piz.get("profundidad_actual", 0.0))
progreso_porcentaje = min(prof_actual / meta, 1.0)
st.progress(progreso_porcentaje, text=f"Progreso: {prof_actual:.2f} m / {meta} m")

# Renderizado según Rol
if st.session_state.rol == "alumno":
    vis.renderizar_cabina_perforador(piz, datos_fisica)
else:
    tab1, tab2, tab3 = st.tabs(["🎮 Control de Pozo", "🔩 Ingeniería de Sarta", "📊 Monitor en Tiempo Real"])
    with tab1:
        control.panel_instructor(piz)
    with tab2:
        sarta.configuracion_ui()
    with tab3:
        st.write("Datos de telemetría enviados a las cabinas.")
        st.json(piz)

# 8. ALERTAS DE SEGURIDAD OPERATIVA
if datos_fisica["max_yield"] > 0 and datos_fisica["hook_load"] > (datos_fisica["max_yield"] * 0.9):
    st.error("🚨 ALERTA: TENSIÓN EXCESIVA EN SARTA - RIESGO DE CORTE")

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.auth = False
    st.rerun()

# Refresco automático cada 1 segundo
time.sleep(1)
st.rerun()
