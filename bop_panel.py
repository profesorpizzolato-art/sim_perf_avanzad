import streamlit as st
from datetime import datetime

def render_bop_ui(pizarra):
    st.header("🛡️ Control Avanzado de Pozos")
    
    # --- SEGURIDAD: Inicialización de variables en el session_state ---
    if "log_eventos" not in st.session_state:
        st.session_state.log_eventos = []
    if "strokes_totales" not in st.session_state:
        st.session_state.strokes_totales = 0  
    
    # --- BLOQUE COGNITIVO 1: DIAGNÓSTICO Y CONTROL DE EMBOLADAS ---
    c_st1, c_st2 = st.columns(2)
    with c_st1:
        strokes = int(st.session_state.get('strokes_totales', 0))
        st.metric("Total Strokes (Emboladas Acumuladas)", strokes)
    with c_st2:
        st.write("")  # Alineador vertical para el botón
        if st.button("🔄 Reiniciar Contador de Emboladas", key="btn_bop_reset_final_ver"):
            st.session_state.strokes_totales = 0  
            st.rerun()

    st.divider()
    
    # Recuperamos variables críticas de la pizarra de simulación
    es_cerrado = pizarra.get("bop_cerrado", False)
    presion_bomba = pizarra.get("presion_bomba", 0.0)
    profundidad = pizarra.get("profundidad_actual", 2500.0)
    
    # --- INDICADOR VISUAL DE ESTADO DEL POZO ---
    color_bg = "#FF4B4B" if es_cerrado else "#28a745"
    st.markdown(
        f"<div style='background-color:{color_bg}; padding:12px; border-radius:10px; text-align:center; color:white;'>"
        f"<h3 style='margin:0;'>ESTADO DEL POZO: {'🛑 CERRADO (Surgencia Detectada)' if es_cerrado else '🟢 ABIERTO EN PRODUCCIÓN/PERFORACIÓN'}</h3>"
        f"</div>", 
        unsafe_allow_html=True
    )
    st.write("") 

    # Mandos de activación del BOP
    c1, _, c3 = st.columns([1.2, 0.6, 1.2])
    with c1: 
        if st.button("🔴 CERRAR POZO (BOP)", use_container_width=True, key="btn_bop_close_final"): 
            pizarra["bop_cerrado"] = True
            pizarra["rpm_maestro"] = 0  # Parada técnica por seguridad cognitiva
            st.session_state.log_eventos.append(
                f"[{datetime.now().strftime('%H:%M:%S')}] 🛑 ACCIÓN: Cierre de emergencia del BOP por el operador."
            )
            st.rerun()
            
    with c3:
        if st.button("🟢 ABRIR POZO", use_container_width=True, key="btn_bop_open_final"):
            pizarra["bop_cerrado"] = False
            st.session_state.log_eventos.append(
                f"[{datetime.now().strftime('%H:%M:%S')}] ✅ ACCIÓN: Apertura de líneas. Pozo abierto."
            )
            st.rerun()

    st.divider()

    # --- BLOQUE COGNITIVO 2: CONTROL DINÁMICO DE PRESIÓN ---
    st.subheader("🕹️ Control de Estrangulación (Choke Manifold)")
    st.write("Ajuste la contrapresión hidrostática para balancear las presiones del yacimiento.")
    
    col_c1, col_c2 = st.columns([2, 1])
    with col_c1:
        choke_pos = st.slider(
            'Apertura del Estrangulador (Choke) en 1/64"', 
            0, 64, 
            int(pizarra.get("choke_pos", 0)), 
            key="slider_choke_bop_operaciones"
        )
        
        # Registro en bitácora si hay movimientos bruscos (Criterio de evaluación de pánico)
        if abs(choke_pos - pizarra.get("choke_pos", 0)) > 5:
            st.session_state.log_eventos.append(
                f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Alerta: Ajuste brusco de Choke a {choke_pos}/64"
            )
        pizarra["choke_pos"] = choke_pos
    
    with col_c2:
        # Ecuación física base: A menor apertura, mayor contrapresión ejercida en el casing
        presion_choke = (64 - choke_pos) * 15 
        st.metric("Presión en Casing (SICP)", f"{presion_choke} psi")

    # --- BLOQUE COGNITIVO 3: BASE TEÓRICA E INGENIERÍA (KILL SHEET) ---
    if es_cerrado:
        st.divider()
        st.subheader("📝 Hoja de Ahogo Nivel Técnico (Kill Sheet)")
        
        with st.expander("📊 Ver Ecuaciones de Control Hidrostático", expanded=True):
            metodo = pizarra.get('metodo_sugerido', 'Del Perforador')
            st.info(f"📋 **Método Operacional Sugerido:** Método {metodo}")
            
            # Recuperamos parámetros teóricos calculados por el simulador para la toma de decisiones
            sidpp = pizarra.get("sidpp", 500)  # Shut-In Drill Pipe Pressure (ejemplo por defecto)
            sicp = presion_choke
            mud_weight = pizarra.get("densidad_lodo", 10.5) # ppg
            
            # Despliegue analítico para que el alumno complete sus registros analógicos
            c_teor1, c_teor2, c_teor3 = st.columns(3)
            with c_teor1:
                st.caption("Presión SIDPP Registrada")
                st.code(f"{sidpp} psi", language="markdown")
            with c_teor2:
                st.caption("Presión SICP Actual")
                st.code(f"{sicp} psi", language="markdown")
            with c_teor3:
                st.caption("Densidad de Lodo Actual")
                st.code(f"{mud_weight} ppg", language="markdown")
            
            # Densidad de ahogo calculada teóricamente (Ecuación matemática base)
            kmd = mud_weight + (sidpp / (0.052 * profundidad))
            
            st.markdown(f"**Densidad de Ahogo Requerida (Kill Mud Density):** `{kmd:.2f} ppg`")
            st.caption("⚠️ *El alumno no debe reanudar la circulación hasta que los tanques de lodo registren este valor corregido.*")

    # BITÁCORA DE CONTROL OPERACIONAL PARA AUDITORÍA
    if st.session_state.log_eventos:
        st.divider()
        st.subheader("📑 Historial de Decisiones del Operador")
        for ev in reversed(st.session_state.log_eventos[-3:]):
            st.caption(ev)
