# Registro de cambios

Continúa el registro de correcciones del proyecto. **Los errores se documentan porque afectaron a conclusiones intermedias.** El historial de errores es parte del producto: es lo que permite confiar en lo que queda en pie.

---

## [1.5] — 2026-07-28

**A4 iniciada con fuentes primarias de la familia StuntDouble.**

### Añadido
- **[I-08](investigacion/I-08-familia-stuntdouble.md)** — comparación base de Nemesis,
  Stinger V2 y Stormbird.
- **[I-06](investigacion/I-06-perfiles-reflexados.md)** y
  **`calculo/calibra_xfoil_e387.py`** — primera calibración reproducible de XFOIL contra
  la polar medida E387 (C).
- Archivos primarios de Stinger V2 y Stormbird para la reconstrucción posterior de planta,
  perfil y torsión.

### Resultados
- Los tres diseños publicados convergen en **AR = 6,05–6,55** `[D]`.
- Nemesis y Stinger conservan doble tractor y carga alar comparable, pero cambian de
  PW51 a PW75; Stormbird además cambia a impulsor único.
- Nemesis publica 2 mm de reflex y Stormbird 1–2 mm `[M]`; falta la cuerda local para
  convertir esos ajustes a ángulo.
- Ncrit 10 minimiza el desacuerdo global de `Cd(Cl)` con un factor RMS 1,208 `[D]`
  (Ncrit 11: 1,209), pero el óptimo deriva hasta Ncrit 12 en Re 3–5×10⁵. B3 debe
  usar una banda 10–12.

### Correcciones

| # | Error | Corrección |
|---|---|---|
| **C19** | A4 describía Nemesis vs. Stinger/Stormbird como una «comparación controlada» capaz de aislar el efecto de la flecha | Es una **comparación cuasi-controlada**: mismo autor, familia constructiva y AR comparable, pero perfil, tamaño y propulsión no permanecen todos constantes. Sirve como prior geométrico; no demuestra causalidad de la flecha |
| **C20** | B1 suponía que ajustar un único Ncrit permitiría «reproducir la polar medida» del E387 en todo el rango | El óptimo cambia con Reynolds: Ncrit 10–12 en la rejilla probada. Se sustituye el número único por una **banda con sensibilidad publicada** y validación contra un segundo modelo físico antes de cribar perfiles |
| **C21** | B2 todavía aceptaba `C_m0 ≥ 0 o cercano` después de que I-07 derivara R-PERFIL | Criterio re-derivado aguas abajo: **C_m0 ≥ +0,008**, preferible +0,010–0,015. El criterio antiguo podía admitir perfiles incapaces de cerrar el trim dentro de R-TORSION |

---

## [1.4] — 2026-07-28

**Primer cálculo propio de estabilidad.** G8 pasa de abierta a parcial.

### Añadido
- **`calculo/vlm_ala_volante.py`** — vortex lattice propio con caso de validación.
- **`calculo/ventana_torsion.py`** — análisis de la ventana de torsión.
- **[I-07](investigacion/I-07-punto-neutro-ventana-torsion.md)** — punto neutro, margen estático y ventana de torsión.
- **R-PERFIL** — Cm0 del perfil ≥ +0,008. Acota G2 con un número.
- **R-TORSION** — wash-in ≤ 2,5°.

### Resultados
- **Punto neutro = 26,7 % CMA**, 101 mm por delante del c/4 de raíz. CG objetivo 18,7 % CMA para 8 % de margen estático.
- **R-NP es fácil de cumplir:** la deriva del NP entre paneles de 1100 a 1600 mm es de solo **1,6 puntos de CMA**, y un ajuste de ±2–4° de flecha los alinea dentro de 0,5 %.
- **La ventana de torsión existe pero es estrecha.** Con torsión pura, equilibrar a 10 % de margen estático exige 3,9° de wash-in, y eso lleva el pico de carga al 62 % de semienvergadura — la zona de elevones. **El perfil debe llevar la mayor parte del trim.**

### Correcciones

| # | Error | Corrección |
|---|---|---|
| **C17** | La primera versión del VLM devolvía el momento adimensionalizado **sin dividir por la CMA**, introduciendo un factor de cuerda espurio en el punto neutro | Detectado por el caso de validación: un ala recta debe dar el NP en c/4 y daba ~0. **Confirma el valor de incluir siempre un caso de contraste analítico en cualquier script de cálculo** |
| **C18** | La lectura optimista de C2 sugería que el wash-in podía liberar al proyecto de usar perfil reflexado | **Parcialmente falso.** El wash-in sirve, pero **canjea trim contra la ventaja que justificó elegir la flecha invertida**: a 4° el pico de carga se desplaza de 27 % a 62 % de semienvergadura. El reflex sigue siendo necesario; la torsión queda para ajuste fino |

---

## [1.3] — 2026-07-28

Reestructuración del repositorio en formato evolutivo, pensado para contribuciones externas.

### Añadido
- **`decisiones/`** — registro ADR: una decisión por archivo, con contexto, alternativas, consecuencias y condiciones de revisión. Índice con estados.
- **`investigacion/`** — cinco líneas de investigación documentadas (I-01 a I-05), separando *el porqué* de *el qué*.
- **`brechas/`** — registro formal de G1–G9 con impacto y vía de cierre.
- **`CONTRIBUTING.md`** — flujo de contribución, orden de valor, calidad de fuentes.
- **`docs/04-convenciones.md`** — etiquetas, identificadores, símbolos y convenciones de signo.
- **D34** — ángulo de bancada como parámetro de diseño, no supuesto a cero.
- **D35** — bisagras impresas en TPU como opción base.
- **G9** — acoplamiento del lazo de altitud con cabeceo (*porpoising*). **Amenaza la validez de E7.**

### Correcciones

| # | Error | Corrección |
|---|---|---|
| **C16** | El requisito `V_pérdida ≤ 40 km/h` se derivó con AUW 1350 g (48 g/dm²) y **no se rehízo** al subir el AUW a 1620 g | Con C_Lmax 0,65 a 57 g/dm² la velocidad real es **42,7 km/h**. Llegar a 40 exigiría C_Lmax 0,74, fuera del rango medido (0,55–0,70). **Requisito relajado a ≤ 45 km/h**, justificado por precedente de Peregrine y Mojito |

---

## [1.2] — 2026-07-28

### Añadido
- **Arquitectura modular** (ADR-0032): CORE + PANEL, junta al 30 % de semienvergadura.
- **R-NP**, **R-JUNTA**, **R-CG**.
- **ADR-0033** — motor y batería fuera del diseño.
- **E7** — Southwell en vuelo.
- **G8** — punto neutro y margen estático, sin calcular. Bloquea Fase 1.
- **`docs/02-referencias-medidas.md`** — datos primarios del Peregrine 840 mm.

### Cambiado
- **ADR-0027** — t/c a **13,5 % / 9 %**, confirmado por medición sobre artículo en servicio.
- **ADR-0028** — relleno **giroide 5 %** en lugar de tercer perímetro.
- V_NE del artículo #1 rebajada a **160 km/h**.

### Anulado
- **ADR-0022 — velo de carbono ±45°.** Retirado por decisión de proyecto (objetivo O5).
- **E4** (torsión de mesa) — sustituido por anclaje a referencia medida y E7.
- **E6** — ver C13.

### Correcciones

| # | Error | Corrección |
|---|---|---|
| **C11** | Se afirmó que tubos y varillas de carbono no aportan rigidez torsional | Cierto para el caso calculado (10/8 mm), **falso como regla**. En pared delgada `J = πD³t/4`: va con el **cubo del diámetro**. Un tubo trenzado ±45° de 18 mm bien pegado sí es elemento torsional |
| **C12** | Se especificó relleno 0 %, heredado de la práctica de LW-PLA | **Erróneo para cáscara de PETG.** Bredt-Batho supone que la piel no pandea; una piel de 0,4–0,9 mm sin apoyo pandea localmente muy por debajo del límite del material. **Sin relleno, el GJ estaba sobreestimado** — el error iba en dirección contraria a la supuesta |
| **C13** | Se propuso E6, calibración inversa del modelo contra el Peregrine | **Retirado.** El Peregrine está a factor ~3 de la predicción. Un ensayo que pasa con ese margen no falsa el modelo **pero tampoco lo valida** |
| **C14** | Se sobreestimó el riesgo estructural y se comunicó con más rotundidad de la que soportaban datos `[E]` ±35 % | Con giroide y cajón D el margen es 1,5–2,0×. La alarma correspondía a una configuración sin relleno y sin cajón D que ya no era la del proyecto |
| **C15** | Se afirmó que un solo perímetro no cumple el criterio de divergencia | **Falsado por hardware volando.** El Peregrine 840 mm vuela con 1 perímetro de 0,42 mm y 4 % de giroide |

---

## [1.1] — 2026-07-28

### Resuelto
- **ADR-0010** — fijada la **rama A (crucero rápido)**, forzada por la densidad del PETG.
- Objetivo de eficiencia cuantificado: **≤ 1,15 Wh/km**.

### Cambiado
- **ADR-0004** — alargamiento apretado de 6–8 a **6,0**.
- **ADR-0005** — invertida: el perfil pasa de «delgado» a espesor mayor *(luego sustituida por ADR-0027)*.

### Añadido
ADR-0012, 0015, 0016, 0018, 0021, 0022, 0023, 0024, 0025, 0026. Brechas **G6** (factor de flecha) y **G7 (flutter, sin analizar)**.

### Superado
ADR-0011, 0013, 0014, 0017, 0019, 0020 — tras evaluar PETG, PLA, PLA+, ASA y LW-PLA.

### Correcciones

| # | Error | Corrección |
|---|---|---|
| C6 | GJ calculado con cuerda de 231 mm siendo la coherente con AR 6,0 de 217 mm | Efecto neto sobre V_div: **−3 %**. La cuerda aparece en numerador y denominador de q_D |
| C7 | Se afirmó que el Eliminator a 360 km/h validaba la construcción impresa en general | Valida **su** material, casi con seguridad PLA. Con G un 40 % menor, el PETG no hereda ese aval |
| C8 | Se afirmó que el PETG tiene mejor adhesión de capas que el PLA | **Falso.** Retención en Z: PLA 55 %, PETG 46 %, ASA 29 %. El PETG gana en tenacidad, no en adhesión |
| C9 | Se afirmó que el PETG no se puede pegar | Demasiado categórico. Existen 3D-Gloop PETG, DCM (restringido en UE) y epoxi de 30 min |
| C10 | Masa de cáscara estimada en 450–500 g | Recuento por área mojada: **550–650 g** |

---

## [1.0] — 2026-07-27

Investigación preliminar cerrada. Consolidación de datos, marco analítico, decisiones ADR-0001 a 0010 y brechas G1–G5.

### Correcciones

| # | Error | Corrección |
|---|---|---|
| C1 | Se afirmó que el factor de Oswald se derrumba con el alargamiento por razones físicas | Es en gran parte **artefacto de definición**: e_v decrece con AR por construcción algebraica. Subir AR sí funciona; el efecto real es la saturación y el acoplamiento cuerda→Re |
| C2 | Se afirmó que la flecha invertida depende exclusivamente del C_m0 del perfil | **Puede y debe usar wash-in.** Las dos plantas son soluciones simétricas. Abre la puerta a perfiles poco reflexados |
| C3 | Se supuso que la impresión 3D sería la opción estructuralmente débil | Es una cáscara cerrada = cajón de torsión |
| C4 | Error aritmético al despejar el L/D del Solar Impulse | El valor correcto es L/D ≈ 49, no 31 |
| C5 | Se estimó el L/D máximo del Mojito en ≈ 11 | El valor despejado de datos de vuelo reales es **≈ 7,4 en crucero rápido** |
