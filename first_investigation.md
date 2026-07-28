# Ala volante FPV de flecha invertida — Documento base de diseño

**Estado:** Fase de investigación preliminar cerrada. Diseño no iniciado.
**Revisión:** 1.0 — 27 julio 2026
**Alcance:** Consolidación de datos, marco analítico, decisiones tomadas y brechas abiertas.

---

## Convención de confianza

Toda afirmación cuantitativa lleva una de estas etiquetas:

| Etiqueta | Significado |
|---|---|
| **[M]** | Medido y publicado por una fuente primaria |
| **[D]** | Derivado por cálculo a partir de datos [M] |
| **[E]** | Estimado sobre supuestos declarados |
| **[I]** | Inferencia razonada, no verificada |

Ningún dato [E] o [I] debe usarse como base de una decisión irreversible sin verificación previa.

---

# 1. Objetivo y estado del problema

## 1.1 Decisión pendiente que bloquea todo lo demás

**El objetivo de diseño no está fijado.** Existen dos funciones objetivo mutuamente excluyentes:

| Rama | Métrica | Consecuencias de planta |
|---|---|---|
| **A — Crucero rápido** | Wh/km a 90–120 km/h | AR bajo (5–7), carga alar alta (55–70 g/dm²), foco en resistencia parásita |
| **B — Autonomía** | Minutos de vuelo | AR alto (8–12), carga alar baja (25–35 g/dm²), foco en resistencia inducida |

No son un compromiso continuo: divergen desde el primer trazo. Todo lo que sigue está calibrado sobre la rama A, porque es la que representan las plataformas de referencia analizadas. **Si el objetivo es B, buena parte de las decisiones de la sección 6 deben reevaluarse.**

---

# 2. Plataformas de referencia

## 2.1 TBS Mojito — datos publicados por el fabricante [M]

| Parámetro | Valor |
|---|---|
| Envergadura | 1300 mm |
| AUW | ≥ 1800 g |
| Autonomía declarada | 60 min / 100 km |
| Velocidad de crucero | 90–120 km/h |
| Velocidad máxima | > 200 km/h |
| Batería | 6S–8S; máx. 70 × 50 × 230 mm; óptima Li-Ion 8S1P 5000 mAh |
| Motor | 3220, 1000 KV |
| Hélice | 8×4.5 o 7×12 |
| Servos | 23 mm; 2 unidades (4 con aerofrenos) |
| Construcción | EPP de alta densidad, refuerzo de carbono, bordes de plástico inyectado |
| Precio (kit) | USD 189,95 |

**Del manual (rev. 2025-11-04) [M]:**

- CG: línea en relieve en la panza, ≈ 10 mm por detrás del borde de ataque. Recomendación explícita de volar con CG adelantado.
- Deflexión de elevones: cabeceo ±15 mm; alabeo 20 mm arriba / 15 mm abajo.
- ESC: 3–12S, límite de corriente 204 A, avance 15°, PWM 24–48 kHz, 14 polos.
- Aerofrenos: producen momento de picado al activarse; requiere compensación.

**No publicado:** superficie alar, alargamiento, ángulo de flecha, torsión, perfil, coordenadas. El fabricante solo declara que *el perfil deriva de planeadores de dynamic soaring*.

## 2.2 TBS Mojito — datos de vuelo medidos [M]

Fuente: Noah Waldner, 3,5 meses de ensayo, cientos de baterías.

- Crucero cómodo a 70–80 km/h con ≈ 8 A en 8S.
- ≈ 50 km de recorrido con dos LiPo 4S 2300 mAh en serie.

## 2.3 Nemesis (StuntDouble) [M]

| Parámetro | Valor |
|---|---|
| Envergadura | 1200 mm |
| Configuración | Ala volante, flecha invertida, bimotor tractor |
| Perfil | PW51 |
| Construcción | Impresión 3D, archivos STL abiertos |
| Coste | Gratuito |

Pertenece a una familia de diseños del mismo autor que permite una **comparación
cuasi-controlada**: misma familia de fabricación y AR comparable, pero no la misma escala,
perfil ni propulsión. Ver corrección C19 e
[I-08](investigacion/I-08-familia-stuntdouble.md).

| Modelo | Planta | Nota |
|---|---|---|
| Interceptor V1/V2 | Flecha invertida, bimotor | Origen de la línea |
| **Eliminator** | Flecha invertida, bimotor | **Récord: 360 km/h, nov. 2025 (P. Heiniger)** |
| Nemesis | Flecha invertida, bimotor | Versión crucero FPV |
| Stinger V2 | Plank recto, bimotor, 1,3 m | Comparador sin flecha; perfil PW75 |
| Stormbird | Plank recto, 1,1 m | Comparador sin flecha; perfil PW75 e impulsor único |

---

# 3. Análisis energético

## 3.1 Validación cruzada del Mojito [D]

Dos fuentes independientes de energía específica:

| Fuente | Energía | Distancia | Wh/km |
|---|---|---|---|
| Waldner (medido) | 68,1 Wh (8S 2300 mAh LiPo) | 50 km | **1,36** |
| TBS (declarado) | 144,0 Wh (8S1P 5000 mAh Li-Ion) | 100 km | **1,44** |

**Concordancia dentro del 5 %.** La cifra oficial de TBS queda verificada de forma independiente. Se adopta **1,40 Wh/km** como valor de referencia.

*Nota de consistencia:* los dos datos de Waldner (8 A a 70–80 km/h, y 50 km con 68 Wh) solo son mutuamente compatibles si el vuelo de 50 km se realizó a velocidad considerablemente mayor que 80 km/h. Corresponden a puntos de operación distintos, no al mismo vuelo.

## 3.2 Comparativa de energía específica [D]

Normalizando por masa se elimina el efecto de tamaño:

| Plataforma | Wh/km | Masa | **Wh/(km·kg)** | Velocidad |
|---|---|---|---|---|
| Sonicmodell AR Wing 1000 | 0,78 [E] | 1,0 kg | **0,78** | ~55 km/h |
| **TBS Mojito** | 1,40 [D] | 1,9 kg | **0,74** | 100–150 km/h |
| Mini Talon | 1,20 [M] | 1,3 kg | **0,92** | 50 km/h |
| Solar Impulse 2 | 160 [D] | 2300 kg | **0,070** | 70 km/h |

### Conclusión 3.2 — El Mojito no es más eficiente, es más rápido

El Mojito consume **la misma energía por kilómetro y kilogramo** que un ala de foam de 40 USD. Su logro no es reducir el consumo específico: es **sostenerlo a dos o tres veces la velocidad**. Eso es exactamente lo que compra un perfil de linaje dynamic soaring — no mejor L/D máximo, sino conservar el L/D al extremo derecho de la polar.

**Implicación de diseño:** si la misión no requiere velocidad, la arquitectura Mojito no aporta ventaja energética alguna sobre alternativas mucho más baratas.

## 3.3 Despeje inverso del L/D [D]

De la energía específica se despeja la eficiencia aerodinámica real:

$$\frac{E/d}{W} = \frac{1}{\eta}\cdot\frac{D}{W} \quad\Longrightarrow\quad \left(\frac{L}{D}\right)_{aero} = \frac{1}{\eta}\left(\frac{L}{D}\right)_{efectivo}$$

| Plataforma | L/D efectivo | η supuesto | **L/D aerodinámico** |
|---|---|---|---|
| TBS Mojito | 3,7 | 0,50 [E] | **7,4** |
| AR Wing | 3,5 | 0,50 [E] | **7,0** |
| Mini Talon | 3,0 | 0,50 [E] | **5,9** |
| Solar Impulse 2 | 39,2 | 0,80 [E] | **49** |

**El L/D del Mojito en crucero rápido es ≈ 7,4**, muy por debajo de su L/D máximo (que ocurre a menor velocidad). El factor ~7 de diferencia contra el Solar Impulse cuantifica el castigo combinado de escala: Reynolds bajo, alargamiento bajo y cadena propulsiva mediocre.

⚠️ El valor del Solar Impulse depende de entradas gruesas (15 CV medios sobre 24 h, 70 km/h medios) y debe tomarse como orden de magnitud, no como dato. Es probablemente un límite superior.

---

# 4. Marco analítico adoptado

## 4.1 Ecuación maestra

Para propulsión eléctrica, el alcance se descompone en tres factores multiplicativos independientes:

$$R = \underbrace{\frac{E_{esp}}{g}\cdot\frac{m_{bat}}{m_{total}}}_{\text{energía}} \cdot \underbrace{\eta_{total}}_{\text{propulsión}} \cdot \underbrace{\frac{L}{D}}_{\text{aerodinámica}}$$

Duplicar cualquiera de los tres duplica el alcance. Ninguno compensa la deficiencia de otro.

## 4.2 Descomposición de resistencia — formulación obligatoria

**Esta es la decisión metodológica más importante del documento.** Spedding & McArthur (2010) demuestran que en la literatura conviven dos coeficientes distintos llamados igual:

| | Definición | Contenido |
|---|---|---|
| **e_i** (no viscoso) | $1/(1+\delta)$ | Solo desviación de la carga elíptica |
| **e_v** (Oswald) | $1/(1+\delta+k\pi AR)$ | Lo anterior **+ alargamiento + forma de la polar viscosa** |

**e_v decrece con el alargamiento por construcción algebraica**, no por física. Usarlo lleva a concluir erróneamente que subir AR es contraproducente.

**Formulación adoptada** — separar los términos y no colapsarlos nunca en un solo número:

$$C_D = \underbrace{C_d(C_l, Re)}_{\text{tabla de polar real}} + \underbrace{\frac{C_L^2}{\pi\,AR\,e_i}}_{\text{inducida}}$$

Límite de validez documentado por los autores: la polar parabólica con un único Oswald **solo es válida por encima de Re ≈ 5×10⁶**. Nuestro régimen está tres órdenes de magnitud por debajo.

## 4.3 Relación de mérito para L/D máximo

$$\left(\frac{L}{D}\right)_{max} = \frac{1}{2}\sqrt{\frac{\pi\,e\,AR}{C_{D0}}} \quad\propto\quad \sqrt{\frac{b^2}{C_f\,S_{mojada}}}$$

El L/D máximo no depende del alargamiento ni de la superficie por separado, sino de la relación **envergadura² / superficie mojada**. Agrandar el ala sin agrandar el resto mejora dos veces.

**Validación de la relación [D]:** aplicada al planeador Eta (AR 51,33; L/D 70), despeja **C_D0 = 0,0081**. Es un valor físicamente coherente para un planeador de competición de composite pulido, lo que confirma la fórmula. Un ala de foam típica está entre 0,025 y 0,035 — de tres a cuatro veces peor.

---

# 5. Hallazgos por línea de investigación

## 5.1 Línea 1 — Frontera alargamiento / Reynolds

### Datos primarios

**Spedding & McArthur (J. Aircraft 47(1), 2010)** — Eppler 387, AR 6, túnel de baja turbulencia:

| Re | k (polar 2-D) | e_v resultante | e_i |
|---|---|---|---|
| 10–20 ×10³ | 0,24 | **0,22** | 0,53–0,76 |

- A C_L = 0,4: **C_D = 0,019 a Re 60×10³ contra 0,075 a Re 10×10³** — factor ~4. [M]
- Pendiente de sustentación degradada: **C_lα ∝ Re^0,19** (2-D) y **Re^0,18** (AR 6). [M]
- Causa física identificada: **avance del punto de separación desde el borde de fuga**, incluso a ángulos de ataque pequeños. [M]

**Ananda, Sukumar & Selig (Aerosp. Sci. Tech. 42, 2015)** — 10 alas de placa plana, AR 2–5, Re 60–160×10³:

- e_v de **0,81 (AR 2) a 0,33 (AR 5)** [M] — magnitud de tipo e_v, ver §4.2.
- C_Lmax entre 0,55 y 0,70 [M].
- C_Dmin entre 0,01 y 0,02 [M].
- **Sin beneficio detectable del estrechamiento** (λ 0,5 y 0,75) a Reynolds bajo [M].
- Carmichael, citado: la burbuja de separación laminar domina en **70×10³ ≤ Re ≤ 200×10³** [M].

**Hepperle** — los perfiles reflexados, obligatorios en ala volante, **sufren más a Reynolds bajo porque el reflex agrava el gradiente de presión adverso** [M]. Castigo doble para nuestra configuración.

### Conclusión 5.1

Sí existe un alargamiento óptimo finito, pero **no por el mecanismo que se suele citar**. La cadena causal correcta es:

1. La inducida sigue cayendo como 1/(π·AR·e_i) — subir AR **sí funciona**.
2. El término viscoso k·C_L² **no depende del alargamiento** y no mejora.
3. Por tanto el beneficio de subir AR **se satura**.
4. A superficie constante, subir AR **acorta la cuerda → baja Re → sube k y sube C_D0** — y a partir de cierto punto empeora activamente.

El punto 4 es el que genera el óptimo. El punto 3 es el que lo hace plano.

⚠️ **Límite de transferencia:** los ensayos citados cubren Re 10–160×10³. Nuestro régimen de crucero es ≈ 4×10⁵. Las **magnitudes no se transfieren**; las tendencias y la metodología sí.

## 5.2 Línea 2 — Flecha invertida sin cola

### Mecanismo de equilibrio

Un ala sin cola requiere momento de cabeceo positivo. Solo hay dos vías: perfil con C_m0 positivo (reflex), o combinación de flecha y torsión. Para la flecha, las dos soluciones son **simétricas**:

| Planta | Torsión requerida | Carga en punta a sustentación nula |
|---|---|---|
| Flecha atrás | **Wash-out** (punta abajo) | Hacia abajo — resta sustentación |
| **Flecha invertida** | **Wash-in** (punta arriba) | Hacia arriba — suma sustentación |

*(Corrige la afirmación previa de que la flecha invertida depende exclusivamente del reflex del perfil.)*

### Ventaja cuantificable: resistencia de trim

Documentado en las patentes de configuración US 4.545.552 y US 4.674.709: en flecha invertida la fuerza de equilibrio actúa **hacia arriba y por delante del CG**, de modo que la sustentación total necesaria es esencialmente igual al peso. En flecha atrás, el equilibrio exige carga negativa en las puntas y el ala debe generar **más** de lo que pesa el avión.

⚠️ Son documentos de patente, no literatura revisada por pares. El argumento físico es correcto y verificable; **la magnitud del beneficio no está cuantificada por fuente independiente**.

### Ventaja secundaria: comportamiento en pérdida

El flujo transversal va de punta a raíz. **La raíz entra en pérdida primero**, y los elevones exteriores conservan efectividad al permanecer en aire de alta energía. [M, múltiples fuentes independientes]

Para un ala volante esto pesa el doble: los elevones son la totalidad del control.

### Riesgo dominante: divergencia aeroelástica

El centro aerodinámico queda **por delante** del centro de rigidez torsional. La carga produce torsión de encabritado → más ángulo de ataque → más sustentación → más torsión. Realimentación positiva hasta fallo estructural. [M]

Remedios conocidos: aumentar rigidez (penalización de peso) o **adaptación aeroelástica del laminado** (solución del X-29). [M]

**Acoplamiento peligroso identificado [I]:** la flecha invertida sin cola necesita wash-in para el trim, y la divergencia aeroelástica **también produce wash-in**. Los dos efectos se suman y el segundo crece con la presión dinámica. Consecuencia: **el estado de trim se desplaza con la velocidad**. Un ala de flecha atrás tiene el signo contrario y se auto-atenúa.

Esto explica tres características del Mojito que antes no tenían explicación: CG extremadamente adelantado, recomendación de adelantarlo aún más, y deflexiones de elevón deliberadamente cortas.

Riesgo adicional documentado: con deflexión aeroelástica suficiente, **las puntas pueden entrar en pérdida primero, anulando la ventaja principal de la flecha invertida** — precisamente cuando más se necesita. [M]

### Evidencia empírica que acota el riesgo [D]

El **Eliminator** (misma familia, flecha invertida, impreso en 3D) alcanzó 360 km/h. La presión dinámica es **13 veces** la del crucero del Mojito (6.100 Pa contra 470 Pa). Si la velocidad de divergencia estuviera cerca del envolvente operativo, se habría manifestado.

**Hipótesis explicativa [I]:** un ala impresa en 3D es una **cáscara cerrada — un cajón de torsión por construcción**. La rigidez torsional de una sección cerrada supera en órdenes de magnitud a la de espuma con varillas embebidas. Para flecha invertida, donde la rigidez torsional es el parámetro crítico, la impresión 3D es probablemente **superior** a la espuma moldeada.

Esto invierte una suposición inicial y es la conclusión de mayor consecuencia práctica del documento.

### ⚠️ Advertencia de calidad de fuentes

Existe una fuente secundaria (Grokipedia) que afirma que la flecha adelante *retrasa* la divergencia aeroelástica. **Contradice a la totalidad de fuentes primarias y revisadas por pares consultadas, incluida la documentación del programa X-29. No debe usarse.**

## 5.3 Línea 3 — Cadena propulsiva

### Datos primarios

**Brandt & Selig (AIAA 2011-1255)** — 79 hélices, 9–11 in, Re 50–100×10³ en la estación al 75 %:

- Eficiencia de pico entre **0,65 (buena) y 0,28 (mala)** — factor 2,3. [M]
- La eficiencia **mejora sistemáticamente al aumentar rpm**, por efecto Reynolds. [M]
- Caso extremo: la Master Airscrew G/F 11×4 **casi duplica** su eficiencia de pico en el rango de rpm ensayado. [M]
- Trabajos previos: hélices de modelismo dan **7,5 %–15 % menos** que hélices de 36 in con P/D similar. [M]
- Las palas muy delgadas pueden entrar en **flutter** a J alto y perder rendimiento. [M]

### Extracción propia de la base de datos UIUC [D]

Pico de eficiencia a ≈ 6000 rpm y velocidad de vuelo correspondiente:

| Hélice | P/D | η máx | J óptimo | V @6000 rpm | V @16000 rpm |
|---|---|---|---|---|---|
| APC-E 8×4 | 0,50 | 0,600 | 0,481 | 35 km/h | 94 km/h |
| APC-E 8×6 | 0,75 | 0,678 | 0,689 | 50 km/h | 134 km/h |
| **APC-E 8×8** | 1,00 | **0,731** | 0,784 | 57 km/h | 153 km/h |
| APC-E 9×6 | 0,67 | 0,683 | 0,583 | 48 km/h | 128 km/h |
| APC-E 10×7 | 0,70 | 0,705 | 0,576 | 53 km/h | 140 km/h |
| APC-Sport 8×10 | 1,25 | 0,513* | 0,596 | 44 km/h | 116 km/h |

\* Rango de medición truncado; la eficiencia seguía subiendo.

**Lecturas:**

1. **El paso domina.** De 8×4 a 8×8, mismo diámetro: +22 % de eficiencia de pico.
2. **La velocidad óptima es un producto hélice×rpm, no una propiedad de la hélice.** La misma 8×8 pica a 57 km/h a 6000 rpm y a 153 km/h a 16000 rpm.
3. **El 7×12 del Mojito carece de respaldo de datos.** Su P/D es 1,71; el máximo de la base UIUC vol. 1 ronda 1,25, y ese caso ni siquiera alcanzó su pico dentro del rango medido.

### Cierre del balance [D]

| Componente | Rango |
|---|---|
| Hélice en su J óptimo | 0,65 – 0,73 |
| Motor + ESC bien dimensionado | ≈ 0,85 |
| **Producto teórico** | **0,55 – 0,62** |
| **Valor real despejado del vuelo (§3.3)** | **≈ 0,50** |

La brecha indica que **la hélice no opera en su relación de avance óptima**. Margen recuperable: pasar de 0,50 a 0,60 son **+20 % de alcance sin modificar la aerodinámica**.

---

# 6. Decisiones de diseño

| # | Decisión | Fundamento | Confianza | Reversible |
|---|---|---|---|---|
| **D1** | Adoptar configuración **ala volante de flecha invertida** | Ventaja de trim (§5.2) + pérdida por raíz + convergencia independiente de dos diseñadores | Alta | No |
| **D2** | Estructura de **cáscara cerrada** (impresión 3D o composite moldeado). **Rechazar espuma con varillas** | La rigidez torsional gobierna la divergencia; evidencia del Eliminator a 360 km/h | Media [I] | No |
| **D3** | Torsión geométrica de tipo **wash-in**; magnitud por determinar | Requisito de equilibrio en flecha invertida (§5.2) | Alta | Parcial |
| **D4** | Alargamiento objetivo **6–8** | Óptimo plano por saturación (§5.1); penaliza acortar cuerda por debajo de Re 3×10⁵ | Media [E] | No |
| **D5** | Perfil **reflexado y delgado**; **selección diferida** hasta disponer de polares al Re de diseño | No existen polares publicadas de reflexados a Re 3–5×10⁵ | — | Sí |
| **D6** | **Monomotor propulsor** preferido sobre bimotor tractor | Re de pala mayor con hélice única grande; ala en aire limpio preserva flujo laminar | Baja [I] | Sí |
| **D7** | Hélice de **P/D ≈ 0,8–1,0**, emparejada por J a la velocidad de crucero, con rpm alta | Datos UIUC (§5.3); Re de pala sube con rpm | Alta | Sí |
| **D8** | **Rechazar la hélice 7×12** salvo validación experimental propia | P/D 1,71 fuera de todo dato publicado | Alta | Sí |
| **D9** | Usar **siempre** la descomposición de §4.2. Nunca un Oswald único | Spedding & McArthur; validez de la polar parabólica solo sobre Re 5×10⁶ | Alta | No |
| **D10** | **Fijar la rama A o B antes de trazar geometría** | §1.1 | — | **Pendiente** |

## 6.1 Notas sobre las decisiones de baja confianza

**D6 está en disputa.** El bimotor tractor tiene argumentos legítimos a favor: mayor área de disco total, control de guiñada por empuje diferencial, redundancia y equilibrado de masa contra flutter. Y la estela sobre el ala tiene signo ambiguo — puede **suprimir la burbuja de separación laminar**, que es el mecanismo que Hepperle identifica como el castigo principal de los perfiles reflexados. **No hay datos para resolverlo.** Es la pregunta abierta de mayor valor experimental.

**D2 se apoya en una inferencia**, no en una medición. Se valida con un ensayo de mesa de media hora: aplicar un par conocido en la punta y medir el ángulo de torsión, comparando ambas construcciones.

---

# 7. Brechas de datos

| # | Brecha | Impacto | Vía de cierre |
|---|---|---|---|
| **G1** | Ningún fabricante publica superficie alar, perfil ni torsión | Todos los cálculos de §3 dependen de S ≈ 0,30 m² [E] | **Medir sobre las mallas STL del Nemesis** |
| **G2** | No existen polares medidas de perfiles reflexados a Re 3–5×10⁵ | Bloquea D5 | XFOIL/XFLR5 con transición calibrada, o ensayo propio |
| **G3** | Reparto de C_D0 por componente desconocido | Impide priorizar reducción de parásita | Ensayo de planeo (§8) |
| **G4** | Rigidez torsional de ambas construcciones sin medir | D2 sin verificar | Ensayo de torsión de mesa |
| **G5** | Efecto de la estela de hélice sobre perfil delgado a Re 4×10⁵ | D6 sin resolver | Ensayo comparativo en vuelo |

## 7.1 Sensibilidad de G1

La incertidumbre en la superficie alar propaga a todo:

| S [m²] | AR | Carga alar | Cuerda media | Re @100 km/h |
|---|---|---|---|---|
| 0,26 | 6,50 | 73 g/dm² | 200 mm | 3,7×10⁵ |
| **0,30** | **5,63** | **63 g/dm²** | **231 mm** | **4,3×10⁵** |
| 0,34 | 4,97 | 56 g/dm² | 262 mm | 4,8×10⁵ |

Un ±13 % en S produce ±13 % en alargamiento y en carga alar. **Cerrar G1 es prioridad absoluta.**

---

# 8. Programa experimental propuesto

Ordenado por relación resultado/esfuerzo.

### E1 — Extracción de geometría desde mallas STL
**Esfuerzo:** bajo. **Cierra:** G1, y parcialmente G2 y la validación de D3.

Cortar secciones de la malla del Nemesis a distintas estaciones de envergadura. Obtener coordenadas de perfil, superficie, alargamiento, estrechamiento, flecha del c/4 y **distribución de torsión** — verificando si efectivamente emplea wash-in y en qué magnitud.

Repetir sobre el Stormbird o Stinger (*plank* recto, mismo autor y familia de fabricación)
para obtener una **comparación cuasi-controlada de planta**. El perfil PW51/PW75 y la
propulsión no permanecen constantes, por lo que no puede aislarse causalmente el efecto de
la flecha. Ver corrección C19 e [I-08](investigacion/I-08-familia-stuntdouble.md).

### E2 — Ensayo de planeo para polar completa
**Esfuerzo:** medio. **Cierra:** G3; alimenta las tres líneas.

Vuelos de planeo con motor parado a velocidades estabilizadas, registrando velocidad de descenso con el barómetro del controlador de vuelo. Produce la polar real del avión completo sin túnel de viento. Es el único instrumento que separa pérdidas propulsivas de pérdidas aerodinámicas.

### E3 — Barrido de emparejamiento de hélice
**Esfuerzo:** bajo. **Cierra:** brecha de D7; realiza el +20 % de §5.3.

Vuelo estabilizado a velocidad fija, registrando corriente, para 3–4 combinaciones diámetro/paso. Comparar contra el J predicho por la base UIUC.

### E4 — Ensayo de rigidez torsional
**Esfuerzo:** bajo. **Cierra:** G4, valida D2.

Par conocido aplicado en la punta, medición del ángulo de torsión, ambas construcciones. Permite estimar el margen de velocidad de divergencia.

---

# 9. Registro de correcciones

Errores cometidos durante la investigación y corregidos. Se documentan porque afectaron conclusiones intermedias.

| # | Error | Corrección | Origen |
|---|---|---|---|
| C1 | Se afirmó que el factor de Oswald se derrumba con el alargamiento por razones físicas, y que ello invalida subir AR | Es en gran parte **artefacto de definición**: e_v decrece con AR por construcción algebraica. Subir AR sí funciona; el efecto real es la **saturación** y el acoplamiento cuerda→Re | Spedding & McArthur (2010) |
| C2 | Se afirmó que la flecha invertida depende exclusivamente del C_m0 del perfil por no poder usar torsión | Puede y debe usar **wash-in**. Las dos plantas son soluciones simétricas | Literatura de equilibrio sin cola |
| C3 | Se supuso que la impresión 3D sería la opción estructuralmente débil | Es una **cáscara cerrada** = cajón de torsión. Probablemente superior a espuma para flecha invertida | Inferencia + evidencia Eliminator |
| C4 | **Error aritmético:** al despejar el L/D del Solar Impulse se multiplicó por η en vez de dividir. Se reportó L/D ≈ 31 | El valor correcto es **L/D ≈ 49**. La relación es L/D_aero = L/D_ef / η | Verificación numérica |
| C5 | Se estimó el L/D máximo del Mojito en ≈ 11 | El valor despejado de datos de vuelo reales es **≈ 7,4 en crucero rápido** — punto de operación distinto del L/D máximo | Datos Waldner |

---

# 10. Fuentes

**Revisadas por pares**

1. Spedding, G. R. & McArthur, J. — *Span Efficiencies of Wings at Low Reynolds Numbers*. Journal of Aircraft 47(1), 2010, pp. 120–128. DOI 10.2514/1.44247
2. Ananda, G. K., Sukumar, P. P. & Selig, M. S. — *Measured aerodynamic characteristics of wings at low Reynolds numbers*. Aerospace Science and Technology 42, 2015, pp. 392–406.
3. Brandt, J. B. & Selig, M. S. — *Propeller Performance Data at Low Reynolds Numbers*. 49th AIAA Aerospace Sciences Meeting, AIAA 2011-1255.

**Bases de datos**

4. UIUC Propeller Database, vols. 1–4. Brandt, Deters, Ananda, Dantsker & Selig, University of Illinois.
5. Hepperle, M. — *MH AeroTools*: burbujas de separación laminar y turbuladores.
6. aerodesign.de — base de datos de perfiles para alas volantes y sin cola.

**Documentación de fabricante**

7. Team BlackSheep — TBS Mojito, ficha de producto y manual rev. 2025-11-04.
8. StuntDouble — Nemesis y familia asociada, Thingiverse.

**Patentes** *(no revisadas por pares — usar con la reserva de §5.2)*

9. US 4.545.552 y US 4.674.709 — configuración sin cola de flecha invertida.

**Ensayo de vuelo independiente**

10. Waldner, N. — informe de ensayo del TBS Mojito, 3,5 meses.

---

# 11. Síntesis ejecutiva

1. La arquitectura **ala volante de flecha invertida está justificada** por trim y comportamiento en pérdida, no por empaquetado. Dos diseñadores independientes convergieron en ella.
2. El riesgo dominante **no es aerodinámico sino estructural**: rigidez torsional frente a divergencia aeroelástica. Eso reordena las prioridades del proyecto.
3. La plataforma de referencia **no es energéticamente eficiente** — es rápida al mismo coste energético específico que alternativas mucho más baratas. La arquitectura solo se justifica si la misión exige velocidad.
4. La **cadena propulsiva** es la palanca de mayor retorno inmediato: +20 % de alcance disponible por emparejamiento de hélice, sin tocar la aerodinámica.
5. El obstáculo transversal es la **ausencia de geometría publicada**. Los archivos abiertos del Nemesis lo resuelven: convierten el problema de simulación especulativa en medición directa.

**Acción siguiente recomendada:** ejecutar E1 (extracción de geometría) y resolver D10 (rama A o B). Ambas son prerrequisitos de cualquier trazo de diseño.
