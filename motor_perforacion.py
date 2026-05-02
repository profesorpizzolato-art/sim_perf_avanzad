import numpy as np

def calcular_todo(piz):
    """
    Motor Técnico Avanzado MENFA 3.0
    Integra hidráulica, mecánica de rocas y eventos dinámicos.
    """
    # 1. Inputs operativos
    rpm = piz.get("rpm", 0)
    wob = piz.get("wob", 0)
    caudal = piz.get("caudal", 0)
    prof = piz.get("profundidad_actual", 1000)
    densidad_lodo = piz.get("densidad_lodo", 9.5)
    evento = piz.get("evento_activo", None)
    
    # 2. Litología y Dureza (Material Técnico)
    dureza_map = {
        "Areniscas Consolidadas": 1.0, 
        "Arcillas Plásticas": 0.7, 
        "Tobas y Cenizas": 1.2, 
        "Vaca Muerta (Shale)": 2.5
    }
    litologia = piz.get("litologia", "Areniscas Consolidadas")
    dureza = dureza_map.get(litologia, 1.0)
    factor_desgaste = piz.get("factor_desgaste", 1.0) # 1.0 = Nuevo

    # 3. Mecánica de Perforación (ROP y Torque)
    # ROP: Basado en dureza y desgaste
    if wob > 2 and rpm > 10:
        rop = (rpm * wob * 0.002) / (dureza * factor_desgaste)
    else:
        rop = 0

    # Torque: Evolución con profundidad y parámetros mecánicos
    torque = (wob * 0.85) + (rpm * 0.15) + (prof * 0.02)

    # 4. Hidráulica Avanzada
    # SPP: Presión de bomba influenciada por densidad y caudal
    spp_base = (caudal ** 1.8) * 0.005 * (densidad_lodo / 8.33) if caudal > 0 else 0
    
    # Lógica de Crisis (Comandos del Instructor)
    influjo = 0
    spp_extra = 0
    if evento == "KICK":
        influjo = 4.0  # bbl/min ganancia
        spp_extra = 200 # Contrapresión
    elif evento == "LOST_CIRC":
        influjo = -6.5 # bbl/min pérdida
        spp_extra = -150

    spp = spp_base + spp_extra

    # PH: Presión Hidrostática (Fórmula 0.052 con prof en ft)
    ph = 0.052 * densidad_lodo * (prof * 3.28)
    
    # ECD: Densidad Equivalente considerando Pérdidas por Fricción Anular (APL)
    apl = spp * 0.1 # Simplificación técnica del 10% de SPP
    ecd = densidad_lodo + (apl / (0.052 * prof * 3.28)) if prof > 0 else densidad_lodo

    return {
        "ROP": round(rop, 2),
        "SPP": round(spp, 2),
        "ECD": round(ecd, 2),
        "PH": round(ph, 2),
        "Torque": round(torque, 2),
        "Carga_Gancho": round(150 + (prof * 0.025), 2),
        "Influjo": round(influjo, 2)
    }
