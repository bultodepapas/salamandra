# I-02 — Equilibrio sin cola y flecha invertida

**Estado:** Cerrada · **Alimenta:** ADR-0001, ADR-0003, ADR-0027

## Pregunta

¿Cómo se equilibra un ala sin cola, y qué gana o pierde la flecha invertida frente a la flecha atrás?

## Mecanismo de equilibrio

Un ala sin cola requiere momento de cabeceo positivo. **Solo hay dos vías:** perfil con C_m0 positivo (reflex), o combinación de flecha y torsión.

Para la flecha, las dos soluciones son **simétricas**:

| Planta | Torsión requerida | Carga en punta a sustentación nula |
|---|---|---|
| Flecha atrás | **Wash-out** (punta abajo) | Hacia abajo — resta sustentación |
| **Flecha invertida** | **Wash-in** (punta arriba) | Hacia arriba — suma sustentación |

En flecha invertida las puntas van **por delante** del CG: wash-in genera más sustentación por delante → momento de encabritado. Es la fuente natural de trim de esta planta.

> **Corrección C2.** Se afirmó inicialmente que la flecha invertida depende exclusivamente del C_m0 del perfil por no poder usar torsión. **Falso: puede y debe usar wash-in.**
>
> Consecuencia práctica de gran valor: **el perfil puede ser poco o nada reflexado**, con mejor C_Lmax y mejor L/D que los reflexados clásicos — si el wash-in basta para cerrar el trim.

## Ventaja 1 — resistencia de trim

En flecha invertida la fuerza de equilibrio actúa **hacia arriba y por delante del CG**: la sustentación total necesaria es esencialmente igual al peso. En flecha atrás el equilibrio exige carga negativa en las puntas y el ala debe generar **más** de lo que pesa el avión.

Documentado en US 4.545.552 y US 4.674.709.

⚠️ Patentes, no literatura revisada por pares. El argumento físico es correcto y verificable; **la magnitud del beneficio no está cuantificada por fuente independiente.**

## Ventaja 2 — comportamiento en pérdida

El flujo transversal va de punta a raíz. **La raíz entra en pérdida primero**, y los elevones exteriores conservan efectividad al permanecer en aire de alta energía. `[M]`, múltiples fuentes independientes.

Para un ala volante esto pesa doble: **los elevones son la totalidad del control.**

## Riesgo — divergencia aeroelástica

Ver [I-05](I-05-divergencia-flutter.md) para el tratamiento completo.

### Acoplamiento peligroso `[I]`

La flecha invertida sin cola **necesita wash-in para el trim**, y la divergencia aeroelástica **también produce wash-in**. Los dos efectos se suman, y el segundo crece con la presión dinámica.

**Consecuencia: el estado de trim se desplaza con la velocidad.** Un ala de flecha atrás tiene el signo contrario y se auto-atenúa.

Esto explica tres características del TBS Mojito que antes no tenían explicación: CG extremadamente adelantado, recomendación de adelantarlo aún más, y deflexiones de elevón deliberadamente cortas.

Riesgo adicional documentado: con deflexión aeroelástica suficiente, **las puntas pueden entrar en pérdida primero, anulando la ventaja principal** — precisamente cuando más se necesita `[M]`.

## La ventana de torsión — problema central de Fase 1

    trim mínimo  ≤  ε_wash-in  ≤  límite de pérdida en punta

| Límite | Origen | Efecto de violarlo |
|---|---|---|
| Inferior | Hace falta C_m suficiente al CL de crucero | No compensa sin deflexión permanente → resistencia de trim y pérdida de autoridad |
| Superior | Wash-in sube la incidencia de punta | **Se anula la ventaja de pérdida por raíz** |

Y hay que **dejar hueco al wash-in elástico**, que crece con la velocidad.

**Si la ventana está vacía, hay que meter reflex** — y el reflex cuesta C_Lmax, que ya es requisito por lanzamiento a mano.

## Dato empírico relevante `[M]`

La documentación del Peregrine 840 mm indica ajustar en INAV **«cabeceo nivelado: 0 → 3°»**. Significa que el avión necesita 3° de actitud de morro arriba para vuelo nivelado: **su incidencia/torsión construida se queda 3° corta**.

Es el único dato disponible sobre el estado de trim real de un ala de flecha invertida impresa en servicio.

## Fuentes

- US 4.545.552 y US 4.674.709 — configuración sin cola de flecha invertida *(patentes)*
- Documentación del programa X-29
- aerodesign.de — base de datos de perfiles para alas volantes y sin cola
- Ficha técnica del Peregrine 840 mm
