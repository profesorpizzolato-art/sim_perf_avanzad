import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os

def crear_manometro(valor, titulo, unidad, max_val, color_bar):
    """Genera los relojes analógicos de la consola"""
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
    fig.update_layout(
        height=260, 
        margin=dict(l=30, r=30, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "white", 'family': "Arial"}
    )
    return fig

def renderizar_cabina_perforador(piz, datos):
    # --- 1. MANDOS DE OPERACIÓN (SIDEBAR) ---
    # Estos controles escriben directamente en la pizarra (piz)
    st.sidebar.header("🕹️ CONSOLA DE MANDO")
    
    piz["wob"] = st.sidebar.slider("Peso sobre Trépano (WOB klbs)", 0, 60, value=int(piz.get("wob", 0)))
    piz["rpm"] = st.sidebar.slider("Rotación (RPM)", 0, 180, value=int(piz.get("rpm", 0)))
    piz["caudal"] = st.sidebar.slider("Caudal Bombas (GPM)", 0, 1200, value=int(piz.get("caudal", 0)))
    
    st.sidebar.divider()
    
    st.sidebar.subheader("🧭 NAVEGACIÓN DIRECCIONAL")
    piz["toolface"] = st.sidebar.number_input("Toolface Orient. (°)", 0, 360, value=int(piz.get("toolface", 0)))
    
    # --- 2. ESTILO CSS Y BRANDING ---
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

    # Encabezado
    col_logo, col_tit = st.columns([1, 4])
    with col_logo:
        path_logo = "assets/logo_menfa.png"
        if os.path.exists(path_logo):
            st.image(path_logo, width=120)
        else:
            st.markdown("<h2 style='color:#00ffcc; margin:0;'>MENFA</h2>", unsafe_allow_html=True)
    
    with col_tit:
        st.title("🛡️ MENFA 3.0 | MENDOZA")
        st.caption(f"YACIMIENTO: {piz.get('yacimiento', 'CUENCA CUYANA')} | PROFUNDIDAD: {piz.get('profundidad_actual', 0):.2f} m")

    # --- 3. COMUNICACIÓN CON INSTRUCTOR ---
    if piz.get("mensaje_instructor"):
        st.markdown('<div class="msg-instructor">', unsafe_allow_html=True)
        st.warning(f"📻 **RADIO INSTRUCTOR:** {piz['mensaje_instructor']}")
        
        c_acc, c_send = st.columns([3, 1])
        with c_acc:
            accion = st.selectbox("Confirmar acción técnica:", 
                                 ["Seleccionar...", "Peso ajustado", "Bomba encendida", 
                                  "Cambio de Toolface", "Pozo controlado"])
        with c_send:
            if st.button("ENVIAR REPORTE"):
                if accion != "Seleccionar...":
                    piz["ultima_accion"] = accion
                    piz["mensaje_instructor"] = None
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- 4. PANELES TÉCNICOS (TABS) ---
    t_op, t_geo, t_mud, t_bop = st.tabs(["📊 OPERACIÓN", "🧭 GEONAVEGACIÓN", "🛢️ LODOS", "🛡️ SEGURIDAD"])

    with t_op:
        # Relojes principales
        col1, col2, col3 = st.columns(3)
        with col1: 
            st.plotly_chart(crear_manometro(datos.get("SPP", 0), "PRESIÓN (SPP)", "PSI", 5000, "#00ffcc"), use_container_width=True)
        with col2: 
            st.plotly_chart(crear_manometro(datos.get("ROP", 0), "AVANCE (ROP)", "m/h", 80, "#ffcc00"), use_container_width=True)
        with col3: 
            st.plotly_chart(crear_manometro(datos.get("Carga_Gancho", 150), "PESO (HOOK)", "klbs", 400, "#ff3300"), use_container_width=True)

        st.divider()
        
        # Gráficos de Torque y Arrastre (Drag)
        c_graf, c_info = st.columns([2, 1])
        with c_graf:
            st.subheader("📈 Perfil de Torque vs Profundidad")
            prof_base = piz.get("profundidad_actual", 1000)
            # Generamos datos que simulan vibración real
            df_t = pd.DataFrame({
                'Torque': np.random.normal(datos.get("Torque", 15), 2, 40),
                'Prof': np.linspace(prof_base - 50, prof_base, 40)
            })
            fig_t = go.Figure()
            fig_t.add_trace(go.Scatter(x=df_t['Torque'], y=df_t['Prof'], 
                                     line=dict(color='#00ffcc', width=3), 
                                     fill='toself', fillcolor='rgba(0,255,204,0.1)'))
            fig_t.update_layout(yaxis=dict(autorange="reversed"), template="plotly_dark", height=350, margin=dict(t=20))
            st.plotly_chart(fig_t, use_container_width=True)
        
        with c_info:
            st.subheader("📋 Parámetros")
            st.markdown(f"""
                <div class="console-box">
                    <p><b>DENSIDAD (ECD):</b> {datos.get('ECD', 9.5)} ppg</p>
                    <p><b>PRES. HIDRO:</b> {int(datos.get('PH', 0))} PSI</p>
                    <p><b>WOB REAL:</b> {piz.get('wob', 0)} klbs</p>
                    <p><b>RPM REAL:</b> {piz.get('rpm', 0)}</p>
                </div>
            """, unsafe_allow_html=True)

    with t_geo:
        st.subheader("🧭 Trayectoria y Geonavegación")
        prof_actual = piz.get("profundidad_actual", 100)
        puntos = max(int(prof_actual / 10), 2)
        
        # Simulación de curva basada en WOB y Toolface
        z = np.linspace(0, prof_actual, puntos)
        # La curva se desvía según el peso y la orientación
        desvio = (piz.get("wob", 0) / 60) * (prof_actual / 100)
        x = np.sin(np.radians(piz.get("toolface", 0))) * desvio * np.sqrt(z)
        y = np.cos(np.radians(piz.get("toolface", 0))) * desvio * np.sqrt(z)
        
        fig_3d = go.Figure(data=[go.Scatter3d(x=x, y=y, z=-z, mode='lines', line=dict(color='#00ffcc', width=6))])
        fig_3d.update_layout(title="Trayectoria 3D del Pozo", template="plotly_dark", height=500)
        st.plotly_chart(fig_3d, use_container_width=True)

    with t_mud:
        st.subheader("🛢️ Sistema de Circulación de Lodos")
        m1, m2, m3 = st.columns(3)
        m1.metric("Densidad Entrada", f"{piz.get('densidad_lodo', 9.5)} ppg")
        m2.metric("Nivel Piletas", "1250 bbl", delta="-2 bbl", delta_color="inverse")
        m3.metric("Retorno Flowline", f"{int(piz.get('caudal', 0) * 0.98)} GPM")

    with t_bop:
        st.subheader("🛡️ Control de Pozo (BOP Stack)")
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if piz.get("bop_cerrado"):
                st.error("🚨 BOP CERRADO")
                if st.button("ABRIR RAMS", use_container_width=True):
                    piz["bop_cerrado"] = False
                    st.rerun()
            else:
                st.success("✅ FLOW OPEN")
                if st.button("CERRAR POZO (SHUT-IN)", use_container_width=True):
                    piz["bop_cerrado"] = True
                    st.rerun()
        with col_b2:
            st.info("Presión en Casing: " + str(datos.get("Presion_Casing", 0)) + " PSI")
