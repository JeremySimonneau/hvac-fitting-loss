"""
system.py — System class for chaining duct elements and computing total
            static pressure loss.

Usage example
-------------
>>> import hvac_pressure as hp
>>> sys = hp.System(flow_m3s=0.5, temp_c=20)
>>> sys.add_duct(length_m=10, diameter_m=0.3)
>>> sys.add_fitting('CD3-12', diameter_m=0.3, r_over_D=1.0)
>>> sys.add_filter(rated_drop_pa=50, rated_flow_m3s=0.5)
>>> print(sys.total_pa())
>>> print(sys.report())
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any
from .core import (
    duct_loss, rectangular_duct_loss, fitting_loss,
    filter_loss, custom_loss,
)
from .units import (
    pa_to_inwg, pa_to_mmwg, m3s_to_m3h, m3s_to_cfm,
    ms_to_fpm,
)


@dataclass
class Element:
    """Represents a single element in the duct system."""
    label: str
    element_type: str          # 'duct', 'fitting', 'filter', 'custom'
    delta_p_pa: float
    velocity_ms: Optional[float] = None
    pv_pa: Optional[float] = None
    C: Optional[float] = None
    warnings: List[str] = field(default_factory=list)
    details: dict = field(default_factory=dict)


class System:
    """
    A linear duct system — a series of elements whose pressure drops are summed.

    Parameters
    ----------
    flow_m3s : float
        System design airflow in m³/s. Used as the default flow for all
        elements unless overridden per element.
    temp_c : float
        Air temperature in °C. Default 20 °C.
    altitude_m : float
        Altitude above sea level in metres. Default 0.
    name : str
        Optional system name for reports.
    """

    def __init__(
        self,
        flow_m3s: float,
        temp_c: float = 20.0,
        altitude_m: float = 0.0,
        name: str = "Duct System",
    ):
        self.flow_m3s = flow_m3s
        self.temp_c = temp_c
        self.altitude_m = altitude_m
        self.name = name
        self._elements: List[Element] = []

    # ------------------------------------------------------------------
    # Element addition methods
    # ------------------------------------------------------------------

    def add_duct(
        self,
        length_m: float,
        diameter_m: Optional[float] = None,
        width_m: Optional[float] = None,
        height_m: Optional[float] = None,
        roughness_m: float = 0.00009,
        flow_m3s: Optional[float] = None,
        label: Optional[str] = None,
    ) -> "System":
        """
        Add a straight duct section (round or rectangular).

        For round ducts, supply `diameter_m`.
        For rectangular ducts, supply `width_m` and `height_m`.
        """
        Q = flow_m3s if flow_m3s is not None else self.flow_m3s
        n = len(self._elements) + 1
        lbl = label or f"Duct {n}"

        if diameter_m is not None:
            result = duct_loss(Q, length_m, diameter_m, roughness_m,
                               self.temp_c, self.altitude_m)
            shape_str = f"Round Ø{diameter_m*1000:.0f} mm"
        elif width_m is not None and height_m is not None:
            result = rectangular_duct_loss(Q, length_m, width_m, height_m,
                                           roughness_m, self.temp_c, self.altitude_m)
            shape_str = f"Rect {width_m*1000:.0f}×{height_m*1000:.0f} mm"
        else:
            raise ValueError("Supply either 'diameter_m' or 'width_m' + 'height_m'.")

        self._elements.append(Element(
            label=lbl,
            element_type="duct",
            delta_p_pa=result["delta_p_pa"],
            velocity_ms=result["velocity_ms"],
            pv_pa=result["pv_pa"],
            C=result["friction_f"],
            warnings=result["warnings"],
            details={
                "shape": shape_str,
                "length_m": length_m,
                "roughness_mm": roughness_m * 1000,
                "Re": result["reynolds"],
                "f": result["friction_f"],
            },
        ))
        return self

    def add_fitting(
        self,
        code: str,
        diameter_m: Optional[float] = None,
        width_m: Optional[float] = None,
        height_m: Optional[float] = None,
        flow_m3s: Optional[float] = None,
        label: Optional[str] = None,
        **params,
    ) -> "System":
        """
        Add an ASHRAE fitting element.

        Parameters
        ----------
        code : str
            ASHRAE fitting code (e.g. 'CD3-12', 'CR3-1').
        diameter_m : float, optional
            Upstream duct diameter in metres (round fittings).
        width_m : float, optional
            Upstream duct width in metres (rectangular fittings).
        height_m : float, optional
            Upstream duct height in metres (rectangular fittings).
        flow_m3s : float, optional
            Override system flow for this element.
        label : str, optional
            Display label. Defaults to fitting code.
        **params :
            Geometry parameters required by the fitting
            (e.g. r_over_D=1.0, theta_deg=90).
        """
        Q = flow_m3s if flow_m3s is not None else self.flow_m3s
        lbl = label or f"Fitting {code}"

        result = fitting_loss(
            code, Q,
            diameter_m=diameter_m,
            width_m=width_m,
            height_m=height_m,
            temp_c=self.temp_c,
            altitude_m=self.altitude_m,
            **params,
        )

        self._elements.append(Element(
            label=lbl,
            element_type="fitting",
            delta_p_pa=result["delta_p_pa"],
            velocity_ms=result["velocity_ms"],
            pv_pa=result["pv_pa"],
            C=result["C"],
            warnings=result["warnings"],
            details={
                "code": code,
                "params": params,
                "C2": result.get("C2"),
                "delta_p2_pa": result.get("delta_p2_pa"),
            },
        ))
        return self

    def add_filter(
        self,
        rated_drop_pa: float,
        rated_flow_m3s: float,
        actual_flow_m3s: Optional[float] = None,
        label: Optional[str] = None,
    ) -> "System":
        """
        Add a filter element.

        Parameters
        ----------
        rated_drop_pa : float
            Manufacturer-rated pressure drop in Pa at rated flow.
        rated_flow_m3s : float
            Manufacturer-rated airflow in m³/s.
        actual_flow_m3s : float, optional
            Actual system flow through the filter. Defaults to system flow.
        label : str, optional
            Display label.
        """
        Q = actual_flow_m3s if actual_flow_m3s is not None else self.flow_m3s
        n = len(self._elements) + 1
        lbl = label or f"Filter {n}"

        result = filter_loss(rated_drop_pa, rated_flow_m3s, Q)

        self._elements.append(Element(
            label=lbl,
            element_type="filter",
            delta_p_pa=result["delta_p_pa"],
            warnings=result["warnings"],
            details={
                "rated_drop_pa": rated_drop_pa,
                "rated_flow_m3h": m3s_to_m3h(rated_flow_m3s),
                "actual_flow_m3h": m3s_to_m3h(Q),
                "scale_ratio": result["scale_ratio"],
            },
        ))
        return self

    def add_custom(
        self,
        delta_p_pa: float,
        label: Optional[str] = None,
    ) -> "System":
        """
        Add a custom element with a fixed pressure drop.

        Parameters
        ----------
        delta_p_pa : float
            Fixed pressure drop in Pa.
        label : str, optional
            Display label.
        """
        n = len(self._elements) + 1
        lbl = label or f"Custom {n}"
        result = custom_loss(delta_p_pa)
        self._elements.append(Element(
            label=lbl,
            element_type="custom",
            delta_p_pa=result["delta_p_pa"],
            warnings=result["warnings"],
        ))
        return self

    # ------------------------------------------------------------------
    # Results
    # ------------------------------------------------------------------

    def total_pa(self) -> float:
        """Total system pressure loss in Pa."""
        return sum(e.delta_p_pa for e in self._elements)

    def total_inwg(self) -> float:
        """Total system pressure loss in inches of water gauge."""
        return pa_to_inwg(self.total_pa())

    def total_mmwg(self) -> float:
        """Total system pressure loss in mm of water gauge."""
        return pa_to_mmwg(self.total_pa())

    def elements(self) -> List[Element]:
        """Return the list of elements."""
        return list(self._elements)

    def all_warnings(self) -> List[str]:
        """Return all warnings from all elements."""
        out = []
        for e in self._elements:
            for w in e.warnings:
                out.append(f"[{e.label}] {w}")
        return out

    def report(self, unit: str = "SI") -> str:
        """
        Generate a formatted text report of the system.

        Parameters
        ----------
        unit : str
            'SI' for Pa / m³/h / m/s, or 'IP' for in.w.g. / CFM / fpm.

        Returns
        -------
        str
            Multi-line formatted report.
        """
        use_ip = unit.upper() == "IP"

        def _p(pa):
            return f"{pa_to_inwg(pa):.4f} in.w.g." if use_ip else f"{pa:.2f} Pa"

        def _v(ms):
            if ms is None:
                return "—"
            return f"{ms_to_fpm(ms):.0f} fpm" if use_ip else f"{ms:.2f} m/s"

        def _q(m3s):
            return f"{m3s_to_cfm(m3s):.1f} CFM" if use_ip else f"{m3s_to_m3h(m3s):.1f} m³/h"

        lines = [
            "=" * 72,
            f"  HVAC Static Pressure Report — {self.name}",
            "=" * 72,
            f"  System airflow : {_q(self.flow_m3s)}",
            f"  Temperature    : {self.temp_c:.1f} °C",
            f"  Altitude       : {self.altitude_m:.0f} m",
            "-" * 72,
            f"  {'#':<3}  {'Label':<28}  {'Type':<10}  {'Velocity':<12}  {'ΔP':>12}  {'Cumul.':>12}",
            "-" * 72,
        ]

        cumul = 0.0
        for i, e in enumerate(self._elements, 1):
            cumul += e.delta_p_pa
            lines.append(
                f"  {i:<3}  {e.label:<28}  {e.element_type:<10}  "
                f"{_v(e.velocity_ms):<12}  {_p(e.delta_p_pa):>12}  {_p(cumul):>12}"
            )
            if e.warnings:
                for w in e.warnings:
                    lines.append(f"       ⚠  {w}")

        lines += [
            "-" * 72,
            f"  {'TOTAL SYSTEM PRESSURE LOSS':>55}  {_p(self.total_pa()):>12}",
            "=" * 72,
        ]
        return "\n".join(lines)

    def to_dict(self) -> dict:
        """
        Return a JSON-serialisable dict of the full system results.
        Suitable for use in a REST API response.
        """
        elements_out = []
        cumul = 0.0
        for e in self._elements:
            cumul += e.delta_p_pa
            elements_out.append({
                "label": e.label,
                "type": e.element_type,
                "delta_p_pa": round(e.delta_p_pa, 4),
                "delta_p_inwg": round(pa_to_inwg(e.delta_p_pa), 5),
                "cumulative_pa": round(cumul, 4),
                "cumulative_inwg": round(pa_to_inwg(cumul), 5),
                "velocity_ms": round(e.velocity_ms, 3) if e.velocity_ms else None,
                "velocity_fpm": round(ms_to_fpm(e.velocity_ms), 1) if e.velocity_ms else None,
                "pv_pa": round(e.pv_pa, 4) if e.pv_pa else None,
                "C": round(e.C, 4) if e.C else None,
                "warnings": e.warnings,
                "details": e.details,
            })
        return {
            "name": self.name,
            "flow_m3s": self.flow_m3s,
            "flow_m3h": round(m3s_to_m3h(self.flow_m3s), 2),
            "flow_cfm": round(m3s_to_cfm(self.flow_m3s), 2),
            "temp_c": self.temp_c,
            "altitude_m": self.altitude_m,
            "total_pa": round(self.total_pa(), 4),
            "total_inwg": round(self.total_inwg(), 5),
            "total_mmwg": round(self.total_mmwg(), 3),
            "elements": elements_out,
            "warnings": self.all_warnings(),
        }
