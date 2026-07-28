# I-03 — Cadena propulsiva

**Estado:** Cerrada · **Alimenta:** ADR-0007, ADR-0008, y el **objetivo O1** del proyecto

## Por qué esta línea es la más importante del proyecto

La ecuación de alcance se descompone en tres factores multiplicativos independientes:

    R = (E_esp/g · m_bat/m_total) · η_total · (L/D)
        ────────────────────────    ───────    ─────
              energía              propulsión  aerodinámica

**Duplicar cualquiera de los tres duplica el alcance. Ninguno compensa la deficiencia de otro.**

De los tres, el propulsivo es el que tiene **margen recuperable inmediato y demostrable**. Es la base de la afirmación central del proyecto.

## El hallazgo que define el objetivo

### Validación cruzada del TBS Mojito `[D]`

| Fuente | Energía | Distancia | Wh/km |
|---|---|---|---|
| Waldner (medido) | 68,1 Wh (8S 2300 mAh LiPo) | 50 km | **1,36** |
| TBS (declarado) | 144,0 Wh (8S1P 5000 mAh Li-Ion) | 100 km | **1,44** |

**Concordancia dentro del 5 %.** Se adopta **1,40 Wh/km** como referencia.

### Comparativa de energía específica `[D]`

| Plataforma | Wh/km | Masa | **Wh/(km·kg)** | Velocidad |
|---|---|---|---|---|
| Sonicmodell AR Wing 1000 | 0,78 `[E]` | 1,0 kg | **0,78** | ~55 km/h |
| **TBS Mojito** | 1,40 `[D]` | 1,9 kg | **0,74** | 100–150 km/h |
| Mini Talon | 1,20 `[M]` | 1,3 kg | **0,92** | 50 km/h |
| Solar Impulse 2 | 160 `[D]` | 2300 kg | **0,070** | 70 km/h |

> **El Mojito no es más eficiente, es más rápido.** Consume la misma energía por kilómetro y kilogramo que un ala de foam de 40 USD. Su logro no es reducir el consumo específico: es **sostenerlo a dos o tres veces la velocidad**.

### L/D despejado del vuelo real `[D]`

    (L/D)_aero = (1/η) · (L/D)_efectivo

| Plataforma | L/D efectivo | η supuesto | **L/D aerodinámico** |
|---|---|---|---|
| TBS Mojito | 3,7 | 0,50 `[E]` | **7,4** |
| AR Wing | 3,5 | 0,50 `[E]` | 7,0 |
| Solar Impulse 2 | 39,2 | 0,80 `[E]` | 49 |

El L/D del Mojito en crucero rápido es **≈ 7,4**, muy por debajo de su L/D máximo.

## Datos primarios de hélice

**Brandt & Selig, AIAA 2011-1255** — 79 hélices, 9–11 in, Re 50–100×10³ al 75 % de pala:

- Eficiencia de pico entre **0,65 (buena) y 0,28 (mala)** — factor 2,3 `[M]`
- La eficiencia **mejora sistemáticamente al aumentar rpm**, por efecto Reynolds `[M]`
- Caso extremo: la Master Airscrew G/F 11×4 **casi duplica** su eficiencia de pico en el rango de rpm ensayado `[M]`
- Hélices de modelismo dan **7,5–15 % menos** que hélices de 36 in con P/D similar `[M]`
- Palas muy delgadas pueden entrar en **flutter** a J alto `[M]`

**Extracción propia de la base UIUC `[D]`** — ver [ADR-0007](../decisiones/ADR-0007-helice.md) para la tabla completa.

## El hueco cuantificado

| Componente | Rango |
|---|---|
| Hélice en su J óptimo | 0,65 – 0,73 |
| Motor + ESC bien dimensionado | ≈ 0,85 |
| **Producto teórico** | **0,55 – 0,62** |
| **Valor real despejado del vuelo** | **≈ 0,50** |

La brecha indica que **la hélice no opera en su relación de avance óptima**.

> **Margen recuperable: pasar de 0,50 a 0,60 son +20 % de alcance sin modificar la aerodinámica.**

De ahí sale el objetivo O1: **≤ 1,15 Wh/km** contra 1,40 del Mojito. Un 18 % de mejora justificable **solo con la cadena propulsiva**.

## Caso concreto: la hélice 7×12 del Mojito

Su P/D es **1,71**. El máximo de la base UIUC vol. 1 ronda 1,25, y ese caso ni siquiera alcanzó su pico dentro del rango medido. **Carece de respaldo de datos** → ADR-0008.

## Cómo se verifica

- **E3** — barrido de emparejamiento: vuelo estabilizado a velocidad fija registrando corriente, 3–4 combinaciones diámetro/paso, contra el J predicho por UIUC.
- **E2** — polar de planeo: es el único instrumento que **separa pérdidas propulsivas de pérdidas aerodinámicas**.

## Fuentes

1. Brandt, J. B. & Selig, M. S. — *Propeller Performance Data at Low Reynolds Numbers*. AIAA 2011-1255.
2. UIUC Propeller Database, vols. 1–4.
3. Team BlackSheep — ficha y manual del TBS Mojito rev. 2025-11-04.
4. Waldner, N. — informe de ensayo del TBS Mojito, 3,5 meses.
