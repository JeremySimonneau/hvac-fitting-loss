"""
units.py — Unit conversion utilities for hvac_pressure.

All internal calculations are performed in SI units:
  - Lengths / diameters : metres (m)
  - Roughness           : metres (m)
  - Airflow             : cubic metres per second (m³/s)
  - Velocity            : metres per second (m/s)
  - Pressure            : Pascals (Pa)
  - Density             : kg/m³
  - Temperature         : Kelvin (K)

Helper functions convert to/from common Imperial and metric display units.
"""

# ---------------------------------------------------------------------------
# Length
# ---------------------------------------------------------------------------

def mm_to_m(v: float) -> float:
    """Millimetres → metres."""
    return v / 1000.0

def m_to_mm(v: float) -> float:
    """Metres → millimetres."""
    return v * 1000.0

def inch_to_m(v: float) -> float:
    """Inches → metres."""
    return v * 0.0254

def m_to_inch(v: float) -> float:
    """Metres → inches."""
    return v / 0.0254

def ft_to_m(v: float) -> float:
    """Feet → metres."""
    return v * 0.3048

def m_to_ft(v: float) -> float:
    """Metres → feet."""
    return v / 0.3048

# ---------------------------------------------------------------------------
# Airflow
# ---------------------------------------------------------------------------

def m3h_to_m3s(v: float) -> float:
    """m³/h → m³/s."""
    return v / 3600.0

def m3s_to_m3h(v: float) -> float:
    """m³/s → m³/h."""
    return v * 3600.0

def cfm_to_m3s(v: float) -> float:
    """CFM (ft³/min) → m³/s."""
    return v * 0.000471947

def m3s_to_cfm(v: float) -> float:
    """m³/s → CFM."""
    return v / 0.000471947

def cfm_to_m3h(v: float) -> float:
    """CFM → m³/h."""
    return v * 1.69901

def m3h_to_cfm(v: float) -> float:
    """m³/h → CFM."""
    return v / 1.69901

# ---------------------------------------------------------------------------
# Pressure
# ---------------------------------------------------------------------------

def pa_to_inwg(v: float) -> float:
    """Pascals → inches of water gauge (in. w.g.)."""
    return v * 0.00401463

def inwg_to_pa(v: float) -> float:
    """Inches of water gauge → Pascals."""
    return v / 0.00401463

def pa_to_mmwg(v: float) -> float:
    """Pascals → millimetres of water gauge (mm w.g.)."""
    return v * 0.101972

def mmwg_to_pa(v: float) -> float:
    """Millimetres of water gauge → Pascals."""
    return v / 0.101972

# ---------------------------------------------------------------------------
# Velocity
# ---------------------------------------------------------------------------

def fpm_to_ms(v: float) -> float:
    """Feet per minute → m/s."""
    return v * 0.00508

def ms_to_fpm(v: float) -> float:
    """m/s → feet per minute."""
    return v / 0.00508

# ---------------------------------------------------------------------------
# Temperature
# ---------------------------------------------------------------------------

def celsius_to_kelvin(v: float) -> float:
    """°C → K."""
    return v + 273.15

def fahrenheit_to_kelvin(v: float) -> float:
    """°F → K."""
    return (v - 32) * 5 / 9 + 273.15

# ---------------------------------------------------------------------------
# Air density
# ---------------------------------------------------------------------------

def air_density(temp_c: float = 20.0, pressure_pa: float = 101325.0) -> float:
    """
    Calculate dry air density using the ideal gas law.

    Parameters
    ----------
    temp_c : float
        Air temperature in °C. Default 20 °C.
    pressure_pa : float
        Absolute static pressure in Pa. Default 101 325 Pa (sea level).

    Returns
    -------
    float
        Air density in kg/m³.
    """
    R_air = 287.058  # J/(kg·K) — specific gas constant for dry air
    T = celsius_to_kelvin(temp_c)
    return pressure_pa / (R_air * T)
