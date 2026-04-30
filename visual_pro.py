import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

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
    # --- ESTILO CSS PARA EL DASHBOARD ---
    st.markdown("""
        <style>
        .main { background-color: #0e1117; }
        [data-testid="stMetricValue"] { font-size: 35px; color: #00ffcc; }
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] {
            background-color: #1e1e1e; border-radius: 4px; padding: 8px 16px; color: white; border: 1px solid #333;
        }
        .stTabs [data-baseweb="tab"]:hover { border-color: #00ffcc; }
        .console-box {
            background-color: #1e1e1e; padding: 15px; border-radius: 8px; border-left: 5px solid #00ffcc; margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- ENCABEZADO SUPERIOR ---
    c_tit, c_inst = st.columns([3, 2])
    with c_tit:
        st.title("🛡️ MENFA 3.0 | MENDOZA")
        st.caption(f"YACIMIENTO: {piz.get('yacimiento', 'GODOY CRUZ')} | STATUS: OPERACIÓN EN VIVO")
    with c_inst:
        if piz.get("mensaje_profesor"):
            st.info(f"📻 **RADIO INSTRUCTOR:** {piz['mensaje_profesor']}")
        if piz.get("alarma"):
            st.error("🚨 ALERTA: SURGENCIA / KICK DETECTADO")

    # --- SIDEBAR DE MANDOS ---
    with st.sidebar:
        st.subheader("🕹️ Controles de Cuadro")
        piz["rpm"] = st.slider("Rotación (RPM)", 0, 180, int(piz.get("rpm", 0)), key="s_rpm")
        piz["wob"] = st.slider("Peso (klbs)", 0, 60, int(piz.get("wob", 0)), key="s_wob")
        piz["caudal"] = st.slider("Bombas (GPM)", 0, 1200, int(piz.get("caudal", 0)), key="s_caudal")
        
        st.divider()
        st.metric("PROFUNDIDAD", f"{piz.get('profundidad_actual', 0):.2f} m")
        st.metric("TVD OBJETIVO", f"{piz.get('tvd_target', 3000)} m")

    # --- SISTEMA DE PESTAÑAS (TABS) ---
    t_op, t_geo, t_mud, t_bop = st.tabs(["📊 OPERACIÓN", "🌍 GEOLOGÍA", "🛢️ LODOS", "🛡️ SEGURIDAD"])

    with t_op:
        # Fila 1: Manómetros
        col1, col2, col3 = st.columns(3)
        with col1: st.plotly_chart(crear_manometro(datos.get("SPP", 0), "BOMBAS", "PSI", 5000, "#00ffcc"), use_container_width=True)
        with col2: st.plotly_chart(crear_manometro(datos.get("ROP", 0), "AVANCE", "m/h", 80, "#ffcc00"), use_container_width=True)
        with col3: st.plotly_chart(crear_manometro(datos.get("Carga_Gancho", 150), "PESO", "klbs", 400, "#ff3300"), use_container_width=True)

        st.divider()

        # Fila 2: Gráfico y Datos
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
            fig_t.update_layout(yaxis=dict(autorange="reversed", title="Profundidad (m)"), 
                               xaxis=dict(title="Torque (ft-lbs)"), height=350, template="plotly_dark")
            st.plotly_chart(fig_t, use_container_width=True)

        with c_info:
            st.subheader("📋 Parámetros de Control")
            st.markdown(f"""
                <div class="console-box">
                    <p><b>ECD:</b> {datos.get('ECD', 0)} ppg</p>
                    <p><b>PRES. HIDRO:</b> {datos.get('PH', 0)} PSI</p>
                    <p><b>TEMP. RETORNO:</b> 54 °C</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.subheader("📝 Bitácora")
            st.code(f"""
{pd.Timestamp.now().strftime('%H:%M:%S')} - PERFORANDO {piz.get('litologia', 'CAPA')}
{pd.Timestamp.now().strftime('%H:%M:%S')} - CAUDAL ESTABLE
{pd.Timestamp.now().strftime('%H:%M:%S')} - WOB CONTROLADO
            """, language="text")

    with t_geo:
        st.subheader("🧭 Geonavegación LWD")
        g1, g2 = st.columns([1, 2])
        with g1:
            st.metric("Litología", piz.get('litologia', 'Cuyana'))
            st.metric("Gradiente", f"{piz.get('gradiente', 0.44)} psi/ft")
        with g2:
            st.write("Registro Gamma Ray (API)")
            gr_data = pd.DataFrame({"GR": np.random.randint(40, 140, 20), "P": np.linspace(0, 100, 20)})
            st.line_chart(gr_data, x="P", y="GR", color="#ffaa00")

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
