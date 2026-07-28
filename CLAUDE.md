# CLAUDE.md

Contexto y reglas de trabajo para asistentes de IA en este repositorio.

---

## Qué es este proyecto

Ala volante FPV de **flecha invertida**, impresa en PETG, modular. No es un repositorio de STL: **es un repositorio de razonamiento**. El STL vendrá después.

La aportación es que **cada decisión lleva su fundamento, su fuente y su nivel de confianza**, y que **los errores quedan registrados en vez de borrados**.

Si al terminar una sesión el repositorio tiene más geometría pero menos trazabilidad, la sesión ha sido negativa.

---

## La regla central — no negociable

Toda afirmación cuantitativa lleva etiqueta:

| Etiqueta | Significado |
|---|---|
| `[M]` | Medido y publicado por una fuente primaria |
| `[D]` | Derivado por cálculo a partir de datos `[M]` |
| `[E]` | Estimado sobre supuestos declarados |
| `[I]` | Inferencia razonada, no verificada |

> **Ningún dato `[E]` o `[I]` sostiene una decisión irreversible sin verificación previa.**

**Corolario operativo:** si vas a escribir un número, primero decide su etiqueta. Si no sabes qué etiqueta ponerle, no lo escribas todavía.

**No se aceptan cifras sin fuente, aunque sean correctas.** Una cifra huérfana correcta hoy es una cifra no verificable mañana.

---

## Estado actual

**Fase 0 cerrada. Fase 1 (geometría y estabilidad) en curso.**

Antes de proponer nada, lee en este orden:

1. [`README.md`](README.md) — estado y navegación
2. [`docs/00-objetivos-y-requisitos.md`](docs/00-objetivos-y-requisitos.md) — el pliego
3. [`brechas/README.md`](brechas/README.md) — **lo que no sabemos**
4. [`docs/03-plan-fase1.md`](docs/03-plan-fase1.md) — qué toca ahora

**El bloqueante actual está en `brechas/`.** No lo asumas: léelo, cambia.

---

## Mapa del repositorio

| Carpeta | Qué contiene | Cuándo escribir aquí |
|---|---|---|
| `docs/` | Pliego, plan de fase, convenciones, datos medidos | Cambia un requisito o un objetivo |
| `decisiones/` | **ADR: una decisión por archivo** | Se toma, se supera o se anula una decisión |
| `investigacion/` | Líneas de investigación: qué se buscó y se encontró | Se investiga algo, aunque no decida nada |
| `brechas/` | Registro de incógnitas G1–G9 | Se abre, se acota o se cierra una brecha |
| `ensayos/` | Programa experimental y datos | Se define o se ejecuta un ensayo |
| `calculo/` | Scripts de análisis **con caso de validación** | Se escribe o modifica cálculo |
| `geometria/` `stl/` `cad/` | Salidas de Fase 1 en adelante | Todavía no |

**`decisiones/` e `investigacion/` están separados a propósito.** Una ADR dice *qué se decidió*; una línea de investigación dice *qué sabemos y cómo*. Una investigación alimenta varias decisiones y una decisión se apoya en varias investigaciones. Fusionarlos obliga a duplicar o a perder trazabilidad.

---

## Cómo trabajar aquí

### Al tomar una decisión

Crea una ADR desde [`decisiones/PLANTILLA.md`](decisiones/PLANTILLA.md). Numeración correlativa. Debe responder:

- ¿Qué obligaba a decidir?
- ¿Qué se descartó y por qué?
- ¿Qué obliga esta decisión aguas abajo?
- **¿Qué dato la haría reconsiderar?** ← esto es lo que hace el repo evolutivo

Actualiza el índice de `decisiones/README.md` con el estado.

### Al encontrar un error

**No lo silencies editando el texto.** Corrígelo **y** añade entrada al [`CHANGELOG.md`](CHANGELOG.md) con número `C`. Alguien que leyó la versión anterior necesita saber que cambió y por qué.

Van 21 correcciones. Varias son errores del análisis original tumbados por datos posteriores. **Documentarlas es lo que permite confiar en lo que queda en pie.**

### Al anular una decisión

**Conserva el archivo**, márcalo ❌ y explica qué proponía, por qué se anula y **bajo qué condiciones volvería**. Borrarla hace que dentro de seis meses alguien la proponga otra vez sin saber que ya se estudió. Ejemplo: [`ADR-0022`](decisiones/ADR-0022-velo-carbono-anulada.md).

### Al escribir cálculo

**Todo script lleva un caso de validación contra solución analítica conocida, y debe pasarlo antes de usarse.** No es ceremonia: el error C17 (falta de normalización por la CMA en el VLM) lo destapó exactamente eso.

```bash
python3 calculo/vlm_ala_volante.py    # incluye el caso de contraste
```

---

## Modos de fallo conocidos

Documentados porque **ya ocurrieron en este proyecto**. Léelos antes de trabajar.

### 1. Orden invertido — el más frecuente y el más caro

Se dimensionó estructura **sin definir cargas** (n_max no existía). Se dimensionaron elevones y se calculó su flutter y su equilibrado de masa **sin haber calculado nunca el punto neutro ni la autoridad de mando**.

> **Antes de dimensionar algo, pregunta qué lo carga y qué lo restringe. Si no está definido, esa es la tarea.**

### 2. Precisión falsa

Se calcularon frecuencias de flutter con tres cifras significativas sobre un ala cuya superficie era `[E]` ±13 %, cuyo perfil no existía y cuya flecha era un rango de 4°.

> **Las cifras significativas de la salida no pueden superar las de la entrada peor.**

### 3. No re-derivar aguas abajo

- **C6** — se arrastró una cuerda de 231 mm de una tabla antigua tras cambiar el alargamiento.
- **C16** — el requisito de velocidad de pérdida se derivó con 1350 g y **no se rehizo** al subir el AUW a 1620 g. El propio requisito dejó de cumplirse con nuestro propio C_Lmax.

> **Cuando cambie un número aguas arriba, busca todo lo que dependía de él. Es la corrección más repetida del proyecto.**

### 4. Transferencia indebida

- **C7** — se dio por válida la evidencia del Eliminator a 360 km/h para el PETG. Validaba **su** material.
- **C12** — se especificó relleno 0 %, heredado de la práctica de LW-PLA en modo vaso, sobre una cáscara de PETG.

> **Un aval vale para el material, la escala y el régimen en que se obtuvo. Declara el límite de transferencia.**

### 5. Generalizar de un solo caso calculado

- **C11** — «los tubos de carbono no sirven para torsión», concluido de un tubo de 10 mm. En pared delgada `J ∝ D³`: a 18 mm el resultado se invierte.

> **Antes de convertir un cálculo en regla, mira de qué depende y en qué potencia.**

### 6. Rotundidad sin datos

- **C9** — «el PETG no se puede pegar». Existen tres soluciones.
- **C14** — se comunicó un riesgo estructural con más certeza de la que soportaban datos `[E]` ±35 %.

> **El tono debe llevar la etiqueta de confianza. Un `[E]` no se comunica como un `[M]`.**

### 7. Ignorar hardware que vuela

- **C15** — «un perímetro no cumple criterio». Falsado por un ejemplar en servicio.

> **Un artículo volando gana a un cálculo `[E]`. Si el modelo contradice hardware real, el sospechoso es el modelo.**

### 8. Ensayos que no discriminan

- **C13** — se propuso calibrar el modelo contra un artículo que resultó estar a factor ~3 del límite. No falsaba ni validaba.

> **Antes de proponer un ensayo, pregunta qué resultado lo haría fracasar. Si no hay ninguno, no mide nada.**

---

## Antes de proponer algo, verifica

- [ ] ¿En qué fase estamos, y esto pertenece a esta fase?
- [ ] ¿Está bloqueado por alguna brecha abierta?
- [ ] ¿Qué etiqueta de confianza tiene cada número que estoy escribiendo?
- [ ] ¿Contradice alguna ADR vigente? ¿Alguna corrección ya registrada?
- [ ] Si cambio un número, ¿qué depende de él aguas abajo?
- [ ] ¿Hay hardware volando que diga otra cosa?
- [ ] ¿Qué documento hay que actualizar además del que estoy tocando?

---

## Convenciones técnicas

Detalle completo en [`docs/04-convenciones.md`](docs/04-convenciones.md).

| Prefijo | Significado |
|---|---|
| `ADR-XXXX` | Decisión · `I-XX` Investigación · `GX` Brecha |
| `EX` | Ensayo · `OX` Objetivo · `R-XXX` Requisito · `CX` Corrección |

**Signos:** flecha negativa hacia delante (el proyecto usa ≈ −20°) · torsión positiva = wash-in (punta a mayor incidencia) · en `calculo/`, `x` positivo hacia atrás con origen en el c/4 de raíz.

**Unidades:** SI en cálculo. En tablas se admiten km/h y g/dm², por ser las de uso corriente.

**Nunca usar** un único factor de Oswald para la resistencia. Separar siempre el término viscoso del inducido — ver [`ADR-0009`](decisiones/README.md) e [`I-01`](investigacion/I-01-alargamiento-reynolds.md). Es un artefacto de definición que ya causó la corrección C1.

---

## Calidad de fuentes

Orden de preferencia: revisadas por pares → bases de datos experimentales (UIUC) → ensayo controlado con método declarado → documentación de fabricante → patentes → medición propia sobre artículos en servicio.

**Fuente marcada como no utilizable:** Grokipedia, por contradecir a la totalidad de fuentes primarias consultadas sobre divergencia en flecha invertida.

---

## Qué no hacer

- **No inventar cifras** para rellenar un hueco. Una brecha declarada vale más que un número plausible.
- **No borrar historial.** Ni ADR anuladas, ni correcciones, ni resultados que salieron mal.
- **No saltar de fase.** Si la Fase 1 no tiene puerta cerrada, no se diseña geometría de detalle.
- **No optimizar un parámetro** cuando hay otro sin definir. Es el modo de fallo nº 1.
- **No dar por buena una polar de XFOIL** a Re bajo sin calibrar contra dato medido. Es `[D]`, nunca `[M]`.
- **No prescribir motor ni batería.** El proyecto diseña el airframe y recomienda — [`ADR-0033`](decisiones/ADR-0033-electronica-fuera.md).
