# Registro de brechas

**Lo que no sabemos.** Una brecha es una incógnita que impide o degrada una decisión.

Es tan importante como el registro de decisiones: la regla del proyecto es que **ningún dato `[E]` o `[I]` sostiene una decisión irreversible sin verificación previa**, y esta tabla es donde se lleva la cuenta.

| # | Brecha | Impacto | Estado | Cierra con |
|---|---|---|---|---|
| **G1** | Geometría de referencia: superficie, perfil, torsión | Todos los cálculos dependen de S ≈ 0,282 m² `[E]` | 🔄 **Parcial** — t/c medido `[M]`, falta planta | E1 |
| **G2** | Sin polares medidas de reflexados a Re 3–5×10⁵ | Bloquea selección de perfil | 🔄 **Parcial** — XFOIL acotado con E387; falta cribar y medir reflexados | I-06, E2 |
| **G3** | Reparto de C_D0 por componente | Impide priorizar reducción de parásita | ⬜ Abierta | E2 |
| **G4** | Rigidez torsional real | ADR-0002 sin verificar | 🔄 `[E]` ±35 %, anclada a referencia medida | E5, E7 |
| **G5** | Efecto de estela de hélice sobre perfil delgado a Re 4×10⁵ | ADR-0006 en disputa | ⬜ Abierta | Ensayo comparativo en vuelo |
| **G6** | **Factor de flecha para divergencia** | **Eslabón más débil del cálculo estructural** | ⬜ Abierta | **E7** |
| **G7** | Flutter | Sin verificar. Aparición súbita, sin aviso | ⬜ Abierta | E5 |
| **G8** | Punto neutro y margen estático | Bloquea Fase 1 | 🔄 **Parcial** — NP = 26,7 % CMA `[D]` por VLM propio. Falta verificación independiente | I-07, C2 del plan |
| **G9** | Acoplamiento del lazo de altitud con cabeceo (*porpoising*) | **Amenaza la validez de E7** | ⬜ Abierta | Ajuste de PID antes de ensayar |

---

## Detalle de las críticas

### G1 — geometría de referencia

Ningún fabricante publica superficie alar, perfil ni torsión.

**Cerrado parcialmente:** medición sobre el archivo del Peregrine 840 mm da **t/c = 13,5 %** `[M]`. Falta planta completa: flecha del c/4, estrechamiento y **distribución de torsión** — este último es el que valida o tumba ADR-0003.

Sensibilidad: un ±13 % en S produce ±13 % en alargamiento y en carga alar.

### G6 — factor de flecha

El cálculo de divergencia usa un factor de reducción de **0,50–0,70** para −20° de flecha, tomado de literatura general y **no calculado sobre la relación EI/GJ de esta sección**. Es el término que domina la incertidumbre `[E]` ±35 %.

### G8 — punto neutro y margen estático

**Cerrada parcialmente.** VLM propio da **NP = 26,7 % CMA** `[D]`, validado contra caso analítico (ala recta AR 6: 24,0 % calculado contra 25 % teórico).

CG objetivo: **18,7 % CMA** para 8 % de margen estático.

**Falta:** verificación con un segundo método independiente, incorporar el cuerpo central, y **verificar la autoridad de elevón** — que sigue sin hacerse.

Ver [I-07](../investigacion/I-07-punto-neutro-ventana-torsion.md).

### G2 — ahora acotada con números

El análisis de I-07 convierte la selección de perfil de problema abierto en problema acotado:

| Requisito | Valor |
|---|---|
| **R-PERFIL** | Cm0 ≥ +0,008, preferentemente +0,010–0,015 |
| **R-TORSION** | Wash-in ≤ 2,5° |

Y destapa el conflicto central: **el reflex que da Cm0 positivo cuesta cl_max**, y con cl_max 0,65 la velocidad de pérdida sale a 44,5 km/h, justo dentro del requisito de 45. Si el reflex baja cl_max a 0,60, el requisito se incumple.

[I-06](../investigacion/I-06-perfiles-reflexados.md) acota además el modelo de transición:
la calibración E387 (C) da una banda Ncrit 10–12 `[D]`, no un valor único. En
Re ≈ 3–5×10⁵, Ncrit 12 minimiza el desacuerdo de la rejilla `[D]`, pero falta validarlo
contra un segundo modelo físico y cribar los perfiles reflexados. **G2 no está cerrada.**

### G9 — porpoising

La documentación del Peregrine reporta oscilación de altitud en modos RTH / Cruise / Loiter de INAV, con ajustes correctivos publicados (P de posición Z de 30 a 15, relación cabeceo-acelerador de 10 a 5, cabeceo nivelado de 0 a 3°).

**E7 depende de vuelo estabilizado en Cruise.** Si el avión oscila, la deflexión de trim contra q es ruido.

---

## Brechas cerradas

Ninguna todavía. Se moverán aquí con la referencia del ensayo que las cerró y el dato resultante.
