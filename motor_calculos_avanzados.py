import numpy as np

def calcular_fisica_perforacion(wob, rpm, torque, rop, profundidad, flow_rate):
    # Constantes Vaca Muerta
    diam_mecha = 8.5 
    area_mecha = np.pi * (diam_mecha**2) / 4
    
    # 1. MSE (Mechanical Specific Energy)
    # Evitamos división por cero si ROP es 0
    rop_efectiva = rop if rop > 0 else 0.1
    mse = (wob / area_mecha) + (480 * torque * rpm) / (area_mecha * rop_efectiva * 3.28)
    mse_kpsi = mse / 1000

    # 2. Hidráulica (Velocidad Anular)
    id_casing = 9.625
    od_dp = 5.0
    av = (24.5 * flow_rate) / (id_casing**2 - od_dp**2)
    
    # 3. Control de Pozos (Kill Mud Weight)
    sidpp = 500
    tvd = profundidad * 3.28 # Conversión a pies para la fórmula
    mw_actual = 11.5
    kmw = mw_actual + (sidpp / (0.052 * tvd))


import numpy as np

def calcular_fisica_perforacion(wob, rpm, torque, profundidad, flow_rate):
    # --- CONSTANTES VACA MUERTA ---
    diam_mecha = 8.5 
    area_mecha = np.pi * (diam_mecha**2) / 4
    id_casing = 9.625
    od_dp = 5.0
    
    # --- 1. CÁLCULO DE ROP DINÁMICA (Simulación simplificada de Maurer) ---
    # La ROP sube con WOB y RPM, pero se estanca si no hay suficiente limpieza (AV)
    av = (24.5 * flow_rate) / (id_casing**2 - od_dp**2)
    
    # Factor de limpieza (si AV < 120 ft/min, la ROP cae por embotamiento)
    f_limpieza = 1.0 if av > 120 else (av / 120)
    
    # Fórmula de ROP estimada (m/hr)
    # ROP ∝ (WOB * RPM) / Diam_Mecha
    rop_dinamica = (wob * rpm * 0.005) * f_limpieza
    rop_efectiva = max(rop_dinamica, 0.5) # Evitamos 0 para no romper el MSE
    
    # --- 2. MSE (Mechanical Specific Energy) ---
    # El MSE sube si la ROP es baja para el mismo WOB/RPM (ineficiencia)
    mse = (wob / area_mecha) + (480 * torque * rpm) / (area_mecha * rop_efectiva * 3.28)
    mse_kpsi = mse / 1000

    # --- 3. CONTROL DE POZOS (Kill Mud Weight) ---
    sidpp = 500
    tvd = profundidad * 3.28 
    mw_actual = 11.5
    kmw = mw_actual + (sidpp / (0.052 * tvd))

    # --- 4. CARGA EN EL GANCHO (Hook Load) ---
    bf = 0.82 
    peso_sarta = profundidad * 25 
    hook_load = (peso_sarta * bf) - (wob * 1000)

    return {
        "ROP": round(rop_efectiva, 1),
        "MSE": round(mse_kpsi, 2),
        "AV": round(av, 2),
        "KMW": round(kmw, 2),
        "HOOK_LOAD": round(hook_load / 1000, 1)
    }

    # 4. Carga en el Gancho (Hook Load)
    bf = 0.82 # Factor de flotación
    peso_sarta = profundidad * 25 # lbs/pie aprox
    hook_load = (peso_sarta * bf) - (wob * 1000)

    return {
        "MSE": round(mse_kpsi, 2),
        "AV": round(av, 2),
        "KMW": round(kmw, 2),
        "HOOK_LOAD": round(hook_load / 1000, 1)
    }
