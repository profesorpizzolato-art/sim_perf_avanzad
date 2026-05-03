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
    # --- 1. ESTILO CSS Y BRANDING ---
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

    # Encabezado con Logo (Capa de seguridad para la ruta)
    col_logo, col_tit = st.columns([1, 4])
    with col_logo:
        path_logo = "assets/logo_menfa.png"
        if os.path.exists(path_logo):
            st.image(path_logo, width=120)
        else:
            st.markdown("<h2 style='color:#00ffcc; margin:0;'>MENFA</h2>", unsafe_allow_html=True)
    
    with col_tit:
        st.title("🛡️ MENFA 3.0 | MENDOZA")
        st.caption(f"YACIMIENTO: {piz.get('yacimiento', 'GODOY CRUZ')} | STATUS: OPERANDO")

    # --- 2. INTERACCIÓN CON EL INSTRUCTOR ---
    if piz.get("mensaje_instructor"):
        st.markdown('<div class="msg-instructor">', unsafe_allow_html=True)
        st.warning(f"📻 **RADIO INSTRUCTOR:** {piz['mensaje_instructor']}")
        
        c_acc, c_send = st.columns([3, 1])
        with c_acc:
            accion = st.selectbox("Acción técnica realizada:", 
                                 ["Seleccionar...", "Caudal ajustado", "Peso corregido", 
                                  "Pozo cerrado (BOP)", "Densidad incrementada"])
        with c_send:
            if st.button("ENVIAR REPORTE"):
                if accion != "Seleccionar...":
                    piz["ultima_accion"] = accion
                    piz["mensaje_instructor"] = None
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- 3. PESTAÑAS (TABS) ---
    t_op, t_geo, t_mud, t_bop = st.tabs(["📊 OPERACIÓN", "🧭 GEONAVEGACIÓN", "🛢️ LODOS", "🛡️ SEGURIDAD"])

    with t_op:
        # Fila de Manómetros (Aquí es donde daba el error)
        col1, col2, col3 = st.columns(3)
        with col1: 
            st.plotly_chart(crear_manometro(datos.get("SPP", 0), "BOMBAS", "PSI", 5000, "#00ffcc"), use_container_width=True)
        with col2: 
            st.plotly_chart(crear_manometro(datos.get("ROP", 0), "AVANCE", "m/h", 80, "#ffcc00"), use_container_width=True)
        with col3: 
            st.plotly_chart(crear_manometro(datos.get("Carga_Gancho", 150), "PESO", "klbs", 400, "#ff3300"), use_container_width=True)

        st.divider()
        
        # Gráficos dinámicos
        c_graf, c_info = st.columns([2, 1])
        with c_graf:
            st.subheader("📈 Perfil de Torque vs Profundidad")
            prof_base = piz.get("profundidad_actual", 1000)
            df_t = pd.DataFrame({
                'Torque': np.random.normal(datos.get("Torque", 0), 8, 40),
                'Prof': np.linspace(prof_base - 80, prof_base, 40)
            })
            fig_t = go.Figure()
            fig_t.add_trace(go.Scatter(x=df_t['Torque'], y=df_t['Prof'], fill='toself', 
                                     line=dict(color='#00ffcc'), fillcolor='rgba(0,255,204,0.1)'))
            fig_t.update_layout(yaxis=dict(autorange="reversed"), template="plotly_dark", height=350)
            st.plotly_chart(fig_t, use_container_width=True)
        
        with c_info:
            st.subheader("📋 Parámetros")
            st.markdown(f"""
                <div class="console-box">
                    <p><b>ECD:</b> {datos.get('ECD', 0)} ppg</p>
                    <p><b>PRES. HIDRO:</b> {datos.get('PH', 0)} PSI</p>
                </div>
            """, unsafe_allow_html=True)

    with t_geo:
        # Lógica de Navegación 3D (Trayectoria y Target)
        st.subheader("🧭 Trayectoria Direccional")
        prof_actual = piz.get("profundidad_actual", 1000)
        puntos = int(prof_actual / 30) if prof_actual > 30 else 1
        profundidades = np.linspace(0, prof_actual, puntos)
        inclinaciones = np.linspace(0, (piz.get("wob", 0) * 0.12), puntos)
        azimuts = np.linspace(45, 45 + (piz.get("rpm", 0) * 0.02), puntos)
        
        norte = np.cumsum(np.sin(np.radians(inclinaciones)) * np.cos(np.radians(azimuts)) * 30)
        este = np.cumsum(np.sin(np.radians(inclinaciones)) * np.sin(np.radians(azimuts)) * 30)
        
        fig_map = go.Figure()
        fig_map.add_trace(go.Scatter(x=este, y=norte, name="Trayectoria Real", line=dict(color="#00ffcc", width=4)))
        fig_map.update_layout(title="Vista de Planta", template="plotly_dark", height=400)
        st.plotly_chart(fig_map, use_container_width=True)

    with t_mud:
        st.subheader("🛢️ Sistema de Circulación")
        l1, l2 = st.columns(2)
        l1.metric("Volumen Piletas", "1250 bbl", delta=f"{datos.get('Influjo', 0)} bbl/min", delta_color="inverse")
        l2.metric("Densidad Lodo", f"{piz.get('densidad_lodo', 9.5)} ppg")

    with t_bop:
        st.subheader("🛡️ Seguridad de Pozo (BOP)")
        if piz.get("bop_cerrado"):
            st.error("🚨 POZO CERRADO (SHUT-IN)")
            if st.button("ABRIR CONJUNTO DE RAMS"):
                piz["bop_cerrado"] = False
                st.rerun()
        else:
            st.success("✅ FLUJO ABIERTO")
            if st.button("CERRAR ANULAR (EMERGENCIA)"):
                piz["bop_cerrado"] = True
                st.rerun()
