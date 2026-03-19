import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.graph_objects as go
import os
import time

# --- 1. CONFIGURACIÓN E IDENTIDAD MENFA ---
st.set_page_config(page_title="SIMULADOR PROFESIONAL MENFA V5", layout="wide", initial_sidebar_state="collapsed")

def mostrar_imagen(archivo, ancho=None):
    if os.path.exists(archivo):
        st.image(archivo, width=ancho)
    else:
        st.warning(f"Archivo {archivo} no encontrado. Cargue el logo en el repositorio.")

# --- 2. ESTADO DEL SISTEMA (LÓGICA DE INGENIERÍA API) ---
if "auth" not in st.session_state: st.session_state.auth = False
if "menu" not in st.session_state: st.session_state.menu = "HOME"
if "kick_alert" not in st.session_state: st.session_state.kick_alert = False
if "time_kick" not in st.session_state: st.session_state.time_kick = 0
if "reaccion_sec" not in st.session_state: st.session_state.reaccion_sec = 0
if "vida_sarta" not in st.session_state: st.session_state.vida_sarta = 100.0 
if "pesca_activa" not in st.session_state: st.session_state.pesca_activa = False
if "examen_ok" not in st.session_state: st.session_state.examen_ok = False

# Historial de perforación
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame([{
        "DEPTH": 2500.0, "WOB": 20.0, "RPM": 100, "TORQUE": 15000, 
        "SPP": 2800, "ROP": 10.0, "GR": 120, "TANQUES": 1000, "GPM": 500
    }])

curr = st.session_state.history.iloc[-1]

# --- 3. MÓDULOS DEL SIMULADOR ---
def login_menfa():
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    mostrar_imagen("logo_menfa.png", ancho=300)
    st.title("SISTEMA DE ENTRENAMIENTO - IPCL MENFA")
    st.subheader("INGRESO DE OPERADOR")
    st.markdown('</div>', unsafe_allow_html=True)
    
    with st.form("acceso_directo"):
        nombre = st.text_input("Nombre y Apellido:")
        legajo = st.text_input("Número de Legajo:")
        
        if st.form_submit_button("CONECTAR A CABINA"):
            if nombre and legajo:
                st.session_state.usuario = nombre
                st.session_state.legajo = legajo
                # Definimos el yacimiento internamente para el reporte
                st.session_state.yacimiento = "OPERACIÓN MENDOZA" 
                st.session_state.auth = True
                st.rerun()
            else:
                st.warning("Complete los campos para habilitar el simulador.")
                
def render_perfil_grafico():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("📉 PERFIL DE AVANCE DINÁMICO")
    
    # Creamos un gráfico de trayectoria vertical
    df = st.session_state.history
    
    fig = go.Figure()

    # Dibujamos el pozo (Trayectoria)
    fig.add_trace(go.Scatter(
        x=[0] * len(df), 
        y=df['DEPTH'],
        mode='lines+markers',
        name='Trayectoria del Pozo',
        line=dict(color='white', width=4),
        marker=dict(size=2, color='yellow')
    ))

    # Añadimos franjas de colores para simular capas geológicas (Formaciones)
    # Basado en el Gamma Ray (GR) capturado por el LWD
    for i in range(1, len(df)):
        depth_start = df.iloc[i-1]['DEPTH']
        depth_end = df.iloc[i]['DEPTH']
        gr_val = df.iloc[i]['GR']
        
        # Lógica de color por formación (Norma API para litología)
        color_capa = "gold" if gr_val < 60 else "gray" if gr_val < 100 else "darkred"
        
        fig.add_hrect(
            y0=depth_start, y1=depth_end, 
            fillcolor=color_capa, opacity=0.3, 
            layer="below", line_width=0
        )

    fig.update_layout(
        title="Visualización de Penetración y Litología",
        yaxis=dict(title="Profundidad (m)", autorange="reversed"), # El pozo va hacia abajo
        xaxis=dict(title="Desviación Lateral (m)", range=[-10, 10]),
        template="plotly_dark",
        height=700
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.info("🟡 Arena (Reservorio) | ⚪ Arcilla | 🔴 Roca Dura / Basalto")
def render_home():
    if st.session_state.kick_alert:
        st.error(f"⚠️ ¡ALERTA DE ARREMETIDA! TIEMPO DE REACCIÓN: {int(time.time() - st.session_state.time_kick)}s")
    if st.session_state.pesca_activa:
        st.error("🚨 EMERGENCIA: Tubería cortada. Se requiere operación de PESCA.")

    st.title(f"🕹️ CENTRAL MENFA - {st.session_state.yacimiento}")
    st.write(f"Operador: {st.session_state.usuario} | Integridad Sarta: {round(st.session_state.vida_sarta, 1)}%")
    st.divider()
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📊 MONITOR SCADA / LWD", use_container_width=True): st.session_state.menu = "SCADA"; st.rerun()
    with c2:
        tipo = "primary" if st.session_state.kick_alert else "secondary"
        if st.button("🛡️ PANEL BOP (API S53)", use_container_width=True, type=tipo): st.session_state.menu = "BOP"; st.rerun()
    with c3:
        if st.button("🔩 SARTA / PESCA", use_container_width=True): st.session_state.menu = "SARTAS"; st.rerun()
    
    st.write("")
    c4, c5, c6 = st.columns(3)
    with c4:
        if st.button("🧪 FLUIDOS (API 13B)", use_container_width=True): st.session_state.menu = "LODOS"; st.rerun()
    with c5:
        if st.button("⚙️ HIDRÁULICA", use_container_width=True): st.session_state.menu = "BOMBAS"; st.rerun()
    with c6:
        if st.button("🏆 EXAMEN Y REPORTE", use_container_width=True): st.session_state.menu = "EXAMEN"; st.rerun()

    st.divider()
    if st.button("📖 MANUAL DE USUARIO API", use_container_width=True): st.session_state.menu = "MANUAL"; st.rerun()
# Agregar esto después de los otros botones de módulos
st.write("---")

def modulo_pesca():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("🧲 OPERACIONES DE PESCA (API RP 7G)")
    st.error(f"Pescado a {curr['DEPTH']}m. Seleccione herramienta normada.")
    
    herramienta = st.selectbox("Herramienta de Pesca:", ["Overshot", "Die Collar", "Taper Tap"])
    tension = st.slider("Tensión de Tracción (klbs):", 0, 400, 100)
    
    if st.button("INTENTAR RECUPERACIÓN"):
        if herramienta == "Overshot" and tension > 180:
            st.session_state.vida_sarta = 100.0
            st.session_state.pesca_activa = False
            st.session_state.menu = "HOME"
            st.success("¡Pesca Exitosa! Sarta recuperada.")
            st.rerun()
        else:
            st.error("Fallo en la recuperación. Ajuste la herramienta o la tensión.")

def modulo_examen():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("📝 EVALUACIÓN DE COMPETENCIA API")
    if not st.session_state.examen_ok:
        p1 = st.radio("¿Constante API para Hidrostática?", ["0.052", "0.433", "0.0465"])
        p2 = st.radio("¿Norma para Control de Pozos?", ["API S53", "API 5DP", "API RP 13B"])
        if st.button("VALIDAR"):
            if p1 == "0.052" and p2 == "API S53":
                st.session_state.examen_ok = True
                st.rerun()
            else: st.error("Respuestas incorrectas.")
    else:
        st.success("Examen Aprobado. Reporte Habilitado.")
        st.write(f"Tiempo reacción Kick: {st.session_state.reaccion_sec}s")
        st.download_button("📥 DESCARGAR LOG DE GUARDIA", st.session_state.history.to_csv(), f"Reporte_{st.session_state.usuario}.csv")

# --- 5. LÓGICA DE CONTROL (SIDEBAR) ---

if not st.session_state.auth:
    login_menfa()
else:
    with st.sidebar:
        mostrar_imagen("logo_menfa.png", ancho=150)
        st.divider()
        wob = st.slider("WOB (klbs)", 0, 60, int(curr['WOB']))
        rpm = st.slider("RPM", 0, 180, int(curr['RPM']))
        
        if st.button("AVANZAR PERFORACIÓN") and not st.session_state.pesca_activa:
            # Desgaste API
            st.session_state.vida_sarta -= (wob * 0.05) + (rpm * 0.01)
            if st.session_state.vida_sarta <= 0:
                st.session_state.pesca_activa = True
                st.session_state.menu = "SARTAS"
                st.rerun()
            
            # Evento de Kick
            kick = 0
            if random.random() < 0.06 and not st.session_state.kick_alert:
                st.session_state.kick_alert = True
                st.session_state.time_kick = time.time()
                kick = 20
            
            nueva_fila = {
                "DEPTH": curr['DEPTH'] + 1.0, "WOB": wob, "RPM": rpm, 
                "TORQUE": (wob * 420), "SPP": 2800 + (curr['DEPTH'] * 0.02),
                "ROP": (rpm * 0.1), "GR": random.randint(60, 140), "TANQUES": curr['TANQUES'] + kick, "GPM": 500
            }
            st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([nueva_fila])], ignore_index=True)
            st.rerun()
def render_manual_interactivo():
    st.button("🔙 VOLVER AL MONITOR", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("📖 MANUAL DEL OPERADOR - IPCL MENFA")
    st.info("Siga estas instrucciones para una operación segura bajo normas API.")
    st.divider()

    # Definición de las 5 pestañas
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🚀 Operación", 
        "🛡️ Control de Pozo", 
        "🔩 Sartas y Pesca", 
        "🧪 Fluidos",
        "📚 Glosario"
    ])

    with tab1:
        st.subheader("🕹️ Guía de Inicio y Perforación")
        st.write("""
        1. **Ingreso:** Registre su Nombre y Legajo. El sistema asignará automáticamente el yacimiento de Mendoza.
        2. **Control de Sarta:** Use los deslizadores (Sliders) en la barra lateral para ajustar el **WOB** (Peso) y las **RPM**.
        3. **Avance:** Presione 'AVANZAR PERFORACIÓN'. Cada clic representa un avance de 1 metro.
        4. **Monitoreo:** Observe el panel **SCADA**. Si el Torque sube demasiado, reduzca el WOB inmediatamente para evitar fatiga.
        """)
        st.success("🎯 Objetivo: Llegar a la profundidad programada manteniendo la integridad de la herramienta arriba del 80%.")

    with tab2:
        st.subheader("🛡️ Protocolo de Emergencia (API S53)")
        st.write("""
        Si detecta un incremento en el nivel de **TANQUES** o una alerta de **KICK**:
        1. Deje de perforar (suelte los controles).
        2. Ingrese rápidamente al módulo **PANEL BOP**.
        3. Presione el botón **'CIERRE DE EMERGENCIA'**.
        4. El sistema calculará su tiempo de respuesta. Un tiempo menor a 30 segundos es 'Excelente'.
        """)
        st.warning("⚠️ No intente seguir perforando con un Kick activo; el pozo podría entrar en surgencia descontrolada.")

    with tab3:
        st.subheader("🔩 Integridad Mecánica y Pesca (API 7G)")
        st.write("""
        * **Fatiga:** La sarta sufre desgaste por fricción y torque. Si llega a **0%**, la tubería se corta (Broken Pipe).
        * **Procedimiento de Pesca:**
            * El sistema lo derivará al módulo de Pesca automáticamente.
            * Seleccione la herramienta **Overshot** (es la más efectiva para pescados cilíndricos).
            * Ajuste la tensión de tracción. Se requiere vencer el peso de la sarta (aprox. **180-220 klbs** en este simulador).
            * Si falla, intente variar la tensión o cambiar de herramienta.
        """)

    with tab4:
        st.subheader("🧪 Cálculos de Ingeniería (API 13B)")
        st.write("El simulador aplica las siguientes fórmulas automáticas:")
        st.latex(r"Presión Hidrostática (psi) = 0.052 \cdot \text{Densidad (ppg)} \cdot \text{Profundidad (ft)}")
        st.latex(r"Potencia Hidráulica (HHP) = \frac{\text{Caudal (GPM)} \cdot \text{Presión (PSI)}}{1714}")
        st.info("Recuerde: Mantener la Ph > Pf (Presión de formación) es la primera barrera de seguridad.")

    with tab5:
        st.subheader("📚 Diccionario Técnico")
        glosario = {
            "WOB": "Weight on Bit. Peso real aplicado sobre el trépano para cortar la roca.",
            "ROP": "Rate of Penetration. Velocidad a la que el trépano avanza en el subsuelo.",
            "SPP": "Standpipe Pressure. Presión de circulación del lodo medida en la superficie.",
            "Overshot": "Herramienta de pesca externa que 'agarra' la tubería caída por su diámetro exterior.",
            "Gamma Ray": "Herramienta LWD que mide la radiactividad natural para identificar arenas o arcillas."
        }
        for k, v in glosario.items():
            st.write(f"**{k}:** {v}")

    st.divider()
    st.caption("Instrucciones de entrenamiento - Propiedad de IPCL MENFA")
    
    # --- 6. RUTEADOR DE MENÚS ---
    if st.session_state.menu == "HOME": render_home()
    elif st.session_state.menu == "SCADA":
        st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
        st.title("📊 MONITOREO LWD / SCADA")
        st.metric("Profundidad", f"{curr['DEPTH']} m")
        st.metric("Gamma Ray", f"{curr['GR']} API Units")
    elif st.session_state.menu == "BOP":
        st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
        st.title("🛡️ PANEL BOP (API S53)")
        if st.button("CIERRE DE EMERGENCIA", type="primary"):
            if st.session_state.kick_alert:
                st.session_state.reaccion_sec = int(time.time() - st.session_state.time_kick)
                st.session_state.kick_alert = False
                st.success(f"¡POZO SEGURO! Reacción: {st.session_state.reaccion_sec} seg.")
    elif st.session_state.menu == "SARTAS":
        if st.session_state.pesca_activa: modulo_pesca()
        else: 
            st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
            st.write("Sarta en condiciones operativas (API 5DP).")
    elif st.session_state.menu == "LODOS":
        st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
        st.title("🧪 FLUIDOS (API 13B)")
        st.write(f"Presión Hidrostática: {round(0.052 * 9.5 * curr['DEPTH'] * 3.28, 2)} psi")
    elif st.session_state.menu == "BOMBAS":
        st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
        st.title("⚙️ HIDRÁULICA")
        st.write(f"HHP: {round((curr['GPM'] * curr['SPP']) / 1714, 2)}")
    elif st.session_state.menu == "EXAMEN": modulo_examen()
    elif st.session_state.menu == "MANUAL":
        st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
        st.write("Cargue aquí las instrucciones técnicas para el alumno.")
    elif st.session_state.menu == "PERFIL": render_perfil_grafico()
    elif st.session_state.menu == "MANUAL": render_manual_interactivo()
