# Plan de Fase 1 — Geometría y estabilidad

**Revisión 1.1** · 28 julio 2026
Cierra G1, G2 y G8. **Puerta de salida: OML congelada y margen estático verificado.**

---

# 1. Por qué esto no es una secuencia

La tentación es hacer perfil → planta → punto neutro → CG → torsión. **No funciona así.** Los cuatro son un único problema acoplado:

- El **punto neutro** depende de planta *y* de perfil.
- El **CG** depende de dónde quepa la batería, que depende del espesor, que depende del perfil.
- La **torsión** debe cerrar el equilibrio al CL de diseño, que depende del margen estático.
- El **reflex** y la **torsión** son **sustitutos**: los dos aportan el momento de cabeceo positivo.

Fase 1 es una iteración. Lo que sigue la organiza para que converja en pocas vueltas.

---

# 2. El trade central: la ventana de torsión

Desarrollo en [I-02](../investigacion/I-02-equilibrio-sin-cola.md).

    trim mínimo  ≤  ε_wash-in  ≤  límite de pérdida en punta

| Límite | Origen | Efecto de violarlo |
|---|---|---|
| **Inferior** | Hace falta C_m suficiente al CL de crucero | No compensa sin deflexión permanente → resistencia de trim y pérdida de autoridad |
| **Superior** | Wash-in sube la incidencia de punta | **Se anula la ventaja principal de la flecha invertida** |

Y hay que **dejar hueco al wash-in elástico**, que crece con la presión dinámica.

**Si la ventana está vacía, hay que meter reflex** — y el reflex cuesta C_Lmax, requisito duro por lanzamiento a mano. **Esta es la decisión de Fase 1.**

**Dato de partida `[M]`:** el Peregrine necesita +3° de cabeceo nivelado en INAV — su torsión construida se queda corta. Sugiere que la ventana existe pero es estrecha.

---

# 3. Líneas de trabajo

## A — Geometría de referencia *(bloqueante)*

| # | Tarea | Cierra | Estado |
|---|---|---|---|
| A1 | Planta del panel Peregrine: flecha c/4, estrechamiento, cuerdas | G1, R1 | Bloqueada — falta archivo de alas |
| **A2** | **Distribución de torsión del Peregrine** | G1, valida ADR-0003 | Bloqueada |
| A3 | Coordenadas de perfil a 3–5 estaciones | R2 | Parcial — t/c hecho |
| A4 | Familia StuntDouble (Nemesis + Stinger/Stormbird) | R3, R4 | **Vía alternativa disponible** |

**A2 es la de mayor valor:** responde empíricamente la pregunta de §2 antes de calcular nada.
**A4 da comparación controlada** flecha invertida vs plank recto, mismo autor y fabricación: experimento natural ya realizado.

## B — Perfil y polares *(bloqueante, G2)*

Se resuelve por **calibración**, no por búsqueda.

| # | Tarea | Método |
|---|---|---|
| **B1** | **Calibrar XFOIL contra dato medido** | Correr E387 a Re 60–200×10³ y comparar con túnel (Spedding & McArthur, UIUC). Ajustar N_crit hasta reproducir la polar medida |
| B2 | Criterios de cribado | t/c 13,5 % · C_Lmax ≥ 0,65 · C_m0 ≥ 0 o cercano · L/D al CL de crucero |
| B3 | Cribar candidatos con N_crit calibrado | Familias MH y EH (aerodesign.de), más candidatos poco reflexados si A2 confirma wash-in suficiente |
| B4 | Publicar polares con su calibración | Salida `[D]`, declararlo |

⚠️ Sin calibrar, XFOIL a Re bajo es optimista y sistemáticamente erróneo en la burbuja laminar. Salida siempre `[D]`; se convierte en `[M]` con E2.

## C — Estabilidad *(la puerta, G8)*

| # | Tarea | Método |
|---|---|---|
| C1 | Punto neutro con método de paneles | XFLR5 VLM sobre la planta de A1 con el perfil de B3 |
| C2 | Verificar con método analítico independiente | Corrección de flecha sobre AC de sección. **Dos métodos que no coinciden = error en uno** |
| C3 | Fijar margen estático objetivo | 8–12 % de CMA. No bajar de 6 % ni con FC |
| C4 | Posición de CG y **ventana de ajuste** | Debe cumplir **R-CG**: ±5 mm en las cuatro configuraciones |
| C5 | Resolver la ventana de torsión (§2) | Iterar torsión y reflex hasta cerrar trim con margen de pérdida en punta |
| **C6** | **Verificar autoridad de elevón** | Deflexión necesaria en toda la envolvente, incluida ráfaga y CG extremo |
| C7 | Caracterizar rigidez de charnela TPU | Entra en ω_β y por tanto en el análisis de flutter |

> **C6 nunca se había hecho.** Se dimensionó la charnela al 72 % y se calculó su flutter y su equilibrado de masa **sin comprobar que da autoridad suficiente**. Orden invertido, corregido aquí.

**C4 puede obligar a rediseñar la bahía o el CORE.** Es donde la modularidad de batería se paga o se cobra.

## D — Propulsión *(paralelo, desacoplado)*

**No depende de nada de lo anterior.** Y contiene la afirmación central del proyecto.

| # | Tarea | Nota |
|---|---|---|
| D1 | Montar cadena de medida: pitot + blackbox + registro de corriente | Instrumento de E2, E3 y E7 |
| **D2** | **Validar el método sobre una plataforma existente** | Vuelo estabilizado, barrido de velocidad, reducción de datos |
| D3 | Barrido de emparejamiento de hélice | 3–4 combinaciones contra J predicho por UIUC |
| D4 | Tabla de emparejamiento por pack (4S / 6S) | **Salida publicable del proyecto** |

**D2 es el paso más infravalorado del plan.** Valida la cadena de medida completa en un avión que ya vuela, antes de que exista el nuevo. Si el método no funciona ahí, no funcionará después — y sería mucho peor descubrirlo con el artículo #1.

⚠️ **Verificar antes de comprar:** el SpeedyBee F405 WING **MINI** puede no tener entrada de pitot. Sin ella, E2 y E7 no son posibles en esa plataforma.

---

# 4. Secuencia

```
AHORA          A3 A4            ──┐
               B1                ─┼──► pueden empezar hoy
               D1 D2             ─┘

BLOQUEADO      A1 A2  (requiere archivo de alas o vía A4)

DESPUÉS DE A+B C1 C2 C3
               ↓
               C4 ──► ¿cumple R-CG?          NO ──► rediseño de bahía/CORE
               ↓ SÍ
               C5 ──► ¿ventana de torsión?   NO ──► volver a B3 con reflex
               ↓ SÍ
               C6 ──► ¿autoridad suficiente? NO ──► replantear charnela
               ↓ SÍ
        ═══ PUERTA DE FASE 1 ═══

PARALELO       D3 D4  (en cualquier momento tras D2)
```

## Criterios de salida

- [ ] Planta definida: envergadura, cuerdas, flecha c/4, estrechamiento
- [ ] Perfil seleccionado con polares `[D]` calibradas
- [ ] Distribución de torsión definida
- [ ] Punto neutro calculado por **dos métodos** que concuerdan
- [ ] Margen estático 8–12 % con CG alcanzable
- [ ] **R-CG verificado** en las cuatro configuraciones
- [ ] **Autoridad de elevón verificada** en toda la envolvente
- [ ] Ventana de torsión cerrada con margen de pérdida en punta

**Nada de esto requiere imprimir.**

---

# 5. Riesgos del plan

| Riesgo | Prob. | Mitigación |
|---|---|---|
| **La ventana de torsión sale vacía** | Media | Aceptar reflex y perder C_Lmax → puede obligar a subir superficie |
| **R-CG no se cumple con 6S2P** | **Alta** | Ya previsto: 6S2P declarado fuera de envolvente |
| XFOIL calibrado sigue poco fiable en la burbuja | Media | Declarar `[D]`, cerrar con E2. No congelar decisiones irreversibles sobre B |
| No conseguir el archivo de alas del Peregrine | **Alta** | A4 (StuntDouble) como fuente alternativa de planta |
| El FC de pruebas no admite pitot | Media | Verificar antes de comprar; buscar FC alternativo para banco |
| **G9 impide E7** | Media | Ajustar lazo de altitud antes de ensayar |

---

# 6. Qué se puede empezar hoy

1. **B1** — calibración de XFOIL contra el E387 medido. No depende de nada; los datos están publicados.
2. **D1** — pedir el pitot. Material con plazo de entrega; bloquea E2, E3 y E7.
3. **A4** — descargar los STL de la familia StuntDouble. Vía alternativa a A1/A2 y única fuente de comparación controlada de planta.
