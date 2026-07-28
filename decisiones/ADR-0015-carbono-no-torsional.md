# ADR-0015 — El carbono es elemento de flexión y alineación, no de torsión

**Estado:** ✅ Vigente (corregida) · **Fecha:** 2026-07-28 · **Confianza:** Alta `[D]`
**Corrección asociada:** C11

## Contexto

La intuición del modelismo dice que "meter carbono" resuelve cualquier problema estructural. En torsión de ala eso es falso en el caso habitual y cierto en un caso concreto — y la diferencia importa.

## Versión original (incorrecta)

Se calculó un tubo de 10/8 mm, salieron 2,3 N·m² frente a los ~70 de la piel, y se concluyó: **"los tubos no sirven para torsión"**.

## La corrección (C11)

En tubo de pared delgada:

    J = π·D³·t / 4

**Va con el cubo del diámetro.** Pasar de 10 a 18 mm no es un 80 % más: es casi **6 veces** más.

| Elemento | GJ | Nota |
|---|---|---|
| Varilla maciza 6 mm | ~0,5 N·m² | Nada |
| Tubo 10/8 | 2,3 N·m² | El caso que se calculó |
| Tubo 18/16 pultruido | ~18 N·m² | +26 % sobre la piel |
| **Tubo 18/16 trenzado ±45°** | **~69 N·m²** | **Duplica el GJ del ala** |

## Decisión

**El carbono se usa como larguero de flexión y pasador de alineación de junta. No como elemento torsional principal.**

El tubo torsional trenzado queda documentado como **opción B** (ADR-0030), no descartado.

## Fundamento del rechazo como vía principal

Tres condiciones, las tres eliminatorias:

1. **Diámetro ≥ 16 mm.** Por debajo no compensa la masa.
2. **Trenzado ±45°, no pultruido.** Un pultruido tiene la fibra en el eje: en torsión trabaja la matriz y G cae a 3–4 GPa frente a 15. **Es un factor 4 en el resultado** — y **casi ningún vendedor de modelismo declara el laminado**. Se puede comprar un tubo, obtener +26 % en vez de +100 %, y no enterarse.
3. **Pegado continuo, no alojado.** Un tubo flotando en un manguito aporta **cero**. Exige costillas de transferencia a lo largo de todo el recorrido.

**Se rechaza como vía principal porque introduce dos incertidumbres nuevas — laminado desconocido y calidad de encolado — en el parámetro que ya es el riesgo dominante y que solo se conoce a ±35 %.**

## Referencia

El Peregrine 840 mm usa tubo Ø8 × 654 mm — un **larguero de flexión**, con aportación torsional ~1 N·m². Confirma el criterio.
