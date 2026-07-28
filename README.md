# Ala volante FPV de flecha invertida — plataforma modular impresa en 3D

Ala volante de flecha invertida impresa en PETG, **modular y configurable**: módulo central estándar y paneles de ala intercambiables. Vuelo FPV de crucero eficiente, con electrónica a elección del constructor.

**Revisión 1.4** · 28 julio 2026 · **Fase 0 cerrada · Fase 1 en curso**

---

## Qué es este proyecto

Existen decenas de alas impresas de código abierto. Casi ninguna publica **por qué** tiene la geometría que tiene.

La aportación de este proyecto no es el STL: es que **cada decisión lleva su fundamento, su fuente y su nivel de confianza**, y que **los errores cometidos por el camino quedan registrados en vez de borrados**.

Es un repositorio **evolutivo**. Ahora mismo define las bases; la geometría vendrá después. Lo que no cambia es el criterio: **ninguna decisión sin fundamento declarado.**

## Objetivo medible

| | Valor |
|---|---|
| Referencia de mercado | **TBS Mojito** — 1,40 Wh/km medido, 189,95 USD |
| **Objetivo** | **≤ 1,15 Wh/km** a 95 km/h |
| De dónde sale | **Emparejamiento de hélice**, +20 % demostrado sobre datos UIUC `[D]` |

El análisis de partida demostró que el Mojito **no es energéticamente eficiente** — gasta 0,74 Wh/(km·kg), lo mismo que un ala de espuma de 40 USD; su logro es sostenerlo a 2–3× la velocidad. La eficiencia de este proyecto no viene de aerodinámica optimista: viene de la cadena propulsiva, que es donde los datos dicen que está el hueco.

**Es falsable.** Se mide con [E2](ensayos/) y [E3](ensayos/).

---

## Cómo navegar este repositorio

| Carpeta | Qué contiene |
|---|---|
| [`docs/`](docs/) | Pliego, estado, plan de fase, convenciones, [plan maestro hasta el primer prototipo](docs/05-plan-maestro.md) |
| [`decisiones/`](decisiones/) | **Un archivo por decisión (ADR)**: contexto, alternativas, consecuencias |
| [`investigacion/`](investigacion/) | **Líneas de investigación**: qué se buscó, qué se encontró, qué fuentes |
| [`brechas/`](brechas/) | Registro de lo que **no** sabemos y cómo se cierra |
| [`ensayos/`](ensayos/) | Programa experimental y datos |
| [`calculo/`](calculo/) | Scripts de análisis, con casos de validación |
| `geometria/` `stl/` `cad/` | Salidas de Fase 1 en adelante |

**Empieza por:** [`docs/00-objetivos-y-requisitos.md`](docs/00-objetivos-y-requisitos.md) → [`decisiones/README.md`](decisiones/README.md) → [`brechas/README.md`](brechas/README.md)

---

## Convención de confianza

Es la regla central del proyecto. Toda afirmación cuantitativa lleva etiqueta:

| Etiqueta | Significado |
|---|---|
| `[M]` | Medido y publicado por una fuente primaria |
| `[D]` | Derivado por cálculo a partir de datos `[M]` |
| `[E]` | Estimado sobre supuestos declarados |
| `[I]` | Inferencia razonada, no verificada |

> **Regla dura:** ningún dato `[E]` o `[I]` sostiene una decisión irreversible sin verificación previa.
>
> **Corolario:** cuando un dato mejor tumba una conclusión, se anota en el [CHANGELOG](CHANGELOG.md) con número de corrección. Van 16.

---

## Artículo #1 — configuración Cruise

| Parámetro | Valor | Decisión |
|---|---|---|
| Envergadura | 1300 mm | [ADR-0010](decisiones/ADR-0010-rama-de-mision.md) |
| Alargamiento | 6,0 · S = 0,282 m² `[E]` | [ADR-0004](decisiones/ADR-0004-alargamiento.md) |
| **t/c** | **13,5 % raíz / 9 % punta** | [ADR-0027](decisiones/ADR-0027-espesor-relativo.md) |
| Material | **PETG convencional**, color claro | [ADR-0021](decisiones/ADR-0021-material-base.md) |
| Perímetros / relleno | 2 (0,9 mm) / **giroide 5 %** | [ADR-0028](decisiones/ADR-0028-relleno-giroide.md) |
| Sección | Tres células: cajón D + central + charnela | [ADR-0002](decisiones/ADR-0002-cascara-cerrada.md) |
| Carbono | Tubo de flexión + pasador. **No torsional** | [ADR-0015](decisiones/ADR-0015-carbono-no-torsional.md) |
| AUW (6S1P) | ~1620 g · 57 g/dm² | — |
| V_NE artículo #1 | **160 km/h** (diseño 180) | — |
| Aviónica | INAV 9.1+ o ArduPlane · **pitot obligatorio** | — |

---

## Arquitectura modular

```
CORE-1          Módulo central. Muñones hasta el ~30 % de semienvergadura,
                bahía de batería con ajuste longitudinal, aviónica, bancada.

PANEL-xxxx-y    xxxx = envergadura total · y = familia de perfil
```

| Config | Paneles | Batería sugerida | Uso | Estado |
|---|---|---|---|---|
| **Range** | 1600 | 4S2P Li-Ion 21700 | Alcance máximo | Diseño |
| **Cruise** | 1300 | 6S1P Li-Ion 21700 | **Artículo #1** | Diseño |
| **Sport** | 1100 | 6S LiPo | Vuelo rápido | Diseño |

⚠️ Ver [ADR-0032](decisiones/ADR-0032-modularidad.md): los paneles **no son arbitrarios**. Cada juego se diseña contra un punto neutro común.

---

## Estado

| Fase | Estado |
|---|---|
| 0 — Pliego | ✅ **Cerrada** |
| **1 — Geometría y estabilidad** | 🔄 En curso · ver [`docs/03-plan-fase1.md`](docs/03-plan-fase1.md) |
| 2 — Pesos y centrado | ⬜ |
| 3 — Prestaciones | ⬜ |
| 4 — Cargas y estructura | ⬜ |
| 5 — Sistemas y propulsión | ⬜ |
| 6 — Fabricación y publicación | ⬜ |

**Bloqueante actual: [G2](brechas/README.md) — selección de perfil.**

G8 (punto neutro) cerrada parcialmente: **NP = 26,7 % CMA**, CG objetivo 18,7 % CMA. Ver [I-07](investigacion/I-07-punto-neutro-ventana-torsion.md).

## Contribuir

Ver [CONTRIBUTING.md](CONTRIBUTING.md). En resumen: se aceptan contribuciones que **suban el nivel de confianza de un dato**. No se aceptan cifras sin fuente, aunque sean correctas.

## Licencia

Pendiente. Candidatas: CERN-OHL-S (hardware, copyleft fuerte) o CC BY-SA 4.0 para documentación.
