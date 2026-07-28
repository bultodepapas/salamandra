# ADR-0022 — Velo de carbono ±45° sobre la piel

**Estado:** ❌ **ANULADA** · **Fecha de anulación:** 2026-07-28

## Qué proponía

Laminar tejido de carbono de 80 g/m² a ±45° sobre el 60 % interior de la semienvergadura, continuo sobre las juntas entre segmentos.

## Por qué se propuso

Resolvía **dos problemas a la vez**:

1. **Rigidez torsional.** Una capa de 0,12 mm curados a ±45° aporta G·t ≈ 2,0 kN/mm frente a 0,50 de 0,9 mm de PETG. Multiplicaba GJ por ~4 con 60–90 g.
2. **Juntas.** Laminado continuo sobre los empalmes convierte la unión encolada en un **empalme laminado**: el adhesivo posiciona, la fibra pasa el par.

## Por qué se anula

**Decisión de proyecto**, alineada con el objetivo O5 (facilidad de fabricación): el laminado húmedo introduce una habilidad manual, tiempo de curado y un consumible que el resto del proyecto no necesita.

Motivos técnicos concurrentes:

- **El velo es una pantalla de RF.** La antena GPS no puede quedar bajo el laminado; obligaba a ventana en la fibra o a externalizar el módulo.
- Impide la reparación por reimpresión de segmento (O7).

## Qué ocupa su lugar

| Vía | Efecto en V_div | Masa |
|---|---|---|
| t/c 11 % → 13,5 % | ×1,18 | +30 g |
| Relleno giroide ([ADR-0028](ADR-0028-relleno-giroide.md)) | Evita el pandeo de piel | +40 g |
| Segunda alma de cortante (tres células) | ×1,12 | +40 g |

Coste neto frente al velo: ~+35 g. Se acepta.

## Consecuencias de la anulación

- **ADR-0025 (equilibrado de masa de elevones) pasa a innegociable.** Sin velo, ω_α baja y se acerca a los modos de servo.
- **G6 sube de prioridad**: con menos margen absoluto, estrechar el factor de flecha importa más.
- Desaparece el conflicto GPS–carbono. Ala 100 % plástica = transparente a RF en todas partes.

## Condiciones de reconsideración

Si E7 midiera una divergencia por debajo de criterio y el remedio plástico saliera demasiado pesado, el velo vuelve a la mesa como solución de mínima masa.
