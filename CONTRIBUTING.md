# Cómo contribuir

Este proyecto acepta contribuciones que **suban el nivel de confianza de un dato**.

## Orden de valor

| Prioridad | Tipo | Ejemplo |
|---|---|---|
| **1** | **Medidas** | Convertir un `[E]` o `[I]` en `[M]` con método publicado |
| **2** | **Correcciones** | Una fuente mejor tumba una conclusión existente |
| **3** | **Réplicas** | Construcción independiente con datos de blackbox |
| **4** | **Geometría** | Solo después de cerrada la Fase 1 |

## Lo que no se acepta

**Cifras sin fuente, aunque sean correctas.** No es rigidez burocrática: el valor de este repositorio es que cualquiera pueda rastrear de dónde sale cada número. Una cifra huérfana correcta hoy es una cifra no verificable mañana.

Tampoco se aceptan decisiones irreversibles apoyadas en `[E]` o `[I]` sin declararlo explícitamente.

## La convención de confianza

| Etiqueta | Significado | Ejemplo |
|---|---|---|
| `[M]` | Medido y publicado por fuente primaria | «C_Lmax entre 0,55 y 0,70 (Ananda et al. 2015)» |
| `[D]` | Derivado por cálculo desde `[M]` | «L/D aerodinámico ≈ 7,4, despejado de datos de vuelo» |
| `[E]` | Estimado sobre supuestos declarados | «Masa de cáscara 550–650 g, por área mojada y espesor medio» |
| `[I]` | Inferencia razonada, no verificada | «La rigidez torsional gobierna la divergencia en esta construcción» |

## Flujo de una contribución

1. **Abre un issue** describiendo qué brecha (G) o decisión (ADR) toca.
2. **Trabaja sobre los documentos**, no solo sobre el código o la geometría.
3. **Rellena la plantilla de PR.** Pide declarar decisiones y brechas afectadas, y el nivel de confianza del dato nuevo.
4. **Si invalidas una afirmación previa, añade entrada al [CHANGELOG](CHANGELOG.md)** con número de corrección C.

## Sobre las correcciones

**El registro de correcciones es parte del producto, no una lista de vergüenzas.** Van 16, varias de ellas errores del análisis original corregidos por datos posteriores. Documentarlas es lo que permite confiar en lo que queda en pie.

Si encuentras un error, **no lo silencies editando el texto**: corrígelo y anótalo. Alguien que leyó la versión anterior necesita saber que cambió y por qué.

## Escribir una ADR nueva

Copia [`decisiones/PLANTILLA.md`](decisiones/PLANTILLA.md). Numeración correlativa. Una decisión por archivo.

Una buena ADR responde: **¿qué obligaba a decidir? ¿qué se descartó y por qué? ¿qué obliga esta decisión aguas abajo? ¿qué dato la haría reconsiderar?**

## Escribir una línea de investigación

Copia el formato de `investigacion/I-0X`. Una línea documenta **qué se buscó, qué se encontró, con qué fuentes, y qué decisiones alimenta** — no qué se decidió.

## Datos de ensayo

Deben declarar la **configuración completa**: pack, motor, hélice, masa al despegue, material, perímetros, relleno, versión de firmware. Sin eso no son comparables entre constructores.

## Calidad de fuentes

Orden de preferencia: revisadas por pares → bases de datos experimentales → ensayo controlado con método declarado → documentación de fabricante → patentes → medición propia.

**Fuente marcada como no utilizable:** Grokipedia, por contradecir a la totalidad de fuentes primarias consultadas sobre divergencia en flecha invertida.
