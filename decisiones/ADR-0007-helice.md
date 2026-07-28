# ADR-0007 — Hélice de P/D 0,8–1,0 emparejada por relación de avance

**Estado:** ✅ Vigente · **Fecha:** 2026-07-27 · **Confianza:** Alta · **Reversible:** Sí
**Investigación:** [I-03 — Cadena propulsiva](../investigacion/I-03-cadena-propulsiva.md)

## Contexto

La cadena propulsiva es el término de la ecuación de alcance con mayor margen de mejora inmediata, y el que sostiene el objetivo O1 (≤ 1,15 Wh/km).

## Decisión

**Hélice de paso/diámetro 0,8–1,0, emparejada por relación de avance J a la velocidad de crucero, operando a rpm alta.**

## Fundamento `[D]` — extracción propia de la base UIUC

Pico de eficiencia a ~6000 rpm:

| Hélice | P/D | η máx | J óptimo | V @6000 rpm | V @16000 rpm |
|---|---|---|---|---|---|
| APC-E 8×4 | 0,50 | 0,600 | 0,481 | 35 km/h | 94 km/h |
| APC-E 8×6 | 0,75 | 0,678 | 0,689 | 50 km/h | 134 km/h |
| **APC-E 8×8** | **1,00** | **0,731** | 0,784 | 57 km/h | 153 km/h |
| APC-E 9×6 | 0,67 | 0,683 | 0,583 | 48 km/h | 128 km/h |
| APC-E 10×7 | 0,70 | 0,705 | 0,576 | 53 km/h | 140 km/h |

Tres lecturas:

1. **El paso domina.** De 8×4 a 8×8, mismo diámetro: **+22 % de eficiencia de pico**.
2. **La velocidad óptima es un producto hélice × rpm**, no una propiedad de la hélice. La misma 8×8 pica a 57 km/h a 6000 rpm y a 153 km/h a 16000.
3. **Subir rpm mejora la eficiencia** por efecto Reynolds en la pala `[M]` (Brandt & Selig).

## El hueco que justifica O1

| Componente | Rango |
|---|---|
| Hélice en su J óptimo | 0,65 – 0,73 |
| Motor + ESC bien dimensionado | ≈ 0,85 |
| **Producto teórico** | **0,55 – 0,62** |
| **Valor real despejado del vuelo del Mojito** | **≈ 0,50** |

**Pasar de 0,50 a 0,60 son +20 % de alcance sin tocar la aerodinámica.** Es la afirmación central del proyecto.

## Consecuencias

- El motor debe elegirse para que la hélice caiga en su J óptimo a la velocidad de crucero, no por empuje estático.
- La tabla de emparejamiento por pack es una salida publicable ([ADR-0033](ADR-0033-electronica-fuera.md)).
- Se realiza y verifica con el ensayo E3.
