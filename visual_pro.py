import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os

def renderizar_cabina_perforador(piz, datos):
    # --- 1. ESTILO CSS Y BRANDING (LOGO) ---
    st.markdown("""
        <style>
        .main { background-color: #0e1117; }
        [data-testid="stMetricValue"] { font-size: 35px; color: #00ffcc; }
        .console-box {
            background-color: #1e1e1e; padding: 15px; border-radius: 8px; 
            border-left: 5px solid #00ffcc; margin-bottom: 10px;
        }
        .msg-instructor {
            background-color: #262730; padding: 15px; border-radius: 10px;
            border: 1px solid #ffcc00; margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Encabezado con Logo
    col_logo, col_tit = st.columns([1, 4])
    with col_logo:
        # Intento de cargar logo desde assets
        path_logo = "assets/logo_menfa.png"
        if os.path.exists(path_logo):
            st.image(path_logo, width=120)
        else:
            st.markdown("<h2 style='color:#00ffcc;'>MENFA</h2>", unsafe_allow_html=True)
    
    with col_tit:
        st.title("🛡️ MENFA 3.0 | MENDOZA")
        st.caption(f"YACIMIENTO: {piz.get('yacimiento', 'GODOY CRUZ')} | PERFORADOR: {st.session_state.get('user', 'ALUMNO')}")

    # --- 2. CONSOLA DE ÓRDENES INTERACTIVAS ---
    if piz.get("mensaje_instructor"):
        st.markdown('<div class="msg-instructor">', unsafe_allow_html=True)
        st.warning(f"📻 **RADIO INSTRUCTOR:** {piz['mensaje_instructor']}")
        
        c_acc, c_send = st.columns([3, 1])
        with c_acc:
            accion_alumno = st.selectbox("Confirmar acción realizada:", 
                                        ["Seleccionar...", "Caudal ajustado", "Peso en fondo corregido", 
                                         "Pozo cerrado (BOP)", "Densidad de lodo incrementada"])
        with c_send:
            if st.button("ENVIAR REPORTE"):
                if accion_alumno != "Seleccionar...":
                    piz["ultima_accion"] = accion_alumno
                    piz["mensaje_instructor"] = None # Limpia la orden al responder
                    st.success("Reporte enviado.")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if piz.get("alarma"):
        st.error("🚨 ALERTA: SURGENCIA / KICK DETECTADO")

    # --- 3. SIDEBAR DE MANDOS ---
    with st.sidebar:
        st.subheader("🕹️ Controles de Cuadro")
        piz["rpm"] = st.slider("Rotación (RPM)", 0, 180, int(piz.get("rpm", 0)), key="s_rpm")
        piz["wob"] = st.slider("Peso (klbs)", 0, 60, int(piz.get("wob", 0)), key="s_wob")
        piz["caudal"] = st.slider("Bombas (GPM)", 0, 1200, int(piz.get("caudal", 0)), key="s_caudal")
        
        st.divider()
        st.metric("PROFUNDIDAD", f"{piz.get('profundidad_actual', 0):.2f} m")
        st.metric("TVD OBJETIVO", f"{piz.get('tvd_target', 3000)} m")

    # --- 4. SISTEMA DE PESTAÑAS (TABS) ---
    t_op, t_geo, t_mud, t_bop = st.tabs(["📊 OPERACIÓN", "🚀 GEONAVEGACIÓN", "🛢️ LODOS", "🛡️ SEGURIDAD"])

    with t_op:
        # Fila 1: Manómetros
        col1, col2, col3 = st.columns(3)
        with col1: st.plotly_chart(crear_manometro(datos.get("SPP", 0), "BOMBAS", "PSI", 5000, "#00ffcc"), use_container_width=True)
        with col2: st.plotly_chart(crear_manometro(datos.get("ROP", 0), "AVANCE", "m/h", 80, "#ffcc00"), use_container_width=True)
        with col3: st.plotly_chart(crear_manometro(datos.get("Carga_Gancho", 150), "PESO", "klbs", 400, "#ff3300"), use_container_width=True)

        st.divider()
        # Gráfico y Datos (Tu código de Torque vs Profundidad aquí...)
        # [Mantenemos tu lógica de fig_t y c_info]

    with t_geo:
        # [Mantenemos tu excelente lógica de Navegación 3D y Mapas]
        st.subheader("🧭 Navegación Direccional")
        # ... (Tu código de trayectoria real y target)

    with t_mud:
        st.subheader("🛢️ Sistema de Circulación")
        l1, l2 = st.columns(2)
        gain = datos.get("Influjo", 0)
        l1.metric("Volumen Piletas", "1250 bbl", delta=f"{gain} bbl/min", delta_color="inverse")
        l2.metric("Densidad Lodo", f"{piz.get('densidad_lodo', 9.5)} ppg")
        st.progress(0.75, text="Tanque de Reserva")

    with t_bop:
        st.subheader("🛡️ Seguridad de Pozo (BOP)")
        if piz.get("bop_cerrado"):
            st.error("🚨 POZO BAJO PRESIÓN (SHUT-IN)")
            st.metric("SICP", "450 PSI")
            if st.button("ABRIR CONJUNTO DE RAMS", key="bop_open"):
                piz["bop_cerrado"] = False
                st.rerun()
        else:
            st.success("✅ OPERACIÓN NORMAL - FLUJO ABIERTO")
            if st.button("CERRAR ANULAR (EMERGENCIA)", key="bop_close"):
                piz["bop_cerrado"] = True
                st.rerun()
