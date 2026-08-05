# ADR-0002 — Cáscara cerrada de tres células

**Estado:** ✅ Vigente · **Fecha:** 2026-07-28 · **Confianza:** Media `[I]` · **Reversible:** No
**Investigación:** [I-05](../investigacion/I-05-divergencia-flutter.md)

## Contexto

En flecha invertida la rigidez torsional gobierna el riesgo dominante. La construcción determina esa rigidez más que el material.

## Alternativas

| Construcción | Rigidez torsional | Veredicto |
|---|---|---|
| Espuma moldeada con varillas embebidas | Sección abierta o casi. Órdenes de magnitud peor | **Rechazada** |
| **Cáscara impresa cerrada** | Cajón de torsión por construcción | **Adoptada** |

## Decisión

**Cáscara cerrada de tres células:** cajón D en borde de ataque + célula central + célula de charnela.

## Fundamento

Una pieza impresa es una **cáscara cerrada — un cajón de torsión por construcción**. En sección cerrada, `J = 4A²t/s`; la rigidez de una sección cerrada supera en órdenes de magnitud a la de una abierta.

**Detalle que no era evidente:** la célula cerrada **no llega al borde de fuga**. La línea de charnela del elevón abre la sección, y en un ala volante los elevones ocupan casi toda la envergadura. El cajón útil termina hacia el 72 % de cuerda.

De ahí las tres células: añadir un alma delante (cajón D) recupera área encerrada donde el par es mayor.

## Consecuencias

- Obliga a relleno giroide ([ADR-0028](ADR-0028-relleno-giroide.md)): sin él la piel pandea y la hipótesis de sección cerrada no se cumple.
- Fija la charnela del elevón como frontera estructural, no solo aerodinámica.

## Correcciones asociadas

- **C7** — se afirmó que la evidencia del Eliminator a 360 km/h validaba la construcción impresa en general. Valida **su** material (casi con seguridad PLA); con G un 40 % menor, el PETG no hereda ese aval.
