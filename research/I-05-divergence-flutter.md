# I-05 — Divergencia aeroelástica y flutter

**Estado:** **Abierta** · **Alimenta:** ADR-0002, ADR-0025, ADR-0028 · **Brechas:** G4, G6, G7

Es el **riesgo dominante del proyecto**. Ninguna otra línea de investigación reordena tantas prioridades.

## Mecanismo

En flecha invertida el centro aerodinámico queda **por delante** del centro de rigidez torsional. La carga produce torsión de encabritado → más ángulo de ataque → más sustentación → más torsión. **Realimentación positiva hasta fallo estructural** `[M]`.

Remedios conocidos: aumentar rigidez (penalización de masa) o **adaptación aeroelástica del laminado** (solución del X-29) `[M]`.

## Formulación

Sección cerrada de pared delgada (Bredt-Batho):

    J = 4·A²·t / s

Divergencia de ala uniforme:

    q_D = π²·GJ / (4·L²·c·e·a)

Con e ∝ c y AR = b²/S, la ley de escalado resulta:

    V_div ∝ (h/c) · AR^(−3/4) · S^(−1/4) · √(G·t_pared)

**El espesor relativo entra lineal. Es la palanca más potente disponible** → [ADR-0027](../decisiones/ADR-0027-espesor-relativo.md).

### Ley de escala a pared constante

Con `t` fijo (mismo nozzle, mismos perímetros) y geometría semejante de factor λ:

    GJ ∝ λ³ ,  q_D ∝ 1/λ ,  **V_div ∝ λ^(−1/2)**

Un ala más grande impresa con la misma pared es **inherentemente peor**. Explica por qué un diseño de 840 mm no transfiere a 1300 mm sin corrección.

## El error que iba en dirección contraria

La especificación original decía **relleno 0 %**, heredada de la práctica de LW-PLA en modo vaso.

**Bredt-Batho supone que la piel no pandea.** Una piel de 0,4–0,9 mm sobre un tramo sin apoyo de 100 mm o más, bajo cortante, **pandea localmente muy por debajo del límite del material**, y al pandear el GJ efectivo **se cae**.

> **Corrección C12.** Sin relleno, el cálculo de GJ estaba **sobreestimado, no subestimado**.

El giroide al 4–5 % **no aporta torsión directa** — está cerca del centro de cortante — sino que **estabiliza la piel** para que la célula cerrada funcione → [ADR-0028](../decisiones/ADR-0028-relleno-giroide.md).

## Anclaje a artículo en servicio

El **Peregrine 840 mm** es un ala volante de flecha invertida impresa, volando. Ver [datos medidos](../docs/02-referencias-medidas.md).

| | Peregrine | Proyecto | Ratio |
|---|---|---|---|
| Cuerda de referencia | ~180 mm | 260 mm | 1,44 |
| Semienvergadura | 420 mm | 650 mm | 1,55 |
| Pared | 0,42 mm (1 perímetro) | 0,90 mm (2) | 2,14 |
| t/c | 13,5 % `[M]` | 13,5 % | 1,00 |
| **GJ** (∝ c³·t) | — | — | **6,45×** |
| **V_div** | — | — | **1,14×** |

**El diseño del proyecto es un 14 % mejor en velocidad de divergencia que la referencia, pese a ser un 55 % más grande.**

⚠️ Esto **ancla** la comparación en geometría medida. **No da el valor absoluto.**

> **Corrección C13.** Se propuso calibrar el modelo contra el Peregrine (ensayo E6). **Retirado:** el Peregrine está a factor ~3 de la predicción. Un ensayo que pasa con ese margen **no falsa el modelo pero tampoco lo valida**.

> **Corrección C15.** Se afirmó que un solo perímetro no cumple criterio. **Falsado por hardware volando.**

> **Corrección C14.** Se sobreestimó el riesgo y se comunicó con más rotundidad de la que soportaban datos `[E]` ±35 %.

## Flutter — análisis preliminar `[E]`

| Modo | Frecuencia |
|---|---|
| Flexión ω_h | ~25 Hz |
| Torsión ω_α | ~106 Hz |
| **Elevón ω_β** | **~82 Hz** |

- **ω_h/ω_α = 0,23** — modos muy separados: **el flutter clásico flexión-torsión no es crítico.**
- **ω_β/ω_α = 0,77** — dentro de la banda de acoplamiento.

**Hallazgo clave: la separación no es alcanzable por rigidez.** No existe valor de GJ que resuelva el problema; si baja, ω_α cruza por debajo, si sube cruza por arriba. **Es inercial** → [ADR-0025](../decisiones/ADR-0025-equilibrado-elevones.md).

⚠️ K_charnela es estimación que puede fallar por factor 3, y ω_β va con su raíz. Las bisagras de TPU añaden rigidez mal caracterizada.

## Cómo se cierra: E7, gráfico de Southwell

Al aproximarse a divergencia la torsión elástica se amplifica como **1/(1 − q/q_D)**: la deflexión de elevón necesaria para compensar **se dispara de forma hiperbólica mucho antes de llegar**.

**Método:**
1. Vuelo estabilizado en modo Cruise a 90, 110, 130 y 150 km/h.
2. De la blackbox: deflexión de trim de elevón contra presión dinámica del pitot.
3. **Representar 1/Δtrim contra q: sale una recta que corta el eje en q_D.**

Técnica estándar para extrapolar la velocidad crítica **sin alcanzarla nunca**. Convierte G6 de brecha bibliográfica en medición de la primera tarde de vuelo.

⚠️ **Amenaza identificada (G9):** la documentación del Peregrine reporta *porpoising* en modos RTH / Cruise / Loiter de INAV. **Si el avión oscila en altitud, los datos de trim contra q son ruido y Southwell no sale.** Hay que estabilizar el lazo de altitud antes de intentar E7.

## Estado de la línea

**Abierta.** Cierra cuando E7 dé un q_D medido.
