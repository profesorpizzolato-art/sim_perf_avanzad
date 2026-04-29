import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# [Aquí mantenés tu función crear_manometro que ya tenés]

def renderizar_cabina_perforador(piz, datos):
    # 0. SISTEMA DE ALERTAS (Viene de lo que el Instructor dispare)
    if piz.get("alarma"):
        st.error(f"🚨 ¡ALERTA DE SEGURIDAD!: {piz.get('mensaje_evento', 'Surgencia Detectada')}")
        if st.button("SILENCIAR ALARMA"):
            piz["alarma"] = False

    st.header(f"🎮 Consola de Perforación - {piz.get('yacimiento', 'Mendoza')}")
    
    # --- Sidebar con controles ---
    with st.sidebar:
        st.subheader("🕹️ Controles de Cuadro")
        piz["rpm"] = st.slider("Rotación (RPM)", 0, 180, int(piz.get("rpm", 0)), key="s_rpm")
        piz["wob"] = st.slider("Peso (klbs)", 0, 60, int(piz.get("wob", 0)), key="s_wob")
        piz["caudal"] = st.slider("Bombas (GPM)", 0, 1200, int(piz.get("caudal", 0)), key="s_caudal")
        
        st.divider()
        st.metric("Profundidad TVD", f"{piz.get('profundidad_actual', 0)} m")

    # --- ESTRUCTURA DE PESTAÑAS INTEGRADA ---
    tab_principal, tab_geo, tab_tanques, tab_seguridad = st.tabs([
        "📊 Panel Principal", "🌍 Geonavegación", "🛢️ Sistema de Lodos", "🛡️ BOP & Seguridad"
    ])

    with tab_principal:
        c1, c2, c3 = st.columns(3)
        with c1: st.plotly_chart(crear_manometro(datos.get("SPP", 0), "Presión", "PSI", 5000, "#00ffcc"))
        with c2: st.plotly_chart(crear_manometro(datos.get("ROP", 0), "Penetración", "m/h", 80, "#ffcc00"))
        with c3: st.plotly_chart(crear_manometro(datos.get("Carga_Gancho", 150), "Hook Load", "klbs", 400, "#ff3300"))
        
        # Agregamos Torque que es fundamental
        st.subheader("⚙️ Parámetros de Torsión")
        st.progress(min(datos.get("Torque", 0)/100, 1.0), text=f"Torque: {datos.get('Torque', 0)} ft-lbs")

    with tab_geo:
        st.subheader("📍 Geonavegación y Litología")
        # Aquí integramos lo que tenías en 'estudios_geofisicos_v2.py'
        col_g1, col_g2 = st.columns([1, 2])
        with col_g1:
            st.write(f"**Formación:** {piz.get('litologia', 'Desconocida')}")
            st.write(f"**Gradiente:** {piz.get('gradiente', 0.44)} psi/ft")
        with col_g2:
            # Simulamos el log de Gamma Ray que tenías
            gr_data = pd.DataFrame({
                'Gamma Ray': np.random.randint(40, 140, 20),
                'Prof': np.linspace(piz.get('profundidad_actual', 0)-20, piz.get('profundidad_actual', 0), 20)
            })
            st.line_chart(gr_data, x="Prof", y="Gamma Ray", color="#ffaa00")

    with tab_tanques:
        st.subheader("📈 Monitoreo de Piletas (Lodos)")
        # Recuperamos la lógica de 'bombas_de_lodo.py'
        t1, t2 = st.columns(2)
        gain_loss = datos.get("Influjo", 0)
        t1.metric("Volumen Total", "1250 bbl", delta=f"{gain_loss} bbl/min", delta_color="inverse")
        t2.metric("Densidad Salida", f"{piz.get('densidad_lodo', 9.5)} ppg")

    with tab_seguridad:
        st.subheader("🛡️ Panel de Control de Reventones (BOP)")
        # Aquí conectamos 'bop_panel.py'
        c_bop1, c_bop2 = st.columns(2)
        with c_bop1:
            st.image("BoP.png", width=250) # Usamos tu imagen
        with c_bop2:
            if piz.get("bop_cerrado"):
                st.error("⚠️ STATUS: POZO CERRADO (SHUT-IN)")
                if st.button("ABRIR RAMS", key="open_bop"):
                    piz["bop_cerrado"] = False
                    st.rerun()
            else:
                st.success("✅ STATUS: FLUJO ABIERTO")
                if st.button("CERRAR ANULAR (EMERGENCIA)", key="close_bop"):
                    piz["bop_cerrado"] = True
                    piz["alarma"] = False
                    st.rerun()
