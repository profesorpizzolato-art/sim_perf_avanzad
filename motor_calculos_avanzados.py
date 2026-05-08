import numpy as np

def calcular_fisica_perforacion(wob, rpm, torque, profundidad, flow_rate):
    """
    Cálculos técnicos de perforación optimizados para MENFA 3.0
    """
    # --- CONSTANTES TÉCNICAS ---
    diam_mecha = 8.5  
    area_mecha = np.pi * (diam_mecha**2) / 4
    id_casing = 9.625
    od_dp = 5.0
    
    # --- 1. CÁLCULO DE ROP DINÁMICA ---
    # Cálculo de Velocidad Anular (AV) para limpieza
    av = (24.5 * flow_rate) / (id_casing**2 - od_dp**2)
    
    # Factor de limpieza: si AV < 120 ft/min, la ROP cae por embotamiento
    f_limpieza = 1.0 if av > 120 else (av / 120)
    
    # Estimación de ROP (m/hr)
    rop_dinamica = (wob * rpm * 0.005) * f_limpieza
    rop_efectiva = max(rop_dinamica, 0.5) # Evitamos 0 para no romper el MSE
    
    # --- 2. MSE (Mechanical Specific Energy) ---
    # Energía necesaria para destruir la roca (kpsi)
    # Convertimos ROP a pies para la fórmula estándar
    mse = (wob / area_mecha) + (480 * torque * rpm) / (area_mecha * rop_efectiva * 3.28)
    mse_kpsi = mse / 1000

    # --- 3. CONTROL DE POZOS (Kill Mud Weight) ---
    sidpp = 500
    tvd_ft = profundidad * 3.28 
    mw_actual = 11.5
    kmw = mw_actual + (sidpp / (0.052 * tvd_ft))

    # --- 4. CARGA EN EL GANCHO (Hook Load) ---
    bf = 0.82 # Factor de flotación
    peso_sarta_lbs = profundidad * 25 
    hook_load_lbs = (peso_sarta_lbs * bf) - (wob * 1000)

    return {
        "ROP": round(rop_efectiva, 1),
        "MSE": round(mse_kpsi, 2),
        "AV": round(av, 2),
        "KMW": round(kmw, 2),
        "HOOK_LOAD": round(hook_load_lbs / 1000, 1) # Retorna en klbs
    }