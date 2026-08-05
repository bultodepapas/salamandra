# I-07 — Punto neutro, margen estático y ventana de torsión

**Estado:** Abierta — resultado preliminar `[D]` · **Cierra parcialmente:** G8
**Alimenta:** ADR-0003 (torsión), ADR-0032 (R-NP), y el requisito de perfil de G2
**Herramienta:** [`calculo/vlm_ala_volante.py`](../calculo/vlm_ala_volante.py), [`calculo/ventana_torsion.py`](../calculo/ventana_torsion.py)

---

# 1. Método

Vortex lattice (VLM) propio, 40 paneles en envergadura con distribución coseno × 6 en cuerda, herraduras con vórtice ligado a c/4 de panel y punto de control a 3c/4. Condición de contorno linealizada.

## Validación

Ala recta AR 6, sin flecha ni torsión:

| | Calculado | Teórico | Error |
|---|---|---|---|
| CL_α | 4,274 /rad | 4,527 /rad (Helmbold) | −5,6 % |
| Punto neutro | 24,0 % CMA | 25 % CMA | −1,0 punto |

Aceptable para dimensionado preliminar. **La malla es gruesa en cuerda**; refinarla acercaría CL_α al valor teórico.

> **Corrección detectada durante la validación:** la primera versión devolvía el momento adimensionalizado sin dividir por la CMA, lo que introducía un factor de cuerda espurio en el punto neutro. El caso de validación lo destapó — un ala recta debe dar el NP en c/4, y daba ~0.

---

# 2. Punto neutro — configuración Cruise

Planta: b = 1300 mm · S = 0,282 m² · AR 6,0 · λ = 0,50 · Λ_c/4 = −20°
→ c_raíz 289 mm · c_punta 145 mm · **CMA 225 mm**

| Resultado | Valor |
|---|---|
| **Punto neutro** | **26,7 % CMA** |
| Posición absoluta | 101 mm **por delante** del c/4 de raíz |
| CL_α | 4,187 /rad |

**El NP queda por delante del borde de ataque de la raíz.** Es el comportamiento esperado de una flecha invertida pronunciada, y es la razón por la que el centrado de esta configuración no es intuitivo.

## CG objetivo

| Margen estático | x_CG (% CMA) |
|---|---|
| 6 % | 20,7 % |
| **8 %** | **18,7 %** |
| 10 % | 16,7 % |
| 12 % | 14,7 % |

---

# 3. La ventana de torsión

Condiciones: AUW 1620 g (6S1P) · 57 g/dm² · crucero 95 km/h · pérdida 45 km/h

| | Valor |
|---|---|
| CL de crucero | 0,132 |
| CL_max requerido | 0,589 |
| cl_max de sección `[M]` | 0,65 (Ananda et al., 0,55–0,70) |
| **Rendimiento del wash-in** | **Cm0 = +0,00338 por grado** |

## 3.1 Límite inferior — trim

Condición de equilibrio sin cola: `Cm0 = CL · MargenEstático`

| Margen estático | Cm0 requerido | **Solo torsión** | **Con perfil Cm0 = +0,010** |
|---|---|---|---|
| 6 % | +0,0079 | 2,34° | 0° |
| **8 %** | **+0,0106** | **3,13°** | **0,17°** |
| 10 % | +0,0132 | 3,91° | 0,95° |
| 12 % | +0,0159 | 4,69° | 1,73° |

## 3.2 Límite superior — pérdida en punta

Reparto de cl de sección en la condición de CL_max requerido:

| wash-in | Posición del cl máximo | cl raíz | cl punta | cl máx local | Margen a 0,65 |
|---|---|---|---|---|---|
| 0° | **27 % b/2** | 0,616 | 0,105 | 0,633 | +0,017 |
| 2° | 49 % b/2 | 0,586 | 0,115 | 0,628 | +0,022 |
| 3° | 56 % b/2 | 0,571 | 0,120 | 0,633 | +0,017 |
| 4° | **62 % b/2** | 0,556 | 0,125 | 0,641 | +0,009 |
| 5° | 68 % b/2 | 0,542 | 0,130 | 0,651 | **−0,001** ❌ |
| 6° | 68 % b/2 | 0,527 | 0,135 | 0,663 | −0,013 ❌ |

---

# 4. Conclusión — el resultado central de Fase 1

**La ventana existe, pero es más estrecha de lo que sugería la corrección C2.**

El hallazgo no es el límite duro de 5°, sino **cómo se desplaza el pico de carga**:

| wash-in | Pico de cl | Consecuencia |
|---|---|---|
| 0° | 27 % b/2 | La raíz entra en pérdida primero ✅ |
| 4° | 62 % b/2 | Zona de elevones ⚠️ |
| 5°+ | 68 % b/2 | Pérdida en punta ❌ |

> **El wash-in canjea trim contra la ventaja que justificó elegir la flecha invertida.**
>
> Con torsión pura, equilibrar a 10 % de margen estático exige 3,9°, y eso lleva el pico de carga al 62 % de la semienvergadura — justo donde están los elevones.

## 4.1 Requisito derivado sobre el perfil

**El perfil debe aportar la mayor parte del trim. La torsión hace el ajuste fino.**

| # | Requisito |
|---|---|
| **R-PERFIL** | **Cm0 del perfil ≥ +0,008**, preferentemente +0,010–0,015 |
| **R-TORSION** | **Wash-in ≤ 2,5°**, para mantener el pico de carga por dentro del 50 % de semienvergadura |

Esto **acota G2 con un número**: la selección de perfil deja de ser abierta.

## 4.2 La tensión que esto crea

El reflex que da Cm0 positivo **cuesta cl_max**, y el margen ya es escaso:

- Con cl_max de sección 0,65, el ala alcanza **CL_max ≈ 0,60** — un 92 %, por reparto no elíptico.
- Eso da V_pérdida = 44,5 km/h, **justo dentro** del requisito de ≤ 45.
- Si el reflex baja cl_max a 0,60, V_pérdida sube a **46,6 km/h** y el requisito se incumple.

**R-PERFIL y el requisito de velocidad de pérdida compiten directamente.** Es el conflicto que la Fase 1 tiene que resolver, y ahora está cuantificado.

---

# 5. R-NP — deriva del punto neutro en la familia modular

Manteniendo cuerda de raíz, estrechamiento y flecha:

| Config | b | S | AR | **NP (% CMA)** |
|---|---|---|---|---|
| Sport | 1100 mm | 0,238 m² | 5,07 | **26,0 %** |
| **Cruise** | 1300 mm | 0,282 m² | 6,00 | **26,7 %** |
| Range | 1600 mm | 0,347 m² | 7,38 | **27,6 %** |

**Dispersión total: 1,6 puntos de CMA.** Mucho menor de lo temido.

## Compensación con flecha

| Config | Flecha | NP |
|---|---|---|
| 1100 mm | −24° | 26,8 % |
| 1300 mm | −20° | 26,7 % |
| 1600 mm | −18° | 27,1 % |

**Un ajuste de ±2–4° de flecha alinea los tres paneles dentro de 0,5 % de CMA.**

> **R-NP es fácil de cumplir.** No obliga a rediseñar cada panel: basta ajustar la flecha, que además es un parámetro libre en cada juego. Es la mejor noticia de este análisis para la arquitectura modular.

---

# 6. Limitaciones declaradas

⚠️ Todo lo anterior es `[D]` sobre un modelo lineal no viscoso. Antes de congelar geometría:

| Limitación | Efecto probable |
|---|---|
| **Sin viscosidad** | El VLM no predice pérdida. El criterio de cl_max es un indicador, no una predicción |
| **cl_max supuesto constante en envergadura** | **Optimista.** La punta tiene la mitad de cuerda → la mitad de Re → **menor cl_max real** (ver [I-01](I-01-alargamiento-reynolds.md)). **El margen de pérdida en punta es peor que el calculado** |
| Sin cuerpo central | El fuselaje aporta sustentación y desplaza el NP hacia delante |
| Malla gruesa en cuerda | CL_α un 5,6 % bajo |
| Cm0 del perfil supuesto | Debe venir de G2 con polares calibradas |
| Sin efectos de flecha en cl_max | La flecha invertida modifica el reparto real de pérdida |

**La limitación de cl_max variable con Re es la más grave** y actúa en la dirección peligrosa: agrava el límite superior de la ventana y refuerza la conclusión de que hay que apoyarse en el perfil, no en la torsión.

---

# 7. Qué queda por hacer

1. **Verificar el NP con un segundo método independiente** (C2 del plan de Fase 1). Dos métodos que no coinciden = error en uno.
2. **Cerrar G2** con polares calibradas, para tener Cm0 y cl_max reales del perfil candidato.
3. **Repetir con cl_max variable en envergadura**, función del Re local.
4. **Incorporar el cuerpo central** cuando exista geometría.
5. **Verificar autoridad de elevón** (C6 del plan) — sigue sin hacerse.
