"""
SISTEMA AUTONOMO DE REFRIGERACION PARA POD EN DATA CENTER

OBJETIVO
--------
Controlar automaticamente 4 unidades InRow que refrigeran
12 racks (3 racks por InRow), manteniendo una temperatura
optima de entrada al rack (INLET), maximizando eficiencia
energetica y reduciendo riesgo termico.

ESCENARIOS SOPORTADOS
--------
- CAC : Confinamiento de Pasillo Frio
- HAC : Confinamiento de Pasillo Caliente
- SIN_CONFINAMIENTO : Pasillos abiertos

CARACTERÍSTICAS CLAVE
--------
- Control basado en INLET (sensor critico)
- Loop dinamico segun criticidad termica
- Ajustes graduales y agresivos segun riesgo
- Respeto estricto de limites operativos
- Codigo explicable a nivel tecnico y no tecnico
"""

import time
from datetime import datetime

# 1-CONFIGURACION GENERAL DEL SISTEMA - VARIABLES CLAVE 

# OBJETIVOS TERMICOS
TEMPERATURA_OBJETIVO = 22.0      # °C ideal de entrada al rack
BANDA_MUERTA = 0.5               # Evita oscilaciones

# LIMITES OPERATIVOS DEL INRROW
SETPOINT_MINIMO = 17.0           # °C
SETPOINT_MAXIMO = 25.0           # °C

# SETPOINT SEGURO (MODO CONTINGENCIA)
SETPOINT_SEGURO = 20.0           # °C conservador

#  INTERVALOS DE CONTROL (segundos)
INTERVALO_NORMAL = 20 * 60       # 20 minutos (sistema estable)
INTERVALO_ALERTA = 10 * 60        # 10 minutos (riesgo moderado)
INTERVALO_CRITICO = 2 * 60       # 2 minutos (riesgo alto)

# PASOS DE AJUSTE
AJUSTE_SUAVE = 0.5               # Ajuste estándar
AJUSTE_RAPIDO = 1.5              # Ajuste agresivo (emergencia)

# ESCENARIO DEL POD
ESCENARIO_POD = "HAC"            # Opciones: "CAC", "HAC", "SIN_CONFINAMIENTO"

FALLAS_MAXIMAS = 3               # Fallas consecutivas para modo seguro

fallas_sensor_inlet = {
    1: 0,
    2: 0,
    3: 0,
    4: 0
}

# 2-SENSORES 
def leer_sensor_inlet(inrow_id):
    """
    Sensor CRITICO.
    Devuelve la temperatura del aire que ingresa a los racks.
    """
    sensores_simulados = {
        1: 23.1, # Sensor Inlet InRow 1
        2: 22.4, # Sensor Inlet InRow 2
        3: 24.0, # Sensor Inlet InRow 3
        4: 21.8  # Sensor Inlet InRow 4
    }
    return sensores_simulados.get(inrow_id)

def leer_sensor_contexto(inrow_id):
    """
    Sensor de contexto termico.
    NO gobierna el control, solo aporta diagnostico.
    """
    sensores_simulados = {
        1: 37.5,   # Pasillo caliente y/o ambiente
        2: 26.2,   # Pasillo caliente y/o ambiente
    }
    return sensores_simulados.get(inrow_id)

def puertas_confinamiento_cerradas():
    """
    Verifica si la o las puertas del confinamiento estan correctamente cerradas.
    """
    return True  # Simulación: siempre cerrada


# 3-INTERFAZ DE CONTROL DEL INRROW
def obtener_setpoint_actual(inrow_id):
    """
    Lee el setpoint actual configurado en el InRow.
    """
    setpoints_simulados = {
        1: 22.0, # Setpoint InRow 1
        2: 22.5, # Setpoint InRow 2
        3: 21.5, # Setpoint InRow 3
        4: 23.0  # Setpoint InRow 4
    }
    return setpoints_simulados.get(inrow_id)

def aplicar_setpoint_inrow(inrow_id, nuevo_setpoint):
    """
    Envía el nuevo setpoint al InRow.
    """
    print(f"[INROW {inrow_id}] -> Nuevo setpoint aplicado: {nuevo_setpoint:.1f} °C")


# 4-LOGICA INTELIGENTE DE CONTROL TERMICO
def evaluar_y_controlar_inrow(inrow_id):
    """
    Evalua sensores, determina riesgo termico y ajusta setpoint.
    Devuelve el intervalo recomendado para el próximo ciclo.
    """

    temperatura_inlet = leer_sensor_inlet(inrow_id)
    temperatura_contexto = leer_sensor_contexto(inrow_id)
    setpoint_actual = obtener_setpoint_actual(inrow_id)

    print(f"[INROW {inrow_id}]")
    print(f"INLET: {temperatura_inlet} °C")
    print(f"Contexto: {temperatura_contexto} °C")
    print(f"Setpoint actual: {setpoint_actual} °C")

    # Validacion basica + conteo de fallas
    if temperatura_inlet is None:
        fallas_sensor_inlet[inrow_id] += 1
        print(f"Fallo sensor INLET ({fallas_sensor_inlet[inrow_id]} consecutivos)")
    else:
        fallas_sensor_inlet[inrow_id] = 0

    if setpoint_actual is None:
        print("Setpoint no disponible → Sin ajuste")
        return INTERVALO_NORMAL
    
    # Modo seguro por fallas repetidas
    if fallas_sensor_inlet[inrow_id] >= FALLAS_MAXIMAS:
        print("MODO SEGURO → Setpoint conservador fijo")

        if setpoint_actual != SETPOINT_SEGURO:
            aplicar_setpoint_inrow(inrow_id, SETPOINT_SEGURO)
        else:
            print("Setpoint ya en modo seguro")

        return INTERVALO_CRITICO

    ajuste = 0.0
    intervalo = INTERVALO_NORMAL


    # 1-Evaluacion termica
    if temperatura_inlet >= TEMPERATURA_OBJETIVO + 2.0:
        ajuste = -AJUSTE_RAPIDO
        intervalo = INTERVALO_CRITICO
        print("CONDICIÓN CRÍTICA -> Enfriamiento agresivo")

    elif temperatura_inlet > TEMPERATURA_OBJETIVO + BANDA_MUERTA:
        ajuste = -AJUSTE_SUAVE
        intervalo = INTERVALO_ALERTA
        print("ALERTA -> Ajuste suave de enfriamiento")

    elif temperatura_inlet < TEMPERATURA_OBJETIVO - BANDA_MUERTA:
        ajuste = AJUSTE_SUAVE
        print("Frio excesivo -> Aumento de setpoint")
    else:
        print("Temperatura estable -> Sin cambios")


    # 2-Adaptando por escenario
    if ESCENARIO_POD == "CAC":
        if not puertas_confinamiento_cerradas():
            print("CAC: puerta abierta -> perdida de eficiencia")
            ajuste *= 0.4  

    elif ESCENARIO_POD == "HAC":
        if not puertas_confinamiento_cerradas():
            print("HAC: puerta abierta -> perdida moderada de eficiencia")
            ajuste *= 0.7  


    # 3-Aplicación segura
    nuevo_setpoint = setpoint_actual + ajuste
    nuevo_setpoint = max(
        SETPOINT_MINIMO,
        min(SETPOINT_MAXIMO, nuevo_setpoint)
    )

    if nuevo_setpoint != setpoint_actual:
        aplicar_setpoint_inrow(inrow_id, nuevo_setpoint)
    else:
        print("Setpoint sin modificación")

    return intervalo



# 5-LOOP PRINCIPAL AUTONOMO (AIRFLOW)

def ejecutar_control_autonomo():
    """
    Ejecuta el control continuo del POD.
    El sistema ajusta dinamicamente la frecuencia de control.
    """

    print("INICIO DEL CONTROL AUTÓNOMO DEL POD")

    while True:
        print(f"Ciclo iniciado: {datetime.now()}")

        intervalos = []

        for inrow_id in range(1, 5):
            intervalo = evaluar_y_controlar_inrow(inrow_id)
            intervalos.append(intervalo)

        # Se prioriza el escenario mas crítico
        proximo_ciclo = min(intervalos)

        print(f"Próximo ciclo en {proximo_ciclo / 60:.0f} minutos")
        time.sleep(proximo_ciclo)


# 6-EJECUCION DEL SISTEMA

if __name__ == "__main__":
    ejecutar_control_autonomo()
