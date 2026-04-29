 import streamlit as st
import numpy as np

def calcular_todo(piz):
    # Variables de la Pizarra
    rpm = piz.get("rpm", 0)
    wob = piz.get("wob", 0)
    caudal = piz.get("caudal", 0)
    prof = piz.get("profundidad_actual", 1000)
    densidad_lodo = piz.get("densidad_lodo", 9.5)
    evento = piz.get("evento_activo", None)

    # --- Lógica de Eventos del Instructor ---
    influjo = 0
    if evento == "KICK":
        influjo = 5.5  # bbl/min de ganancia
        piz["spp"] = piz.get("spp", 0) + 150 # Aumento de presión por fricción del influjo
    
    # --- Física de Perforación ---
    gradiente = piz.get("gradiente", 0.44)
    factor_roca = 0.5 if gradiente > 0.5 else 1.2
    rop = (rpm * wob * 0.002) * factor_roca if (wob > 2 and rpm > 10) else 0
    
    # Torque y Arrastre (Simplificado)
    torque = (wob * 0.8) + (rpm * 0.2) + (prof * 0.01)

    # --- Hidráulica ---
    spp = (caudal ** 1.8) * 0.005 * (densidad_lodo / 8.33) if caudal > 0 else 0
    presion_hidro = 0.052 * densidad_lodo * (prof * 3.28)
    ecd = densidad_lodo + (spp / (0.052 * prof * 3.28 * 0.1)) if prof > 0 else densidad_lodo

    return {
        "ROP": round(rop, 2),
        "SPP": round(spp, 2),
        "ECD": round(ecd, 2),
        "PH": round(presion_hidro, 2),
        "Torque": round(torque, 2),
        "Carga_Gancho": round(150 + (prof * 0.02), 2),
        "Influjo": influjo
    }
