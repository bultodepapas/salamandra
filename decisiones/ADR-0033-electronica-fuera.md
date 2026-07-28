# ADR-0033 — Motor y batería fuera del diseño

**Estado:** ✅ Vigente · **Fecha:** 2026-07-28 · **Confianza:** Decidida

## Contexto

Un proyecto abierto puede prescribir una lista de materiales cerrada o dejar la electrónica abierta. La primera opción da resultados reproducibles; la segunda da adopción.

## Decisión

**El proyecto diseña el airframe y publica recomendaciones. No prescribe motor ni batería.**

## Fundamento

- **El KV óptimo depende del pack.** Con 4S y 6S el punto de operación del motor cambia. Prescribir un motor obligaría a prescribir una batería, y eso rompe el objetivo O2 (flexibilidad 4S–6S).
- **La aportación del proyecto es el emparejamiento, no la pieza.** El valor de [I-03](../investigacion/I-03-cadena-propulsiva.md) es la **tabla de emparejamiento hélice–pack–velocidad**, no una recomendación única.
- La adopción de un proyecto abierto sube cuando la gente puede usar lo que ya tiene.

## Qué sí publica el proyecto

| Salida | Contenido |
|---|---|
| Tabla de emparejamiento | Hélice (D×P) contra pack y velocidad de crucero, con J y η previstos |
| Configuraciones sugeridas | Range / Cruise / Sport con motor y batería de referencia |
| Restricciones duras | Volumen de bahía, rango de masa admisible, límites de corriente |
| Requisitos de aviónica | Pitot obligatorio, blackbox, GPS y magnetómetro fuera del camino de corriente |

## Consecuencias

- El balance de masas se publica como **rango**, no como valor único.
- R-CG (bahía con ajuste longitudinal) pasa de deseable a **obligatorio**: sin él, la libertad de batería rompe el centrado.
- Los datos de ensayo de contribuyentes deben declarar su configuración completa para ser comparables.
