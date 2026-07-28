# ADR-0025 — Equilibrado de masa de elevones

**Estado:** ✅ Vigente · **Fecha:** 2026-07-28 · **Confianza:** Alta · **Reversible:** No
**Brechas:** G7 · **Investigación:** [I-05](../investigacion/I-05-divergencia-flutter.md)

## Contexto

Análisis preliminar de flutter `[E]`:

| Modo | Frecuencia estimada |
|---|---|
| Flexión ω_h | ~25 Hz |
| Torsión ω_α | ~106 Hz |
| **Elevón ω_β** | **~82 Hz** |

**ω_h/ω_α = 0,23** — modos muy separados: el flutter clásico flexión-torsión **no es crítico**.

**ω_β/ω_α = 0,77** — dentro de la banda de acoplamiento.

## El hallazgo que fuerza la decisión

**La separación de frecuencias no es alcanzable por rigidez.** No existe valor de GJ que resuelva el problema: si baja, ω_α cruza por debajo de ω_β; si sube, cruza por arriba. **Es un problema inercial, no de rigidez.**

## Decisión

**Equilibrado de masa de elevones, con el CG de la superficie sobre la línea de charnela. Innegociable.**

Presupuesto: ~60 g en total (~3,5 % del AUW).

## Fundamento

Con el CG del elevón sobre la charnela, el acoplamiento inercial desaparece y el modo deja de alimentarse. Es la solución estándar y ataca el mecanismo dominante en lugar de rodearlo.

Elevón de 25 g con CG a ~24 mm por detrás de la charnela → momento 0,60 g·m. Con cuerno de compensación de 20 mm hacia delante: **m_b ≈ 30 g por elevón**.

## Medidas concurrentes obligatorias

- **Cero holgura en el varillaje** (ADR-0026). La holgura es una no linealidad que dispara ciclo límite **por debajo** de la velocidad crítica lineal. Es la causa número uno de flutter en modelos.
- **Doble punto de accionamiento** si el elevón supera ~400 mm: duplica K_charnela y sube ω_β un 41 %.
- Servos digitales de alta rigidez de retención. El par estático importa menos que la rigidez.

## Elevada a innegociable

Tras anular el velo de carbono ([ADR-0022](ADR-0022-velo-carbono-anulada.md)), ω_α baja y el margen se estrecha. Lo que era prudencia pasó a requisito.

## Incertidumbre declarada

⚠️ **K_charnela es una estimación que puede fallar por factor 3**, y ω_β va con su raíz. Además, las bisagras de TPU impresas (ADR-0035) añaden rigidez mal caracterizada. **Caracterizarla es tarea de Fase 1.**

Se cierra con **E5** — FFT de trazas de giro de blackbox.
