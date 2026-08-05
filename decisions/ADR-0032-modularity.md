# ADR-0032 — Arquitectura modular CORE + PANEL

**Estado:** ✅ Vigente · **Fecha:** 2026-07-28 · **Confianza:** Alta · **Reversible:** No

## Contexto

El proyecto debe soportar distintos usos (alcance, crucero, sport) y distintas baterías (4S–6S) sin rediseñar el avión. La vía natural es modularizar. **En un avión sin cola esa vía tiene una trampa.**

## La trampa

En un avión convencional cambias alas y la cola sigue mandando la estabilidad. **Aquí el ala *es* la estabilidad.** Un panel más largo cambia alargamiento, CMA y **posición del punto neutro**. Un perfil distinto cambia el C_m0 y con él el trim.

**Consecuencia: no se pueden ofrecer paneles arbitrarios.** Un juego que desplace el punto neutro 15 mm convierte un margen estático del 8 % en 15 % — o en negativo.

## Decisión

**Módulo central estándar (CORE) + paneles intercambiables (PANEL)**, con dos requisitos derivados obligatorios.

```
CORE-1          Muñones de ala hasta el ~30 % de semienvergadura,
                bahía de batería con ajuste longitudinal, aviónica, bancada.
                Dimensionado para el panel más exigente.

PANEL-xxxx-y    xxxx = envergadura total resultante · y = familia de perfil
```

## R-NP — punto neutro común de familia

**Cada juego de paneles se diseña contra un punto neutro objetivo común.** Los paneles largos compensan con flecha o torsión distinta para devolver el NP a la banda.

No hay libertad de panel: hay un **catálogo validado que comparte centrado**.

## R-JUNTA — rigidez de la interfaz

La junta es un **muelle torsional en serie** con el ala:

    1/k_ef = 1/k_ala + 1/k_junta

| Rigidez de junta | GJ efectivo | Penalización en V_div |
|---|---|---|
| Igual que la sección | 50 % | −29 % ❌ |
| 3× | 75 % | −13 % ⚠️ |
| **5×** | **83 %** | **−9 %** ✅ |

**Requisito: rigidez torsional de junta ≥ 5× la de la sección adyacente.**

Dos consecuencias de diseño:

1. **La junta no va en la raíz** — es donde el par es máximo. El CORE lleva muñones hasta el ~30 % de semienvergadura, donde el par ha caído a la mitad. Es lo que hacen los veleros modulares, y por esta razón.
2. **Dos pasadores, no uno.** Un tubo único transmite flexión pero deja la torsión al ajuste del manguito. Dos pasadores separados transmiten el par **como par de fuerzas**, con el brazo entrando lineal: tubo principal + pasador antirrotación 60–80 mm por detrás.

## Consecuencias

- El CORE va **sobredimensionado** para el panel corto. Es el precio, y es aceptable: es la parte que no se reimprime.
- La modularidad es también la **estrategia de iteración del proyecto**: si un panel sale blando o mal centrado, se reimprime el panel y el CORE sobrevive.
- Obliga a publicar **configuraciones validadas**, no piezas sueltas.

## Configuraciones publicadas

| Config | Paneles | Batería sugerida | Uso |
|---|---|---|---|
| Range | 1600 | 4S2P Li-Ion 21700 | Alcance máximo |
| **Cruise** | 1300 | 6S1P Li-Ion 21700 | **Artículo #1** |
| Sport | 1100 | 6S LiPo | Vuelo rápido |
