# ADR-0027 — Espesor relativo 13,5 % raíz / 9 % punta

**Estado:** ✅ Vigente · **Fecha:** 2026-07-28 · **Confianza:** Alta `[M]` · **Reversible:** No
**Sustituye a:** ADR-0005 (perfil «delgado»)
**Datos:** [02-referencias-medidas](../docs/02-referencias-medidas.md)

## Contexto

La decisión original (ADR-0005) pedía perfil **delgado**, por argumento de resistencia parásita. Tres análisis posteriores la invirtieron.

## Decisión

**t/c = 13,5 % en raíz, 9 % en punta.**

## Fundamento — tres caminos independientes al mismo número

**1. Divergencia.** En sección cerrada, `J = 4A²t/s`. Como el área encerrada va con el espesor, el t/c entra **lineal en la velocidad de divergencia**:

    V_div ∝ (h/c) · AR^(−3/4) · S^(−1/4) · √(G·t_pared)

Subir de 11 % a 13 % da ×1,18 de V_div por ~30 g. Es la palanca más barata del proyecto.

**2. Alojamiento de celda.** Las 21700 miden 21 mm de diámetro y **no se apilan**. Con piel, holgura y estructura hacen falta ~28 mm útiles.

| t/c | Espesor en raíz (c = 260 mm) | Margen sobre celda |
|---|---|---|
| 11 % | 28,6 mm | 6 mm — muy justo |
| **13,5 %** | **35,1 mm** | **Holgado** |

**3. Convergencia con artículo que vuela `[M]`.** Medición sobre el Peregrine 840 mm:

| Estación | Cuerda | Espesor | t/c |
|---|---|---|---|
| 0,15 | 125,6 mm | 17,0 mm | 13,5 % |
| 0,55 | 140,6 mm | 19,3 mm | 13,8 % |
| 0,90 | 160,1 mm | 21,3 mm | 13,3 % |

**Un ala de flecha invertida impresa que está en servicio usa 13,5 %.** Tres razonamientos distintos, mismo resultado.

## Consecuencias

- Restringe la selección de perfil (brecha G2) a familias de 13–14 % de espesor.
- Penaliza C_D0 respecto a un perfil delgado. Se acepta: la rigidez manda.
- Facilita la bahía de batería y por tanto R-CG.

## Condiciones de revisión

Ninguna prevista. Es de las decisiones mejor sostenidas del proyecto.
