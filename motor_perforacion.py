import streamlit as st
import numpy as np

def calcular_todo(piz):
    """
    Cerebro técnico del simulador MENFA 3.0.
    """
    # 1. Variables de entrada desde la pizarra
    rpm = piz.get("rpm", 0)
    wob = piz.get("wob", 0)
    caudal = piz.get("caudal", 0)
    prof = piz.get("profundidad_actual", 1000)
    densidad_lodo = piz.get("densidad_lodo", 9.5)
    evento = piz.get("evento_activo", None)

    # 2. Lógica de Eventos (Instructor)
    influjo = 0
    spp_extra = 0
    if evento == "KICK":
        influjo = 5.5
        spp_extra = 150
    elif evento == "PERDIDA":
        influjo = -8.0

    # 3. Física de Perforación
    gradiente = piz.get("gradiente", 0.44)
    # Vaca muerta (gradiente alto) ofrece más resistencia
    factor_roca = 0.5 if gradiente > 0.5 else 1.2
    
    if wob > 2 and rpm > 10:
        rop = (rpm * wob * 0.002) * factor_roca
    else:
        rop = 0

    # Torque y Arrastre (Modelo simplificado)
    torque = (wob * 0.8) + (rpm * 0.2) + (prof * 0.01)

    # 4. Hidráulica de Bombas
    if caudal > 0:
        spp = ((caudal ** 1.8) * 0.005 * (densidad_lodo / 8.33)) + spp_extra
    else:
        spp = 0

    # Presión Hidrostática
    presion_hidro = 0.052 * densidad_lodo * (prof * 3.28)
    
    # ECD (Densidad Equivalente)
    if prof > 0:
        ecd = densidad_lodo + (spp / (0.052 * prof * 3.28 * 0.1))
    else:
        ecd = densidad_lodo

    # 5. Guardar resultados en la pizarra para otros módulos
    piz["spp"] = round(spp, 2)
    piz["rop"] = round(rop, 2)
    piz["ecd"] = round(ecd, 2)

    # 6. Retornar diccionario de datos para la interfaz
    return {
        "ROP": round(rop, 2),
        "SPP": round(spp, 2),
        "ECD": round(ecd, 2),
        "PH": round(presion_hidro, 2),
        "Torque": round(torque, 2),
        "Carga_Gancho": round(150 + (prof * 0.02), 2),
        "Influjo": influjo
    }
