import streamlit as st
import numpy as np

def calcular_todo(piz):
    """
    Este es el cerebro técnico. Integra bombas, sarta y física de perforación.
    """
    # 1. Captura de Variables de la Pizarra
    rpm = piz.get("rpm", 0)
    wob = piz.get("wob", 0)  # Weight on Bit (klbs)
    caudal = piz.get("caudal", 0) # GPM
    prof = piz.get("profundidad_actual", 1000)
    densidad_lodo = piz.get("densidad_lodo", 9.5) # ppg
    
    # --- LÓGICA DE BOMBAS (Basado en tus bombas_de_lodo.py) ---
    # Simulamos la presión de circulación (Stand Pipe Pressure)
    # SPP proporcional al cuadrado del caudal (Ley de afinidad)
    if caudal > 0:
        spp = (caudal ** 1.8) * 0.005 * (densidad_lodo / 8.33)
    else:
        spp = 0
        
    # --- LÓGICA DE AVANCE (Basado en tu motor_físico.py) ---
    # ROP = Velocidad de penetración (m/h)
    # Depende de RPM, WOB y un factor de formación (litología)
    gradiente = piz.get("gradiente", 0.44)
    factor_roca = 0.5 if gradiente > 0.5 else 1.2 # Vaca Muerta es más dura
    
    if wob > 2 and rpm > 10:
        rop = (rpm * wob * 0.002) * factor_roca
    else:
        rop = 0

    # --- LÓGICA DE HIDRÁULICA Y SEGURIDAD ---
    # Presión Hidrostática (PH = 0.052 * dens * prof_tv)
    # Pasamos metros a pies para la fórmula estándar (m * 3.28)
    presion_hidro = 0.052 * densidad_lodo * (prof * 3.28)
    
    # ECD (Densidad Equivalente de Circulación)
    ecd = densidad_lodo + (spp / (0.052 * prof * 3.28 * 0.1)) if prof > 0 else densidad_lodo

    # 2. Actualizamos la pizarra con los resultados calculados
    piz["spp"] = round(spp, 2)
    piz["rop"] = round(rop, 2)
    piz["ecd"] = round(ecd, 2)
    
    # 3. Retornamos los datos para que 'visual_pro.py' los use en los relojes
    return {
        "ROP": round(rop, 2),
        "SPP": round(spp, 2),
        "ECD": round(ecd, 2),
        "PH": round(presion_hidro, 2),
        "Carga_Gancho": round(150 + (prof * 0.02), 2) # Peso de la sarta estimado
    }
