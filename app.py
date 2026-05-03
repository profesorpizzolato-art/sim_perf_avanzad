import streamlit as st
import os
import time
import pizarra_maestra as pm
import motor_perforacion as motor
import control_operativo as control
import visual_pro as vis

# 1. CONFIGURACIÓN TÉCNICA DE PÁGINA
st.set_page_config(
    layout="wide", 
    page_title="MENFA Drilling Sim 3.0", 
    page_icon="🏗️",
    initial_sidebar_state="expanded"
)

# 2. CONEXIÓN A LA PIZARRA (Estado Global)
piz = pm.conectar_pizarra()

# 3. FILTRO DE ACCESO (Muro de seguridad)
if not piz.get("configurado"):
    pm.selector_yacimiento_mendoza(piz)
    st.stop()

# 4. PROCESAMIENTO DE FÍSICA (Cálculos antes de renderizar)
# Calculamos Torque, Drag, Hook Load y Geonavegación con los datos actuales
datos_fisica = motor.calcular_todo(piz)

# 5. INTERFAZ SEGÚN ROL
if st.session_state.rol == "alumno":
    # LA CABINA: Aquí se capturan RPM, WOB, Caudal, Inclinación y Azimut
    vis.renderizar_cabina_perforador(piz, datos_fisica)
    
    # 6. MOTOR DE AVANCE Y DINÁMICA MECÁNICA
    # Solo si hay actividad mecánica (RPM > 0) el pozo progresa
    if piz.get("rpm", 0) > 0 and not piz.get("bop_cerrado"):
        # Recuperamos el ROP calculado por el motor
        rop_actual = datos_fisica.get("ROP", 0)
        
        # Simulación de avance (Ajustado para visibilidad en clase)
        factor_tiempo = 5 
        avance = (rop_actual / 3600) * factor_tiempo
        piz["profundidad_actual"] = round(piz.get("profundidad_actual", 0) + avance, 4)
        
        # Actualizamos variables de navegación en la pizarra
        piz["torque"] = datos_fisica.get("torque", 0)
        piz["hook_load"] = datos_fisica.get("hook_load", 0)
        piz["spp"] = datos_fisica.get("spp", 0)
        
    if st.sidebar.button("Terminar Turno (Cerrar Sesión)"):
        st.session_state.rol = None
        st.rerun()

elif st.session_state.rol == "instructor":
    # PANEL DEL INSTRUCTOR: Monitoreo de Torque/Drag y envío de fallas
    control.panel_instructor(piz)
    
    if st.sidebar.button("Finalizar Simulación"):
        pm.resetear_simulacion(piz)
        st.session_state.rol = None
        st.rerun()

# 7. SISTEMA DE ALERTAS CRÍTICAS
if piz.get("alarma"):
    st.toast("⚠️ ALERTA DE SEGURIDAD EN POZO", icon="🚨")

# 8. LATIDO DEL SIMULADOR (Auto-refresh)
# Un delay de 0.5s permite que los manómetros se muevan fluidos
time.sleep(0.5)
st.rerun()
