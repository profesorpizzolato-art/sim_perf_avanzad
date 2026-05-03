import streamlit as st
import os
import time
import pizarra_maestra as pm
import motor_perforacion as motor
import control_operativo as control
import visual_pro as vis

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(layout="wide", page_title="MENFA Drilling Sim 3.0", initial_sidebar_state="expanded")

# 2. CONEXIÓN Y LOGO
piz = pm.conectar_pizarra()

def mostrar_logo():
    ruta_logo = "assets/logo_menfa.png" 
    if os.path.exists(ruta_logo):
        st.sidebar.image(ruta_logo, use_container_width=True)
    else:
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

# 5. RENDERIZADO Y LÓGICA SEGÚN ROL
mostrar_logo()

if st.session_state.rol == "alumno":
    # Primero renderizamos para capturar inputs de los sliders
    datos_actuales = motor.calcular_todo(piz)
    vis.renderizar_cabina_perforador(piz, datos_actuales)
    
    # Segundo: Calculamos el avance físico con los datos recién capturados
    if piz.get("rpm", 0) > 0 and piz.get("wob", 0) > 0 and not piz.get("bop_cerrado"):
        rop_actual = datos_actuales.get("ROP", 0)
        # Multiplicador x5 para visibilidad pedagógica en clase
        avance = (rop_actual / 3600) * 5  
        piz["profundidad_actual"] = round(piz.get("profundidad_actual", 0) + avance, 2)
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.rol = None
        st.rerun()

elif st.session_state.rol == "instructor":
    # El instructor ve el panel de control y el progreso del alumno
    control.panel_instructor(piz)
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.rol = None
        st.rerun()

# 6. AUTO-REFRESH (El corazón del simulador)
time.sleep(0.5)
st.rerun()
