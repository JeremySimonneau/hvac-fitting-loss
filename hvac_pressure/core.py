"""
core.py — Core HVAC pressure drop calculation functions.

All functions accept and return SI units unless explicitly stated.
  - Lengths / diameters : metres (m)
  - Roughness           : metres (m)
  - Airflow             : m³/s
  - Velocity            : m/s
  - Pressure            : Pascals (Pa)
  - Density             : kg/m³
"""

import math
from typing import Optional, Tuple
from .units import air_density
from .interpolation import interp1d, interp2d, interp3d
from .data.ashrae_tables import get_fitting, FITTING_REGISTRY


# ---------------------------------------------------------------------------
# Velocity and velocity pressure
# ---------------------------------------------------------------------------

def velocity(flow_m3s: float, area_m2: float) -> float:
    """
    Calculate mean air velocity.

    Parameters
    ----------
    flow_m3s : float
        Volumetric airflow in m³/s.
    area_m2 : float
        Cross-sectional area in m².

    Returns
    -------
    float
        Mean velocity in m/s.
    """
    if area_m2 <= 0:
        raise ValueError("Cross-sectional area must be positive.")
    return flow_m3s / area_m2


def velocity_pressure(v_ms: float, rho: float = 1.204) -> float:
    """
    Calculate velocity pressure (dynamic pressure).

    Pv = ½ × ρ × V²

    Parameters
    ----------
    v_ms : float
        Air velocity in m/s.
    rho : float
        Air density in kg/m³. Default 1.204 kg/m³ (20 °C, sea level).

    Returns
    -------
    float
        Velocity pressure in Pa.
    """
    return 0.5 * rho * v_ms ** 2


# ---------------------------------------------------------------------------
# Duct cross-section geometry
# ---------------------------------------------------------------------------

def round_area(diameter_m: float) -> float:
    """Cross-sectional area of a round duct in m²."""
    return math.pi * (diameter_m / 2) ** 2


def rectangular_area(width_m: float, height_m: float) -> float:
    """Cross-sectional area of a rectangular duct in m²."""
    return width_m * height_m


def rectangular_hydraulic_diameter(width_m: float, height_m: float) -> float:
    """
    Hydraulic diameter of a rectangular duct.

    Dh = 4A / P = 2WH / (W + H)

    Parameters
    ----------
    width_m : float
        Duct width in metres.
    height_m : float
        Duct height in metres.

    Returns
    -------
    float
        Hydraulic diameter in metres.
    """
    return (2 * width_m * height_m) / (width_m + height_m)


def flat_oval_hydraulic_diameter(major_m: float, minor_m: float) -> float:
    """
    Hydraulic (equivalent) diameter of a flat oval duct.

    Uses the ASHRAE approximation:
        Dh = (1.55 × A^0.625) / P^0.25
    where A = cross-sectional area and P = perimeter.

    Parameters
    ----------
    major_m : float
        Major axis (long dimension) in metres.
    minor_m : float
        Minor axis (short dimension) in metres.

    Returns
    -------
    float
        Hydraulic diameter in metres.
    """
    # Area and perimeter of flat oval
    r = minor_m / 2
    A = math.pi * r ** 2 + minor_m * (major_m - minor_m)
    P = math.pi * minor_m + 2 * (major_m - minor_m)
    return 1.55 * (A ** 0.625) / (P ** 0.25)


# ---------------------------------------------------------------------------
# Friction factor (Colebrook-White / Swamee-Jain)
# ---------------------------------------------------------------------------

def friction_factor(Re: float, roughness_m: float, diameter_m: float) -> float:
    """
    Darcy-Weisbach friction factor using the Swamee-Jain explicit approximation
    to the Colebrook-White equation.

    Valid for: 5 × 10³ ≤ Re ≤ 10⁸ and 10⁻⁶ ≤ ε/D ≤ 10⁻².

    For laminar flow (Re < 2300): f = 64 / Re.
    For transitional flow (2300 ≤ Re < 4000): linear interpolation.

    Parameters
    ----------
    Re : float
        Reynolds number (dimensionless).
    roughness_m : float
        Absolute roughness ε in metres.
    diameter_m : float
        Hydraulic diameter in metres.

    Returns
    -------
    float
        Darcy friction factor (dimensionless).
    """
    if Re <= 0:
        raise ValueError("Reynolds number must be positive.")

    if Re < 2300:
        # Laminar flow
        return 64.0 / Re

    relative_roughness = roughness_m / diameter_m

    # Turbulent — Swamee-Jain explicit approximation
    f_turb = 0.25 / (
        math.log10(relative_roughness / 3.7 + 5.74 / (Re ** 0.9)) ** 2
    )

    if Re >= 4000:
        return f_turb

    # Transitional (2300–4000): linear blend between laminar and turbulent
    f_lam = 64.0 / 2300.0
    t = (Re - 2300) / (4000 - 2300)
    return f_lam + t * (f_turb - f_lam)


def reynolds_number(v_ms: float, diameter_m: float,
                    temp_c: float = 20.0) -> float:
    """
    Calculate Reynolds number for air in a duct.

    Re = V × D / ν

    Parameters
    ----------
    v_ms : float
        Air velocity in m/s.
    diameter_m : float
        Hydraulic diameter in metres.
    temp_c : float
        Air temperature in °C. Default 20 °C.

    Returns
    -------
    float
        Reynolds number (dimensionless).
    """
    # Kinematic viscosity of air (Sutherland's law approximation)
    # ν ≈ 1.458e-6 × T^1.5 / (T + 110.4) / ρ  — simplified to:
    T = temp_c + 273.15
    mu = 1.458e-6 * T ** 1.5 / (T + 110.4)  # dynamic viscosity Pa·s
    rho = air_density(temp_c)
    nu = mu / rho  # kinematic viscosity m²/s
    return v_ms * diameter_m / nu


# ---------------------------------------------------------------------------
# Straight duct pressure loss (Darcy-Weisbach)
# ---------------------------------------------------------------------------

def duct_loss(
    flow_m3s: float,
    length_m: float,
    diameter_m: float,
    roughness_m: float = 0.00009,
    temp_c: float = 20.0,
    altitude_m: float = 0.0,
) -> dict:
    """
    Calculate pressure loss in a straight round duct using Darcy-Weisbach.

    ΔP = f × (L/D) × Pv

    Parameters
    ----------
    flow_m3s : float
        Volumetric airflow in m³/s.
    length_m : float
        Duct length in metres.
    diameter_m : float
        Internal diameter in metres.
    roughness_m : float
        Absolute wall roughness ε in metres. Default 0.09 mm (galvanised steel).
    temp_c : float
        Air temperature in °C. Default 20 °C.
    altitude_m : float
        Altitude above sea level in metres. Default 0 (sea level).

    Returns
    -------
    dict with keys:
        'delta_p_pa'   : float — pressure loss in Pa
        'velocity_ms'  : float — mean velocity in m/s
        'pv_pa'        : float — velocity pressure in Pa
        'friction_f'   : float — Darcy friction factor
        'reynolds'     : float — Reynolds number
        'warnings'     : list of str — any out-of-range warnings
    """
    # Atmospheric pressure correction for altitude
    p_atm = 101325.0 * (1 - 2.2557e-5 * altitude_m) ** 5.2559
    rho = air_density(temp_c, p_atm)

    area = round_area(diameter_m)
    v = velocity(flow_m3s, area)
    pv = velocity_pressure(v, rho)
    Re = reynolds_number(v, diameter_m, temp_c)
    f = friction_factor(Re, roughness_m, diameter_m)

    delta_p = f * (length_m / diameter_m) * pv

    warnings = []
    if Re < 2300:
        warnings.append(f"Laminar flow detected (Re = {Re:.0f}). "
                        "Darcy-Weisbach is less accurate in this regime.")
    if v > 20.0:
        warnings.append(f"High velocity ({v:.1f} m/s). Verify duct sizing.")
    if roughness_m / diameter_m > 0.05:
        warnings.append("Relative roughness ε/D > 0.05. Consider a larger duct.")

    return {
        "delta_p_pa": delta_p,
        "velocity_ms": v,
        "pv_pa": pv,
        "friction_f": f,
        "reynolds": Re,
        "warnings": warnings,
    }


def rectangular_duct_loss(
    flow_m3s: float,
    length_m: float,
    width_m: float,
    height_m: float,
    roughness_m: float = 0.00009,
    temp_c: float = 20.0,
    altitude_m: float = 0.0,
) -> dict:
    """
    Calculate pressure loss in a straight rectangular duct.

    Uses the hydraulic diameter Dh = 2WH/(W+H) in the Darcy-Weisbach equation.

    Parameters
    ----------
    flow_m3s : float
        Volumetric airflow in m³/s.
    length_m : float
        Duct length in metres.
    width_m : float
        Internal duct width in metres.
    height_m : float
        Internal duct height in metres.
    roughness_m : float
        Absolute wall roughness ε in metres.
    temp_c : float
        Air temperature in °C.
    altitude_m : float
        Altitude above sea level in metres.

    Returns
    -------
    dict — same structure as duct_loss().
    """
    Dh = rectangular_hydraulic_diameter(width_m, height_m)
    return duct_loss(flow_m3s, length_m, Dh, roughness_m, temp_c, altitude_m)


# ---------------------------------------------------------------------------
# Fitting pressure loss (ASHRAE C-coefficient method)
# ---------------------------------------------------------------------------

def fitting_loss(
    code: str,
    flow_m3s: float,
    diameter_m: Optional[float] = None,
    width_m: Optional[float] = None,
    height_m: Optional[float] = None,
    temp_c: float = 20.0,
    altitude_m: float = 0.0,
    **params,
) -> dict:
    """
    Calculate pressure loss for an ASHRAE fitting using ΔP = C × Pv.

    The loss coefficient C is looked up from the ASHRAE table and interpolated
    for the user's geometry parameters.

    Parameters
    ----------
    code : str
        ASHRAE fitting code, e.g. 'CD3-12', 'CR3-1', 'SR5-1'.
    flow_m3s : float
        Upstream volumetric airflow in m³/s.
    diameter_m : float, optional
        Upstream duct diameter in metres (round ducts).
    width_m : float, optional
        Upstream duct width in metres (rectangular ducts).
    height_m : float, optional
        Upstream duct height in metres (rectangular ducts).
    temp_c : float
        Air temperature in °C. Default 20 °C.
    altitude_m : float
        Altitude above sea level in metres.
    **params : keyword arguments
        Geometry parameters required by the specific fitting.
        The required parameter names are listed in the fitting's 'params' entry.
        Examples:
          - CD3-12: r_over_D=1.0
          - CR3-1:  r_over_W=1.0, H_over_W=1.0, theta_deg=90
          - SR5-1:  As_over_Ac=0.5, Ab_over_Ac=0.5, Qb_over_Qc=0.4

    Returns
    -------
    dict with keys:
        'delta_p_pa'   : float — pressure loss in Pa (branch loss for tees)
        'delta_p2_pa'  : float — straight path loss in Pa (tees only, else None)
        'C'            : float — resolved loss coefficient
        'C2'           : float — straight path C (tees only, else None)
        'velocity_ms'  : float — upstream velocity in m/s
        'pv_pa'        : float — upstream velocity pressure in Pa
        'warnings'     : list of str

    Raises
    ------
    KeyError
        If the fitting code is not found.
    ValueError
        If required geometry parameters are missing.
    """
    fitting = get_fitting(code)

    # Determine upstream area and hydraulic diameter
    if fitting["shape"] == "round":
        if diameter_m is None:
            raise ValueError(f"Fitting {code} requires 'diameter_m'.")
        area_m2 = round_area(diameter_m)
        Dh = diameter_m
    else:
        if width_m is None or height_m is None:
            raise ValueError(f"Fitting {code} requires 'width_m' and 'height_m'.")
        area_m2 = rectangular_area(width_m, height_m)
        Dh = rectangular_hydraulic_diameter(width_m, height_m)

    p_atm = 101325.0 * (1 - 2.2557e-5 * altitude_m) ** 5.2559
    rho = air_density(temp_c, p_atm)
    v = velocity(flow_m3s, area_m2)
    pv = velocity_pressure(v, rho)

    dims = fitting["dims"]
    warnings = []

    # --- Resolve C coefficient ---
    if dims == 0:
        # Constant
        C = fitting["c"]
        C2 = None

    elif dims == 1:
        p = fitting["params"][0]
        p_name = p["name"]
        if p_name not in params:
            raise ValueError(
                f"Fitting {code} requires parameter '{p_name}' "
                f"({p['label']}, unit: {p['unit']})."
            )
        C = interp1d(p["values"], fitting["c"], params[p_name])
        C2 = None

        # Special case: ED2-1 applies formula C_o = C1 × (Ao/A1)²
        if code == "ED2-1":
            raise ValueError(
                "ED2-1 is a 2D fitting. Use dims=2 path. "
                "Call fitting_loss('ED2-1', ..., A1_over_Ao=..., L_over_Do=...)."
            )

    elif dims == 2:
        p1 = fitting["params"][0]
        p2 = fitting["params"][1]
        p1_name, p2_name = p1["name"], p2["name"]

        missing = [n for n in [p1_name, p2_name] if n not in params]
        if missing:
            raise ValueError(
                f"Fitting {code} requires parameters: "
                + ", ".join(f"'{n}'" for n in [p1_name, p2_name])
                + f". Missing: {missing}."
            )

        C = interp2d(
            p1["values"], p2["values"], fitting["c"],
            params[p1_name], params[p2_name],
        )
        C2 = None

        # CR3-1: apply angle factor K for non-90° bends
        if code == "CR3-1":
            theta = params.get("theta_deg", 90.0)
            af = fitting["angle_factor"]
            K = interp1d(af["theta_vals"], af["K_vals"], theta)
            C = K * C

        # ED2-1: apply formula C_o = C1 × (Ao/A1)²
        if code == "ED2-1":
            A1_over_Ao = params.get("A1_over_Ao", 1.0)
            if A1_over_Ao <= 0:
                raise ValueError("A1_over_Ao must be positive.")
            Ao_over_A1 = 1.0 / A1_over_Ao
            C = C * (Ao_over_A1 ** 2)

    elif dims == 3:
        p1 = fitting["params"][0]
        p2 = fitting["params"][1]
        p3 = fitting["params"][2]
        p1_name, p2_name, p3_name = p1["name"], p2["name"], p3["name"]

        missing = [n for n in [p1_name, p2_name, p3_name] if n not in params]
        if missing:
            raise ValueError(
                f"Fitting {code} requires parameters: "
                + ", ".join(f"'{n}'" for n in [p1_name, p2_name, p3_name])
                + f". Missing: {missing}."
            )

        C = interp3d(
            p1["values"], p2["values"], p3["values"], fitting["c"],
            params[p1_name], params[p2_name], params[p3_name],
        )
        C2 = interp3d(
            p1["values"], p2["values"], p3["values"], fitting["c2"],
            params[p1_name], params[p2_name], params[p3_name],
        )
    else:
        raise ValueError(f"Unknown table dimension: {dims}")

    delta_p = C * pv
    delta_p2 = C2 * pv if C2 is not None else None

    if v > 20.0:
        warnings.append(f"High velocity ({v:.1f} m/s). Verify duct sizing.")

    return {
        "delta_p_pa": delta_p,
        "delta_p2_pa": delta_p2,
        "C": C,
        "C2": C2,
        "velocity_ms": v,
        "pv_pa": pv,
        "warnings": warnings,
    }


# ---------------------------------------------------------------------------
# Filter pressure loss
# ---------------------------------------------------------------------------

def filter_loss(
    rated_drop_pa: float,
    rated_flow_m3s: float,
    actual_flow_m3s: float,
) -> dict:
    """
    Calculate filter pressure drop using the square-law scaling formula.

    ΔP_actual = ΔP_rated × (Q_actual / Q_rated)²

    Parameters
    ----------
    rated_drop_pa : float
        Manufacturer-rated pressure drop in Pa at the rated airflow.
    rated_flow_m3s : float
        Manufacturer-rated airflow in m³/s.
    actual_flow_m3s : float
        Actual system airflow through the filter in m³/s.

    Returns
    -------
    dict with keys:
        'delta_p_pa' : float — actual pressure drop in Pa
        'scale_ratio': float — (Q_actual / Q_rated)²
        'warnings'   : list of str
    """
    if rated_flow_m3s <= 0:
        raise ValueError("Rated airflow must be positive.")

    ratio = actual_flow_m3s / rated_flow_m3s
    delta_p = rated_drop_pa * ratio ** 2

    warnings = []
    if ratio > 1.5:
        warnings.append(
            f"Actual flow is {ratio:.1f}× the rated flow. "
            "Verify filter selection — pressure drop may be very high."
        )
    if ratio < 0.5:
        warnings.append(
            f"Actual flow is only {ratio:.1%} of rated flow. "
            "Square-law scaling may be less accurate at very low flow ratios."
        )

    return {
        "delta_p_pa": delta_p,
        "scale_ratio": ratio ** 2,
        "warnings": warnings,
    }


# ---------------------------------------------------------------------------
# Custom element (fixed pressure drop)
# ---------------------------------------------------------------------------

def custom_loss(delta_p_pa: float) -> dict:
    """
    User-defined fixed pressure drop element.

    Parameters
    ----------
    delta_p_pa : float
        Fixed pressure drop in Pa.

    Returns
    -------
    dict with keys:
        'delta_p_pa' : float
        'warnings'   : list of str
    """
    warnings = []
    if delta_p_pa < 0:
        warnings.append("Negative pressure drop entered. Verify intent.")
    return {"delta_p_pa": delta_p_pa, "warnings": warnings}
