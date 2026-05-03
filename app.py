import streamlit as st
import os
import time
import pizarra_maestra as pm
import motor_perforacion as motor
import control_operativo as control
import visual_pro as vis

# 1. CONFIGURACIÓN DE PÁGINA (Debe ser la primera instrucción de Streamlit)
st.set_page_config(layout="wide", page_title="MENFA Drilling Sim 3.0", initial_sidebar_state="expanded")

# 2. CONEXIÓN Y LOGO
piz = pm.conectar_pizarra()

def mostrar_logo():
    # Buscamos el logo en la ruta que mencionaste con manejo de errores
    ruta_logo = "assets/logo_menfa.png" 
    if os.path.exists(ruta_logo):
        st.sidebar.image(ruta_logo, use_container_width=True)
    else:
        # Fallback visual si el logo no carga
        st.sidebar.markdown("""
            <div style="background-color:#00ffcc; padding:10px; border-radius:5px; text-align:center;">
                <h2 style="color:black; margin:0;">MENFA</h2>
                <small style="color:black; font-weight:bold;">IPCL MENDOZA</small>
            </div><br>
        """, unsafe_allow_html=True)

# 3. LÓGICA DE LOGIN / ROL
if "rol" not in st.session_state or st.session_state.rol is None:
    mostrar_logo()
    st.title("🛡️ Sistema de Simulación IPCL MENFA")
    st.subheader("Seleccione su perfil de acceso:")
    
    col_ins, col_alu = st.columns(2)
    with col_ins:
        if st.button("INGRESAR COMO INSTRUCTOR", use_container_width=True):
            st.session_state.rol = "instructor"
            st.rerun()
    with col_alu:
        if st.button("INGRESAR COMO ALUMNO", use_container_width=True):
            st.session_state.rol = "alumno"
            st.rerun()
    st.stop()

# 4. CONFIGURACIÓN INICIAL DEL YACIMIENTO
if not piz.get("configurado"):
    pm.selector_yacimiento_mendoza(piz)
    st.stop()

if st.session_state.rol == "alumno":
    # Aquí el alumno mueve los controles y se guardan en 'piz'
    vis.renderizar_cabina_perforador(piz, motor.calcular_todo(piz))
    
    # 2. AHORA calculamos el avance con los datos frescos
    datos_fisica = motor.calcular_todo(piz)
    if piz.get("rpm", 0) > 0 and piz.get("wob", 0) > 0:
        rop_actual = datos_fisica.get("ROP", 0)
        # Aumentamos la velocidad de simulación para que se note el movimiento
        avance = (rop_actual / 3600) * 5  
        piz["profundidad_actual"] += avance

elif st.session_state.rol == "instructor":
    control.panel_instructor(piz)

# 7. AUTO-REFRESH (Mantiene vivos los manómetros)
time.sleep(0.5)
st.rerun()
