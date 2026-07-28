# Referencias medidas — datos primarios

Datos `[M]` obtenidos por medición directa sobre artículos de referencia. **Es la aportación original del proyecto**: cifras que no estaban publicadas en ninguna parte.

---

# 1. Peregrine 840 mm

Ala volante de flecha invertida impresa en 3D, con soporte para DJI O4. **En servicio, volando.** Único artículo comparable verificado de esta configuración.

Fuentes: archivo de proyecto Bambu Studio `Peregrine_body_LWPLA.3mf` y ficha del diseñador. Medido 28 julio 2026.

## 1.1 Ficha publicada `[M]`

| Parámetro | Valor |
|---|---|
| Envergadura | 840 mm |
| Longitud | 500 mm |
| **Peso impreso** | **315 g** (en LW-PLA) |
| **Peso al despegue** | **720 g** |
| **Velocidad de pérdida** | **35 km/h** |
| Tubo de carbono principal | Ø8 × 654 mm |
| Tubo secundario | Ø4 × 194 mm |
| Motor sugerido | 2208 kv2000 / 2207 kv1980 |
| Hélice sugerida | 5146 tripala o APC 6×4 |
| Batería | 4S LiPo o 18650 |
| FC | SpeedyBee F405 WING MINI (INAV 8.1) |
| Servos | 13 g digitales |
| **Inclinación de bancada** | **0,8° arriba** |
| Bisagras | Impresas en TPU, pegadas |

## 1.2 Perfil de impresión del diseñador `[M]`

```
filament_type          PLA-AERO (Bambu PLA Aero) — LW-PLA espumado
wall_loops             1
sparse_infill_density  4 %
sparse_infill_pattern  gyroid
filament_flow_ratio    0.60          ← compensación de espumado
layer_height           0.20 mm
outer / inner wall     0.42 / 0.45 mm
nozzle / bed           247 °C / 55 °C
fan                    30 %
spiral_mode            off
```

**Un solo perímetro de 0,42 mm y 4 % de giroide.** Eso es lo que vuela.

## 1.3 Geometría medida `[M]`

Secciones extraídas del panel interior:

| Estación relativa | Cuerda | Espesor máx. | **t/c** |
|---|---|---|---|
| 0,15 | 125,6 mm | 17,0 mm | **13,5 %** |
| 0,55 | 140,6 mm | 19,3 mm | **13,8 %** |
| 0,90 | 160,1 mm | 21,3 mm | **13,3 %** |

**t/c esencialmente constante en 13,5 %**, con estrechamiento en cuerda.

## 1.4 Planta reconstruida `[D]`

Los objetos del archivo encajan: por semiala, panel interior 222,5 mm + exterior 157,4 mm = 380 mm, más ~118 mm de cuerpo → **840 mm**. Coincide con la ficha.

| | Valor |
|---|---|
| Superficie estimada | **0,140 m²** |
| Cuerda media | 166 mm |
| **Alargamiento** | **5,05** |
| **Carga alar (720 g)** | **51,6 g/dm²** |
| Fracción estructural | 315/720 = **43,8 %** |

⚠️ La velocidad de pérdida publicada (35 km/h) implicaría C_Lmax ≈ 0,87 con esta superficie — por encima del rango medido para placas y reflexados a Re bajo (0,55–0,70, Ananda et al.). **La cifra publicada es probablemente optimista;** un C_Lmax realista de 0,65 daría ~41 km/h.

## 1.5 Consecuencias para el proyecto

1. **Convergencia independiente sobre t/c.** ADR-0027 fijó 13 % por argumento de divergencia y por alojamiento de celda 21700. El artículo que vuela está en 13,5 %. Dos caminos, mismo resultado.

2. **Un perímetro vuela** — corrección C15.

3. **El relleno es parte de la estructura.** El diseñador especifica 4 % de giroide, no relleno cero — corrección C12.

4. **Dato de trim `[M]`.** El ajuste recomendado en INAV de **«cabeceo nivelado: 0 → 3°»** indica que el avión necesita 3° de morro arriba para vuelo nivelado: su incidencia construida se queda 3° corta. Es el único dato disponible sobre el estado de trim real de un ala FSW impresa en servicio. Alimenta la **ventana de torsión** de [I-02](../investigacion/I-02-equilibrio-sin-cola.md).

5. **Riesgo operativo `[M]`.** La ficha documenta *porpoising* en modos RTH / Cruise / Loiter, con ajustes correctivos. **Amenaza directa a la validez de E7** → brecha G9.

6. **El tubo Ø8 es larguero de flexión.** Aportación torsional ~1 N·m², frente a ~70 de la piel. Confirma [ADR-0015](../decisiones/ADR-0015-carbono-no-torsional.md).

## 1.6 Ejemplar impreso en PETG — estimación `[E]`

Un ejemplar impreso en PETG con la geometría de un perfil calculado para LW-PLA:

| | Diseño LW-PLA | Ejemplar en PETG |
|---|---|---|
| Impreso | 315 g | **~690 g** |
| AUW | 720 g | **~1095 g** |
| Carga alar | 51,6 g/dm² | **~78 g/dm²** |
| V_pérdida | 35 km/h (declarada) | **~43 km/h** |
| G en cortante | 0,35 GPa | **0,55 GPa** (×1,6) |

**Es evidencia estructural más fuerte de lo que parece:** más masa a la misma geometría significa más velocidad de crucero y más presión dinámica — y aun así no diverge.

## 1.7 Advertencia de reproducción

⚠️ El perfil trae `filament_flow_ratio = 0.60`, que compensa el espumado del LW-PLA. **Al cambiar a PETG hay que subirlo a ~0,95.** Si no, se deposita un 40 % menos de material: pared real de ~0,25 mm en vez de 0,42 mm.

## 1.8 Límites de transferencia

- El archivo disponible es el **cuerpo**, no los paneles exteriores. Planta completa (flecha del c/4, estrechamiento, **torsión**) sigue pendiente.
- Sin datos de velocidad máxima real alcanzada.
- Escala 840 mm frente a 1300 mm: **las tendencias transfieren, las magnitudes no** sin la ley de escalado de [I-05](../investigacion/I-05-divergencia-flutter.md).

---

# 2. Datos pendientes de medir

| # | Qué | Cómo |
|---|---|---|
| R1 | Planta del panel Peregrine: flecha c/4, estrechamiento, **torsión** | Archivo de alas |
| R2 | Coordenadas de perfil a varias estaciones | Corte de malla |
| R3 | Geometría de la familia StuntDouble | STL abiertos |
| R4 | **Comparación controlada de planta**: flecha invertida vs plank recto | R3, mismo autor y fabricación |
