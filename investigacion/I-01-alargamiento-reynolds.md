# I-01 — Frontera alargamiento / Reynolds

**Estado:** Cerrada · **Alimenta:** ADR-0004 (alargamiento 6,0), ADR-0009 (descomposición de resistencia)

## Pregunta

¿Existe un alargamiento óptimo finito a Reynolds bajo, y por qué mecanismo?

## Hallazgo metodológico — el más importante del proyecto

**Spedding & McArthur (2010) demuestran que en la literatura conviven dos coeficientes distintos llamados igual:**

| | Definición | Contenido |
|---|---|---|
| **e_i** (no viscoso) | 1/(1+δ) | Solo desviación de la carga elíptica |
| **e_v** (Oswald) | 1/(1+δ+kπAR) | Lo anterior **+ alargamiento + forma de la polar viscosa** |

**e_v decrece con el alargamiento por construcción algebraica, no por física.** Usarlo lleva a concluir erróneamente que subir AR es contraproducente.

### Formulación adoptada — nunca colapsar en un solo número

    C_D = C_d(C_l, Re)  +  C_L² / (π · AR · e_i)
          ─────────────     ──────────────────
          polar real 2-D         inducida

Límite de validez documentado por los autores: la polar parabólica con un único Oswald **solo es válida por encima de Re ≈ 5×10⁶**. Nuestro régimen está tres órdenes de magnitud por debajo.

## Datos primarios

**Spedding & McArthur, J. Aircraft 47(1), 2010** — Eppler 387, AR 6, túnel de baja turbulencia:

| Re | k (polar 2-D) | e_v | e_i |
|---|---|---|---|
| 10–20 ×10³ | 0,24 | 0,22 | 0,53–0,76 |

- A C_L = 0,4: **C_D = 0,019 a Re 60×10³ contra 0,075 a Re 10×10³** — factor ~4 `[M]`
- Pendiente de sustentación degradada: **C_lα ∝ Re^0,19** (2-D), **Re^0,18** (AR 6) `[M]`
- Causa física: **avance del punto de separación desde el borde de fuga**, incluso a ángulos pequeños `[M]`

**Ananda, Sukumar & Selig, Aerosp. Sci. Tech. 42, 2015** — 10 alas de placa plana, AR 2–5, Re 60–160×10³:

- e_v de **0,81 (AR 2) a 0,33 (AR 5)** `[M]` — magnitud de tipo e_v
- **C_Lmax entre 0,55 y 0,70** `[M]` ← restricción dura sobre la velocidad de pérdida
- C_Dmin entre 0,01 y 0,02 `[M]`
- **Sin beneficio detectable del estrechamiento** (λ 0,5 y 0,75) a Reynolds bajo `[M]`
- Carmichael, citado: la burbuja de separación laminar domina en **70×10³ ≤ Re ≤ 200×10³** `[M]`

**Hepperle** — los perfiles reflexados, obligatorios en ala volante, **sufren más a Reynolds bajo porque el reflex agrava el gradiente de presión adverso** `[M]`. Castigo doble para esta configuración.

## Conclusión

Sí existe un alargamiento óptimo finito, **pero no por el mecanismo que se suele citar**. La cadena causal correcta:

1. La inducida sigue cayendo como 1/(π·AR·e_i) — subir AR **sí funciona**.
2. El término viscoso k·C_L² **no depende del alargamiento**.
3. Por tanto el beneficio **se satura**.
4. A superficie constante, subir AR acorta la cuerda → baja Re → sube k y sube C_D0 — y a partir de cierto punto **empeora activamente**.

El punto 4 genera el óptimo. El punto 3 lo hace plano.

## Relación de mérito

    (L/D)_max = ½ · √(π·e·AR / C_D0)  ∝  √(b² / (C_f · S_mojada))

**El L/D máximo no depende del alargamiento ni de la superficie por separado, sino de envergadura² / superficie mojada.** Agrandar el ala sin agrandar el resto mejora dos veces.

**Validación `[D]`:** aplicada al planeador Eta (AR 51,33; L/D 70) despeja C_D0 = 0,0081 — valor coherente para composite pulido de competición. Un ala de foam típica está entre 0,025 y 0,035.

## Límite de transferencia

⚠️ Los ensayos citados cubren Re 10–160×10³. El régimen de crucero del proyecto es ≈ 4×10⁵. **Las magnitudes no se transfieren; las tendencias y la metodología sí.**

## Corrección asociada

**C1** — se afirmó inicialmente que el factor de Oswald se derrumba con el alargamiento por razones físicas, invalidando subir AR. Es en gran parte **artefacto de definición**.

## Fuentes

1. Spedding, G. R. & McArthur, J. — *Span Efficiencies of Wings at Low Reynolds Numbers*. J. Aircraft 47(1), 2010, pp. 120–128. DOI 10.2514/1.44247
2. Ananda, G. K., Sukumar, P. P. & Selig, M. S. — *Measured aerodynamic characteristics of wings at low Reynolds numbers*. Aerosp. Sci. Tech. 42, 2015, pp. 392–406.
3. Hepperle, M. — *MH AeroTools*: burbujas de separación laminar y turbuladores.
