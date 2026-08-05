# ADR-0004 — Alargamiento 6,0

**Estado:** 🔄 Provisional · **Fecha:** 2026-07-28 · **Confianza:** Media `[E]` · **Reversible:** No
**Brechas:** G1, G6 · **Investigación:** [I-01](../investigacion/I-01-alargamiento-reynolds.md), [I-05](../investigacion/I-05-divergencia-flutter.md)

## Contexto

La intuición dice "más alargamiento, menos resistencia inducida". A números de Reynolds bajos eso deja de ser cierto a partir de cierto punto, y en flecha invertida hay un segundo motivo para no subirlo.

## Historia de la decisión

- **Rev 1.0:** AR 6–8, por saturación del beneficio y acoplamiento cuerda→Reynolds.
- **Rev 1.1:** apretado a **6,0** al aparecer el término de divergencia.

## Decisión

**Alargamiento 6,0** → con b = 1300 mm, S = 0,282 m², cuerda media 217 mm.

## Fundamento

**Argumento 1 — Reynolds (I-01).** La cadena causal correcta:
1. La inducida sigue cayendo como 1/(π·AR·e_i) — subir AR **sí funciona**.
2. El término viscoso k·C_L² **no depende del alargamiento**.
3. Por tanto el beneficio **se satura**.
4. A superficie constante, subir AR acorta la cuerda → baja Re → sube k y sube C_D0.

El punto 4 genera el óptimo; el 3 lo hace plano.

**Argumento 2 — Divergencia (I-05).** La velocidad de divergencia escala como:

    V_div ∝ AR^(−3/4)

Subir de 6 a 8 cuesta ~19 % de V_div, además del castigo de cuerda.

**Contraste `[M]`:** el Peregrine 840 mm, que vuela, tiene AR ≈ 5,05.

## Consecuencias

- Fija S = 0,282 m² para b = 1300 mm.
- Carga alar 57 g/dm² con 6S1P → velocidad de pérdida ~43 km/h (ver corrección C16).
- Los paneles alternativos (1100 / 1600) cambian el AR y por tanto el punto neutro. Ver [ADR-0032](ADR-0032-modularidad.md) y R-NP.

## Condiciones de revisión

Cerrar G1 con la planta real de referencia. Si el análisis de estabilidad (Fase 1) exige más superficie para bajar la velocidad de pérdida, AR bajará antes que subir la envergadura.
