# Convenciones y nomenclatura

## Etiquetas de confianza

| Etiqueta | Significado |
|---|---|
| `[M]` | Medido y publicado por una fuente primaria |
| `[D]` | Derivado por cálculo a partir de datos `[M]` |
| `[E]` | Estimado sobre supuestos declarados |
| `[I]` | Inferencia razonada, no verificada |

**Regla dura:** ningún dato `[E]` o `[I]` sostiene una decisión irreversible sin verificación previa.

## Identificadores

| Prefijo | Significado | Vive en |
|---|---|---|
| `ADR-XXXX` | Decisión de diseño | `decisiones/` |
| `I-XX` | Línea de investigación | `investigacion/` |
| `GX` | Brecha de datos | `brechas/` |
| `EX` | Ensayo | `ensayos/` |
| `OX` | Objetivo | `docs/00-...` |
| `R-XXX` | Requisito derivado | `docs/00-...` |
| `CX` | Corrección registrada | `CHANGELOG.md` |
| `FX` | Fase del proyecto | `docs/` |

## Símbolos

| Símbolo | Magnitud | Unidad |
|---|---|---|
| b | Envergadura | m |
| S | Superficie alar | m² |
| AR | Alargamiento, b²/S | — |
| c | Cuerda | m |
| c̄ | Cuerda media aerodinámica | m |
| t/c, h/c | Espesor relativo | % |
| ε | Torsión geométrica (wash-in positivo) | ° |
| Λ | Flecha del c/4 (negativa = invertida) | ° |
| q | Presión dinámica | Pa |
| GJ | Rigidez torsional | N·m² |
| EI | Rigidez a flexión | N·m² |
| J | Constante de torsión / relación de avance de hélice | m⁴ / — |
| e_i | Eficiencia de envergadura no viscosa | — |
| e_v | Factor de Oswald (**no usar solo** — ver I-01) | — |
| η | Rendimiento propulsivo | — |
| V_div | Velocidad de divergencia | km/h |
| ω_h, ω_α, ω_β | Frecuencias de flexión, torsión, elevón | Hz |

## Convenciones de signo

- **Flecha:** negativa hacia delante. Este proyecto usa Λ ≈ −20°.
- **Torsión:** wash-in positivo (punta a mayor incidencia). Este proyecto usa wash-in.
- **Factor de carga:** positivo hacia arriba.

## Unidades

SI en cálculo. En tablas de presentación se admiten km/h para velocidad y g/dm² para carga alar, por ser las de uso corriente en el ámbito.

## Convenciones de escritura

- Toda cifra cuantitativa lleva etiqueta de confianza la primera vez que aparece en un documento.
- Los rangos se escriben `a–b`, no `a-b`.
- Las advertencias importantes van con ⚠️ y explican **la consecuencia**, no solo el hecho.
- Las correcciones **no se silencian editando**: se corrige el texto y se anota en el CHANGELOG.
