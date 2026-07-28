# Objetivos y requisitos — Pliego de Fase 0

**Revisión 1.2** · 28 julio 2026 · **Fase 0 cerrada**
Define **qué se construye y por qué**. Ningún trazo de geometría precede a este documento.

---

# 1. La tensión central, resuelta

El análisis de partida demostró que **el TBS Mojito no es energéticamente eficiente**: 0,74 Wh/(km·kg), igual que un ala de espuma de 40 USD. Su logro es sostener ese consumo a 2–3× la velocidad.

Por tanto "eficiente" y "parecido al Mojito" solo son compatibles si la eficiencia se busca **donde el Mojito la está dejando sobre la mesa**:

| Fuente de mejora | Potencial | Base |
|---|---|---|
| **Emparejamiento de hélice** (η 0,50 → 0,60) | **+20 %** | [I-03](../investigacion/I-03-cadena-propulsiva.md) `[D]` |
| Acabado superficial y C_D0 | +5–8 % | `[E]` |
| Alargamiento y torsión optimizados | +3–5 % | `[E]` |

**Objetivo: ≤ 1,15 Wh/km.** Mejora del 18 % justificable **solo con la cadena propulsiva**. Es falsable: se mide con E2 y E3.

---

# 2. Objetivos

## 2.1 Imprescindibles

| # | Objetivo | Criterio de aceptación |
|---|---|---|
| **O1** | Eficiencia demostrada | ≤ 1,15 Wh/km a 95 km/h, medido con blackbox |
| **O2** | Batería flexible 4S–6S | 4S1P, 4S2P, 6S1P y 6S2P en 21700 sin cambiar el molde exterior |
| **O3** | Imprimible en máquina de 256 mm | Clase Bambu P1S. Sin cámara activa. Sin filamento exótico |
| **O4** | PETG como material único de estructura | Precio, disponibilidad, tolerancia térmica, facilidad |
| **O5** | Fácil de fabricar | ≤ 20 h de impresión por semiala · ≤ 3 h de montaje · **sin laminado de fibra** |
| **O6** | Fundamento publicado | Toda cifra con etiqueta de confianza y fuente |
| **O11** | Modularidad | Central estándar + paneles intercambiables con NP común |

## 2.2 Deseables

| # | Objetivo |
|---|---|
| O7 | Reparable por reimpresión de segmento |
| O8 | Coste de estructura < 60 € contra 189,95 USD del kit de referencia |
| O9 | Transportable — semialas desmontables, caja de 700 mm |
| O10 | Compatible con INAV y ArduPlane sin geometría dependiente de firmware |

## 2.3 No-objetivos

- **No es un avión de récord de velocidad.** Lo cubre el Eliminator, mismo linaje, 360 km/h.
- **No es un velero térmico.** La autonomía pura exige AR 8–12 y 25–35 g/dm², incompatible con PETG a esta escala.
- **No es un primer avión.** Sin cola, flecha invertida, lanzamiento a mano.
- **No busca masa mínima a cualquier precio.** La rigidez torsional manda.
- **No prescribe motor ni batería.** Ver [ADR-0033](../decisiones/ADR-0033-electronica-fuera.md).

---

# 3. Requisitos

## 3.1 Misión

| Requisito | Valor | Confianza |
|---|---|---|
| Alcance de diseño | 80 km con 20 % de reserva | `[E]` |
| Alcance objetivo extendido | 100 km, condicionado a E3 | `[E]` |
| Autonomía | 60 min a velocidad de mínima potencia | `[E]` |
| Velocidad de crucero | 90–105 km/h | Decidido |
| V_NE de diseño | 180 km/h | Decidido |
| **V_NE artículo #1** | **160 km/h** | Conservador hasta E7 |
| n_max / n_min | +6 / −3, último +9 | `[E]`, dominado por ráfaga |
| **Velocidad de pérdida** | **≤ 45 km/h** | Ver corrección C16 |
| C_Lmax requerido | ≥ 0,65 | `[D]` |

> **Corrección C16.** El requisito original era ≤ 40 km/h, derivado con AUW 1350 g (4S1P, 48 g/dm²). Al subir el AUW a 1620 g (6S1P, 57 g/dm²) **no se rehízo el cálculo**. Con C_Lmax 0,65 la velocidad de pérdida real es **42,7 km/h**; llegar a 40 exigiría C_Lmax 0,74, fuera del rango realista (0,55–0,70, Ananda et al.).
>
> **Relajado a ≤ 45 km/h**, justificado por precedente: el Peregrine a 52 g/dm² y el Mojito a ~60 se lanzan a mano.

## 3.2 Requisitos derivados de la modularidad

Ver [ADR-0032](../decisiones/ADR-0032-modularidad.md) para el desarrollo completo.

- **R-NP** — punto neutro común de familia. **No se admiten paneles arbitrarios.**
- **R-JUNTA** — rigidez torsional de junta ≥ 5× la de la sección adyacente. Junta al 30 % de semienvergadura, dos pasadores.

## 3.3 R-CG — centrado con batería variable

| Pack | Celdas | Energía | Masa | AUW | Carga alar |
|---|---|---|---|---|---|
| 4S1P | 4 | 65 Wh | ~300 g | ~1480 g | 52 g/dm² |
| **6S1P** | 6 | 97 Wh | ~455 g | **~1620 g** | **57 g/dm²** |
| 4S2P | 8 | 130 Wh | ~605 g | ~1785 g | 63 g/dm² |
| 6S2P | 12 | 195 Wh | ~910 g | ~2090 g | 74 g/dm² ⚠️ |

Rango de masa **610 g, el 41 % del AUW base**.

> **R-CG: la bahía debe permitir ajuste longitudinal del pack suficiente para mantener el CG dentro de ±5 mm en las cuatro configuraciones.**

- Las 21700 **no se apilan**: capa única de 21 mm. A 13,5 % de t/c y c_raíz 260 mm hay ~35 mm — holgado. **Con 11 % no entraba.**
- **6S2P queda fuera de la banda de crucero.** Soportado mecánicamente, documentado fuera de envolvente.

## 3.4 Estructura

| Requisito | Valor |
|---|---|
| Material | PETG convencional, color claro |
| Perímetros / relleno | 2 (0,9 mm) / **giroide 5 %** |
| Sección | Tres células: cajón D + central + charnela |
| Carbono | Tubo de flexión + pasador de junta. **No torsional principal** |
| Criterio de divergencia | V_div ≥ 1,5 × V_NE |
| Juntas | Espiga + adhesivo PETG específico, área ≥ 3× la sección de piel |
| Elevones | **Equilibrado de masa obligatorio**, varillaje sin holgura |

## 3.5 Aviónica

| Requisito | Valor |
|---|---|
| Controlador | INAV 9.1+ o ArduPlane. Geometría agnóstica |
| **Pitot** | **Obligatorio.** Sin él, E2 y E7 no son válidos |
| Blackbox | SD o flash. Instrumento de todo el programa de ensayo |
| GPS y magnetómetro | Fuera del camino de corriente de raíz |
| Lanzamiento | Autolaunch por detección de aceleración |

---

# 4. Riesgo dominante

**No es aerodinámico. Es estructural: rigidez torsional frente a divergencia aeroelástica.**

Desarrollo completo en [I-05](../investigacion/I-05-divergencia-flutter.md).

**Riesgo abierto sin verificar: flutter** (G7). El modo crítico identificado es el de elevón, y **no se resuelve con rigidez** — es inercial. Ver [ADR-0025](../decisiones/ADR-0025-equilibrado-elevones.md).
