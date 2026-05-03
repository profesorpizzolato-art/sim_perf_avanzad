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

# Inicializar variables críticas si no existen
if "volumen_piletas" not in piz: piz["volumen_piletas"] = 1200.0
if "profundidad_actual" not in piz: piz["profundidad_actual"] = 0.0

# --- SELECTOR DE ROL EN SIDEBAR ---
st.sidebar.title("👤 ACCESO DE USUARIO")
if st.sidebar.checkbox("Modo Instructor"):
    st.session_state.rol = "instructor"
else:
    st.session_state.rol = "alumno"

st.sidebar.divider()

# 3. FILTRO DE ACCESO
if not piz.get("configurado"):
    pm.selector_yacimiento_mendoza(piz)
    st.stop()

# 4. PROCESAMIENTO DE FÍSICA (Motor de cálculo)
datos_fisica = motor.calcular_todo(piz)

# --- 5. MOTOR DE AVANCE GLOBAL + GEONAVEGACIÓN ---
if not piz.get("bop_cerrado"):
    # A. Avance de Profundidad
    rop_actual = datos_fisica.get("ROP", 0)
    if rop_actual > 0:
        factor_tiempo = 5 
        avance = (rop_actual / 3600) * factor_tiempo
        piz["profundidad_actual"] = round(piz.get("profundidad_actual", 0) + avance, 4)
        
        # B. LÓGICA DE GEONAVEGACIÓN (Reincorporada)
        # Actualizamos la trayectoria según el Toolface y la potencia de curva
        piz["inclinacion"] = datos_fisica.get("nueva_inclinacion", piz.get("inclinacion", 0))
        piz["azimut"] = datos_fisica.get("nuevo_azimut", piz.get("azimut", 0))
        piz["tvd"] = datos_fisica.get("TVD", piz.get("profundidad_actual", 0))
    
    # C. Dinámica de Tanques
    influjo_rate = datos_fisica.get("Influjo", 0)
    if influjo_rate != 0:
        piz["volumen_piletas"] += (influjo_rate * 0.1)

# 6. INTERFAZ SEGÚN ROL
if st.session_state.rol == "alumno":
    # Cabina con Manómetros y Pestaña de Trayectoria
    vis.renderizar_cabina_perforador(piz, datos_fisica)
    
    if st.sidebar.button("Terminar Turno (Cerrar Sesión)"):
        st.session_state.rol = None
        st.rerun()

elif st.session_state.rol == "instructor":
    # Panel para sabotajes y monitoreo de geonavegación
    control.panel_instructor(piz)
    
    if st.sidebar.button("Finalizar Simulación"):
        pm.resetear_simulacion(piz)
        st.session_state.rol = None
        st.rerun()

# 7. ALERTAS Y LATIDO
if datos_fisica.get("Influjo", 0) > 0:
    st.toast("⚠️ GANANCIA EN PILETAS DETECTADA", icon="🚨")

time.sleep(0.5)
st.rerun()
