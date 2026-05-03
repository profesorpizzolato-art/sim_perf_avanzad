import streamlit as st
import os
import time
import pizarra_maestra as pm
import motor_perforacion as motor
import control_operativo as control
import visual_pro as vis

# 1. CONFIGURACIÓN TÉCNICA
st.set_page_config(layout="wide", page_title="MENFA Drilling Sim 3.0", page_icon="🏗️")

# 2. ESTADO GLOBAL
piz = pm.conectar_pizarra()

# Inicializar volumen si no existe
if "volumen_piletas" not in piz:
    piz["volumen_piletas"] = 1200.0

if not piz.get("configurado"):
    pm.selector_yacimiento_mendoza(piz)
    st.stop()

# 3. PROCESAMIENTO DE FÍSICA (Cálculos base)
# Esto se ejecuta en cada ciclo para ambos roles
datos_fisica = motor.calcular_todo(piz)

# --- 4. MOTOR DE AVANCE GLOBAL (Aquí es donde sucede la magia) ---
# Movimos esto afuera de los IF de rol para que el pozo avance siempre
if not piz.get("bop_cerrado"):
    # A. Avance de Profundidad
    rop_actual = datos_fisica.get("ROP", 0)
    if rop_actual > 0:
        factor_tiempo = 5 
        avance = (rop_actual / 3600) * factor_tiempo
        piz["profundidad_actual"] = round(piz.get("profundidad_actual", 0) + avance, 4)
    
    # B. Dinámica de Tanques (Influjo o Pérdida)
    influjo_rate = datos_fisica.get("Influjo", 0)
    if influjo_rate != 0:
        # Actualizamos el volumen en la pizarra maestra
        piz["volumen_piletas"] += (influjo_rate * 0.1)

# 5. INTERFAZ SEGÚN ROL
if st.session_state.rol == "alumno":
    vis.renderizar_cabina_perforador(piz, datos_fisica)
    
    if st.sidebar.button("Terminar Turno (Cerrar Sesión)"):
        st.session_state.rol = None
        st.rerun()

elif st.session_state.rol == "instructor":
    # El instructor usa su panel pero los datos_fisica ya traen el avance
    control.panel_instructor(piz)
    
    if st.sidebar.button("Finalizar Simulación"):
        pm.resetear_simulacion(piz)
        st.session_state.rol = None
        st.rerun()

# 6. SISTEMA DE ALERTAS
if datos_fisica.get("Influjo", 0) > 0:
    st.toast("⚠️ GANANCIA EN PILETAS DETECTADA", icon="🚨")

# 7. LATIDO DEL SIMULADOR
time.sleep(0.5)
st.rerun()
