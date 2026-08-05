# ADR-0001 — Ala volante de flecha invertida

**Estado:** ✅ Vigente · **Fecha:** 2026-07-27 · **Confianza:** Alta · **Reversible:** No
**Investigación:** [I-02 — Equilibrio sin cola y flecha invertida](../investigacion/I-02-equilibrio-sin-cola.md)

## Contexto

La misión (FPV de crucero, lanzamiento a mano, transporte compacto) admite ala volante o configuración con cola. Dentro de ala volante, la flecha puede ser atrás o adelante.

## Alternativas consideradas

| Opción | A favor | En contra |
|---|---|---|
| Cola convencional | Estabilidad trivial, perfil libre | Más piezas, más resistencia, más frágil al aterrizar de panza |
| Ala volante flecha atrás | Solución mayoritaria, sin divergencia | Requiere wash-out: la punta resta sustentación; pérdida por punta primero |
| **Flecha invertida** | Trim más eficiente, pérdida por raíz | **Divergencia aeroelástica** |

## Decisión

**Ala volante de flecha invertida, sin cola.**

## Fundamento

1. **Ventaja de resistencia de trim.** En flecha invertida la fuerza de equilibrio actúa hacia arriba y por delante del CG: la sustentación total necesaria es esencialmente igual al peso. En flecha atrás el equilibrio exige carga negativa en punta y el ala debe generar **más** de lo que pesa el avión. Documentado en US 4.545.552 y US 4.674.709.
   ⚠️ Son patentes, no literatura revisada por pares. El argumento físico es verificable; **la magnitud no está cuantificada por fuente independiente.**

2. **Comportamiento en pérdida.** El flujo transversal va de punta a raíz: **la raíz entra en pérdida primero** y los elevones exteriores conservan efectividad. `[M]`, múltiples fuentes independientes. En un ala volante esto pesa doble: los elevones son la totalidad del control.

3. **Convergencia independiente.** Dos diseñadores llegaron a la misma planta sin relación entre sí: la familia StuntDouble (Interceptor / Eliminator / Nemesis) y el Peregrine 840 mm.

## Consecuencias

- **Abre el riesgo dominante del proyecto:** divergencia aeroelástica. Ver [I-05](../investigacion/I-05-divergencia-flutter.md).
- Obliga a torsión de tipo **wash-in** (ADR-0003), no wash-out.
- Obliga a priorizar **rigidez torsional** sobre masa en todo el dimensionado.
- El CG y el punto neutro dejan de ser intuitivos: requieren cálculo (brecha G8).

## Condiciones de revisión

Solo se reconsideraría si el ensayo E7 midiera una velocidad de divergencia inaceptablemente baja y no hubiera solución estructural dentro del presupuesto de masa.
