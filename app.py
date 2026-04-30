import streamlit as st
import pizarra_maestra as pm
import motor_perforacion as motor
import control_operativo as control
import visual_pro as vis
import time

# Configuración de página ancha para que no se vea vacío
st.set_page_config(layout="wide", page_title="MENFA Drilling Sim 3.0")

piz = pm.conectar_pizarra()

if not piz.get("configurado"):
    pm.selector_yacimiento_mendoza(piz)
    st.stop()

# --- Bucle de simulación automática ---
if piz.get("rpm", 0) > 0 and piz.get("wob", 0) > 0:
    # El pozo avanza: ROP (m/h) / 3600 para pasarlo a metros por segundo
    avance = (piz.get("rop", 0) / 3600) * 2  # Aceleramos un poco para la clase
    piz["profundidad_actual"] = round(piz.get("profundidad_actual", 0) + avance, 2)

# Cálculo de física
datos_pozo = motor.calcular_todo(piz)

if st.session_state.rol == "instructor":
    control.panel_instructor(piz)
else:
    vis.renderizar_cabina_perforador(piz, datos_pozo)

# Auto-refresh para que los relojes se muevan solos
time.sleep(0.5)
st.rerun()
