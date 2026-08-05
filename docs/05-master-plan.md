# Plan maestro — hoja de ruta hasta el primer prototipo

**Revisión 1.0** · 28 julio 2026 · Fase 1 en curso

Este documento **no sustituye** a [`03-plan-fase1.md`](03-plan-fase1.md), que sigue siendo el detalle operativo de Fase 1. Este documento es la capa de orquestación: **secuencia las fases 1→6 de la tabla de estado del [README](../README.md) hasta el primer artículo físico volando**, señala qué brecha (`brechas/README.md`) y qué ADR bloquea cada tramo, y fija dónde entra el modelado CAD (Fusion 360).

No fija fechas de calendario. El repo no tiene datos `[M]` de cuánto tarda cada tarea; poner semanas sería una cifra `[I]` disfrazada de plan. Se ordena por **dependencia**, no por duración.

---

## 0. Qué es "el primer prototipo"

**Definición de trabajo, revisable:** el primer prototipo es **el artículo #1** ya descrito en el README — configuración **Cruise (1300 mm, 6S1P)** — impreso, montado, equilibrado según [ADR-0025](../decisiones/ADR-0025-equilibrado-elevones.md), con aviónica y **pitot instalado** (requisito de [O1](00-objetivos-y-requisitos.md)), capaz de volar de forma estabilizada para ejecutar **E2, E3 y E7**.

No es "algo que imprime y vuela una vez". Es la plataforma instrumentada que **puede generar los datos `[M]` que el proyecto todavía no tiene** (G2, G4, G6, G7 en `brechas/`). Si no lleva pitot y blackbox operativos, no cuenta como prototipo del proyecto — cuenta como maqueta.

Si esta definición no es la que tenías en mente, dímelo y ajusto el resto del plan.

---

## 1. Vista global — de Fase 1 a artículo volando

| Fase | Objetivo | Puerta de salida | Bloqueada por | Detalle |
|---|---|---|---|---|
| **F1 — Geometría y estabilidad** | OML congelada, perfil elegido, NP verificado | Checklist de [`03-plan-fase1.md §4`](03-plan-fase1.md) | G1, G2, G8 | Documento dedicado |
| **F2 — Pesos y centrado** | CG real dentro de R-CG en las 4 configuraciones de batería | R-CG verificado en CAD, no solo en tabla | Necesita OML de F1 | §3 de este doc |
| **F3 — Prestaciones** | Polar completa del avión, curva de potencia, emparejamiento de hélice cerrado | D3/D4 ejecutados, objetivo O1 con vía de cierre | Parcialmente paralelo a F1 (línea D de `03-plan-fase1.md`) | §4 |
| **F4 — Cargas y estructura** | n_max/n_min con base de ráfaga declarada, V-n, GJ/EI verificados, autoridad de elevón confirmada | C6 y C7 de `03-plan-fase1.md`, G4 y G6 acotadas | Necesita CG de F2 y polar de F3 | §5 |
| **F5 — Sistemas y propulsión** | Bahía final, cadena de instrumentación (pitot+blackbox) operativa, firmware configurado | D1/D2 completados, G9 resuelto | Necesita estructura de F4 | §6 |
| **F6 — Fabricación y publicación** | Artículo #1 impreso, montado, equilibrado, volando | Primer vuelo estabilizado con datos de blackbox válidos | Necesita F2–F5 cerradas | §7 |

Fase 0 (pliego) está cerrada. Este plan cubre F1→F6; more allá de F6 empieza el programa de ensayos completo (E2, E3, E7 a fondo), que ya vive en `ensayos/README.md` y no se repite aquí.

---

## 2. Por qué el orden importa — el modo de fallo nº 1

`CLAUDE.md` documenta el error más caro del proyecto hasta ahora: dimensionar estructura y elevones **sin haber definido cargas ni verificado autoridad de mando**. Este plan existe para que no se repita:

```
F1 (geometría, NP)
  └─► F2 (CG real)          ← necesita geometría para calcular masas por componente
        └─► F3 (polar, potencia)   ← paralelizable con F1/F2 vía línea D, no depende de ellas
              └─► F4 (cargas, GJ/EI, autoridad de elevón)   ← necesita CG (F2) y CL de crucero (F3)
                    └─► F5 (bahía final, instrumentación)    ← necesita estructura cerrada (F4)
                          └─► F6 (fabricación, montaje, primer vuelo)
```

**F3 (línea D de propulsión) puede y debe empezar ya**, en paralelo — no depende de la geometría del ala nueva (`03-plan-fase1.md §3.D`). Todo lo demás es secuencial porque cada fase consume la salida verificada de la anterior, no su estimación.

---

## 3. F2 — Pesos y centrado

| # | Tarea | Cierra | Entrada necesaria |
|---|---|---|---|
| P1 | Modelo de masas por componente (cáscara, carbono, servos, cableado, aviónica) | Base para CG real | OML congelada (F1) |
| P2 | Modelo CAD paramétrico del CORE-1 y PANEL-1300 con densidades por material | Sustituye la tabla de masas estimada por geometría real | **Fusion 360** — ver §8 |
| P3 | Verificar R-CG: CG dentro de ±5 mm en 4S1P, 4S2P, 6S1P, 6S2P | R-CG (docs/00, §3.3) | P1, P2 |
| P4 | Si P3 falla: rediseñar bahía / mover CORE respecto al NP | C4 de `03-plan-fase1.md` | P3 |

**Riesgo conocido:** `03-plan-fase1.md` ya marca "R-CG no se cumple con 6S2P" como probabilidad **Alta** y lo da por asumido — 6S2P queda fuera de envolvente de crucero, documentado, no hay que redescubrirlo.

---

## 4. F3 — Prestaciones y cadena propulsiva

Esto es la línea D de `03-plan-fase1.md` llevada a cierre. Se repite aquí solo la secuencia, el detalle vive allí:

| # | Tarea | Nota |
|---|---|---|
| D1 | Montar pitot + blackbox + registro de corriente | Bloquea D2, D3, E2, E3, E7 |
| D2 | Validar la cadena de medida en una plataforma **que ya vuela** | No esperar al artículo #1 para descubrir que el método falla |
| D3 | Barrido de emparejamiento de hélice, 3–4 combinaciones | Contra J de UIUC |
| D4 | Tabla de emparejamiento por pack | **Salida publicable** — es la demostración de O1 |

**Esto no bloquea F1/F2.** Puede y debe adelantarse.

---

## 5. F4 — Cargas y estructura

| # | Tarea | Cierra | Depende de |
|---|---|---|---|
| S1 | Fijar n_max/n_min con base de ráfaga declarada (hoy `[E]`, dominado por ráfaga — docs/00 §3.1) | Precondición de todo lo demás | — |
| S2 | V-n diagram con V_NE 160 km/h (artículo #1) | Envolvente de carga | S1 |
| S3 | Verificar GJ/EI real de la sección (cajón D + célula central + charnela) contra ADR-0002/0015 | G4 | S1, geometría de F1, **Fusion 360** para geometría de sección (§8) |
| S4 | Factor de flecha para divergencia sobre la relación EI/GJ real, no literatura genérica | **G6** — eslabón más débil declarado | S3 |
| S5 | Verificar autoridad de elevón en toda la envolvente, incluida ráfaga y CG extremo | **C6 — nunca se había hecho**, ver `03-plan-fase1.md` | S2, CG de F2 |
| S6 | Rigidez de charnela TPU (ω_β) | Entra en análisis de flutter (G7) | S3 |
| S7 | Verificación de flutter con Southwell si hay datos de vuelo previos, si no, análisis preliminar | G7 | S3, S6 |

⚠️ **S5 es la tarea que corrige el modo de fallo nº1.** No se dimensiona charnela final ni se calcula su equilibrado de masa sin haber pasado S5.

---

## 6. F5 — Sistemas y propulsión (integración final)

| # | Tarea | Depende de |
|---|---|---|
| Y1 | Bahía de batería final con ajuste longitudinal (R-CG confirmado en CAD) | F2, F4 |
| Y2 | Instalación de pitot, blackbox, GPS/magnetómetro fuera del camino de corriente de raíz (docs/00 §3.5) | D1 |
| Y3 | Configuración INAV 9.1+ / ArduPlane | — |
| Y4 | **Resolver G9** (porpoising) — ajuste de PID de altitud/cabeceo antes de volar en modos automáticos | Precedente del Peregrine (brechas/README) |
| Y5 | Varillaje de elevón sin holgura, doble accionamiento (ADR-0026) | F4 (autoridad verificada) |

**Y4 es prerrequisito explícito de E7** (ya declarado en `ensayos/README.md`). No es opcional para el programa de ensayos, aunque no impide el primer vuelo no instrumentado.

---

## 7. F6 — Fabricación y publicación (llegar al artículo #1)

| # | Tarea | ADR / referencia |
|---|---|---|
| M1 | Segmentación para bandeja de impresión: 3 segmentos por semiala, 45° | ADR-0024 |
| M2 | Impresión: 2 perímetros (0,9 mm), relleno giroide 5 % | ADR-0028 |
| M3 | Juntas: espiga + adhesivo PETG específico, área ≥ 3× sección de piel | ADR-0023 |
| M4 | Pasador de carbono en juntas | ADR-0031 |
| M5 | Montaje completo, verificación de masa real contra modelo de F2 | Cierra P2 con dato `[M]` |
| M6 | **Equilibrado de masa de elevones** — obligatorio antes de volar | ADR-0025 |
| M7 | Primer vuelo — estabilizado, sin condiciones automáticas hasta cerrar G9 | Y4 |
| M8 | Publicación de la configuración fabricada (planos, ajustes reales vs. diseño) | Coherente con "fundamento publicado" (O6) |

**M7 es el primer prototipo según la definición de §0.** A partir de aquí arranca el programa de ensayos (E2, E3, E5, E7) documentado en `ensayos/README.md`.

---

## 8. Fusion 360 — dónde entra y con qué reglas

### 8.1 Estado de la herramienta

Instalado en esta sesión: add-in **`fusion360-mcp-server`** (faust-machines, versión Beta, 84 tools) copiado a la carpeta de Add-Ins de Fusion 360 y registrado como servidor MCP de este proyecto (`claude mcp add fusion360`). Arquitectura: cliente MCP ↔ servidor Python (stdio) ↔ TCP `localhost:9876` ↔ add-in dentro de Fusion (hilo principal).

**Pendiente de tu lado:** activar el add-in dentro de Fusion (Shift+S → Add-Ins → Fusion360MCP → Run) cuando quieras que empiece a usarse. No hace falta tenerlo corriendo hasta que el plan llegue a una tarea que lo necesite (ver abajo) — no es necesario para F1, que sigue siendo cálculo puro (VLM, XFOIL calibrado).

### 8.2 Cuándo entra en el flujo — no antes de tiempo

El README ya lo dice: `geometria/`, `stl/`, `cad/` son **salidas de Fase 1 en adelante**. Fusion 360 no tiene tarea en F1: F1 es geometría paramétrica en papel/script (planta, perfil, torsión) validada por VLM propio, no un sólido 3D. Meter CAD antes de congelar la OML sería optimizar geometría de detalle sin puerta cerrada — exactamente lo que `CLAUDE.md` prohíbe ("No saltar de fase").

| Fase | Uso concreto de Fusion 360 MCP | Por qué ahí y no antes |
|---|---|---|
| **Cierre de F1** | Construir el sólido paramétrico CORE-1 + PANEL-1300-cruise a partir de la planta ya congelada (perfil, cuerdas, flecha Λ_c/4, torsión) | Materializa una decisión ya tomada; no decide nada nuevo |
| **F2 (P2)** | Mass properties del ensamblaje con densidades por material, para CG real y verificación de R-CG | Sustituye la estimación manual de masas por geometría real |
| **F4 (S3)** | Geometría de sección real (cajón D, célula central, charnela) para comprobar encaje físico del tubo de carbono y espesores de pared antes de calcular GJ/EI | El cálculo de G4/G6 necesita la sección real, no un supuesto |
| **F6 (M1)** | Segmentación para bandeja de impresión, orientación a 45°, export STL/STEP final por segmento | Es literalmente para lo que sirve el CAD al final del proceso |

### 8.3 Regla de confianza aplicada al CAD — no se salta la convención del repo

Este es el punto que más fácil se pasa por alto con una herramienta nueva: **una cifra que sale de Fusion no es automáticamente `[M]`.**

- Masa, CG, volumen o momento de inercia calculados sobre el modelo paramétrico son **`[D]`** — derivados de un modelo que a su vez asume densidades de material declaradas y una geometría todavía no impresa.
- Solo se convierten en `[M]` cuando se **miden sobre la pieza física** (báscula, balancín de CG) — igual que ya se hizo con el t/c del Peregrine (G1).
- El add-in es de terceros y está en fase **Beta** — no es fuente de verdad geométrica. Cualquier salida crítica para una decisión irreversible (p. ej. GJ estructural que alimenta S4) **se contrasta con el cálculo analítico propio** del repo, no se sustituye por él. Es la misma regla que ya aplica `03-plan-fase1.md` (C2: "dos métodos que no coinciden = error en uno") — aquí el segundo método es CAD vs. analítico, no VLM vs. VLM.
- Si el add-in devuelve un número y no hay cómo etiquetarlo todavía, **no se escribe** (regla dura de `CLAUDE.md`) hasta decidir la etiqueta.

### 8.4 Riesgo declarado

El servidor es un proyecto Beta de terceros, no de Autodesk. Si se abandona o rompe con una versión nueva de Fusion, el modelo paramétrico debe seguir reconstruible manualmente desde los parámetros documentados en `docs/04-convenciones.md` — el CAD es una representación de las decisiones, no su registro. El registro sigue siendo `decisiones/` e `investigacion/`.

---

## 9. Puertas de salida — checklist consolidado

- [ ] **F1** — checklist completo de `03-plan-fase1.md §4`
- [ ] **F2** — R-CG verificado en CAD para 4S1P, 4S2P, 6S1P, 6S2P
- [ ] **F3** — D3/D4 completados, tabla de emparejamiento publicada
- [ ] **F4** — n_max/n_min fijados, GJ/EI verificado en sección real, autoridad de elevón confirmada (S5), factor de flecha de G6 calculado sobre la sección real
- [ ] **F5** — cadena de instrumentación operativa y validada en plataforma existente (D2), G9 resuelto
- [ ] **F6** — artículo #1 montado, equilibrado, primer vuelo estabilizado con datos de blackbox válidos

## 10. Qué no cubre este plan

- No fija fechas de calendario — el repo no tiene datos `[M]` para estimarlas.
- No prescribe motor ni batería — ver [ADR-0033](../decisiones/ADR-0033-electronica-fuera.md).
- No sustituye ninguna ADR ni línea de investigación existente — solo las secuencia.
- No autoriza saltar F1: mientras G1/G2/G8 sigan abiertas, F2 en adelante no tiene entrada válida.
