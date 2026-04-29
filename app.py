import streamlit as st
import pizarra_maestra as pm
import motor_perforacion as motor
import control_operativo as control
import visual_pro as vis

# 1. Conexión a la nube de datos de Mendoza
piz = pm.conectar_pizarra()

# 2. Pantalla de Selección (Mendoza/Alumnos)
if not piz.get("configurado"):
    pm.selector_yacimiento_mendoza(piz)
    st.stop()

# 3. Cálculo de la física en tiempo real
datos_pozo = motor.calcular_todo(piz)

# 4. Interfaz dividida por Roles
if st.session_state.rol == "instructor":
    control.panel_instructor(piz)
else:
    vis.renderizar_cabina_perforador(piz, datos_pozo)
