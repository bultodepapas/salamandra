# ADR-0021 — PETG como material base de estructura

**Estado:** ✅ Vigente · **Fecha:** 2026-07-28 · **Confianza:** Alta · **Reversible:** Parcial
**Investigación:** [I-04 — Materiales de impresión](../investigacion/I-04-materiales-impresion.md)

## Contexto

La estructura primaria es una cáscara impresa. El material gobierna la rigidez torsional, que es el riesgo dominante del proyecto ([ADR-0001](ADR-0001-flecha-invertida.md)).

Se evaluaron cinco materiales con datos de ensayo apareados.

## Alternativas consideradas

| Material | E impreso | G_eff | ρ | **G/ρ** | Veredicto |
|---|---|---|---|---|---|
| PLA normal | 3,00 GPa `[M]` | 0,90 | 1,24 | **0,73** | Mejor rigidez. Falla a 65 °C. Frágil |
| PLA+ | 2,20 GPa `[M]` | 0,66 | 1,24 | 0,53 | **Rechazado** — ADR-0016 |
| ASA | 1,9–2,2 GPa `[E]` | 0,58 | 1,07 | 0,53 | Mejor térmica y soldable, pero alabea |
| **PETG** | **1,94 GPa** `[M]` | **0,55** | **1,27** | **0,43** | **Adoptado** |
| LW-PLA | ~1,0 GPa `[E]` | 0,35 | 0,68 | 0,51 | Ligero pero blando y caro |

## Decisión

**PETG convencional de bobina**, color claro, como material único de estructura.

## Fundamento

**El PETG es el peor de los termoplásticos en rigidez torsional específica.** Se adopta igualmente porque, con relleno giroide y sección de tres células, el criterio de divergencia se cumple — y entonces la elección se decide por criterios secundarios donde el PETG gana:

| Criterio | PETG | Alternativa |
|---|---|---|
| Margen térmico | HDT ≈ 70 °C | PLA/PLA+ fallan a 65 °C `[M]` |
| Tenacidad en aterrizaje de panza | Cede, no rompe | PLA astilla |
| Repetibilidad sin cámara activa | Buena | ASA alabea |
| Precio y disponibilidad | Mejor | LW-PLA ~3× |

**La torsión geométrica es un parámetro de trim** ([ADR-0003](README.md)). Un material que deforma de forma poco repetible corrompe la variable que gobierna el equilibrio. Eso descartó el ASA pese a sus ventajas.

## Consecuencias

- Fuerza la **rama A** de misión ([ADR-0010](ADR-0010-rama-de-mision.md)).
- Obliga a **color claro** (ADR-0012).
- Las juntas necesitan adhesivo específico (ADR-0023): 3D-Gloop PETG o epoxi de 30 min. No E6000.
- Obliga a relleno giroide ([ADR-0028](ADR-0028-relleno-giroide.md)) para que la sección cerrada funcione.

## Correcciones asociadas

- **C8** — se afirmó que el PETG tiene mejor adhesión de capas que el PLA. **Falso**: retención en Z, PLA 55 %, PETG 46 %, ASA 29 % `[M]`.
- **C9** — se afirmó que el PETG no se puede pegar. Demasiado categórico.

## Condiciones de revisión

Si el ensayo E7 midiera una divergencia por debajo de criterio y el remedio plástico saliera demasiado pesado, PLA normal (G/ρ 0,73) es la alternativa técnica, con el coste de perder el margen térmico.
