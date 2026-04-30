import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def crear_manometro(valor, titulo, unidad, max_val, color_bar):
    """Dibuja el reloj indicador de parámetros"""
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
    # --- MENSAJES DEL INSTRUCTOR ---
    if piz.get("mensaje_profesor"):
        st.toast(f"📻 RADIO: {piz['mensaje_profesor']}", icon="🎙️")

    st.header(f"🎮 Consola MENFA 3.0 - {piz.get('yacimiento', 'Mendoza')}")
    
    # --- SIDEBAR ---
    with st.sidebar:
        st.image("logo_menfa.png", width=200)
        st.subheader("🕹️ Controles de Cuadro")
        piz["rpm"] = st.slider("Rotación (RPM)", 0, 180, int(piz.get("rpm", 0)), key="s_rpm")
        piz["wob"] = st.slider("Peso (klbs)", 0, 60, int(piz.get("wob", 0)), key="s_wob")
        piz["caudal"] = st.slider("Bombas (GPM)", 0, 1200, int(piz.get("caudal", 0)), key="s_caudal")
        
        st.divider()
        st.metric("PROFUNDIDAD", f"{piz.get('profundidad_actual', 0):.2f} m")
        st.metric("OBJETIVO TVD", f"{piz.get('tvd_target', 3000)} m")

    # --- PESTAÑAS DETALLADAS ---
    t_main, t_geo, t_mud, t_bop = st.tabs(["📊 OPERACIÓN", "🧭 GEOLOGÍA", "🛢️ LODOS", "🛡️ SEGURIDAD"])

    with t_main:
        col_relojes, col_well = st.columns([2, 1])
        
        with col_relojes:
            c1, c2 = st.columns(2)
            c1.plotly_chart(crear_manometro(datos.get("SPP", 0), "BOMBAS", "PSI", 5000, "cyan"), use_container_width=True)
            c2.plotly_chart(crear_manometro(datos.get("ROP", 0), "ROP", "m/h", 80, "gold"), use_container_width=True)
            
            # Gráfico de Torque en tiempo real
            st.subheader("📈 Histórico de Torque")
            torque_data = pd.DataFrame({"Torque": np.random.normal(datos.get("Torque", 0), 2, 20)})
            st.line_chart(torque_data, height=150)

        with col_well:
            st.subheader("🏗️ Esquema del Pozo")
            # Dibujamos un pozo simple que baja según la profundidad
            prof = piz.get("profundidad_actual", 0)
            target = piz.get("tvd_target", 3000)
            
            fig_well = go.Figure()
            # Casing
            fig_well.add_shape(type="rect", x0=-1, y0=0, x1=1, y1=-target, line=dict(color="Gray", width=2))
            # Trépano (Bit)
            fig_well.add_trace(go.Scatter(x=[0], y=[-prof], mode="markers+text", 
                                         marker=dict(symbol="triangle-down", size=20, color="red"),
                                         text=["TREPANO"], textposition="top center"))
            
            fig_well.update_layout(yaxis=dict(range=[-target, 50]), height=400, showlegend=False, 
                                  margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_well, use_container_width=True)

    with t_geo:
        st.subheader("🕵️ Perfil Geofísico (LWD)")
        # Curvas de Gamma Ray y Resistividad
        prof_base = piz.get("profundidad_actual", 0)
        chart_data = pd.DataFrame({
            "Profundidad": np.linspace(prof_base-50, prof_base, 50),
            "Gamma Ray": np.random.randint(40, 150, 50),
            "Resistividad": np.random.uniform(2, 20, 50)
        })
        st.line_chart(chart_data, x="Profundidad", y=["Gamma Ray", "Resistividad"])

    with t_mud:
        st.subheader("🌊 Gestión de Fluidos")
        m1, m2, m3 = st.columns(3)
        gain = datos.get("Influjo", 0)
        m1.metric("Nivel Piletas", "1250 bbl", delta=f"{gain} bbl/min", delta_color="inverse")
        m2.metric("Densidad In", f"{piz.get('densidad_lodo', 9.5)} ppg")
        m3.metric("Densidad Out", f"{piz.get('densidad_lodo', 9.5) - (0.1 if gain > 0 else 0)} ppg")
        
        # Simulación visual de tanques
        st.write("Estado de Piletas:")
        st.progress(0.75 + (gain/100), text="Tanque Activo 1")

    with t_bop:
        st.subheader("🛡️ Panel de Control de Pozo")
        # Imagen interactiva del BOP
        st.image("BoP.png", caption="BOP Stack - Mendoza Operations", width=300)
        if piz.get("bop_cerrado"):
            st.error("🚨 SHUT-IN DETECTADO: Pozo bajo presión.")
            st.metric("SICP (Presión Anular)", "450 PSI")
            if st.button("ABRIR PREVENTORES"):
                piz["bop_cerrado"] = False
                st.rerun()
        else:
            st.success("Operación en flujo normal.")
            if st.button("COLAPSAR ANULAR (CERRAR)"):
                piz["bop_cerrado"] = True
                st.rerun()
