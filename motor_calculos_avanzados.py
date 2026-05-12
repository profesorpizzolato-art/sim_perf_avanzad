import numpy as np

def calcular_fisica_perforacion(wob, rpm, torque, profundidad, flow_rate, mw_actual):
    """
    Cálculos técnicos de perforación optimizados para MENFA 3.0
    Ahora incluye el efecto de la densidad sobre la ROP y la hidrostática.
    """
    # --- CONSTANTES TÉCNICAS ---
    diam_mecha = 8.5  
    area_mecha = np.pi * (diam_mecha**2) / 4
    id_casing = 9.625
    od_dp = 5.0
    tvd_ft = profundidad * 3.28 
    
    # --- 1. EFECTO DE LA DENSIDAD EN LA ROP (Chip Hold-down) ---
    # A medida que aumenta la densidad, la eficiencia de penetración cae.
    # Usamos un factor de corrección: a 9 ppg el factor es 1.0, a 18 ppg cae un ~40%
    f_densidad = max(0.4, 1.0 - (mw_actual - 9.0) * 0.05)
    
    # --- 2. CÁLCULO DE ROP DINÁMICA ---
    # Velocidad Anular (AV) para limpieza
    av = (24.5 * flow_rate) / (id_casing**2 - od_dp**2)
    
    # Factor de limpieza: si AV < 120 ft/min, la ROP cae por embotamiento
    f_limpieza = 1.0 if av > 120 else (av / 120)
    
    # Estimación de ROP (m/hr) considerando WOB, RPM, Limpieza y Densidad
    rop_dinamica = (wob * rpm * 0.005) * f_limpieza * f_densidad
    rop_efectiva = max(rop_dinamica, 0.5) 
    
    # --- 3. MSE (Mechanical Specific Energy) ---
    # Energía necesaria para destruir la roca (kpsi)
    # Si el MSE sube mucho sin que suba la ROP, estamos ante un problema (mecha gastada o roca muy dura)
    mse = (wob / area_mecha) + (480 * torque * rpm) / (area_mecha * rop_efectiva * 3.28)
    mse_kpsi = mse / 1000

    # --- 4. HIDROSTÁTICA Y FACTOR DE FLOTACIÓN ---
    # El factor de flotación (BF) cambia según la densidad del lodo
    # BF = (Densidad Acero - Densidad Lodo) / Densidad Acero
    bf = (65.5 - mw_actual) / 65.5 
    
    presion_hidro = 0.052 * mw_actual * tvd_ft

    # --- 5. CARGA EN EL GANCHO (Hook Load) ---
    peso_sarta_lbs = profundidad * 25 # Suponiendo peso lineal promedio
    hook_load_lbs = (peso_sarta_lbs * bf) - (wob * 1000)

    return {
        "ROP": round(rop_efectiva, 1),
        "MSE": round(mse_kpsi, 2),
        "AV": round(av, 2),
        "PH": round(presion_hidro, 0),
        "BF": round(bf, 3),
        "HOOK_LOAD": round(hook_load_lbs / 1000, 1) # Retorna en klbs
    }
