import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.graph_objects as go
import time

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="SIMULADOR MENFA V6 - FULL", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #f4ecd8; color: #5d4037; }
    @keyframes blinker { 50% { opacity: 0; } }
    .alarm-kick { background-color: #d32f2f; padding: 20px; border-radius: 10px; border: 5px solid #fff; text-align: center; animation: blinker 1s linear infinite; color: white; margin-bottom: 20px; }
    .warning-pesca { background-color: #610000; padding: 15px; border-radius: 10px; text-align: center; color: #ffaa00; font-weight: bold; }
    .manual-box { background-color: #eaddca; padding: 15px; border-left: 5px solid #8b4513; font-family: 'Courier New', monospace; font-size: 0.9em; }
    .target-reached { background-color: #2e7d32; padding: 30px; border-radius: 15px; text-align: center; color: white; border: 4px double #ffd700; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. INICIALIZACIÓN DE VARIABLES ---
if "auth" not in st.session_state: st.session_state.auth = False
if "kick_alert" not in st.session_state: st.session_state.kick_alert = False
if "vida_sarta" not in st.session_state: st.session_state.vida_sarta = 100.0 
if "pesca_activa" not in st.session_state: st.session_state.pesca_activa = False
if "target_met" not in st.session_state: st.session_state.target_met = False
if "densidad_lodo" not in st.session_state: st.session_state.densidad_lodo = 1.15
if "presion_anular" not in st.session_state: st.session_state.presion_anular = 0
if "kicks_recibidos" not in st.session_state: st.session_state.kicks_recibidos = 0
if "sartas_rotas" not in st.session_state: st.session_state.sartas_rotas = 0

TARGET_DEPTH = 3000.0

if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame([{
        "DEPTH": 2500.0, "WOB": 20.0, "RPM": 100, "TORQUE": 8000, 
        "SPP": 2800, "ROP": 12.0, "GR": 110, "TANQUES": 1200, "DENS": 1.15
    }])

# --- 3. LOGIN ---
if not st.session_state.auth:
    st.title("🛡️ IPCL MENFA - MENDOZA")
    st.subheader("Simulador Técnico de Perforación v6.0")
    with st.form("login_form"):
        u = st.text_input("Nombre del Operador:")
        l = st.text_input("Legajo:")
        if st.form_submit_button("INGRESAR A CABINA"):
            if u:
                st.session_state.usuario = u
                st.session_state.auth = True
                st.rerun()
    st.stop()

# --- 4. LÓGICA DE SIMULACIÓN (SIDEBAR) ---
curr = st.session_state.history.iloc[-1]

with st.sidebar:
    st.header(f"Op: {st.session_state.usuario}")
    st.divider()
    wob = st.slider("WOB (klbs)", 0, 60, int(curr['WOB']))
    rpm = st.slider("RPM", 0, 180, int(curr['RPM']))
    
    if st.button("⏩ AVANZAR 200 METROS", use_container_width=True):
        if not st.session_state.pesca_activa and not st.session_state.target_met:
            # Desgaste
            st.session_state.vida_sarta -= (wob * 0.22)
            if st.session_state.vida_sarta <= 0:
                st.session_state.pesca_activa = True
                st.session_state.sartas_rotas += 1
                st.session_state.vida_sarta = 0
            
            # Profundidad
            n_prof = curr['DEPTH'] + 1.0
            if n_prof >= TARGET_DEPTH: st.session_state.target_met = True
            
            # Gamma Ray (Lógica de reservorio)
            gr = random.randint(25, 45) if 2850 < n_prof < 2950 else random.randint(85, 125)
            
            # Lógica de Kick
            tanques = curr['TANQUES']
            if random.random() < 0.08 and not st.session_state.kick_alert:
                st.session_state.kick_alert = True
                st.session_state.kicks_recibidos += 1
                tanques += 45
                st.session_state.presion_anular = random.randint(400, 850)

            nueva_fila = {
                "DEPTH": n_prof, "WOB": wob, "RPM": rpm,
                "TORQUE": (wob * 310) + random.randint(-50, 50),
                "SPP": 2800 + (wob * 2), "ROP": (wob * rpm) / 450, 
                "GR": gr, "TANQUES": tanques, "DENS": st.session_state.densidad_lodo
            }
            st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([nueva_fila])], ignore_index=True)
            st.rerun()
    
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.clear()
        st.rerun()

# --- 5. CUERPO PRINCIPAL ---

# Alertas Críticas
if st.session_state.kick_alert:
    st.markdown('<div class="alarm-kick"><h1>🚨 KICK ACTIVO</h1><p>SURGENCIA EN TANQUES - CIERRE BOP</p></div>', unsafe_allow_html=True)
if st.session_state.pesca_activa:
    st.markdown('<div class="warning-pesca">⚠️ SARTA ROTA POR SOBREPESO. REALICE MANIOBRA DE PESCA.</div>', unsafe_allow_html=True)
if st.session_state.target_met:
    st.markdown('<div class="target-reached"><h1>🎯 OBJETIVO LOGRADO</h1><p>Pozo terminado a 3000m. Genere el reporte.</p></div>', unsafe_allow_html=True)

tabs = st.tabs(["📊 SCADA", "🧪 LODOS", "🛡️ WELL CONTROL", "🔩 SARTA & PESCA", "📈 GEOLOGÍA", "📖 MANUAL & EVAL"])

with tabs[0]: # SCADA
    st.title("Monitor en Tiempo Real")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Profundidad", f"{curr['DEPTH']} m")
    c2.metric("WOB", f"{curr['WOB']} klbs")
    c3.metric("ROP", f"{round(curr['ROP'], 1)} m/h")
    c4.metric("DENSIDAD", f"{curr['DENS']} SG")
    st.subheader("Historial de Perforación")
    st.dataframe(st.session_state.history.tail(10), use_container_width=True)

with tabs[1]: # LODOS
    st.title("🧪 Sistema de Lodos")
    st.info(f"Presión Hidrostática Estimada: {round(curr['DEPTH'] * 1.422 * st.session_state.densidad_lodo / 10, 0)} psi")
    st.write("Ajuste de Densidad para controlar el pozo:")
    nueva_dens = st.number_input("Densidad (SG)", 1.0, 2.0, st.session_state.densidad_lodo, step=0.01)
    if st.button("Aplicar Nuevo Lodo"):
        st.session_state.densidad_lodo = nueva_dens
        st.success("Lodo pesado en circulación...")

with tabs[2]: # WELL CONTROL
    st.title("🛡️ Panel BOP")
    if st.session_state.kick_alert:
        col_b1, col_b2 = st.columns(2)
        col_b1.metric("SIDP (Presión Interna)", "420 psi")
        col_b2.metric("SICP (Presión Anular)", f"{st.session_state.presion_anular} psi")
        if st.button("🔒 CERRAR BOP ANULAR", type="primary", use_container_width=True):
            st.session_state.kick_alert = False
            st.session_state.presion_anular = 0
            st.balloons()
            st.success("Surgencia controlada.")
    else:
        st.success("Presiones estables. No se detecta flujo.")

with tabs[3]: # SARTA & PESCA
    st.title("🔩 Integridad Mecánica")
    st.metric("Vida Útil Sarta", f"{round(st.session_state.vida_sarta, 1)}%")
    st.progress(max(0.0, st.session_state.vida_sarta / 100))
    if st.session_state.pesca_activa:
        tension = st.number_input("Tensión de Overshot (klbs)", 0, 300, 100)
        if st.button("🎣 INTENTAR PESCA"):
            if tension > 220:
                st.session_state.pesca_activa = False
                st.session_state.vida_sarta = 100
                st.success("¡Pez recuperado! Sarta nueva instalada.")
                st.rerun()
            else: st.warning("Tensión insuficiente para liberar el pez.")
    else:
        if st.button("Mantenimiento de BHA"):
            st.session_state.vida_sarta = 100
            st.rerun()

with tabs[4]: # GEOLOGÍA
    st.title("📈 Gráfico de Perforación (Gamma Ray)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=st.session_state.history['GR'], y=st.session_state.history['DEPTH'], mode='lines', line=dict(color='#8B4513')))
    fig.update_layout(yaxis=dict(autorange="reversed", title="Depth (m)"), xaxis=dict(title="GR (API)"), template="simple_white")
    st.plotly_chart(fig, use_container_width=True)

with tabs[5]: # MANUAL & EVALUACIÓN
    st.title("Evaluación del Operador")
    st.markdown("""
    <div class="manual-box">
    <b>REGLAS DEL SIMULADOR:</b><br>
    - No exceder los 45 klbs de WOB.<br>
    - El reservorio se encuentra por debajo de los 2850m.<br>
    - Si hay Kick, cerrar el pozo inmediatamente.
    </div>
    """, unsafe_allow_html=True)
    
    # Lógica de Puntaje
    score = 100 - (st.session_state.kicks_recibidos * 15) - (st.session_state.sartas_rotas * 30)
    st.metric("PUNTAJE FINAL", f"{max(0, score)}/100")
    
    st.download_button(
        label="📥 DESCARGAR REPORTE EXAMEN",
        data=st.session_state.history.to_csv(index=False),
        file_name=f"Evaluacion_{st.session_state.usuario}.csv",
        mime="text/csv"
    )
    import os

# --- FUNCIÓN DE AUTOGUARDADO EN CARPETA LOCAL ---
def guardar_examen_local(df_historial, nombre_alumno, nro_legajo):
    # Creamos la carpeta si no existe
    carpeta = "EXAMENES_MENFA"
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)
    
    # Nombre del archivo con Legajo y Fecha/Hora para que no se pisen
    timestamp = time.strftime("%Y%m%d-%H%M")
    nombre_archivo = f"{carpeta}/Examen_{nro_legajo}_{nombre_alumno}_{timestamp}.csv"
    
    # Guardamos el CSV
    df_historial.to_csv(nombre_archivo, index=False)
    return nombre_archivo

# --- DENTRO DE LA PESTAÑA DE EVALUACIÓN (TAB 5) ---
with tabs[5]:
    st.title("Finalizar y Entregar Evaluación")
    st.warning("Al presionar el botón, su desempeño se guardará en el servidor local de IPCL MENFA.")
    
    if st.button("🏁 FINALIZAR TURNO Y GUARDAR EXAMEN", type="primary", use_container_width=True):
        if not st.session_state.history.empty:
            ruta = guardar_examen_local(
                st.session_state.history, 
                st.session_state.usuario, 
                st.session_state.legajo
            )
            st.success(f"✅ ¡Examen Guardado! Archivo: {ruta}")
            st.balloons()
            # Bloqueamos para que no sigan tocando
            st.session_state.target_met = True 
        else:
            st.error("No hay datos de perforación para guardar.")

    st.divider()
    st.info("Nota: Una vez guardado, el instructor Fabricio revisará su ROP promedio y el control de Kicks.")
# --- PANEL DE NOTAS AUTOMÁTICO PARA FABRICIO ---
def generar_acta_notas():
    carpeta = "EXAMENES_MENFA"
    if not os.path.exists(carpeta):
        return pd.DataFrame()
    
    archivos = [f for f in os.listdir(carpeta) if f.endswith('.csv')]
    resumen = []
    
    for arc in archivos:
        try:
            df_temp = pd.read_csv(os.path.join(carpeta, arc))
            # Extraemos info del nombre del archivo: Examen_LEGAJO_NOMBRE_FECHA.csv
            partes = arc.replace(".csv", "").split("_")
            legajo_arc = partes[1]
            nombre_arc = partes[2]
            
            # Cálculos de desempeño
            rop_prom = df_temp['ROP'].mean()
            max_depth = df_temp['DEPTH'].max()
            
            # Evaluamos errores (si el volumen de tanques subió mucho y no bajó, hubo error)
            kicks_mal_gestionados = len(df_temp[df_temp['TANQUES'] > 1300])
            
            # Nota lógica
            nota = 100
            if kicks_mal_gestionados > 5: nota -= 30
            if rop_prom < 5: nota -= 10 # Muy lento
            if max_depth < 3000: nota -= 20 # No terminó el pozo
            
            resumen.append({
                "Legajo": legajo_arc,
                "Alumno": nombre_arc,
                "ROP Promedio": round(rop_prom, 2),
                "Prof. Final": max_depth,
                "Estado": "APROBADO" if nota >= 60 else "REPROBADO",
                "Nota Sugerida": max(0, nota)
            })
        except:
            continue
    return pd.DataFrame(resumen)

# --- NUEVA PESTAÑA PARA EL PROFESOR ---
# --- PANEL DE NOTAS ACTUALIZADO (LÓGICA DE 2 INTENTOS) ---
def generar_acta_notas():
    carpeta = "EXAMENES_MENFA"
    if not os.path.exists(carpeta):
        return pd.DataFrame()
    
    archivos = sorted([f for f in os.listdir(carpeta) if f.endswith('.csv')])
    resumen = {}
    
    for arc in archivos:
        try:
            df_temp = pd.read_csv(os.path.join(carpeta, arc))
            partes = arc.replace(".csv", "").split("_")
            legajo_arc = partes[1]
            nombre_arc = partes[2]
            
            # Cálculos de desempeño base
            rop_prom = df_temp['ROP'].mean()
            max_depth = df_temp['DEPTH'].max()
            kicks_mal_gestionados = len(df_temp[df_temp['TANQUES'] > 1300])
            sartas_rotas = len(df_temp[df_temp['WOB'] > 50]) # Detección por exceso de peso
            
            # Nota base
            nota = 100
            if kicks_mal_gestionados > 3: nota -= 25
            if sartas_rotas > 0: nota -= 20
            if max_depth < 3000: nota -= 15
            
            # --- LÓGICA DE INTENTOS ---
            if legajo_arc not in resumen:
                # PRIMER INTENTO
                resumen[legajo_arc] = {
                    "Legajo": legajo_arc,
                    "Alumno": nombre_arc,
                    "Intentos": 1,
                    "Nota Final": nota,
                    "Detalle": "Primer intento limpio."
                }
            else:
                # SEGUNDO INTENTO (Penalización de 2 puntos)
                resumen[legajo_arc]["Intentos"] = 2
                nota_final = nota - 2 # Descuento por re-intento
                resumen[legajo_arc]["Nota Final"] = nota_final
                resumen[legajo_arc]["Detalle"] = "Segundo intento (-2 pts pen.)"
                
        except Exception as e:
            continue
            
    return pd.DataFrame(resumen.values())

# --- INTERFAZ DEL PROFESOR (DENTRO DEL EXPANDER) ---
with st.expander("🔐 PANEL DE INSTRUCTOR (FABRICIO)"):
    pass_docente = st.text_input("Clave de Seguridad:", type="password")
    if pass_docente == "menfa2026":
        st.subheader("📋 Acta de Examen - IPCL MENFA")
        df_notas = generar_acta_notas()
        
        if not df_notas.empty:
            # Colorear aprobados y reprobados
            def color_nota(val):
                color = 'green' if val >= 60 else 'red'
                return f'color: {color}; font-weight: bold'
            
            st.dataframe(df_notas.style.applymap(color_nota, subset=['Nota Final']), use_container_width=True)
            
            st.download_button("📥 Descargar Acta Final", df_notas.to_csv(index=False), "Acta_Oficial_MENFA.csv")
        else:
            st.warning("Aún no hay exámenes procesados.")
from fpdf import FPDF
import datetime

# --- CONFIGURACIÓN DE COLORES INSTITUCIONALES MENFA ---
# Azul Petróleo MENFA: R=0, G=51, B=102
# Naranja Energía MENFA: R=255, G=102, B=0

def generar_pdf_certificado(nombre, legajo, nota):
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    
    # 1. --- BORDE ESTÉTICO EN AZUL PETRÓLEO ---
    pdf.set_draw_color(0, 51, 102) # Azul Petróleo
    pdf.set_line_width(4)
    pdf.rect(10, 10, 277, 190) # Borde principal
    
    pdf.set_line_width(1)
    pdf.rect(12, 12, 273, 186) # Borde interno fino

    # 2. --- LOGO (Asegurate de tener 'logo_menfa.png' en la carpeta) ---
    try:
        # Intenta cargar el logo si existe
        pdf.image("logo_menfa.png", x=120, y=20, w=50)
    except:
        # Si no, pone el nombre institucional en Azul Petróleo
        pdf.set_text_color(0, 51, 102) # Azul Petróleo
        pdf.set_font("Arial", "B", 20)
        pdf.text(125, 30, "IPCL MENFA")
        pdf.set_text_color(0, 0, 0) # Volver a negro

    # 3. --- TÍTULO PRINCIPAL ---
    pdf.set_font("Arial", "B", 35)
    pdf.set_text_color(0, 51, 102) # Azul Petróleo
    pdf.ln(65)
    pdf.cell(0, 15, "CERTIFICADO DE APROBACIÓN", ln=True, align="C")
    
    # 4. --- TEXTO DEL CERTIFICADO ---
    pdf.set_text_color(0, 0, 0) # Volver a negro para el texto normal
    pdf.set_font("Arial", "", 18)
    pdf.ln(10)
    pdf.cell(0, 10, "Se otorga el presente a:", ln=True, align="C")
    
    # 5. --- NOMBRE DEL ALUMNO EN AZUL ---
    pdf.set_font("Arial", "B", 28)
    pdf.set_text_color(0, 51, 102) # Azul Petróleo
    pdf.ln(5)
    pdf.cell(0, 15, nombre.upper(), ln=True, align="C")
    
    # 6. --- CUERPO DEL TEXTO ---
    pdf.set_text_color(0, 0, 0) # Negro
    pdf.set_font("Arial", "", 14)
    pdf.ln(10)
    fecha_hoy = datetime.date.today().strftime("%d/%m/%Y")
    
    # Creamos el texto de la nota destacada en Naranja
    cuerpo_1 = "Por haber completado y aprobado el Simulador Técnico de Perforación con un desempeño de "
    nota_texto = f"{nota}/100."
    cuerpo_2 = " Validado bajo normas de capacitación laboral del IPCL MENFA."

    # Usamos multi_cell para texto normal
    pdf.multi_cell(0, 8, cuerpo_1 + nota_texto + cuerpo_2, align="C")
    
    # 7. --- DETALLES DE FECHA Y LEGAJO ---
    pdf.ln(18)
    pdf.set_font("Arial", "I", 12)
    pdf.set_text_color(100, 100, 100) # Gris oscuro
    pdf.cell(0, 10, f"Mendoza, Argentina - {fecha_hoy} | Legajo: {legajo}", ln=True, align="C")
    
    # 8. --- FIRMA DIGITAL EN AZUL PETRÓLEO ---
    pdf.ln(12)
    pdf.set_draw_color(0, 51, 102) # Azul Petróleo
    pdf.set_line_width(1)
    pdf.cell(90) # Espacio a la izquierda
    pdf.cell(100, 10, "", ln=True, align="C") # Línea de firma
    pdf.line(pdf.get_x() + 95, pdf.get_y(), pdf.get_x() + 195, pdf.get_y())

    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(0, 51, 102) # Azul Petróleo
    pdf.cell(0, 5, "Inst. Fabricio", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, "Capacitación Técnica IPCL MENFA Mendoza", ln=True, align="C")

    # Reseteamos color de texto para Streamlit por las dudas
    pdf.set_text_color(0, 0, 0)

    return pdf.output()

# --- USAR ESTA FUNCIÓN EN LA PESTAÑA DE EVALUACIÓN ---
