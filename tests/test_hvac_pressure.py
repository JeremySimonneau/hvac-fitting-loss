"""
test_hvac_pressure.py — Comprehensive test suite for hvac_pressure library.

Tests are organised into sections:
  1. Unit conversions
  2. Interpolation engine
  3. Geometry helpers
  4. Friction factor and Reynolds number
  5. Straight duct losses
  6. ASHRAE fitting losses
  7. Filter losses
  8. System class
  9. Edge cases and error handling
"""

import math
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import hvac_pressure as hp
from hvac_pressure.interpolation import interp1d, interp2d, interp3d


# =============================================================================
# 1. Unit conversions
# =============================================================================

class TestUnits:
    def test_mm_to_m(self):
        assert hp.mm_to_m(300) == pytest.approx(0.3, rel=1e-6)

    def test_inch_to_m(self):
        assert hp.inch_to_m(12) == pytest.approx(0.3048, rel=1e-4)

    def test_ft_to_m(self):
        assert hp.ft_to_m(1) == pytest.approx(0.3048, rel=1e-6)

    def test_cfm_to_m3s(self):
        # 1000 CFM → 0.4719 m³/s
        assert hp.cfm_to_m3s(1000) == pytest.approx(0.47195, rel=1e-3)

    def test_m3h_to_m3s(self):
        assert hp.m3h_to_m3s(3600) == pytest.approx(1.0, rel=1e-6)

    def test_pa_to_inwg(self):
        # 1 in.w.g. = 249.089 Pa
        assert hp.pa_to_inwg(249.089) == pytest.approx(1.0, rel=1e-3)

    def test_inwg_to_pa(self):
        assert hp.inwg_to_pa(1.0) == pytest.approx(249.089, rel=1e-3)

    def test_pa_to_mmwg(self):
        # 1 mmwg ≈ 9.807 Pa
        assert hp.pa_to_mmwg(9.807) == pytest.approx(1.0, rel=1e-2)

    def test_fpm_to_ms(self):
        # 1000 fpm → 5.08 m/s
        assert hp.fpm_to_ms(1000) == pytest.approx(5.08, rel=1e-4)

    def test_air_density_standard(self):
        # At 20°C, sea level: ρ ≈ 1.204 kg/m³
        rho = hp.air_density(20.0, 101325.0)
        assert rho == pytest.approx(1.204, rel=1e-2)

    def test_air_density_hot(self):
        # Hotter air is less dense
        rho_cold = hp.air_density(10.0)
        rho_hot = hp.air_density(40.0)
        assert rho_hot < rho_cold

    def test_roundtrip_pressure(self):
        pa = 150.0
        assert hp.inwg_to_pa(hp.pa_to_inwg(pa)) == pytest.approx(pa, rel=1e-5)

    def test_roundtrip_flow(self):
        m3s = 0.5
        assert hp.cfm_to_m3s(hp.m3s_to_cfm(m3s)) == pytest.approx(m3s, rel=1e-5)


# =============================================================================
# 2. Interpolation engine
# =============================================================================

class TestInterpolation:
    def test_interp1d_exact_match(self):
        xs = [1.0, 2.0, 3.0]
        ys = [10.0, 20.0, 30.0]
        assert interp1d(xs, ys, 2.0) == pytest.approx(20.0)

    def test_interp1d_midpoint(self):
        xs = [0.0, 1.0]
        ys = [0.0, 10.0]
        assert interp1d(xs, ys, 0.5) == pytest.approx(5.0)

    def test_interp1d_clamp_low(self):
        xs = [1.0, 2.0, 3.0]
        ys = [10.0, 20.0, 30.0]
        assert interp1d(xs, ys, 0.0) == pytest.approx(10.0)

    def test_interp1d_clamp_high(self):
        xs = [1.0, 2.0, 3.0]
        ys = [10.0, 20.0, 30.0]
        assert interp1d(xs, ys, 5.0) == pytest.approx(30.0)

    def test_interp2d_exact_corner(self):
        p1 = [0.0, 1.0]
        p2 = [0.0, 1.0]
        table = [[0.0, 1.0], [2.0, 3.0]]
        assert interp2d(p1, p2, table, 0.0, 0.0) == pytest.approx(0.0)
        assert interp2d(p1, p2, table, 1.0, 1.0) == pytest.approx(3.0)

    def test_interp2d_centre(self):
        p1 = [0.0, 1.0]
        p2 = [0.0, 1.0]
        table = [[0.0, 0.0], [0.0, 4.0]]
        # At (0.5, 0.5): bilinear gives 0.25 × 4.0 = 1.0
        assert interp2d(p1, p2, table, 0.5, 0.5) == pytest.approx(1.0)

    def test_interp3d_exact(self):
        p1 = [0.0, 1.0]
        p2 = [0.0, 1.0]
        p3 = [0.0, 1.0]
        # table[i][j][k] = i + j + k
        table = [[[0, 1], [1, 2]], [[1, 2], [2, 3]]]
        assert interp3d(p1, p2, p3, table, 0.0, 0.0, 0.0) == pytest.approx(0.0)
        assert interp3d(p1, p2, p3, table, 1.0, 1.0, 1.0) == pytest.approx(3.0)
        assert interp3d(p1, p2, p3, table, 0.5, 0.5, 0.5) == pytest.approx(1.5)

    def test_interp1d_raises_on_short_list(self):
        with pytest.raises(ValueError):
            interp1d([1.0], [1.0], 1.0)


# =============================================================================
# 3. Geometry helpers
# =============================================================================

class TestGeometry:
    def test_round_area(self):
        # D = 0.3 m → A = π × 0.15² ≈ 0.07069 m²
        assert hp.round_area(0.3) == pytest.approx(math.pi * 0.0225, rel=1e-6)

    def test_rectangular_area(self):
        assert hp.rectangular_area(0.4, 0.3) == pytest.approx(0.12, rel=1e-6)

    def test_hydraulic_diameter_square(self):
        # Square duct: Dh = side length
        assert hp.rectangular_hydraulic_diameter(0.3, 0.3) == pytest.approx(0.3, rel=1e-6)

    def test_hydraulic_diameter_2to1(self):
        # 600×300 mm: Dh = 2×0.6×0.3/(0.6+0.3) = 0.4 m
        assert hp.rectangular_hydraulic_diameter(0.6, 0.3) == pytest.approx(0.4, rel=1e-6)

    def test_velocity(self):
        # Q = 0.5 m³/s, A = 0.1 m² → V = 5 m/s
        assert hp.velocity(0.5, 0.1) == pytest.approx(5.0, rel=1e-6)

    def test_velocity_pressure(self):
        # V = 10 m/s, ρ = 1.2 kg/m³ → Pv = 0.5×1.2×100 = 60 Pa
        assert hp.velocity_pressure(10.0, 1.2) == pytest.approx(60.0, rel=1e-6)


# =============================================================================
# 4. Friction factor and Reynolds number
# =============================================================================

class TestFluidMechanics:
    def test_reynolds_number_typical(self):
        # V=5 m/s, D=0.3 m, 20°C → Re ≈ 97 000
        Re = hp.reynolds_number(5.0, 0.3, 20.0)
        assert 80_000 < Re < 120_000

    def test_friction_factor_laminar(self):
        # Re=1000 → f = 64/1000 = 0.064
        f = hp.friction_factor(1000, 0.0001, 0.3)
        assert f == pytest.approx(0.064, rel=1e-4)

    def test_friction_factor_turbulent_smooth(self):
        # Re=100 000, ε/D → 0 (smooth): f ≈ 0.018
        f = hp.friction_factor(100_000, 1e-9, 0.3)
        assert 0.015 < f < 0.022

    def test_friction_factor_turbulent_rough(self):
        # Higher roughness → higher friction factor
        f_smooth = hp.friction_factor(100_000, 1e-6, 0.3)
        f_rough = hp.friction_factor(100_000, 0.001, 0.3)
        assert f_rough > f_smooth


# =============================================================================
# 5. Straight duct losses
# =============================================================================

class TestDuctLoss:
    def test_round_duct_basic(self):
        # D=300mm, L=10m, Q=0.5 m³/s, ε=0.09mm
        result = hp.duct_loss(
            flow_m3s=0.5, length_m=10.0,
            diameter_m=0.3, roughness_m=0.00009
        )
        assert result["delta_p_pa"] > 0
        assert result["velocity_ms"] == pytest.approx(0.5 / hp.round_area(0.3), rel=1e-4)
        assert result["pv_pa"] > 0
        assert 0.01 < result["friction_f"] < 0.05

    def test_round_duct_longer_is_higher(self):
        r1 = hp.duct_loss(0.5, 5.0, 0.3)
        r2 = hp.duct_loss(0.5, 10.0, 0.3)
        assert r2["delta_p_pa"] == pytest.approx(2 * r1["delta_p_pa"], rel=1e-4)

    def test_round_duct_larger_diameter_lower_loss(self):
        r_small = hp.duct_loss(0.5, 10.0, 0.25)
        r_large = hp.duct_loss(0.5, 10.0, 0.40)
        assert r_large["delta_p_pa"] < r_small["delta_p_pa"]

    def test_rectangular_duct_basic(self):
        result = hp.rectangular_duct_loss(
            flow_m3s=0.5, length_m=10.0,
            width_m=0.4, height_m=0.3
        )
        assert result["delta_p_pa"] > 0

    def test_duct_warning_high_velocity(self):
        # Very small duct with high flow → high velocity warning
        result = hp.duct_loss(flow_m3s=2.0, length_m=5.0, diameter_m=0.2)
        assert any("velocity" in w.lower() for w in result["warnings"])

    def test_duct_zero_length(self):
        result = hp.duct_loss(0.5, 0.0, 0.3)
        assert result["delta_p_pa"] == pytest.approx(0.0, abs=1e-10)


# =============================================================================
# 6. ASHRAE fitting losses
# =============================================================================

class TestFittingLoss:

    # --- Round elbows ---

    def test_CD3_12_exact_table_value(self):
        # r/D = 0.5 → C = 0.71 (exact table value)
        result = hp.fitting_loss("CD3-12", flow_m3s=0.5, diameter_m=0.3, r_over_D=0.5)
        assert result["C"] == pytest.approx(0.71, rel=1e-4)

    def test_CD3_12_exact_table_value_r1(self):
        # r/D = 1.0 → C = 0.22
        result = hp.fitting_loss("CD3-12", flow_m3s=0.5, diameter_m=0.3, r_over_D=1.0)
        assert result["C"] == pytest.approx(0.22, rel=1e-4)

    def test_CD3_12_interpolated(self):
        # r/D = 0.875 (between 0.75 and 1.0) → C between 0.33 and 0.22
        result = hp.fitting_loss("CD3-12", flow_m3s=0.5, diameter_m=0.3, r_over_D=0.875)
        assert 0.22 < result["C"] < 0.33

    def test_CD3_1_diameter_interpolated(self):
        # D = 125mm → C = 0.27 (exact table value)
        result = hp.fitting_loss("CD3-1", flow_m3s=0.3, diameter_m=0.125, D_mm=125)
        assert result["C"] == pytest.approx(0.27, rel=1e-3)

    def test_CD9_3_constant(self):
        # Fire damper — constant C = 0.12
        result = hp.fitting_loss("CD9-3", flow_m3s=0.5, diameter_m=0.3)
        assert result["C"] == pytest.approx(0.12, rel=1e-4)

    def test_CD9_1_fully_open(self):
        # Butterfly damper fully open (θ=0°) → C = 0.20
        result = hp.fitting_loss("CD9-1", flow_m3s=0.5, diameter_m=0.3, theta_deg=0)
        assert result["C"] == pytest.approx(0.20, rel=1e-3)

    def test_CD9_1_30deg(self):
        # θ=30° → C = 3.91
        result = hp.fitting_loss("CD9-1", flow_m3s=0.5, diameter_m=0.3, theta_deg=30)
        assert result["C"] == pytest.approx(3.91, rel=1e-3)

    def test_ED1_3_sharp_edge(self):
        # r/D = 0 → C = 0.50 (sharp-edged entry)
        result = hp.fitting_loss("ED1-3", flow_m3s=0.5, diameter_m=0.3, r_over_D=0.0)
        assert result["C"] == pytest.approx(0.50, rel=1e-4)

    def test_ED1_3_full_bellmouth(self):
        # r/D = 0.2 → C = 0.03
        result = hp.fitting_loss("ED1-3", flow_m3s=0.5, diameter_m=0.3, r_over_D=0.2)
        assert result["C"] == pytest.approx(0.03, rel=1e-3)

    # --- Rectangular elbows ---

    def test_CR3_1_exact_90deg(self):
        # r/W=1.0, H/W=1.0, θ=90° → Cp=0.21, K=1.0 → C=0.21
        result = hp.fitting_loss(
            "CR3-1", flow_m3s=0.5,
            width_m=0.4, height_m=0.4,
            r_over_W=1.0, H_over_W=1.0, theta_deg=90
        )
        assert result["C"] == pytest.approx(0.21, rel=1e-3)

    def test_CR3_1_angle_factor_45deg(self):
        # r/W=1.0, H/W=1.0, θ=45° → Cp=0.21, K=0.60 → C=0.126
        result = hp.fitting_loss(
            "CR3-1", flow_m3s=0.5,
            width_m=0.4, height_m=0.4,
            r_over_W=1.0, H_over_W=1.0, theta_deg=45
        )
        assert result["C"] == pytest.approx(0.21 * 0.60, rel=1e-3)

    def test_CR3_9_constant(self):
        # Turning vanes — constant C = 0.11
        result = hp.fitting_loss(
            "CR3-9", flow_m3s=0.5,
            width_m=0.4, height_m=0.3
        )
        assert result["C"] == pytest.approx(0.11, rel=1e-4)

    def test_CR9_1_fully_open(self):
        # Rectangular butterfly damper θ=0°, H/W=1.0 → C = 0.04
        result = hp.fitting_loss(
            "CR9-1", flow_m3s=0.5,
            width_m=0.4, height_m=0.4,
            theta_deg=0, H_over_W=1.0
        )
        assert result["C"] == pytest.approx(0.04, rel=1e-3)

    # --- Tee (SR5-1) ---

    def test_SR5_1_returns_two_coefficients(self):
        result = hp.fitting_loss(
            "SR5-1", flow_m3s=0.5,
            width_m=0.4, height_m=0.4,
            As_over_Ac=0.5, Ab_over_Ac=0.5, Qb_over_Qc=0.5
        )
        assert result["C"] is not None    # Cb
        assert result["C2"] is not None   # Cs
        assert result["delta_p2_pa"] is not None

    def test_SR5_1_exact_table_value(self):
        # As/Ac=0.50, Ab/Ac=0.50, Qb/Qc=0.5 → Cb=0.52, Cs=0.06
        result = hp.fitting_loss(
            "SR5-1", flow_m3s=0.5,
            width_m=0.4, height_m=0.4,
            As_over_Ac=0.50, Ab_over_Ac=0.50, Qb_over_Qc=0.5
        )
        assert result["C"] == pytest.approx(0.52, rel=1e-3)
        assert result["C2"] == pytest.approx(0.06, rel=1e-2)

    # --- Pressure drop calculation ---

    def test_fitting_delta_p_formula(self):
        # ΔP = C × Pv
        result = hp.fitting_loss("CD3-12", flow_m3s=0.5, diameter_m=0.3, r_over_D=1.0)
        expected = result["C"] * result["pv_pa"]
        assert result["delta_p_pa"] == pytest.approx(expected, rel=1e-6)

    def test_fitting_list_fittings(self):
        codes = hp.list_fittings()
        assert "CD3-12" in codes
        assert "SR5-1" in codes
        assert len(codes) >= 15


# =============================================================================
# 7. Filter losses
# =============================================================================

class TestFilterLoss:
    def test_rated_condition(self):
        # At rated flow → ΔP = rated ΔP
        result = hp.filter_loss(50.0, 0.5, 0.5)
        assert result["delta_p_pa"] == pytest.approx(50.0, rel=1e-6)

    def test_half_flow(self):
        # At half rated flow → ΔP = 50 × 0.25 = 12.5 Pa
        result = hp.filter_loss(50.0, 0.5, 0.25)
        assert result["delta_p_pa"] == pytest.approx(12.5, rel=1e-6)

    def test_double_flow(self):
        # At double rated flow → ΔP = 50 × 4 = 200 Pa
        result = hp.filter_loss(50.0, 0.5, 1.0)
        assert result["delta_p_pa"] == pytest.approx(200.0, rel=1e-6)

    def test_scale_ratio(self):
        result = hp.filter_loss(100.0, 1.0, 0.5)
        assert result["scale_ratio"] == pytest.approx(0.25, rel=1e-6)

    def test_warning_high_flow(self):
        result = hp.filter_loss(50.0, 0.5, 1.0)  # 2× rated flow
        assert any("rated" in w.lower() or "flow" in w.lower() for w in result["warnings"])


# =============================================================================
# 8. System class
# =============================================================================

class TestSystem:
    def _make_system(self):
        sys = hp.System(flow_m3s=0.5, temp_c=20, name="Test System")
        sys.add_duct(length_m=10.0, diameter_m=0.3, label="Main Duct")
        sys.add_fitting("CD3-12", diameter_m=0.3, r_over_D=1.0, label="90° Elbow")
        sys.add_filter(rated_drop_pa=50.0, rated_flow_m3s=0.5, label="Pre-filter")
        return sys

    def test_total_pa_positive(self):
        sys = self._make_system()
        assert sys.total_pa() > 0

    def test_total_inwg_consistent(self):
        sys = self._make_system()
        assert sys.total_inwg() == pytest.approx(hp.pa_to_inwg(sys.total_pa()), rel=1e-6)

    def test_element_count(self):
        sys = self._make_system()
        assert len(sys.elements()) == 3

    def test_total_equals_sum(self):
        sys = self._make_system()
        element_sum = sum(e.delta_p_pa for e in sys.elements())
        assert sys.total_pa() == pytest.approx(element_sum, rel=1e-10)

    def test_report_si(self):
        sys = self._make_system()
        report = sys.report(unit="SI")
        assert "Pa" in report
        assert "Test System" in report
        assert "Main Duct" in report

    def test_report_ip(self):
        sys = self._make_system()
        report = sys.report(unit="IP")
        assert "in.w.g." in report

    def test_to_dict_structure(self):
        sys = self._make_system()
        d = sys.to_dict()
        assert "total_pa" in d
        assert "total_inwg" in d
        assert "elements" in d
        assert len(d["elements"]) == 3
        assert d["elements"][0]["label"] == "Main Duct"

    def test_chaining(self):
        # Method chaining should work
        sys = (
            hp.System(flow_m3s=0.3)
            .add_duct(length_m=5.0, diameter_m=0.25)
            .add_fitting("CD9-3", diameter_m=0.25)
            .add_custom(delta_p_pa=20.0, label="Grille")
        )
        assert len(sys.elements()) == 3

    def test_custom_element(self):
        sys = hp.System(flow_m3s=0.5)
        sys.add_custom(delta_p_pa=100.0, label="Grille")
        assert sys.total_pa() == pytest.approx(100.0, rel=1e-6)

    def test_rectangular_duct_in_system(self):
        sys = hp.System(flow_m3s=0.5)
        sys.add_duct(length_m=5.0, width_m=0.4, height_m=0.3)
        assert sys.total_pa() > 0


# =============================================================================
# 9. Edge cases and error handling
# =============================================================================

class TestEdgeCases:
    def test_unknown_fitting_code(self):
        with pytest.raises(KeyError):
            hp.fitting_loss("XX9-99", flow_m3s=0.5, diameter_m=0.3)

    def test_missing_required_param(self):
        with pytest.raises(ValueError):
            # CD3-12 requires r_over_D
            hp.fitting_loss("CD3-12", flow_m3s=0.5, diameter_m=0.3)

    def test_round_fitting_without_diameter(self):
        with pytest.raises(ValueError):
            hp.fitting_loss("CD3-12", flow_m3s=0.5, r_over_D=1.0)

    def test_rectangular_fitting_without_dimensions(self):
        with pytest.raises(ValueError):
            hp.fitting_loss("CR3-1", flow_m3s=0.5, r_over_W=1.0, H_over_W=1.0)

    def test_filter_zero_rated_flow(self):
        with pytest.raises(ValueError):
            hp.filter_loss(50.0, 0.0, 0.5)

    def test_duct_zero_area(self):
        with pytest.raises((ValueError, ZeroDivisionError)):
            hp.duct_loss(0.5, 10.0, 0.0)

    def test_interp1d_mismatched_lengths(self):
        with pytest.raises(ValueError):
            interp1d([1.0, 2.0], [1.0, 2.0, 3.0], 1.5)

    def test_get_fitting_case_insensitive(self):
        f1 = hp.get_fitting("cd3-12")
        f2 = hp.get_fitting("CD3-12")
        assert f1 is f2

    def test_system_no_elements(self):
        sys = hp.System(flow_m3s=0.5)
        assert sys.total_pa() == 0.0

    def test_high_altitude_lower_density(self):
        # Higher altitude → lower air density → lower Pv → lower fitting loss
        r_sea = hp.fitting_loss("CD3-12", flow_m3s=0.5, diameter_m=0.3,
                                r_over_D=1.0, altitude_m=0)
        r_alt = hp.fitting_loss("CD3-12", flow_m3s=0.5, diameter_m=0.3,
                                r_over_D=1.0, altitude_m=2000)
        assert r_alt["delta_p_pa"] < r_sea["delta_p_pa"]
