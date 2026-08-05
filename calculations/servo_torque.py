#!/usr/bin/env python3
"""
Requisito de par de los servos de elevon para Salamandra (articulo #1, 1300 mm).

Motiva la seleccion del servo en research/I-18-servo-catalog.md: el par de
bisagra aerodinamico es pequeno frente a cualquier servo digital de micro clase,
asi que la seleccion NO la domina el par estatico, sino la rigidez de holding,
el juego nulo y la masa (~15 g/servo, ADR-0025: 60 g total).

Modelo de par de bisagra (comun en la practica de aeromodelismo):
    Mh = 0.5 * rho * V^2 * S_control * c_control * Ch
donde Ch es el coeficiente de momento de bisagra de la superficie (orden 1e-2).
La doble actuacion (ADR-0026, 2 puntos por elevon) divide el par por 2.
Todo [D] sobre la geometria del guide §5.3/§7.5 y datos de perfil [M]/[D].
"""
import numpy as np

# --- Geometria de la geometria del ala (guide §4) ---------------------------
B = 1.30                # envergadura, m
S = 0.282               # superficie, m^2
TAPER = 0.50            # afinamiento
CR = 2 * S / (B * (1 + TAPER))          # cuerda raiz, m
CT = TAPER * CR                          # cuerda punta, m
ELEVON_CHORD_FRAC = 1.0 - 0.72           # 0.28 c, bisagra a 0.72 c (ADR-0002)
ETA_IN, ETA_OUT = 0.30, 0.90             # tramo de elevon (guide §7.5)

RHO = 1.225             # densidad ISA nivel del mar, kg/m^3
V_NE = 180.0 / 3.6      # V de diseno 180 km/h -> 50 m/s [D] (guide, design 180)
CH_RANGE = (0.01, 0.05)  # rango razonable de Ch de bisagra de elevon [E]
N_SERVOS_PER_ELEVON = 2   # doble actuacion (ADR-0026)


def elevon_chord_avg():
    """Cuerda media del elevon = 0.28 * cuerda local media sobre el tramo 30-90 %."""
    eta = np.linspace(ETA_IN, ETA_OUT, 200)
    c_local = CR * (1 - (1 - TAPER) * eta)
    return ELEVON_CHORD_FRAC * c_local.mean()


def main():
    print("=" * 70)
    print("REQUISITO DE PAR DE SERVO — elevones Salamandra (todo [D]/[E])")
    print("=" * 70)
    print(f"  Cuerda raiz {CR*1000:.0f} mm, punta {CT*1000:.0f} mm")
    c_av = elevon_chord_avg()
    span_e = B / 2 * (ETA_OUT - ETA_IN)      # 390 mm
    s_control = span_e * c_av                 # superficie de un elevon, m^2
    print(f"  Elevon: cuerda media {c_av*1000:.0f} mm, vano {span_e*1000:.0f} mm, "
          f"S_control = {s_control*1e4:.0f} cm^2 = {s_control*1e2:.1f} dm^2")
    print(f"  V diseno = {V_NE*3.6:.0f} km/h, rho = {RHO} kg/m^3")

    print("\n  Par de bisagra por elevon  (Mh = 0.5 rho V^2 S c Ch):")
    for ch in CH_RANGE:
        mh = 0.5 * RHO * V_NE**2 * s_control * c_av * ch
        mh_servo = mh / N_SERVOS_PER_ELEVON
        print(f"    Ch={ch:.2f}: Mh={mh*1000:.0f} mN.m -> por servo "
              f"{mh_servo*1000:.0f} mN.m ({mh_servo*0.0102*1000:.2f} g.cm)")

    print("\n  Comparacion con el catalogo (I-18): el MG90S mas modesto da")
    print("  ~180 g.cm; el peor caso Mh ~ 49 g.cm por servo. Margen >= 3.7x, y")
    print("  con doble actuacion el margen efectivo es >= 7x. CONCL: el par")
    print("  NO es el driver; la seleccion la domina rigidez/masa/precio.")


if __name__ == "__main__":
    main()
