# Líneas de investigación

Aquí vive **el porqué**. Cada línea documenta qué se buscó, qué se encontró, con qué fuentes, y **qué decisiones alimenta**.

Separado de `decisiones/` a propósito: una ADR dice *qué se decidió*; una línea de investigación dice *qué sabemos y cómo lo sabemos*. Una investigación puede alimentar varias decisiones, y una decisión puede apoyarse en varias investigaciones.

| # | Línea | Estado | Alimenta |
|---|---|---|---|
| [I-01](I-01-alargamiento-reynolds.md) | Frontera alargamiento / Reynolds | Cerrada | ADR-0004, ADR-0009 |
| [I-02](I-02-equilibrio-sin-cola.md) | Equilibrio sin cola y flecha invertida | Cerrada | ADR-0001, ADR-0003 |
| [I-03](I-03-cadena-propulsiva.md) | Cadena propulsiva | Cerrada | ADR-0007, ADR-0008, O1 |
| [I-04](I-04-materiales-impresion.md) | Materiales de impresión | Cerrada | ADR-0016, ADR-0018, ADR-0021 |
| [I-05](I-05-divergencia-flutter.md) | Divergencia aeroelástica y flutter | **Abierta** | ADR-0002, ADR-0025, ADR-0028 |
| I-06 | Perfiles reflexados a Re 3–5×10⁵ | **No iniciada** | Brecha G2 |
| [I-07](I-07-punto-neutro-ventana-torsion.md) | **Punto neutro, margen estático y ventana de torsión** | **Abierta — resultado preliminar** | ADR-0003, ADR-0032, G8, G2 |

## Calidad de fuentes

Orden de preferencia:

1. Revisadas por pares
2. Bases de datos experimentales (UIUC)
3. Ensayo controlado publicado con método declarado (p. ej. CNC Kitchen)
4. Documentación de fabricante
5. Patentes — argumento verificable, magnitud no independiente
6. Medición propia sobre artículos en servicio

### Fuente marcada como no utilizable

**Grokipedia** afirma que la flecha adelante *retrasa* la divergencia aeroelástica. **Contradice a la totalidad de fuentes primarias y revisadas por pares consultadas, incluida la documentación del programa X-29. No debe usarse.**
