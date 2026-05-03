import streamlit as st
import os
import time
import pizarra_maestra as pm
import motor_perforacion as motor
import control_operativo as control
import visual_pro as vis

# 1. CONFIGURACIÓN TÉCNICA
st.set_page_config(layout="wide", page_title="MENFA Drilling Sim 3.0", page_icon="🏗️")

# 2. CONEXIÓN A LA PIZARRA (Estado Global)
piz = pm.conectar_pizarra()

# Inicializar volumen de piletas si es la primera vez
if "volumen_piletas" not in piz:
    piz["volumen_piletas"] = 1200.0

# --- NUEVO: SELECTOR DE ROL EN SIDEBAR ---
st.sidebar.title("👤 ACCESO DE USUARIO")
if st.sidebar.checkbox("Modo Instructor"):
    st.session_state.rol = "instructor"
else:
    st.session_state.rol = "alumno"

st.sidebar.divider()

# 3. FILTRO DE ACCESO (Muro de seguridad)
if not piz.get("configurado"):
    pm.selector_yacimiento_mendoza(piz)
    st.stop()

# 4. PROCESAMIENTO DE FÍSICA (Cálculos base para ambos roles)
datos_fisica = motor.calcular_todo(piz)

# --- 5. MOTOR DE AVANCE GLOBAL (Simulación en tiempo real) ---
if not piz.get("bop_cerrado"):
    # A. Avance de Profundidad acumulativo
    rop_actual = datos_fisica.get("ROP", 0)
    if rop_actual > 0:
        factor_tiempo = 5 
        avance = (rop_actual / 3600) * factor_tiempo
        piz["profundidad_actual"] = round(piz.get("profundidad_actual", 0) + avance, 4)
    
    # B. Dinámica de Tanques (Reacción al Kick o Pérdida)
    influjo_rate = datos_fisica.get("Influjo", 0)
    if influjo_rate != 0:
        # El volumen sube o baja en la pizarra común
        piz["volumen_piletas"] += (influjo_rate * 0.1)

# 6. INTERFAZ SEGÚN ROL SELECCIONADO
if st.session_state.rol == "alumno":
    # Cabina de mando del alumno
    vis.renderizar_cabina_perforador(piz, datos_fisica)
    
    if st.sidebar.button("Terminar Turno (Cerrar Sesión)"):
        st.session_state.rol = None
        st.rerun()

elif st.session_state.rol == "instructor":
    # Panel de control de fallas y monitoreo
    control.panel_instructor(piz)
    
    if st.sidebar.button("Finalizar Simulación"):
        pm.resetear_simulacion(piz)
        st.session_state.rol = None
        st.rerun()

# 7. SISTEMA DE ALERTAS (Visible para ambos)
if datos_fisica.get("Influjo", 0) > 0:
    st.toast("⚠️ GANANCIA EN PILETAS DETECTADA", icon="🚨")

# 8. LATIDO DEL SIMULADOR (Refresco automático)
time.sleep(0.5)
st.rerun()
