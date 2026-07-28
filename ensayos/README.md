# Programa experimental

| # | Ensayo | Cierra | Esfuerzo | Estado |
|---|---|---|---|---|
| **E1** | Extracción de geometría desde mallas de referencia | G1 | Bajo | 🔄 Parcial |
| **E2** | Polar de planeo con pitot y blackbox | G3, G2 · valida **O1** | Medio | ⬜ |
| **E3** | Barrido de emparejamiento de hélice | **Realiza O1** | Bajo | ⬜ |
| **E5** | FFT de trazas de giro de blackbox | G4, G7 | Nulo | ⬜ |
| **E7** | **Southwell en vuelo** | **G6** | Bajo | ⬜ |

## Retirados

| # | Ensayo | Motivo |
|---|---|---|
| E4 | Torsión de mesa sobre cupón impreso | Sustituido por anclaje a referencia medida y por E7 |
| E6 | Calibración inversa del modelo contra el Peregrine | **C13** — el Peregrine está a factor ~3 de la predicción; no falsa el modelo pero tampoco lo valida |

---

## E1 — extracción de geometría

Cortar secciones de las mallas de referencia a distintas estaciones. Obtener coordenadas de perfil, superficie, alargamiento, estrechamiento, flecha del c/4 y **distribución de torsión**.

**Hecho:** t/c del Peregrine = 13,5 % `[M]`, perfil de impresión del diseñador.
**Falta:** planta completa; requiere el archivo de los paneles exteriores.
**Alternativa:** familia StuntDouble (Nemesis + Stinger/Stormbird) — da una
**comparación cuasi-controlada de planta**: mismo autor, familia constructiva y AR
comparable, pero cambian perfil, escala y propulsión. Sirve como prior geométrico; no
permite atribuir causalidad a la flecha. Ver [I-08](../investigacion/I-08-familia-stuntdouble.md).

## E2 — polar de planeo

Vuelos con motor parado a velocidades estabilizadas, registrando velocidad de descenso con el barómetro y **velocidad verdadera con pitot**.

Produce la polar real del avión completo sin túnel de viento. **Es el único instrumento que separa pérdidas propulsivas de pérdidas aerodinámicas.**

⚠️ Sin pitot no es válido: la velocidad de suelo está contaminada por el viento.

## E3 — barrido de emparejamiento de hélice

Vuelo estabilizado a velocidad fija registrando corriente, para 3–4 combinaciones diámetro/paso. Comparar contra el J predicho por la base UIUC.

**Es el ensayo que realiza el objetivo O1.** Puede ejecutarse sobre cualquier plataforma de pruebas, incluida una existente: **no depende del airframe del proyecto.**

## E5 — FFT de blackbox

Con el loop de ala fija a 1000 µs, el giroscopio registra a 1 kHz → Nyquist 500 Hz. Suficiente para resolver ω_α (~106 Hz) y ω_β (~82 Hz).

**No requiere ensayo dedicado:** sale del primer vuelo.

## E7 — Southwell en vuelo

Ver [I-05](../investigacion/I-05-divergencia-flutter.md) para el fundamento.

1. Vuelo estabilizado en Cruise a 90, 110, 130, 150 km/h
2. Blackbox: deflexión de trim de elevón contra presión dinámica
3. **1/Δtrim contra q → recta que corta el eje en q_D**

⚠️ **Prerrequisito: resolver G9** (porpoising en modos automáticos).

---

## Formato de datos

Cada ensayo en su subcarpeta:

```
ensayos/EX-nombre/
  README.md          Método, condiciones, configuración completa del avión
  crudo/             Logs de blackbox sin procesar
  reduccion.py       Script de reducción, versionado
  resultados.md      Resultado con etiqueta de confianza y barras de error
```

**Los datos de contribuyentes deben declarar la configuración completa** (pack, motor, hélice, masa, material, perímetros, relleno) para ser comparables.
