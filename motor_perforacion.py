import numpy as np

def calcular_todo(piz):
    """
    Motor Técnico Avanzado MENFA 3.0.
    Calcula la física en tiempo real cruzando datos del alumno y comandos del instructor.
    """
    # 1. INPUTS OPERATIVOS (Alumno)
    rpm = piz.get("rpm", 0)
    wob = piz.get("wob", 0)
    caudal = piz.get("caudal", 0)
    prof = piz.get("profundidad_actual", 1000)
    densidad_lodo = piz.get("densidad_lodo", 9.5)
    
    # 2. INPUTS DE CONTROL (Instructor / Pizarra)
    # El instructor define estos valores desde su panel
    evento = piz.get("evento_activo", None)
    litologia = piz.get("litologia", "Vaca Muerta (Shale)")
    factor_desgaste = piz.get("factor_desgaste", 1.0) 

    # 3. MATRIZ DE DUREZA (Mecánica de Rocas)
    dureza_map = {
        "Areniscas Consolidadas": 1.0, 
        "Arcillas Plásticas": 0.7, 
        "Tobas y Cenizas": 1.2, 
        "Vaca Muerta (Shale)": 2.5
    }
    dureza = dureza_map.get(litologia, 1.0)

    # 4. MECÁNICA DE PERFORACIÓN (ROP y Torque)
    # ROP: Solo hay avance si hay rotación, peso y bombas encendidas
    if wob > 1 and rpm > 5 and caudal > 100:
        # El ROP se ve afectado por la dureza de la roca y el desgaste del trépano
        rop = (rpm * wob * 0.002) / (dureza * factor_desgaste)
    else:
        rop = 0

    # Torque: Aumenta con la fricción (profundidad) y parámetros mecánicos
    torque = (wob * 0.85) + (rpm * 0.15) + (prof * 0.02)
    if rpm == 0: torque = 0 # Sin rotación no hay torque dinámico

    # 5. HIDRÁULICA Y CONTROL DE POZO
    # SPP: Presión de circulación base
    spp_base = (caudal ** 1.8) * 0.005 * (densidad_lodo / 8.33) if caudal > 0 else 0
    
    # Lógica de Crisis (Instructor)
    influjo = 0
    spp_extra = 0
    if evento == "KICK":
        influjo = 4.0   # Ganancia de 4 bbl/min
        spp_extra = 200 # Contrapresión por gas
    elif evento == "LOST_CIRC":
        influjo = -6.5  # Pérdida de 6.5 bbl/min
        spp_extra = -150

    spp = spp_base + spp_extra

    # 6. PESO EN EL GANCHO (Hook Load Dinámico)
    # Peso base de la sarta + fricción - el WOB que el alumno apoya
    peso_estatico = 150 + (prof * 0.025)
    carga_gancho = peso_estatico - wob

    # 7. PRESIONES Y ECD
    # PH: 0.052 * densidad * Prof(ft)
    ph = 0.052 * densidad_lodo * (prof * 3.28)
    
    # ECD: Incluye pérdidas por fricción anular (APL)
    apl = spp * 0.1 
    ecd = densidad_lodo + (apl / (0.052 * prof * 3.28)) if prof > 0 else densidad_lodo

    return {
        "ROP": round(rop, 2),
        "SPP": round(max(0, spp), 2),
        "ECD": round(ecd, 2),
        "PH": round(ph, 0),
        "Torque": round(torque, 2),
        "Carga_Gancho": round(carga_gancho, 1),
        "Influjo": round(influjo, 2),
        "Presion_Casing": 0 if not piz.get("bop_cerrado") else (500 + spp_extra)
    }
