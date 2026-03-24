# hvac_pressure

A pure Python library for calculating static pressure losses in HVAC duct systems.

`hvac_pressure` implements the Darcy-Weisbach equation for straight ducts and includes a built-in interpolation engine for ASHRAE fitting loss coefficients (based on the 2009 ASHRAE Handbook — Fundamentals, Chapter 21).

It is designed to be the calculation engine behind HVAC design tools, web apps, and automated sizing scripts.

## Features

- **Straight Ducts**: Darcy-Weisbach friction loss with Colebrook-White / Swamee-Jain approximations. Supports round, rectangular, and flat oval ducts.
- **ASHRAE Fittings**: Built-in database of the 15 most common ASHRAE fittings (elbows, tees, transitions, dampers, entries/exits).
- **Interpolation Engine**: Automatically performs 1D, 2D, and 3D linear interpolation on ASHRAE tables based on your exact geometry (e.g., `r/D`, `H/W`, `θ`).
- **Filters & Dampers**: Square-law scaling for filters and blade-angle C-value lookups for dampers.
- **System Chaining**: A `System` class to chain elements together and generate pressure drop reports.
- **Unit Conversion**: Internal calculations are strictly SI (Pa, m³/s, m/s, m), with helper functions for Imperial units (CFM, in.w.g., fpm).
- **Zero Dependencies**: Pure Python, no external libraries required.

## Installation

*(Note: This package is not yet on PyPI. You can install it locally or drop the `hvac_pressure` folder into your project.)*

```bash
pip install .
```

## Quick Start

### 1. Single Element Calculation

```python
import hvac_pressure as hp

# Straight duct (SI units: m³/s, m)
result = hp.duct_loss(flow_m3s=0.5, length_m=10, diameter_m=0.3)
print(f"Duct loss: {result['delta_p_pa']:.2f} Pa")

# ASHRAE Fitting (CD3-12: 3-gore round elbow)
# The library automatically interpolates the C value for r/D = 1.2
result = hp.fitting_loss('CD3-12', flow_m3s=0.5, diameter_m=0.3, r_over_D=1.2)
print(f"Fitting loss: {result['delta_p_pa']:.2f} Pa (C = {result['C']:.3f})")
```

### 2. Full System Calculation

The `System` class makes it easy to build a duct branch and get a total pressure drop.

```python
import hvac_pressure as hp

# Create a system with a design flow of 0.5 m³/s (approx 1060 CFM)
sys = hp.System(flow_m3s=0.5, temp_c=20, name="AHU-1 Supply Main")

# Add elements in order
sys.add_duct(length_m=15.0, diameter_m=0.3, label="Main straight")
sys.add_fitting("CD3-12", diameter_m=0.3, r_over_D=1.5, label="90° Elbow")
sys.add_filter(rated_drop_pa=125.0, rated_flow_m3s=0.6, label="Pre-filter")
sys.add_fitting("CD9-1", diameter_m=0.3, theta_deg=20, label="Balancing Damper")

# Get total pressure drop
print(f"Total Pressure: {sys.total_pa():.1f} Pa")
print(f"Total Pressure: {sys.total_inwg():.4f} in.w.g.")

# Print a formatted report
print(sys.report(unit="IP"))  # 'IP' for Imperial, 'SI' for metric
```

**Output:**
```text
========================================================================
  HVAC Static Pressure Report — AHU-1 Supply Main
========================================================================
  System airflow : 1059.4 CFM
  Temperature    : 20.0 °C
  Altitude       : 0 m
------------------------------------------------------------------------
  #    Label                         Type        Velocity      ΔP        Cumul.
------------------------------------------------------------------------
  1    Main straight                 duct        1393 fpm  0.1164 in.w.g.  0.1164 in.w.g.
  2    90° Elbow                     fitting     1393 fpm  0.0181 in.w.g.  0.1345 in.w.g.
  3    Pre-filter                    filter      —         0.3486 in.w.g.  0.4831 in.w.g.
  4    Balancing Damper              fitting     1393 fpm  0.1863 in.w.g.  0.6694 in.w.g.
------------------------------------------------------------------------
                               TOTAL SYSTEM PRESSURE LOSS  0.6694 in.w.g.
========================================================================
```

## Available ASHRAE Fittings

The library currently includes the following fitting tables:

| Code | Description | Required Parameters |
|---|---|---|
| **CD3-1** | Round elbow, die stamped 90° | `D_mm` |
| **CD3-5** | Round elbow, pleated 90° | `D_mm` |
| **CD3-9** | Round elbow, 5-gore 90° | `D_mm` |
| **CD3-12** | Round elbow, 3-gore | `r_over_D` |
| **CD3-17** | Round elbow, mitered 45° | `D_mm` |
| **CD9-1** | Round butterfly damper | `theta_deg` |
| **CD9-3** | Round fire damper | *(none)* |
| **ED1-3** | Bellmouth entry (exhaust) | `r_over_D` |
| **SD1-1** | Bellmouth entry (supply) | `r_over_Do` |
| **ED2-1** | Conical diffuser | `A1_over_Ao`, `L_over_Do` |
| **CR3-1** | Rectangular elbow, smooth | `r_over_W`, `H_over_W`, `theta_deg` |
| **CR3-6** | Rectangular elbow, mitered | `theta_deg`, `H_over_W` |
| **CR3-9** | Rectangular elbow, mitered w/ vanes | *(none)* |
| **CR9-1** | Rectangular butterfly damper | `theta_deg`, `H_over_W` |
| **SR4-1** | Rectangular transition | `Ao_over_A1`, `theta_deg` |
| **SR5-1** | Rectangular wye (tee), diverging | `As_over_Ac`, `Ab_over_Ac`, `Qb_over_Qc` |

*Note: For `SR5-1` (tees), the function returns both `C` (branch loss) and `C2` (straight path loss).*

## API Integration

If you are building a web app (e.g., on Replit), you can easily expose the system calculation as a JSON endpoint:

```python
import json
import hvac_pressure as hp

sys = hp.System(flow_m3s=0.5)
sys.add_duct(length_m=10, diameter_m=0.3)
# ... add elements ...

# Returns a clean dictionary ready for JSON serialization
response_data = sys.to_dict()
print(json.dumps(response_data, indent=2))
```

## License

MIT License.
