import streamlit as st
import time
import os
import json

# Importación de tus módulos técnicos de MENFA
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

# 2. GESTIÓN DE SESIÓN
if "auth" not in st.session_state:
    st.session_state.auth = False
    st.session_state.rol = None
    st.session_state.usuario = None

# Pantalla de Login (Sin cambios, funciona perfecto)
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color:#00ffcc;'>🛡️ MENFA 3.0 | ACCESO AL RIG</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        input_pass = st.text_input("Código de Seguridad:", type="password")
        if st.button("CONECTAR CON LA CABINA", use_container_width=True):
            if input_pass == "admin_mza":
                st.session_state.auth, st.session_state.rol, st.session_state.usuario = True, "instructor", "Fabricio Pizzolato"
                st.rerun()
            elif input_pass == "menfa2026":
                st.session_state.auth, st.session_state.rol, st.session_state.usuario = True, "alumno", "Operador en Evaluación"
                st.rerun()
            else:
                st.error("Código inválido.")
    st.stop()

# 3. CONEXIÓN A LA PIZARRA (CON PERSISTENCIA)
try:
    piz = pm.conectar_pizarra()
    # Si el archivo existe pero está vacío o corrupto, lanzamos error para ir al except
    if not piz or not isinstance(piz, dict):
        raise ValueError("Pizarra vacía")
except Exception:
    # Mantenemos los valores de la captura image_5df6b7.png para no perder el progreso
    piz = {
        "configurado": True, 
        "profundidad_actual": 1200.0, 
        "tvd_target": 3500.0, 
        "bop_cerrado": False, 
        "volumen_piletas": 500.0,
        "influjo_instructor": 0.0,
        "yacimiento": "Vaca Muerta - Mendoza",
        "orden": "Sin órdenes pendientes"
    }

# 4. FILTRO DE CONFIGURACIÓN (Mendoza Focus)
if not piz.get("configurado"):
    if st.session_state.rol == "instructor":
        st.warning("⚠️ Configuración pendiente.")
        pm.selector_yacimiento_mendoza(piz)
        if st.button("🚀 ACTIVAR OPERACIONES"):
            piz["configurado"] = True
            piz["profundidad_actual"] = 1200.0
            pm.actualizar_fichero(piz)
            st.rerun()
    else:
        st.info("Esperando al Instructor...")
        time.sleep(2)
        st.rerun()
        st.stop()

# 5. MOTOR DE FÍSICA Y SARTA (API 5DP)
datos_fisica = motor.calcular_todo(piz)
resistencia = sarta.modulo_sartas_api(piz) 
datos_fisica["hook_load"] = resistencia.get("hook_load", 180) # Valor base de tu captura

# 6. LÓGICA DE AVANCE (Sólo si no hay BOP cerrado)
if not piz.get("bop_cerrado"):
    rop_actual = datos_fisica.get("ROP", 0)
    if rop_actual > 0:
        avance = (rop_actual / 3600) * 5 # Tiempo simulado acelerado
        piz["profundidad_actual"] = round(float(piz.get("profundidad_actual", 0)) + avance, 2)
    
    # Well Control: El influjo afecta a las piletas
    piz["volumen_piletas"] = float(piz.get("volumen_piletas", 500)) + (piz.get("influjo_instructor", 0) * 0.1)

# 7. INTERFAZ DE USUARIO (DASHBOARD)
st.sidebar.title(f"👤 {st.session_state.usuario}")
st.sidebar.markdown(f"**Yacimiento:** {piz.get('yacimiento')}")

# Barra de progreso blindada
meta = max(float(piz.get("tvd_target", 3500)), 1)
progreso = min(float(piz.get("profundidad_actual", 0)) / meta, 1.0)
st.progress(progreso, text=f"Progreso: {piz['profundidad_actual']} m / {meta} m")

# --- RENDERIZADO POR ROL ---
if st.session_state.rol == "alumno":
    # Mostramos la orden del instructor en pantalla
    st.chat_message("instructor").write(piz.get("orden", "Sin órdenes."))
    # El alumno opera y guardamos su actividad
    piz_retorno = vis.renderizar_cabina_perforador(piz, datos_fisica)
    if piz_retorno:
        pm.actualizar_fichero(piz_retorno)
else:
    # Panel Instructor
    tab1, tab2, tab3 = st.tabs(["🎮 Control Operativo", "🔩 Ingeniería", "📊 Telemetría"])
    with tab1:
        # Pasamos la pizarra para que el instructor vea lo que el alumno hace
        control.panel_instructor(piz) 
    with tab2:
        sarta.configuracion_ui()
    with tab3:
        st.json(piz)

# 8. CIERRE Y REFRESCO
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.auth = False
    st.rerun()

time.sleep(1) # Un segundo para no saturar el disco
st.rerun()
