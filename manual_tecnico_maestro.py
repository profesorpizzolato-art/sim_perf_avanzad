from fpdf import FPDF
import datetime

class MENFA_Manual(FPDF):
    def header(self):
        try:
            # Si el logo no está, el try-except evita que el programa falle
            self.image('logo_menfa.png', 10, 8, 33)
        except:
            pass
        self.set_font('Arial', 'B', 12)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, 'MENFA CAPACITACIONES - MENDOZA, ARGENTINA', 0, 0, 'R')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Pagina {self.page_no()} | Manual Maestro de Perforacion 3.0', 0, 0, 'C')

def generar_manual_completo():
    pdf = MENFA_Manual()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- 1. PORTADA ---
    pdf.add_page()
    pdf.ln(60)
    pdf.set_font('Arial', 'B', 32)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 20, "MANUAL MAESTRO", 0, 1, 'C')
    pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 10, "PERFORACION, CONTROL DE POZOS Y GEONAVEGACION", 0, 1, 'C')
    pdf.ln(10)
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Edicion Especial 2026", 0, 1, 'C')
    pdf.ln(50)
    pdf.set_font('Arial', 'I', 10)
    pdf.multi_cell(0, 7, "Material educativo desarrollado para la formacion de Tecnicos Superiores en Petroleo.\nMendoza, Argentina.", align='C')

    # --- 2. GLOSARIO ---
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "1. GLOSARIO TECNICO PROFESIONAL", 0, 1)
    pdf.ln(5)
    pdf.set_text_color(0, 0, 0)
    
    glosario = [
        ("BHA (Bottom Hole Assembly)", "Conjunto de herramientas al final de la sarta (mecha, portamechas, estabilizadores)."),
        ("WOB (Weight on Bit)", "Carga aplicada a la mecha para lograr la penetracion de la roca."),
        ("KICK", "Entrada imprevista de fluidos de la formacion (gas o petroleo) al pozo."),
        ("MAASP", "Maxima presion anular superficial permitida antes de fracturar el zapato de la cañeria."),
        ("ECD (Equivalent Circulating Density)", "Densidad real que siente el fondo del pozo sumando la friccion anular."),
        ("STUCK PIPE", "Atrapamiento de la sarta por causas mecanicas o presiones diferenciales."),
        ("SWABBING", "Efecto de succion al sacar la herramienta muy rapido, causa principal de surgencias."),
        ("PORE PRESSURE", "Presion natural de los fluidos dentro de la roca (Presion de Poros).")
    ]
    for term, desc in glosario:
        pdf.set_font('Arial', 'B', 11)
        # CAMBIO CLAVE: Se usó "-" en lugar del punto especial para evitar error de Unicode
        pdf.cell(0, 7, f"- {term}:", 0, 1) 
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 6, desc)
        pdf.ln(2)

    # --- 3. FORMULAS ---
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "2. FORMULARIO DE INGENIERIA (UNIDADES DE CAMPO)", 0, 1)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    
    formulas = [
        "Presion Hidrostatica: Ph (psi) = 0.052 x Densidad (ppg) x TVD (ft)",
        "Gradiente de Presion: Gp (psi/ft) = Densidad (ppg) x 0.052",
        "Presion de Fondo (BHP): BHP = Ph + Caida de Presion Anular",
        "Nueva Densidad de Matar (KMW): (SIDPP / (0.052 x TVD)) + Densidad Actual",
        "Capacidad de Tuberia/Pozo: ID^2 / 1029.4 (bbl/ft)",
        "Velocidad Anular (ft/min): (24.5 x Caudal [gpm]) / (Dh^2 - Dp^2)"
    ]
    for f in formulas:
        pdf.set_font('Arial', '', 11)
        pdf.multi_cell(0, 10, f, border=1)
        pdf.ln(2)

    # --- 4. 100 TIPS (SECCIONADA) ---
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "3. LOS 100 TIPS DE ORO DEL PERFORADOR", 0, 1)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 8.5)
    
    # Se mantienen los tips originales pero con codificación segura
    tips = [
        # 1-10 Seguridad y General
        "1. SEGURIDAD: Verifique el freno de emergencia al iniciar el turno.",
        "2. OPERATIVO: Aumento de torque indica cambio de formacion o mecha embotada.",
        "3. CONTROL: Nunca saque tuberia sin llenar el pozo con lodo.",
        "4. GEOLOGIA: El gas en el retorno es la primera alarma de un reservorio.",
        "5. FLUIDOS: Filtrado bajo evita desmoronamiento de la pared del pozo.",
        "6. MENDOZA: Asegure el cemento de la guia para proteger acuiferos.",
        "7. MECANICA: Limpie y engrase siempre las roscas de la sarta.",
        "8. CONTROL: Ante la duda de flujo: ¡CIERRE EL POZO!",
        "9. BOMBAS: Caida de presion puede ser un washout en la tuberia.",
        "10. EQUIPO: Use señales estandarizadas con el enganchador.",
        # 11-30 Direccional y Geo
        "11. DIRECCIONAL: El Toolface es tu volante; orientalo bien antes de deslizar.",
        "12. GEONAVEGACION: Gamma Ray alto indica salida a zona de arcillas.",
        "13. OPERATIVO: Monitoreá la presion diferencial para no plantar el motor.",
        "14. DIRECCIONAL: Controlá el DLS para evitar fatiga en los tubos.",
        "15. GEONAVEGACION: La profundidad medida (MD) siempre es mayor al TVD.",
        "16. TÉCNICO: Un Side Track requiere un tapon de cemento de alta resistencia.",
        "17. DIRECCIONAL: La gravedad hace que la mecha 'camine' a la derecha.",
        "18. GEONAVEGACION: Comparar con pozos vecinos ayuda a anticipar topes.",
        "19. OPERATIVO: Estabilizadores variables permiten ajustar inclinacion.",
        "20. DIRECCIONAL: Evitá micro-doglegs; dificultan bajar el casing.",
        "21. TÉCNICO: RSS permite dirigir mientras la sarta rota continuamente.",
        "22. GEONAVEGACION: Sensores de resistividad detectan contactos agua-petroleo.",
        "23. OPERATIVO: Durante sliding, la limpieza baja; circulá a fondo.",
        "24. DIRECCIONAL: El Azimut es tu direccion cardinal; mantenelo bajo control.",
        "25. SEGURIDAD: Riesgo de Key Seating aumenta en curvas cerradas.",
        "26. GEONAVEGACION: El buzamiento (Dip Angle) afecta la estrategia.",
        "27. TÉCNICO: Calibrá sensores magneticos lejos de estructuras metalicas.",
        "28. OPERATIVO: Arrastre excesivo indica necesidad de mejorar el lodo.",
        "29. DIRECCIONAL: Build rate es tu capacidad de ganar angulo.",
        "30. COMUNICACION: El geologo y el perforador deben hablar constantemente.",
        # 31-50 Well Control
        "31. WELL CONTROL: El flow show es la primera señal de un Kick.",
        "32. TÉCNICO: SIDPP indica diferencia entre hidrostatica y formacion.",
        "33. OPERATIVO: Si fluye con bombas apagadas, haga cierre duro.",
        "34. WELL CONTROL: La burbuja de gas se expande al subir; SICP subirá.",
        "35. SEGURIDAD: Nunca excedas la MAASP; romperás el zapato.",
        "36. TÉCNICO: Metodo del Perforador requiere dos circulaciones.",
        "37. OPERATIVO: Esperar y Pesar mata el pozo en una sola vuelta.",
        "38. WELL CONTROL: Mantenga presion de fondo (BHP) constante al circular.",
        "39. SEGURIDAD: Verifique el Koomey cada turno; es su vida.",
        "40. TÉCNICO: Use el Pobre Boy para separar gas si llega a superficie.",
        "41. WELL CONTROL: Pit Gain es el indicador de volumen mas confiable.",
        "42. OPERATIVO: El choke es tu herramienta para regular la presion.",
        "43. TÉCNICO: El influjo de agua salada es dificil de detectar.",
        "44. SEGURIDAD: Realice Pit Drills con su cuadrilla semanalmente.",
        "45. WELL CONTROL: ICP es la suma de friccion mas el SIDPP.",
        "46. TÉCNICO: Calcule la densidad de matar (KMW) antes de circular.",
        "47. OPERATIVO: Si presiones suben, el gas migra; purgue segun tabla.",
        "48. SEGURIDAD: Personal no esencial evacua en control critico.",
        "49. WELL CONTROL: Use el Trip Tank en todas las maniobras.",
        "50. MENDOZA: Alerta al ROP Break; presion de formacion anormal.",
        # 51-70 Fluidos
        "51. FLUIDOS: Viscosidad Marsh indica capacidad de acarreo.",
        "52. TÉCNICO: Filtrado alto genera revoque grueso y pegamiento.",
        "53. OPERATIVO: Use lodos inhibidores en arcillas reactivas locales.",
        "54. FLUIDOS: Yield Point suspende recortes en bombas apagadas.",
        "55. SEGURIDAD: Use EPP completo al manejar soda caustica.",
        "56. TÉCNICO: Controle densidad cada 15 min; caida dispara Kick.",
        "57. OPERATIVO: Exceso de finos aumenta torque y desgasta bombas.",
        "58. FLUIDOS: En OBM el gas se disuelve; mas dificil de ver.",
        "59. TÉCNICO: pH entre 9 y 10.5 previene corrosion de tuberia.",
        "60. SEGURIDAD: H2S es letal; use equipo autonomo de inmediato.",
        "61. FLUIDOS: Fuerza de gel suspende solidos en conexiones.",
        "62. OPERATIVO: Haga pildora pesada antes de sacar herramienta.",
        "63. TÉCNICO: Combata perdida de circulacion con material LCM.",
        "64. FLUIDOS: Arena menor al 0.5% evita erosion de boquillas.",
        "65. SEGURIDAD: Mantenga hojas MSDS visibles en la cabina.",
        "66. TÉCNICO: En horizontal, use caudales altos para limpieza.",
        "67. OPERATIVO: Olor a huevo podrido indica presencia de H2S.",
        "68. FLUIDOS: Desgasificar lodo es critico despues de un Kick.",
        "69. TÉCNICO: Lodo sobredensificado puede causar arremetida inducida.",
        "70. MENDOZA: Trate recortes segun normativa ambiental local.",
        # 71-90 BHA y Pesca
        "71. BHA: Drill collars dan el peso; no use la tuberia fina.",
        "72. TÉCNICO: Use estabilizadores para controlar la tendencia.",
        "73. OPERATIVO: Haga shifting para evitar pegamiento diferencial.",
        "74. PESCA: Tome impresion con bloque de plomo antes de bajar.",
        "75. TÉCNICO: Martillos (jars) deben tener espacio para actuar.",
        "76. BHA: Verifique diametro de mecha con calibrador antes de bajar.",
        "77. PESCA: Sepa cuando detenerse; a veces Side-track es mejor.",
        "78. OPERATIVO: Torque erratico y caida de peso indican twist-off.",
        "79. TÉCNICO: HWDP sirve como zona de transicion de esfuerzos.",
        "80. BHA: Jets de la mecha limpian el fondo hidráulicamente.",
        "81. PESCA: Overshot requiere grapples del tamaño exacto.",
        "82. TÉCNICO: Lleve registro de horas; la fatiga es invisible.",
        "83. OPERATIVO: Use Monel (no magnetico) cerca del MWD.",
        "84. BHA: Mecha PDC es para ROP alta pero sensible a vibracion.",
        "85. PESCA: Mantenga circulacion minima sobre el pescado.",
        "86. TÉCNICO: Punto Neutro debe caer en portamechas o HWDP.",
        "87. BHA: Escariadores mantienen el pozo en calibre.",
        "88. PESCA: Spear agarra por dentro si el tope externo falló.",
        "89. OPERATIVO: Vibraciones dañan electronica y cortadores.",
        "90. MENDOZA: Shock Subs protegen BHA en pozos profundos.",
        # 91-100 Terminacion
        "91. TERMINACION: Lodo de completacion debe estar bien filtrado.",
        "92. TÉCNICO: Cementacion primaria asegura la vida del pozo.",
        "93. OPERATIVO: Viaje de limpieza antes de bajar el casing.",
        "94. SEGURIDAD: Si el retorno para en cementacion, hay perdida.",
        "95. TÉCNICO: Centralizadores aseguran anillo de cemento uniforme.",
        "96. PRUEBA: Haga Leak-off Test despues de cementar el zapato.",
        "97. OPERATIVO: Registro CBL/VDL confirma adherencia del cemento.",
        "98. SEGURIDAD: Nunca deje el pozo abierto a la atmosfera.",
        "99. TÉCNICO: Minimice Skin Effect con fluidos compatibles.",
        "100. MENFA: La capacitacion continua es su mejor herramienta."

    ]

    for t in tips:
        pdf.cell(0, 4.5, t, 0, 1)

    # --- 5. CONVERSIONES ---
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "4. TABLA DE CONVERSIONES CRITICAS", 0, 1)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    
    conversions = [
        ["De Metros (m)", "a Pies (ft)", "x 3.281"],
        ["De Barrales (bbl)", "a Metros Cubicos (m3)", "x 0.1589"],
        ["De PPG (lb/gal)", "a gr/cm3 (SG)", "x 0.1198"],
        ["De PSI (Presion)", "a BAR", "x 0.0689"],
        ["De Pulgadas (in)", "a Milimetros (mm)", "x 25.4"]
    ]
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(60, 10, "Origen", 1, 0, 'C')
    pdf.cell(60, 10, "Destino", 1, 0, 'C')
    pdf.cell(60, 10, "Factor", 1, 1, 'C')
    pdf.set_font('Arial', '', 10)
    for row in conversions:
        pdf.cell(60, 10, row[0], 1)
        pdf.cell(60, 10, row[1], 1)
        pdf.cell(60, 10, row[2], 1)
        pdf.ln()

    return pdf.output(dest='S')

if __name__ == "__main__":
    try:
        content = generar_manual_completo()
        with open("Manual_Maestro_MENFA_3.0.pdf", "wb") as f:
            f.write(content)
        print("Manual generado con exito.")
    except Exception as e:
        print(f"Error: {e}")
