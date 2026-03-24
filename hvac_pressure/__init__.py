"""
hvac_pressure — HVAC Static Pressure Loss Calculator
=====================================================

A Python library for calculating static pressure losses in HVAC duct systems.
Implements the Darcy-Weisbach equation for straight ducts and ASHRAE fitting
loss coefficients (2009 Handbook — Fundamentals, Chapter 21) for all fittings.

Quick start
-----------
>>> import hvac_pressure as hp

>>> # Single duct section
>>> result = hp.duct_loss(flow_m3s=0.5, length_m=10, diameter_m=0.3)
>>> print(f"ΔP = {result['delta_p_pa']:.2f} Pa")

>>> # ASHRAE fitting
>>> result = hp.fitting_loss('CD3-12', flow_m3s=0.5, diameter_m=0.3, r_over_D=1.0)
>>> print(f"ΔP = {result['delta_p_pa']:.2f} Pa  (C = {result['C']:.3f})")

>>> # Full system
>>> sys = hp.System(flow_m3s=0.5, temp_c=20, name="AHU-1 Supply")
>>> sys.add_duct(length_m=10, diameter_m=0.3)
>>> sys.add_fitting('CD3-12', diameter_m=0.3, r_over_D=1.0)
>>> sys.add_filter(rated_drop_pa=50, rated_flow_m3s=0.5)
>>> print(sys.report())
>>> print(f"Total: {sys.total_inwg():.4f} in.w.g.")

Available fitting codes
-----------------------
CD3-1, CD3-5, CD3-9, CD3-12, CD3-17  — Round elbows
CD9-1, CD9-3                          — Round dampers / fire dampers
ED1-3, SD1-1                          — Bellmouth entries
ED2-1                                 — Conical diffuser (round)
CR3-1, CR3-6, CR3-9                   — Rectangular elbows
CR9-1                                 — Rectangular butterfly damper
SR4-1                                 — Rectangular transition
SR5-1                                 — Rectangular wye (tee, diverging)
"""

__version__ = "0.1.0"
__author__ = "hvac_pressure contributors"
__license__ = "MIT"

from .core import (
    duct_loss,
    rectangular_duct_loss,
    fitting_loss,
    filter_loss,
    custom_loss,
    velocity,
    velocity_pressure,
    reynolds_number,
    friction_factor,
    round_area,
    rectangular_area,
    rectangular_hydraulic_diameter,
    flat_oval_hydraulic_diameter,
)

from .system import System, Element

from .data.ashrae_tables import list_fittings, get_fitting

from .units import (
    # Length
    mm_to_m, m_to_mm, inch_to_m, m_to_inch, ft_to_m, m_to_ft,
    # Airflow
    m3h_to_m3s, m3s_to_m3h, cfm_to_m3s, m3s_to_cfm, cfm_to_m3h, m3h_to_cfm,
    # Pressure
    pa_to_inwg, inwg_to_pa, pa_to_mmwg, mmwg_to_pa,
    # Velocity
    fpm_to_ms, ms_to_fpm,
    # Temperature
    celsius_to_kelvin, fahrenheit_to_kelvin,
    # Density
    air_density,
)

__all__ = [
    # Core calculations
    "duct_loss",
    "rectangular_duct_loss",
    "fitting_loss",
    "filter_loss",
    "custom_loss",
    # Geometry helpers
    "velocity",
    "velocity_pressure",
    "reynolds_number",
    "friction_factor",
    "round_area",
    "rectangular_area",
    "rectangular_hydraulic_diameter",
    "flat_oval_hydraulic_diameter",
    # System
    "System",
    "Element",
    # ASHRAE data
    "list_fittings",
    "get_fitting",
    # Units
    "mm_to_m", "m_to_mm", "inch_to_m", "m_to_inch", "ft_to_m", "m_to_ft",
    "m3h_to_m3s", "m3s_to_m3h", "cfm_to_m3s", "m3s_to_cfm",
    "cfm_to_m3h", "m3h_to_cfm",
    "pa_to_inwg", "inwg_to_pa", "pa_to_mmwg", "mmwg_to_pa",
    "fpm_to_ms", "ms_to_fpm",
    "celsius_to_kelvin", "fahrenheit_to_kelvin",
    "air_density",
]
