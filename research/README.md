# Research threads

Here lives **the why**. Each thread documents what was searched, what was found, with what sources, and **what decisions it feeds**.

Separated from `decisions/` on purpose: an ADR says *what was decided*; a research thread says *what we know and how we know it*. One research effort can feed several decisions, and one decision can rest on several research efforts.

| # | Thread | Status | Feeds |
|---|---|---|---|
| [I-01](I-01-aspect-ratio-reynolds.md) | Aspect-ratio / Reynolds frontier | Closed | ADR-0004, ADR-0009 |
| [I-02](I-02-tailless-trim.md) | Tailless trim and forward sweep | Closed | ADR-0001, ADR-0003 |
| [I-03](I-03-propulsion-chain.md) | Propulsion chain | Closed | ADR-0007, ADR-0008, O1 |
| [I-04](I-04-printing-materials.md) | Printing materials | Closed | ADR-0016, ADR-0018, ADR-0021 |
| [I-05](I-05-divergence-flutter.md) | Aeroelastic divergence and flutter | **Open** | ADR-0002, ADR-0025, ADR-0028 |
| [I-06](I-06-reflexed-airfoils.md) | Reflexed airfoils at Re 3–5×10⁵ | **Open — B1 partial** | Gap G2 |
| [I-07](I-07-neutral-point-torsion-window.md) | **Neutral point, static margin and torsion window** | **Open — preliminary result** | ADR-0003, ADR-0032, G8, G2 |
| [I-08](I-08-stuntdouble-family.md) | **StuntDouble family: compared geometry** | **Open — base comparison** | A4, R3, R4 |

## Source quality

Order of preference:

1. Peer-reviewed
2. Experimental databases (UIUC)
3. Controlled test published with a declared method (e.g. CNC Kitchen)
4. Manufacturer documentation
5. Patents — verifiable argument, magnitude not independent
6. Own measurement on in-service articles

### Source marked as unusable

**Grokipedia** claims that forward sweep *delays* aeroelastic divergence. **It contradicts all the primary and peer-reviewed sources consulted, including the X-29 program documentation. It must not be used.**
