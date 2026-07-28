# I-06 — Perfiles reflexados a Re 3–5×10⁵

**Estado:** Abierta — B1 parcial, calibración E387 (C) reproducible  
**Cierra:** G2  
**Alimenta:** B2/B3 del plan de Fase 1 y R-PERFIL

---

# 1. Pregunta

¿Con qué incertidumbre puede usarse XFOIL para cribar perfiles reflexados en el Reynolds
del proyecto?

La primera tarea no es comparar perfiles candidatos. Es medir cuánto se equivoca XFOIL
contra una polar de túnel antes de confiar en sus salidas.

# 2. Fuentes primarias

- Coordenadas E387 del
  [UIUC Airfoil Data Site](https://m-selig.ae.illinois.edu/ads/coord_seligFmt/e387.dat).
- Polar limpia E387 (C), cinco Reynolds, del
  [UIUC LSATs Vol. 3](https://m-selig.ae.illinois.edu/pd/pub/lsat/vol3/E387C.DRG).
- [XFOIL oficial de Mark Drela](https://web.mit.edu/drela/Public/web/xfoil/),
  versión 6.99 usada en esta corrida.

Los datos de túnel son `[M]`; toda salida de XFOIL y toda comparación calculada son `[D]`.

# 3. Método reproducible

Herramienta: [`calculo/calibra_xfoil_e387.py`](../calculo/calibra_xfoil_e387.py).

1. Descargar coordenadas y polar directamente de UIUC.
2. Correr XFOIL en los Reynolds medidos: 59 885, 99 744, 199 604, 299 856 y
   458 992 `[M]`.
3. Barrer Ncrit = 8–12 `[I]`.
4. Generar la rama previa a pérdida entre α = 0–9° en pasos de 0,5° `[I]`.
5. Comparar `Cd(Cl)` por interpolación para 0,25 ≤ Cl ≤ 0,85 `[I]`.

La métrica es:

`factor = exp(RMSE(log(Cd_XFOIL / Cd_UIUC)))`

Un factor 1 es coincidencia exacta. Un factor 1,20 representa un desacuerdo multiplicativo
RMS del orden del 20 % `[D]`.

La ventana de `Cl` evita mezclar el ajuste de resistencia con la predicción de pérdida,
que XFOIL no reproduce de forma robusta a estos Reynolds. Es una elección metodológica
`[I]`, declarada y modificable.

# 4. Resultado preliminar `[D]`

| Ncrit | Factor global | Re 59 885 | Re 99 744 | Re 199 604 | Re 299 856 | Re 458 992 |
|---:|---:|---:|---:|---:|---:|---:|
| 8 | 1,502 | 1,896 | 1,509 | 1,197 | 1,143 | 1,129 |
| 9 | 1,351 | 1,569 | 1,395 | 1,162 | 1,123 | 1,118 |
| **10** | **1,208** | **1,297** | 1,252 | 1,122 | 1,098 | 1,107 |
| 11 | 1,209 | 1,384 | **1,110** | 1,076 | 1,071 | 1,091 |
| 12 | 1,245 | 1,424 | 1,248 | **1,026** | **1,041** | **1,071** |

## 4.1 Lectura

- El mejor ajuste global de esta rejilla es Ncrit = 10, con factor 1,208 `[D]`;
  Ncrit 11 es prácticamente indistinguible, con 1,209 `[D]`.
- El óptimo deriva con Reynolds: Ncrit 10 a Re ≈ 60 000, Ncrit 11 a Re ≈ 100 000
  y Ncrit 12 desde Re ≈ 200 000 `[D]`.
- En el rango del proyecto, Re ≈ 3–5×10⁵, Ncrit 12 da el menor desacuerdo de la rejilla:
  factores 1,041 y 1,071 `[D]`.

**No existe un Ncrit único que reproduzca toda la familia de polares.** Ajustar un solo
número y llamarlo «calibración de XFOIL» oculta una dependencia con Reynolds que los datos
medidos sí muestran.

# 5. Consecuencia para B3

El cribado de candidatos debe:

1. correr como mínimo la banda Ncrit 10–12 `[I]`;
2. publicar la sensibilidad de `Cm0`, `Clmax` y `L/D`, no solo la curva más favorable;
3. tratar Ncrit 12 como referencia de túnel liso en Re 3–5×10⁵ `[D]`, **no** como
   representación medida de una piel PETG impresa;
4. conservar toda polar resultante como `[D]`.

Una rugosidad o costura de impresión puede forzar transición antes que el túnel. Por eso
esta calibración reduce G2, pero no sustituye E2.

# 6. Qué falta para cerrar B1

- Validar la banda Ncrit 10–12 contra un segundo modelo físico E387 independiente
  (E387 E, UIUC Vol. 5), sin reajustar la métrica.
- Publicar la sensibilidad a panelado y paso de α.
- Separar error de `Cd(Cl)` y error de `Cl(α)`.
- Comprobar que la misma banda no falla de forma sistemática en otro perfil de baja
  velocidad antes de usarla como regla general.

Hasta entonces B1 queda **parcial** y G2 sigue abierta.
