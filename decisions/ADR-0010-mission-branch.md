# ADR-0010 — Rama de misión: crucero rápido

**Estado:** ✅ Vigente · **Fecha:** 2026-07-28 · **Confianza:** Decidida · **Reversible:** No
**Investigación:** [I-01](../investigacion/I-01-alargamiento-reynolds.md), [I-03](../investigacion/I-03-cadena-propulsiva.md)

## Contexto

Existían dos funciones objetivo mutuamente excluyentes. **No son un compromiso continuo: divergen desde el primer trazo.**

| Rama | Métrica | Planta |
|---|---|---|
| **A — Crucero rápido** | Wh/km a 90–120 km/h | AR 5–7, carga alar 55–70 g/dm² |
| **B — Autonomía** | Minutos de vuelo | AR 8–12, carga alar 25–35 g/dm² |

Esta decisión bloqueó todo el proyecto durante la fase de investigación.

## Decisión

**Rama A — crucero rápido.**

## Fundamento

La elección de PETG la fuerza. La rama B exige 25–35 g/dm²; a S = 0,282 m² eso son 700–990 g de AUW. Solo la cáscara de PETG pesa 550–650 g `[E]`; con batería y motor se sale del presupuesto antes de empezar.

**No es una preferencia, es una restricción de material.** Y es coherente: la rama A *quiere* carga alar alta, así que la densidad del PETG deja de ser penalización.

## Consecuencias

- Objetivo de eficiencia expresado como **Wh/km**, no como minutos.
- El alargamiento se fija bajo (ADR-0004), lo que además ayuda a la divergencia.
- **No-objetivo declarado:** este proyecto no es un velero térmico.

## Nota sobre "eficiente"

El análisis de partida demostró que el TBS Mojito **no es energéticamente eficiente** — 0,74 Wh/(km·kg), igual que un ala de espuma barata. La eficiencia de este proyecto se busca donde los datos dicen que está el hueco: **la cadena propulsiva** ([I-03](../investigacion/I-03-cadena-propulsiva.md)), no la aerodinámica.
