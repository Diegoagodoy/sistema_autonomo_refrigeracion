# Sistema Autonomo de Refrigeracion Inteligente para PODs de Data Center

---

## Introduccion

Este proyecto propone un **sistema autonomo y automático de control termico** para PODs de Data Center, tanto **confinados** (CAC / HAC) como  **no confinados** , orientado a:

* Proteger la carga IT
* Optimizar el consumo energético
* Mantener continuidad operativa ante fallas
* Reducir la intervención manual

El sistema se diseña para controlar  **4 unidades InRow** , cada una refrigerando  **3 racks** , utilizando sensores críticos de temperatura de entrada ( **INLET** ) y sensores de contexto segun el escenario operativo.

---

## Objetivos del sistema

* Mantener la temperatura de entrada al rack dentro de un rango óptimo
* Ajustar automáticamente los setpoints de las unidades InRow
* Adaptar dinámicamente el intervalo de control según la criticidad térmica
* Detectar fallas de sensores y operar de forma segura
* Emitir alertas ante condiciones anómalas
* Funcionar como una  **política automática** , no como un simple script

---

## Arquitectura física y sensorica del POD

El siguiente diagrama representa la disposicion fisica del POD, la circulacion de aire
y la ubicación de sensores y unidades InRow utilizados por el sistema de control autonomo.

![Arquitectura del POD con sensores](https://github.com/Diegoagodoy/sistema_autonomo_refrigeracion/blob/60638cb2f6a03e75601e84f0f45ec510f403b53b/Imagenes/pod_diagrama.png)

### Leyenda de sensores y actuadores

ST-AMB = Sensor de temperatura ambiente (sensor de contexto)

ST-HAC = Sensor de temperatura de pasillo caliente (sensor de contexto)

S-DOOR = Sensor de estado de puertas de confinamiento (abierta / cerrada)

ST-IN(x) = Sensor de temperatura de entrada al rack (INLET) asociado al InRow x
(sensor crítico de control termico)

IN-(x) = Unidad de refrigeración InRow x

SP_(x) = Setpoint de temperatura configurado en el InRow x (lectura/escritura)

> **Nota:**
> El control termico automático se gobierna exclusivamente por los sensores ST-IN.
> El resto de los sensores aportan contexto operativo, diagnóstico y validación.

---

## Arquitectura conceptual del sistema

### Ciclo operativo continuo

El sistema opera bajo un  **loop de control autónomo** , que  **nunca se detiene** .

Ante eventos anomalos, cambia su  **modo de operación** , no su ejecución.

**Estados posibles:**

* 🟢 **Modo Normal** → Control fino y eficiente
* 🟡 **Modo Degradado** → Control conservador
* 🔴 **Modo Seguro** → Prioridad operativa

## Diagrama del Ciclo de Control Autónomo

El siguiente diagrama representa el ciclo completo de control termico del sistema,
incluyendo validacion de sensores, modos operativos y toma de decisiones.

```mermaid
flowchart TD
    A[Inicio del Ciclo de Control] --> B[Lectura de Sensores]

    B --> C[Validacion de lecturas]

    C --> D{Estado del sensor}

    D -->|OK| E[Modo Normal]
    D -->|Inestable| F[Modo Degradado]
    D -->|Caido| G[Modo Seguro]

    E --> H[Leer setpoint actual InRow]
    F --> H
    G --> H

    H --> I[Evaluar temperatura de entrada al rack]

    I --> J[Calcular setpoint segun modo activo]

    J --> K[Aplicar setpoint al InRow]

    K --> L[Registrar log / auditoria / DB]

    L --> M[Definir proximo intervalo de control]

    M --> N[Esperar para ejecutar]

    N --> A
```

---

## Sensores y criterios de medicion

### Sensor critico

* **Temperatura de entrada al rack (INLET)**

  Es el sensor principal sobre el cual se toman todas las decisiones de control termico.

### Sensores de contexto (según escenario)

* Ambiente (CAC / sin confinamiento)
* Pasillo caliente (HAC)
* Estado de puertas de confinamiento

> **Importante**
>
> La temperatura del aire caliente es informativa, pero **no reemplaza** la temperatura de entrada al rack como variable de control.

---

## Gestión inteligente de fallas de sensores

El sistema  **no reacciona ante una unica lectura inválida** .

### Política de validacion

* Cada sensor posee un contador de fallas consecutivas
* Una lectura válida reinicia el contador
* Al superar un umbral:
  * El sensor se marca como no confiable
  * Se genera una alerta
  * El sistema entra en **modo seguro**

### Esto evita:

* Oscilaciones innecesarias
* Falsas alarmas
* Ajustes térmicos peligrosos

---

## Lógica general de control térmico

1. Se leen los sensores
2. Se valida la calidad de las lecturas
3. Se determina el estado operativo
4. Se calcula el setpoint adecuado
5. Se aplica el setpoint al InRow
6. Se define el próximo intervalo de control
7. Se registra todo para auditoría

---

## Fragmentos clave del codigo (explicados)

### Configuracion general del sistema

<pre class="overflow-visible! px-0!" data-start="4101" data-end="4456"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-[calc(--spacing(9)+var(--header-height))] @w-xl/main:top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-python"><span><span># OBJETIVOS TÉRMICOS</span><span>
TEMPERATURA_OBJETIVO = </span><span>22.0</span><span>
BANDA_MUERTA = </span><span>0.5</span><span>

</span><span># LÍMITES OPERATIVOS</span><span>
SETPOINT_MINIMO = </span><span>17.0</span><span>
SETPOINT_MAXIMO = </span><span>25.0</span><span>

</span><span># INTERVALOS DE CONTROL</span><span>
INTERVALO_NORMAL = </span><span>20</span><span> * </span><span>60</span><span>
INTERVALO_ALERTA = </span><span>5</span><span> * </span><span>60</span><span>
INTERVALO_CRITICO = </span><span>2</span><span> * </span><span>60</span><span>

</span><span># AJUSTES</span><span>
AJUSTE_SUAVE = </span><span>0.5</span><span>
AJUSTE_RAPIDO = </span><span>1.0</span><span>

</span><span># ESCENARIO</span><span>
ESCENARIO_POD = </span><span>"HAC"</span><span>
</span></span></code></div></div></pre>

---

### Lectura del sensor critico (INLET)

<pre class="overflow-visible! px-0!" data-start="4629" data-end="4783"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-[calc(--spacing(9)+var(--header-height))] @w-xl/main:top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-python"><span><span>def </span><span></span><span>leer_sensor_inlet</span><span>(</span><span>inrow_id</span><span>):
    """
    Lee la temperatura de entrada de aire al rack.
    Sensor CRÍTICO del sistema.
    """
    </span><span>pass</span><span>
</span></span></code></div></div></pre>

**Concepto**

Mide la temperatura real que recibe la carga IT.

Es la referencia principal del sistema.

---

### Sensor de contexto

<pre class="overflow-visible! px-0!" data-start="4927" data-end="5118"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-[calc(--spacing(9)+var(--header-height))] @w-xl/main:top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-python"><span><span>def </span><span></span><span>leer_sensor_contexto</span><span>(</span><span>inrow_id</span><span>):
    """
    Sensores complementarios según escenario:
    - CAC → Ambiente
    - HAC → Pasillo caliente
    - SIN → Ambiente
    """
    </span><span>pass</span><span>
</span></span></code></div></div></pre>

**Concepto**

Aporta diagnóstico y contexto, pero **no gobierna** el control.

---

### Estado del confinamiento

<pre class="overflow-visible! px-0!" data-start="5241" data-end="5403"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-[calc(--spacing(9)+var(--header-height))] @w-xl/main:top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-python"><span><span>def </span><span></span><span>puertas_confinamiento_cerradas</span><span>():
    """
    Verifica si las puertas del confinamiento están cerradas.
    Aplica a CAC / HAC.
    """
    </span><span>pass</span><span>
</span></span></code></div></div></pre>

**Concepto**

El sistema considera variables físicas reales del entorno.

---

### Función central de control

<pre class="overflow-visible! px-0!" data-start="5523" data-end="5772"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-[calc(--spacing(9)+var(--header-height))] @w-xl/main:top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-python"><span><span>def </span><span></span><span>evaluar_y_controlar_inrow</span><span>(</span><span>inrow_id</span><span>):
    """
    Función principal del sistema:
    - Lee sensores
    - Valida datos
    - Define modo operativo
    - Calcula y aplica setpoint
    - Ajusta el intervalo de control
    """
    </span><span>pass</span><span>
</span></span></code></div></div></pre>

**Concepto**

Esta función representa la  **politica automatica de refrigeracion** .

---

## Modo seguro operativo

Ante fallas persistentes:

* Se fija un setpoint conservador
* Se prioriza la protección de la carga IT
* El sistema sigue operando

Ejemplo:

> Setpoint fijo en 20 °C hasta restaurar sensores confiables.

---

## Beneficios del sistema

- Reducción de riesgo térmico
- Menor intervención humana
- Mayor eficiencia energética
- Resiliencia ante fallas
- Escalabilidad
- Auditoría y trazabilidad

---

## Conclusión

El proyecto propone un cambio de enfoque en la gestión térmica del Data Center:

pasar de una operación reactiva y manual, a una  **politica autonoma, gobernada por reglas claras**.

Al operar sobre la  **temperatura real de entrada al rack** , el sistema permite:

* **Optimizar el consumo energético** de las unidades de refrigeración
* **Evitar sobreenfriamientos innecesarios**
* **Proteger y prolongar la vida útil de los equipos IT**

La eficiencia energética no se persigue a costa del riesgo operativo, sino como consecuencia de un control térmico preciso, contextual y seguro.

> Automatizar no es apagar al operador, es darle un sistema que piense de forma consistente, segura y predecible.

---

## Mejoras Futuras

* Integración con DCIM
* Alertas reales (Mail / Teams / WhatsApp)
* Históricos y dashboards
* Pausar/ Accionar por mantenimiento
* Front para visualizacion DB y Sistema de control
* Prediccion termica (ML)
