# I-08 — Familia StuntDouble: geometría comparada

**Estado:** Abierta — fuentes primarias adquiridas, comparación base publicada  
**Alimenta:** A4 del plan de Fase 1, R3 y R4 de referencias medidas  
**No cierra:** G1 ni G2

---

# 1. Pregunta

¿Qué puede aprenderse de la comparación entre un ala de flecha invertida y dos *planks*
del mismo diseñador y de la misma familia constructiva?

La hipótesis de trabajo de A4 era tratar Nemesis, Stinger y Stormbird como un «experimento
natural controlado». La revisión de los archivos primarios muestra que esa formulación era
demasiado fuerte: cambian el perfil, la propulsión y parte de la geometría. La comparación
sigue siendo útil, pero es **cuasi-controlada** y sirve para generar priors geométricos, no
para atribuir causalidad a la flecha.

# 2. Fuentes primarias

Archivos descargados y revisados el 28 de julio de 2026:

- **Nemesis:** manual de construcción, revisión 27 de septiembre de 2025, y STL del
  diseñador. Fuente pública: [Thingiverse 6644675](https://www.thingiverse.com/thing:6644675).
- **Stinger V2:** ficha y STL del diseñador, paquete fechado 21 de junio de 2025.
  Fuente pública: [Thingiverse 6760208](https://www.thingiverse.com/thing:6760208).
- **Stormbird:** manual de construcción, revisión 18 de septiembre de 2023, y STL del
  diseñador. Fuente pública: [Thingiverse 6174038](https://www.thingiverse.com/thing:6174038).

Los valores de la tabla siguiente son los publicados por el diseñador `[M]`.

# 3. Comparación publicada `[M]`

| Modelo | Planta / propulsión | b | Longitud | Perfil | S | AUW | Carga alar |
|---|---|---:|---:|---|---:|---:|---:|
| **Nemesis** | Flecha invertida / dos tractores | 1200 mm | 600 mm | PW51 | 22 dm² | 1100–1400 g | 50–64 g/dm² |
| **Stinger V2** | *Plank* / dos tractores | 1300 mm | 630 mm | PW75 | 26 dm² | 1200–1600 g | 46–62 g/dm² |
| **Stormbird** | *Plank* / un impulsor | 1100 mm | 580 mm | PW75 | 20 dm² | 900–1200 g | 45–60 g/dm² |

## 3.1 Magnitudes derivadas `[D]`

Calculadas directamente de `AR = b²/S` y `c_media = S/b`:

| Modelo | AR `[D]` | Cuerda media geométrica `[D]` |
|---|---:|---:|
| Nemesis | 6,55 | 183 mm |
| Stinger V2 | 6,50 | 200 mm |
| Stormbird | 6,05 | 182 mm |

**Resultado útil:** los tres diseños convergen en AR ≈ 6,0–6,6 `[D]`, pese a sus plantas
distintas. Es evidencia de práctica de diseño compatible con [ADR-0004](../decisiones/ADR-0004-alargamiento.md),
pero no la valida por sí sola: los tres ejemplares proceden del mismo diseñador.

# 4. Qué está y qué no está controlado

| Variable | Nemesis vs. Stinger | Nemesis vs. Stormbird |
|---|---|---|
| Diseñador y familia de fabricación | Igual | Igual |
| Orden de AR y carga alar | Comparable | Comparable |
| Número y posición de motores | Igual: dos tractores | Distinto: dos tractores / un impulsor |
| Perfil | **Distinto: PW51 / PW75** | **Distinto: PW51 / PW75** |
| Envergadura y superficie | Distintas | Distintas |
| Fuselaje | No demostrado idéntico | Idéntico según el manual de Nemesis `[M]` |

Por tanto:

- **Sí** se pueden comparar decisiones geométricas recurrentes de la familia.
- **No** se puede atribuir a la flecha una diferencia de eficiencia, estabilidad o pérdida:
  el cambio PW51↔PW75 es un confusor aerodinámico de primer orden.
- **No** se puede usar Stormbird para aislar el efecto de la flecha sobre propulsión:
  cambia de doble tractor a impulsor único.

# 5. Datos de trim publicados `[M]`

| Modelo | Ajuste publicado |
|---|---|
| Nemesis | 2 mm de reflex de elevón hacia arriba |
| Stormbird | 1–2 mm de reflex de elevón hacia arriba |

Ambos necesitan reflex de mando. La cifra está en milímetros, no en grados, y todavía falta
medir la cuerda local del elevón para convertirla a ángulo `[D]`. Este dato **no permite**
concluir que la flecha invertida cierre el trim sin coste; refuerza que A4 debe medir perfil,
torsión construida y geometría de elevón antes de alimentar R-TORSION.

# 6. Límites de transferencia

- Los STL son geometría nominal del diseñador, no medición de una pieza impresa.
- Una misma familia de autor no constituye replicación independiente.
- Las prestaciones cualitativas del manual no sustituyen polares ni *blackbox*.
- PW51 y PW75 impiden aislar el efecto de la planta.
- El reflex publicado es un ajuste de vuelo; sin cuerda de elevón no es un ángulo comparable.

# 7. Siguiente extracción

1. Reconstruir para cada modelo la planta ensamblada: cuerdas, estrechamiento y flecha de c/4.
2. Cortar las mallas en estaciones equivalentes y medir `t/c`.
3. Medir la distribución de torsión y la cuerda de elevón.
4. Convertir el reflex lineal publicado a ángulo.
5. Solo entonces comparar la ventana de torsión de I-07 con hardware publicado.

Hasta completar estos pasos, **A4 queda parcial** y no congela ninguna geometría del proyecto.
