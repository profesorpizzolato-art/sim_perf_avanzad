import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os

def crear_manometro(valor, titulo, unidad, max_val, color_bar):
    # (Mantenemos tu función de manómetro igual)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=valor,
        title={'text': f"<b>{titulo}</b><br><span style='font-size:0.8em;color:gray'>{unidad}</span>", 'font': {'size': 18}},
        gauge={
            'axis': {'range': [0, max_val], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': color_bar},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "#444",
            'steps': [
                {'range': [0, max_val*0.8], 'color': 'rgba(0,255,0,0.1)'},
                {'range': [max_val*0.8, max_val], 'color': 'rgba(255,0,0,0.2)'}
            ],
        }
    ))
    fig.update_layout(height=260, margin=dict(l=30, r=30, t=50, b=20), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
    return fig

def renderizar_cabina_perforador(piz, datos):
    # --- 1. LÓGICA DE ROLES (Separación Real) ---
    if "rol" not in st.session_state:
        st.session_state.rol = "alumno" # Por defecto

    # --- 2. PANEL DEL INSTRUCTOR (Solo visible si es instructor) ---
    # Para cambiar de rol podés usar un query param o un botón oculto
    if st.session_state.rol == "instructor":
        with st.sidebar.expander("👨‍🏫 COMANDOS TÉCNICOS (INSTRUCTOR)", expanded=True):
            piz["evento_activo"] = st.selectbox("Simular Crisis:", [None, "KICK", "LOST_CIRC"])
            piz["mensaje_instructor"] = st.text_input("Enviar Orden por Radio:")
            piz["litologia"] = st.selectbox("Cambiar Formación:", ["Areniscas", "Arcillas", "Vaca Muerta (Shale)"])
            if st.button("ACTUALIZAR ÓRDENES"):
                st.rerun()

    # --- 3. CONSOLA DEL ALUMNO (SIDEBAR) ---
    st.sidebar.header("🕹️ CONSOLA DEL PERFORADOR")
    piz["wob"] = st.sidebar.slider("Peso sobre Trépano (WOB klbs)", 0, 60, value=int(piz.get("wob", 0)))
    piz["rpm"] = st.sidebar.slider("Rotación (RPM)", 0, 180, value=int(piz.get("rpm", 0)))
    piz["caudal"] = st.sidebar.slider("Caudal Bombas (GPM)", 0, 1200, value=int(piz.get("caudal", 0)))
    
    st.sidebar.divider()
    st.sidebar.subheader("🛢️ GESTIÓN DE FLUIDOS")
    piz["densidad_lodo"] = st.sidebar.number_input("Densidad Actual (ppg)", 8.0, 18.0, value=float(piz.get("densidad_lodo", 9.5)), step=0.1)

    # --- 4. CABECERA DINÁMICA (Branding MENFA) ---
    col_logo, col_tit = st.columns([1, 4])
    with col_logo:
        if os.path.exists("assets/logo_menfa.png"): st.image("assets/logo_menfa.png", width=120)
        else: st.markdown("<h2 style='color:#00ffcc;'>MENFA</h2>", unsafe_allow_html=True)
    
    with col_tit:
        # Aquí mostramos la PROFUNDIDAD REAL que viene del acumulador
        st.title("🛡️ MENFA 3.0 | MENDOZA")
        st.subheader(f"PROFUNDIDAD: {piz.get('profundidad_actual', 0):.2f} m")

    # Mensaje de Radio (Si el instructor escribió algo)
    if piz.get("mensaje_instructor"):
        st.info(f"📻 **RADIO INSTRUCTOR:** {piz['mensaje_instructor']}")

    # --- 5. PANELES TÉCNICOS ---
    t_op, t_mud, t_well_control = st.tabs(["📊 OPERACIÓN", "🛢️ SISTEMA DE LODOS", "🛡️ SEGURIDAD"])

    with t_op:
        # Manómetros (Usando tus funciones)
        c1, c2, c3 = st.columns(3)
        with c1: st.plotly_chart(crear_manometro(datos.get("SPP", 0), "PRESIÓN (SPP)", "PSI", 5000, "#00ffcc"), use_container_width=True)
        with c2: st.plotly_chart(crear_manometro(datos.get("ROP", 0), "AVANCE (ROP)", "m/h", 80, "#ffcc00"), use_container_width=True)
        with c3: st.plotly_chart(crear_manometro(datos.get("Carga_Gancho", 150), "PESO (HOOK)", "klbs", 400, "#ff3300"), use_container_width=True)

    with t_mud:
        st.subheader("Visualización de Tanques")
        cm1, cm2 = st.columns([1, 2])
        
        with cm1:
            # Gráfico de barras para el nivel de piletas
            vol = piz.get("volumen_piletas", 1200)
            color_tanque = "#00ffcc" if vol < 1250 else "#ff3300"
            fig_tank = go.Figure(go.Bar(
                x=["Piletas Activas"], y=[vol],
                marker_color=color_tanque
            ))
            fig_tank.update_layout(yaxis=dict(range=[0, 2000]), template="plotly_dark", height=350)
            st.plotly_chart(fig_tank, use_container_width=True)
            
        with cm2:
            st.metric("Volumen en Piletas", f"{int(vol)} bbl", delta=f"{datos.get('Influjo', 0)} bbl/min")
            st.markdown(f"""
                <div class="console-box">
                    <p><b>DENSIDAD ENTRADA:</b> {piz.get('densidad_lodo')} ppg</p>
                    <p><b>ECD (FONDO):</b> {datos.get('ECD')} ppg</p>
                </div>
            """, unsafe_allow_html=True)

    with t_well_control:
        # (Aquí va tu lógica de BOP que ya tenías)
        st.subheader("Control de Surgencia")
        if piz.get("bop_cerrado"):
            st.error("🚨 POZO CERRADO (SHUT-IN)")
            if st.button("ABRIR RAMS"): 
                piz["bop_cerrado"] = False
                st.rerun()
        else:
            st.success("✅ CIRCULACIÓN NORMAL")
            if st.button("CERRAR BOP"): 
                piz["bop_cerrado"] = True
                st.rerun()
        
        st.metric("Presión en Casing", f"{datos.get('Presion_Casing', 0)} PSI")
