import streamlit as st
import plotly.graph_objects as go

def crear_manometro(valor, titulo, unidad, max_val, color_bar):
    """Función universal para crear los relojes del simulador"""
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
        height=280, 
        margin=dict(l=30, r=30, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "white", 'family': "Arial"}
    )
    return fig

def renderizar_cabina_perforador(piz, datos):
    st.header(f"🎮 Consola de Perforación - {piz.get('yacimiento', 'Mendoza')}")
    
    # --- Sidebar con controles (Lo que ya teníamos) ---
    with st.sidebar:
        st.subheader("🕹️ Controles")
        piz["rpm"] = st.slider("Rotación", 0, 180, int(piz.get("rpm", 0)), key="s_rpm")
        piz["caudal"] = st.slider("Bombas", 0, 1200, int(piz.get("caudal", 0)), key="s_caudal")

    # --- NUEVA ESTRUCTURA DE PESTAÑAS (Aquí vuelve lo que "perdimos") ---
    tab_principal, tab_geo, tab_tanques, tab_seguridad = st.tabs([
        "📊 Panel Principal", "🌍 Geonavegación", "🛢️ Sistema de Lodos", "🛡️ BOP & Seguridad"
    ])

    with tab_principal:
        c1, c2, c3 = st.columns(3)
        with c1: st.plotly_chart(crear_manometro(datos.get("SPP", 0), "Presión", "PSI", 5000, "#00ffcc"))
        with c2: st.plotly_chart(crear_manometro(datos.get("ROP", 0), "Penetración", "m/h", 80, "#ffcc00"))
        with c3: st.plotly_chart(crear_manometro(datos.get("Carga_Gancho", 150), "Hook Load", "klbs", 400, "#ff3300"))

    with tab_geo:
        st.subheader("📍 Monitoreo de Trayectoria (Vaca Muerta)")
        # Aquí es donde llamaríamos a tu viejo geonavegacion_pro.py
        st.info("Visualizando formación: " + piz.get("litologia", "Cuyana"))
        # Simulación de gráfico de trayectoria
        st.line_chart([10, 20, 35, 50, 80, 90], help="Inclinación del pozo")

    with tab_tanques:
        st.subheader("📈 Nivel de Tanques y Retorno")
        col1, col2 = st.columns(2)
        col1.metric("Tanque Activo 1", "450 bbl", "+2 bbl (Gain)")
        col2.metric("Retorno de Flujo", "85%", "-5% (Loss)")

    with tab_seguridad:
        st.subheader("🛡️ Estado del BOP")
        if piz.get("bop_cerrado"):
            st.error("BOP CERRADO - Presión Encajonada")
        else:
            st.success("BOP ABIERTO - Operación Normal")
