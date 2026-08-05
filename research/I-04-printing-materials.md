# I-04 — Materiales de impresión

**Estado:** Cerrada · **Alimenta:** ADR-0016, ADR-0018, ADR-0021

## Pregunta

¿Qué filamento maximiza la rigidez torsional por gramo, y qué otros criterios compiten con ella?

## Figura de mérito

En sección cerrada, `GJ ∝ G·t` y `masa ∝ ρ·t`. Por tanto la figura de mérito es **G/ρ**.

| Material | E impreso | G_eff | ρ | **G/ρ** | Relativo |
|---|---|---|---|---|---|
| **PLA normal** | 3,00 GPa `[M]` | 0,90 | 1,24 | **0,73** | **1,00** |
| PLA+ | 2,20 GPa `[M]` | 0,66 | 1,24 | 0,53 | 0,73 |
| ASA | 1,9–2,2 GPa `[E]` | 0,58 | 1,07 | 0,53 | 0,73 |
| LW-PLA | ~1,0 GPa `[E]` | 0,35 | 0,68 | 0,51 | 0,70 |
| **PETG** | **1,94 GPa** `[M]` | **0,55** | **1,27** | **0,43** | **0,59** |

**El PETG es el peor de los cinco en rigidez torsional específica.** Se adopta igualmente — ver [ADR-0021](../decisiones/ADR-0021-material-base.md).

## Datos primarios

### PLA vs PLA+ `[M]` — mismo fabricante, mismo banco

Polymaker PolyLite (PLA) contra PolyMax (PLA+), ensayo controlado:

| Ensayo | PLA | PLA+ | Δ |
|---|---|---|---|
| Tracción tumbado | 57 MPa | 43 MPa | −25 % |
| Adhesión de capas | 43 MPa (75 % de la resistencia normal) | 75 % también | = |
| **Módulo a flexión** | **3000 MPa** | **2200 MPa** | **−27 %** |
| Impacto | 5 kJ/m², rompe limpio | ~4× más tenaz | +300 % |
| **Fallo térmico bajo carga** | **65 °C** | **65 °C** | **0** |

Tres conclusiones contraintuitivas:

1. **El PLA+ es más blando, no más rígido.** Queda a la altura del PETG y el ABS.
2. **No gana nada en temperatura.** Elimina el único argumento que permitiría salir del PETG sin perder margen térmico.
3. **La adhesión de capas del PLA normal es excepcional** — 75 % de retención, cuando la mayoría de materiales muestran al menos un 50 % de castigo.

⚠️ Un par de marcas, no el universo PLA+. Tendencias sólidas; magnitudes exactas de otras marcas pueden diferir.

### PLA vs PETG `[M]` — dataset apareado

Ultimaker, ASTM D3039, 100 % relleno, capa 0,15 mm:

- Módulo XY: **PLA 3250 ± 119 MPa · PETG 1939 ± 28 MPa**
- PETG en Charpy con entalla: 7,9 ± 0,6 kJ/m² contra 3,9 ± 0,4 del PLA

### Retención en dirección Z `[M]` — mismo banco, mismos ganchos

| Material | Tumbado | De pie | **Retención Z** |
|---|---|---|---|
| PLA | 72 kg | 40 kg | **55 %** |
| PETG | 54 kg | 25 kg | **46 %** |
| ASA | 59 kg | 17 kg | **29 %** |

> **Corrección C8.** Se afirmó que el PETG tiene mejor adhesión de capas que el PLA. **Es al revés.** El PETG gana en tenacidad, no en adhesión.

### ¿Importa la adhesión en Z? `[D]`

La torsión de Bredt carga las juntas de capa en **cortante interlaminar**. Cálculo del par en raíz a V_NE con tirón de 5 g:

    τ = T / (2·A·t) ≈ 5 / (2 · 2,75×10⁻³ · 9×10⁻⁴) ≈ 1,0 MPa

Frente a ~20 MPa de resistencia interlaminar del PETG: **margen ×20**.

**La adhesión de capas no es vinculante. El problema es de rigidez, no de resistencia.** Esto salvó al ASA de ser descartado por su 29 %, y lo descartó por otro motivo.

## Por qué se rechaza cada alternativa

| Material | Motivo del rechazo |
|---|---|
| **PLA+** | −27 % de rigidez sin ganancia térmica. Punto intermedio que no resuelve ninguna restricción → ADR-0016 |
| **ABS** | Amarillea y se fragiliza al sol en unos meses `[M]`. Un ala vive al aire libre → ADR-0018 |
| **ASA** | Ventajas reales (Tg 105 °C, soldable con acetona, alisable). **Rechazado por alabeo**: la torsión geométrica es un parámetro de trim, y un material poco repetible corrompe la variable que gobierna el equilibrio |
| **LW-PLA** | Ligero pero blando, caro y de manejo delicado. Reservado para piezas no estructurales |
| **PLA normal** | Mejor rigidez de todos. Descartado por Tg 55–60 °C y fragilidad en aterrizaje de panza. **Es la alternativa técnica si la rigidez apretara** |

## Adhesivos para PETG

> **Corrección C9.** Se afirmó que el PETG no se puede pegar. Demasiado categórico.

| Opción | Veredicto |
|---|---|
| **3D-Gloop PETG** | Soldadura química específica. Rindió mejor que el cianoacrilato **bajo torsión** con las piezas apretadas — que es el caso de carga del proyecto |
| **Epoxi de 30 min** | Mejor resistencia bruta. Los de 5 min son notablemente peores |
| DCM (diclorometano) | Soldadura por disolvente real, pero **carcinógeno cat. 2 y restringido por REACH en la UE**. No recomendado |
| Cianoacrilato | Solo unión superficial. No estructural en PETG |
| E6000 | **Falla.** Único que pudo separarse a mano tras curar |

## Advertencia de reproducción

⚠️ Los perfiles de impresión de LW-PLA traen `flow_ratio ≈ 0,60` para compensar el espumado. **Al cambiar a PETG hay que subirlo a ~0,95**, o se deposita un 40 % menos de material.

Un ejemplar del Peregrine 840 mm impreso en PETG con el perfil de LW-PLA resulta **~1,6× más rígido en cortante** que el diseño previsto (G 0,55 frente a 0,35) y **~2,2× más pesado**.

## Fuentes

- CNC Kitchen — *The difference of PLA and PLA+ tested (feat. Polymaker)*
- CNC Kitchen — *Comparing PLA, PETG & ASA (feat. Prusament)*
- Ultimaker — dataset apareado PLA/PETG, ASTM D3039 / ISO 179-1
- 3D-Fuel — ensayo comparativo de adhesivos
- 3DLabPrint — *Materials for 3D printing planes*
