# Cálculo

Scripts de análisis. Cada uno autocontenido y ejecutable.

| Archivo | Qué hace | Alimenta |
|---|---|---|
| `vlm_ala_volante.py` | Vortex lattice para ala de flecha invertida con estrechamiento y torsión. Punto neutro, CL_α, reparto de carga | I-07, G8 |
| `ventana_torsion.py` | Torsión requerida para trim contra margen de pérdida en punta | I-07, G2 |
| `calibra_xfoil_e387.py` | Contrasta una rejilla de Ncrit de XFOIL contra la polar E387 (C) medida por UIUC | I-06, G2 |

## Uso

```bash
python3 vlm_ala_volante.py     # incluye caso de validación
python3 ventana_torsion.py     # análisis de la ventana
python3 calibra_xfoil_e387.py --xfoil /ruta/a/xfoil
```

Los dos primeros scripts requieren solo `numpy`.

`calibra_xfoil_e387.py` usa únicamente la biblioteca estándar de Python, pero necesita
el ejecutable oficial de XFOIL. Descarga en tiempo de ejecución las coordenadas y la polar
medida desde UIUC; no las sustituye por una copia secundaria.

## Validación

`vlm_ala_volante.py` incluye un caso de contraste: ala recta AR 6 sin flecha ni torsión, cuyo punto neutro debe caer en c/4 y cuyo CL_α debe aproximar la fórmula de Helmbold.

**Cualquier modificación debe pasar esa validación antes de usarse.** Un error de normalización por la CMA se detectó exactamente así.

`calibra_xfoil_e387.py` valida su interpolación y su métrica contra un caso analítico:
una polar con `Cd_calculado = 1,1 × Cd_medido` debe devolver exactamente un factor 1,1.

## Convenciones

- `x` positivo hacia atrás, origen en el c/4 de la raíz
- `Lambda_c4` negativo = flecha invertida
- `epsilon` positivo = wash-in (punta a mayor incidencia)
