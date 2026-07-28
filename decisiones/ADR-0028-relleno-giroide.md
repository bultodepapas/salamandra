# ADR-0028 — Relleno giroide al 5 %

**Estado:** ✅ Vigente · **Fecha:** 2026-07-28 · **Confianza:** Media `[M]` · **Reversible:** Sí
**Corrección asociada:** C12
**Investigación:** [I-05](../investigacion/I-05-divergencia-flutter.md)

## Contexto

La especificación original decía **relleno 0 %, solo perímetros**, heredada de la práctica de LW-PLA en modo vaso, donde el objetivo es masa mínima.

**Era un error**, y el mecanismo no es el que parece.

## El error

La formulación de Bredt-Batho supone que **la piel no pandea**. Una piel de 0,4–0,9 mm sobre un tramo sin apoyo de 100 mm o más, bajo cortante, **pandea localmente muy por debajo del límite del material**. Al pandear, el GJ efectivo no se degrada progresivamente: **se cae**.

Es decir: **sin relleno, el cálculo de GJ estaba sobreestimado, no subestimado.** El error iba en dirección contraria a la supuesta.

## Decisión

**Relleno giroide al 5 %** en toda la cáscara, en lugar de un tercer perímetro.

## Fundamento

- **La aportación del giroide no es torsional directa** — está cerca del centro de cortante y contribuye poco a `J`. Su función es **estabilizar la piel** para que la célula cerrada funcione de verdad.
- **Más rigidez por gramo que un perímetro adicional**, porque ataca el modo que realmente falla.
- **Precedente `[M]`:** el perfil de impresión del Peregrine 840 mm especifica **4 % de giroide** con **un solo perímetro**, y vuela.

Se adopta 5 % y no 8 % (valor propuesto inicialmente sin base) porque el 4 % está probado en vuelo y el 8 % era una estimación propia sin respaldo.

## Consecuencias

- Sustituye al tercer perímetro: **2 perímetros (0,9 mm) + giroide 5 %**.
- Ahorra ~135 g respecto a la vía de tres perímetros.
- Complica el laminado: el giroide en piezas de pared fina puede salir discontinuo. Verificar en la primera pieza real.

## Correcciones asociadas

- **C12** — relleno 0 % era erróneo para cáscara de PETG.
- **C15** — se afirmó que un perímetro no cumple criterio. **Falsado por hardware volando**: el Peregrine usa 1 perímetro de 0,42 mm.
