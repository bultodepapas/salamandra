# Registro de decisiones (ADR)

Una decisión, un archivo. Cada ADR declara **contexto, alternativas consideradas, decisión, consecuencias y confianza**.

## Estados

| Estado | Significado |
|---|---|
| ✅ **Vigente** | En efecto |
| 🔄 **Provisional** | En efecto pero apoyada en `[E]`/`[I]`; se revisa al cerrar la brecha asociada |
| ⬜ **Superada** | Sustituida por otra ADR |
| ❌ **Anulada** | Retirada sin sustituto |
| ⚠️ **En disputa** | Sin datos para resolver |

---

## Índice

| # | Decisión | Estado | Confianza | Reversible |
|---|---|---|---|---|
| [0001](ADR-0001-flecha-invertida.md) | Ala volante de flecha invertida | ✅ | Alta | No |
| [0002](ADR-0002-cascara-cerrada.md) | Estructura de cáscara cerrada de tres células | ✅ | Media `[I]` | No |
| 0003 | Torsión de tipo wash-in | 🔄 | Alta | Parcial |
| [0004](ADR-0004-alargamiento.md) | Alargamiento 6,0 | 🔄 | Media `[E]` | No |
| 0005 | Perfil reflexado y delgado | ⬜ | — | — |
| 0006 | Monomotor propulsor preferido | ⚠️ | Baja `[I]` | Sí |
| [0007](ADR-0007-helice.md) | Hélice P/D 0,8–1,0 emparejada por J | ✅ | Alta | Sí |
| 0008 | Rechazar hélice 7×12 | ✅ | Alta | Sí |
| 0009 | Descomposición separada de resistencia; nunca Oswald único | ✅ | Alta | No |
| [0010](ADR-0010-rama-de-mision.md) | Rama A — crucero rápido | ✅ | Decidida | No |
| 0012 | Color claro obligatorio | ✅ | Alta | Sí |
| [0015](ADR-0015-carbono-no-torsional.md) | Carbono como flexión y pasador, no torsión | ✅ | Alta `[D]` | Sí |
| 0016 | Rechazar PLA+ | ✅ | Alta `[M]` | — |
| 0018 | Rechazar ABS por degradación UV | ✅ | Alta `[M]` | — |
| [0021](ADR-0021-material-base.md) | PETG como material base | ✅ | Alta | Parcial |
| [0022](ADR-0022-velo-carbono-anulada.md) | Velo de carbono ±45° | ❌ **Anulada** | — | — |
| 0023 | Juntas: espiga + adhesivo PETG, área ≥ 3× | 🔄 | Media | Sí |
| 0024 | 3 segmentos por semiala, 45° en cama | ✅ | Alta | Sí |
| [0025](ADR-0025-equilibrado-elevones.md) | Equilibrado de masa de elevones | ✅ | Alta | No |
| 0026 | Varillaje sin holgura, doble accionamiento | ✅ | Alta | Sí |
| [0027](ADR-0027-espesor-relativo.md) | t/c 13,5 % raíz / 9 % punta | ✅ | Alta `[M]` | No |
| [0028](ADR-0028-relleno-giroide.md) | Relleno giroide 5 % | ✅ | Media `[M]` | Sí |
| 0030 | Vía plástica como base; tubo torsional opción B | 🔄 | Media | Sí |
| 0031 | Pasador de carbono en juntas | ✅ | Alta | Sí |
| [0032](ADR-0032-modularidad.md) | Arquitectura modular CORE + PANEL | ✅ | Alta | No |
| [0033](ADR-0033-electronica-fuera.md) | Motor y batería fuera del diseño | ✅ | Decidida | — |
| 0034 | Ángulo de bancada como parámetro de diseño | 🔄 | Media | Sí |
| 0035 | Bisagras impresas en TPU | 🔄 | Media | Sí |

### Superadas o anuladas

| # | Motivo |
|---|---|
| 0005 | Sustituida por [0027](ADR-0027-espesor-relativo.md). El perfil pasó de «delgado» a 13,5 % |
| 0011, 0013, 0014, 0017, 0019, 0020 | Sustituidas por [0021](ADR-0021-material-base.md) tras evaluar cinco materiales |
| 0022 | **Anulada** por decisión de proyecto — ver [ADR-0022](ADR-0022-velo-carbono-anulada.md) |
| 0029 | Absorbida en [0002](ADR-0002-cascara-cerrada.md) |

> **0015 fue corregida, no anulada.** La versión original afirmaba que los tubos de carbono no aportan torsión. Ver corrección C11 en el [CHANGELOG](../CHANGELOG.md).
