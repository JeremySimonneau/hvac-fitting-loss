"""
ashrae_tables.py — ASHRAE 2009 Handbook Fundamentals, Chapter 21
               Duct Design — Fitting Loss Coefficient Tables.

All data transcribed from the official ASHRAE publication.
Each fitting is stored as a dict with keys:
  'description' : human-readable name
  'shape'       : 'round' or 'rectangular'
  'category'    : 'elbow', 'damper', 'entry', 'exit', 'tee', 'transition'
  'dims'        : 0 (constant), 1 (1D), 2 (2D), 3 (3D)
  'ref_velocity': 'upstream' or 'downstream'
  'params'      : list of parameter dicts {'name', 'label', 'unit', 'values'}
  'c'           : coefficient data (scalar / list / 2D list / 3D list)
  'c2'          : second coefficient (tees only — Cs values)
  'notes'       : additional usage notes

Reference velocity pressure Pv is always computed from the upstream duct
velocity unless noted otherwise (bellmouth entries use downstream velocity).
"""

# =============================================================================
# ROUND DUCT FITTINGS — CD series (exhaust/return) and SD series (supply)
# =============================================================================

# CD3-1: Elbow, Die Stamped, 90°, r/D = 1.5
# C varies with duct diameter (mm). Fixed r/D = 1.5.
CD3_1 = {
    "description": "Round Elbow — Die Stamped 90° (r/D = 1.5)",
    "shape": "round",
    "category": "elbow",
    "dims": 1,
    "ref_velocity": "upstream",
    "params": [
        {"name": "D_mm", "label": "Diameter", "unit": "mm",
         "values": [75, 100, 125, 150, 180, 200, 230, 250]},
    ],
    "c": [0.45, 0.34, 0.27, 0.24, 0.21, 0.20, 0.19, 0.18],
    "notes": "Fixed r/D = 1.5. C decreases with increasing diameter.",
}

# CD3-5: Elbow, Pleated, 90°, r/D = 1.5
CD3_5 = {
    "description": "Round Elbow — Pleated 90° (r/D = 1.5)",
    "shape": "round",
    "category": "elbow",
    "dims": 1,
    "ref_velocity": "upstream",
    "params": [
        {"name": "D_mm", "label": "Diameter", "unit": "mm",
         "values": [75, 100, 125, 150, 180, 200, 230, 250]},
    ],
    "c": [0.57, 0.43, 0.34, 0.30, 0.26, 0.25, 0.23, 0.22],
    "notes": "Fixed r/D = 1.5. Higher loss than die-stamped due to pleating.",
}

# CD3-9: Elbow, 5-Gore, 90°, r/D = 1.5
CD3_9 = {
    "description": "Round Elbow — 5-Gore 90° (r/D = 1.5)",
    "shape": "round",
    "category": "elbow",
    "dims": 1,
    "ref_velocity": "upstream",
    "params": [
        {"name": "D_mm", "label": "Diameter", "unit": "mm",
         "values": [75, 100, 125, 150, 180, 200, 230, 250]},
    ],
    "c": [0.46, 0.35, 0.28, 0.25, 0.22, 0.21, 0.20, 0.19],
    "notes": "Fixed r/D = 1.5. 5-gore construction.",
}

# CD3-12: Elbow, 3-Gore, Variable r/D
# C varies with radius ratio r/D. User specifies r/D.
CD3_12 = {
    "description": "Round Elbow — 3-Gore, Variable r/D",
    "shape": "round",
    "category": "elbow",
    "dims": 1,
    "ref_velocity": "upstream",
    "params": [
        {"name": "r_over_D", "label": "Radius Ratio r/D", "unit": "-",
         "values": [0.50, 0.75, 1.00, 1.50, 2.00]},
    ],
    "c": [0.71, 0.33, 0.22, 0.15, 0.13],
    "notes": "User must supply centreline radius r and diameter D to compute r/D.",
}

# CD3-17: Elbow, Mitered, 45°
CD3_17 = {
    "description": "Round Elbow — Mitered 45°",
    "shape": "round",
    "category": "elbow",
    "dims": 1,
    "ref_velocity": "upstream",
    "params": [
        {"name": "D_mm", "label": "Diameter", "unit": "mm",
         "values": [75, 100, 125, 150, 180, 200, 230, 250]},
    ],
    "c": [0.18, 0.15, 0.13, 0.12, 0.11, 0.11, 0.10, 0.10],
    "notes": "Fixed 45° miter angle without vanes.",
}

# CD9-1: Damper, Butterfly (Round)
# C varies with blade angle θ (0° = fully open, 90° = fully closed).
CD9_1 = {
    "description": "Round Damper — Butterfly",
    "shape": "round",
    "category": "damper",
    "dims": 1,
    "ref_velocity": "upstream",
    "params": [
        {"name": "theta_deg", "label": "Blade Angle θ", "unit": "°",
         "values": [0, 10, 20, 30, 40, 50, 60, 70]},
    ],
    "c": [0.20, 0.52, 1.54, 3.91, 10.8, 32.6, 118.0, 751.0],
    "notes": "θ = 0° fully open; θ = 90° fully closed (infinite resistance). "
             "Do not extrapolate beyond 70°.",
}

# CD9-3: Fire Damper, Curtain Type C (Round) — constant C
CD9_3 = {
    "description": "Round Fire Damper — Curtain Type C",
    "shape": "round",
    "category": "damper",
    "dims": 0,
    "ref_velocity": "upstream",
    "params": [],
    "c": 0.12,
    "notes": "Constant C = 0.12 for fully open curtain-type fire damper.",
}

# ED1-3 / SD1-1: Bellmouth Entry (Exhaust and Supply)
# Same table applies to both exhaust (ED1-3) and supply (SD1-1) bellmouth entries.
# C varies with radius ratio r/D (or r/Do for supply).
ED1_3 = {
    "description": "Entry — Bellmouth (Exhaust/Return)",
    "shape": "round",
    "category": "entry",
    "dims": 1,
    "ref_velocity": "downstream",
    "params": [
        {"name": "r_over_D", "label": "Radius Ratio r/D", "unit": "-",
         "values": [0.000, 0.010, 0.020, 0.030, 0.040, 0.050,
                    0.060, 0.080, 0.100, 0.120, 0.160, 0.200, 10.0]},
    ],
    "c": [0.50, 0.44, 0.37, 0.31, 0.26, 0.22,
          0.20, 0.15, 0.12, 0.09, 0.06, 0.03, 0.03],
    "notes": "r/D = 0 is a sharp-edged entry (C = 0.50). "
             "r/D ≥ 0.20 is a full bellmouth (C = 0.03). "
             "Reference velocity is the duct velocity (downstream of entry).",
}

SD1_1 = {
    "description": "Entry — Bellmouth Plenum to Round (Supply)",
    "shape": "round",
    "category": "entry",
    "dims": 1,
    "ref_velocity": "downstream",
    "params": [
        {"name": "r_over_Do", "label": "Radius Ratio r/Do", "unit": "-",
         "values": [0.000, 0.010, 0.020, 0.030, 0.040, 0.050,
                    0.060, 0.080, 0.100, 0.120, 0.160, 0.200, 10.0]},
    ],
    "c": [0.50, 0.44, 0.37, 0.31, 0.26, 0.22,
          0.20, 0.15, 0.12, 0.09, 0.06, 0.03, 0.03],
    "notes": "Same table as ED1-3. Reference velocity is downstream duct velocity.",
}

# ED2-1: Diffuser, Conical Round to Plenum (Exhaust/Return)
# 2D table: C1 vs A1/Ao (rows) and L/Do (columns).
# Final C_o = C1 × (Ao/A1)²
ED2_1 = {
    "description": "Diffuser — Conical Round to Plenum (Exhaust)",
    "shape": "round",
    "category": "exit",
    "dims": 2,
    "ref_velocity": "upstream",
    "params": [
        {"name": "A1_over_Ao", "label": "Area Ratio A1/Ao", "unit": "-",
         "values": [1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 6.0, 8.0, 10.0, 14.0, 20.0]},
        {"name": "L_over_Do", "label": "Length Ratio L/Do", "unit": "-",
         "values": [0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 14.0]},
    ],
    # table[i][j] = C1 at (A1/Ao[i], L/Do[j])
    "c": [
        # A1/Ao = 1.0
        [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
        # A1/Ao = 1.5
        [0.00, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.10, 0.11, 0.13, 0.13],
        # A1/Ao = 2.0
        [0.08, 0.06, 0.04, 0.04, 0.04, 0.05, 0.05, 0.06, 0.08, 0.09, 0.10],
        # A1/Ao = 2.5
        [0.13, 0.09, 0.06, 0.06, 0.06, 0.06, 0.06, 0.07, 0.08, 0.09, 0.09],
        # A1/Ao = 3.0
        [0.17, 0.12, 0.09, 0.07, 0.07, 0.06, 0.06, 0.07, 0.07, 0.08, 0.08],
        # A1/Ao = 4.0
        [0.23, 0.17, 0.12, 0.10, 0.09, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08],
        # A1/Ao = 6.0
        [0.30, 0.22, 0.16, 0.13, 0.12, 0.10, 0.10, 0.09, 0.09, 0.09, 0.08],
        # A1/Ao = 8.0
        [0.34, 0.26, 0.18, 0.15, 0.13, 0.12, 0.11, 0.10, 0.09, 0.09, 0.09],
        # A1/Ao = 10.0
        [0.36, 0.28, 0.20, 0.16, 0.14, 0.13, 0.12, 0.11, 0.10, 0.09, 0.09],
        # A1/Ao = 14.0
        [0.39, 0.30, 0.22, 0.18, 0.16, 0.14, 0.13, 0.12, 0.10, 0.10, 0.10],
        # A1/Ao = 20.0
        [0.41, 0.32, 0.24, 0.20, 0.17, 0.15, 0.14, 0.12, 0.11, 0.11, 0.10],
    ],
    "notes": "C_o = C1 × (Ao/A1)². A1 = upstream duct area; Ao = outlet/plenum area. "
             "L = diffuser length; Do = upstream duct diameter.",
}

# =============================================================================
# RECTANGULAR DUCT FITTINGS — CR series (exhaust/return) and SR series (supply)
# =============================================================================

# CR3-1: Elbow, Smooth Radius, 90°, Without Vanes (Rectangular)
# 2D table: Cp vs r/W (rows) and H/W (columns).
# For non-90° bends: C_o = K(theta) × Cp(r/W, H/W)
# W = duct width (in the plane of the bend); H = duct height.
CR3_1 = {
    "description": "Rectangular Elbow — Smooth Radius, No Vanes",
    "shape": "rectangular",
    "category": "elbow",
    "dims": 2,
    "ref_velocity": "upstream",
    "params": [
        {"name": "r_over_W", "label": "Radius Ratio r/W", "unit": "-",
         "values": [0.50, 0.75, 1.00, 1.50, 2.00]},
        {"name": "H_over_W", "label": "Aspect Ratio H/W", "unit": "-",
         "values": [0.25, 0.50, 0.75, 1.00, 1.50, 2.00, 3.00, 4.00, 5.00, 6.00, 8.00]},
    ],
    # table[i][j] = Cp at (r/W[i], H/W[j])
    "c": [
        [1.53, 1.38, 1.29, 1.18, 1.06, 1.00, 1.00, 1.06, 1.12, 1.16, 1.18],  # r/W=0.50
        [0.57, 0.52, 0.48, 0.44, 0.40, 0.39, 0.39, 0.40, 0.42, 0.43, 0.44],  # r/W=0.75
        [0.27, 0.25, 0.23, 0.21, 0.19, 0.18, 0.18, 0.19, 0.20, 0.21, 0.21],  # r/W=1.00
        [0.22, 0.20, 0.19, 0.17, 0.15, 0.14, 0.14, 0.15, 0.16, 0.17, 0.17],  # r/W=1.50
        [0.20, 0.18, 0.16, 0.15, 0.14, 0.13, 0.13, 0.14, 0.15, 0.15, 0.15],  # r/W=2.00
    ],
    # Angle factor K for non-90° bends (applied as C_o = K × Cp)
    "angle_factor": {
        "theta_vals": [0, 20, 30, 45, 60, 75, 90, 110, 130, 150, 180],
        "K_vals":     [0.00, 0.31, 0.45, 0.60, 0.78, 0.90, 1.00, 1.13, 1.20, 1.28, 1.40],
    },
    "notes": "W = duct width in the plane of the bend. H = duct height. "
             "For 90° bends, C_o = Cp directly. For other angles, C_o = K(θ) × Cp.",
}

# CR3-6: Elbow, Mitered, Rectangular (any angle, no vanes)
# 2D table: C vs theta (rows) and H/W (columns).
CR3_6 = {
    "description": "Rectangular Elbow — Mitered, No Vanes",
    "shape": "rectangular",
    "category": "elbow",
    "dims": 2,
    "ref_velocity": "upstream",
    "params": [
        {"name": "theta_deg", "label": "Bend Angle θ", "unit": "°",
         "values": [20, 30, 45, 60, 75, 90]},
        {"name": "H_over_W", "label": "Aspect Ratio H/W", "unit": "-",
         "values": [0.25, 0.50, 0.75, 1.00, 1.50, 2.00, 3.00, 4.00, 5.00, 6.00, 8.00]},
    ],
    "c": [
        [0.08, 0.08, 0.08, 0.07, 0.07, 0.07, 0.06, 0.06, 0.05, 0.05, 0.05],  # 20°
        [0.18, 0.17, 0.17, 0.16, 0.15, 0.15, 0.13, 0.13, 0.12, 0.12, 0.11],  # 30°
        [0.38, 0.37, 0.36, 0.34, 0.33, 0.31, 0.28, 0.27, 0.26, 0.25, 0.24],  # 45°
        [0.60, 0.59, 0.57, 0.55, 0.52, 0.49, 0.46, 0.43, 0.41, 0.39, 0.38],  # 60°
        [0.89, 0.87, 0.84, 0.81, 0.77, 0.73, 0.67, 0.63, 0.61, 0.58, 0.57],  # 75°
        [1.30, 1.27, 1.23, 1.18, 1.13, 1.07, 0.98, 0.92, 0.89, 0.85, 0.83],  # 90°
    ],
    "notes": "No turning vanes. H/W where H is parallel to bend axis.",
}

# CR3-9: Elbow, Mitered 90°, Single-Thickness Vanes, 40 mm spacing — constant
CR3_9 = {
    "description": "Rectangular Elbow — Mitered 90°, Single-Thickness Vanes (40 mm)",
    "shape": "rectangular",
    "category": "elbow",
    "dims": 0,
    "ref_velocity": "upstream",
    "params": [],
    "c": 0.11,
    "notes": "Constant C = 0.11. Single-thickness turning vanes at 40 mm spacing.",
}

# CR9-1: Damper, Butterfly (Rectangular)
# 2D table: C vs theta (rows) and H/W (columns).
CR9_1 = {
    "description": "Rectangular Damper — Butterfly",
    "shape": "rectangular",
    "category": "damper",
    "dims": 2,
    "ref_velocity": "upstream",
    "params": [
        {"name": "theta_deg", "label": "Blade Angle θ", "unit": "°",
         "values": [0, 10, 20, 30, 40, 50, 60, 65, 70]},
        {"name": "H_over_W", "label": "Aspect Ratio H/W", "unit": "-",
         "values": [0.10, 0.50, 1.00, 1.50, 2.00]},
    ],
    "c": [
        # theta = 0°
        [0.04, 0.04, 0.04, 0.04, 0.04],
        # theta = 10°
        [0.30, 0.30, 0.30, 0.35, 0.35],
        # theta = 20°
        [1.10, 1.10, 1.10, 1.25, 1.25],
        # theta = 30°
        [3.00, 3.00, 3.00, 3.60, 3.60],
        # theta = 40°
        [8.00, 8.00, 8.00, 8.00, 10.00],
        # theta = 50°
        [23.00, 23.00, 23.00, 29.00, 29.00],
        # theta = 60°
        [60.00, 60.00, 60.00, 80.00, 80.00],
        # theta = 65°
        [100.00, 100.00, 100.00, 155.00, 155.00],
        # theta = 70°
        [190.00, 190.00, 190.00, 230.00, 230.00],
    ],
    "notes": "θ = 0° fully open. Do not extrapolate beyond 70°.",
}

# SR4-1: Transition, Rectangular, Two Sides Parallel, Symmetrical (Supply)
# 2D table: C vs Ao/A1 (rows) and theta (columns).
SR4_1 = {
    "description": "Rectangular Transition — Two Sides Parallel, Symmetrical (Supply)",
    "shape": "rectangular",
    "category": "transition",
    "dims": 2,
    "ref_velocity": "upstream",
    "params": [
        {"name": "Ao_over_A1", "label": "Area Ratio Ao/A1", "unit": "-",
         "values": [0.10, 0.25, 0.50, 1.00, 2.00, 4.00]},
        {"name": "theta_deg", "label": "Half-Angle θ", "unit": "°",
         "values": [0, 3, 5, 10, 15, 20, 30, 45, 60, 90, 120, 150, 180]},
    ],
    "c": [
        # Ao/A1 = 0.10 (contraction)
        [0.00, 0.12, 0.09, 0.05, 0.05, 0.05, 0.05, 0.06, 0.08, 0.19, 0.29, 0.37, 0.43],
        # Ao/A1 = 0.25
        [0.00, 0.10, 0.08, 0.05, 0.04, 0.04, 0.04, 0.06, 0.07, 0.18, 0.27, 0.36, 0.41],
        # Ao/A1 = 0.50
        [0.00, 0.08, 0.09, 0.06, 0.04, 0.04, 0.04, 0.06, 0.07, 0.12, 0.17, 0.20, 0.27],
        # Ao/A1 = 1.00 (straight duct, no change)
        [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
        # Ao/A1 = 2.00 (expansion)
        [0.00, 0.64, 0.96, 0.54, 0.52, 0.62, 0.94, 1.40, 1.48, 1.52, 1.48, 1.44, 1.40],
        # Ao/A1 = 4.00
        [0.00, 4.16, 4.64, 2.72, 3.09, 4.00, 6.72, 9.60, 10.88, 11.20, 11.20, 10.88, 10.56],
    ],
    "notes": "Ao = outlet area; A1 = inlet area. θ is the half-angle of the transition. "
             "For contractions (Ao/A1 < 1), minimum loss is at θ ≈ 10°–20°. "
             "For expansions (Ao/A1 > 1), minimum loss is at θ ≈ 5°–10°.",
}

# SR5-1: Wye, Smooth, As + Ab ≥ Ac, Branch 90° to Main, Diverging (Rectangular)
# 3D table: Cb and Cs vs As/Ac (dim1), Ab/Ac (dim2), Qb/Qc (dim3).
# Returns two coefficients: c1 = Cb (branch), c2 = Cs (straight/main).
SR5_1 = {
    "description": "Rectangular Wye — Smooth Diverging, Branch 90° to Main",
    "shape": "rectangular",
    "category": "tee",
    "dims": 3,
    "ref_velocity": "upstream",
    "params": [
        {"name": "As_over_Ac", "label": "Straight Area Ratio As/Ac", "unit": "-",
         "values": [0.50, 0.75, 1.00]},
        {"name": "Ab_over_Ac", "label": "Branch Area Ratio Ab/Ac", "unit": "-",
         "values": [0.25, 0.50, 1.00]},
        {"name": "Qb_over_Qc", "label": "Branch Flow Ratio Qb/Qc", "unit": "-",
         "values": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]},
    ],
    # c[i][j][k] = Cb at (As/Ac[i], Ab/Ac[j], Qb/Qc[k])
    "c": [
        # As/Ac = 0.50
        [
            [2.25, 0.48, 0.25, 0.18, 0.17, 0.16, 0.17, 0.17, 0.17],   # Ab/Ac=0.25
            [11.00, 2.38, 1.06, 0.64, 0.52, 0.47, 0.47, 0.47, 0.48],  # Ab/Ac=0.50
            [60.00, 13.00, 4.78, 2.06, 0.96, 0.47, 0.31, 0.27, 0.26], # Ab/Ac=1.00
        ],
        # As/Ac = 0.75
        [
            [2.19, 0.55, 0.35, 0.31, 0.33, 0.35, 0.36, 0.37, 0.39],
            [13.00, 2.50, 0.89, 0.47, 0.34, 0.31, 0.32, 0.36, 0.43],
            [70.00, 15.00, 5.67, 2.63, 1.36, 0.78, 0.53, 0.41, 0.36],
        ],
        # As/Ac = 1.00
        [
            [3.44, 0.78, 0.42, 0.33, 0.30, 0.31, 0.40, 0.42, 0.46],
            [15.50, 3.00, 1.11, 0.63, 0.48, 0.42, 0.40, 0.42, 0.46],
            [67.00, 13.75, 5.11, 2.31, 1.28, 0.81, 0.59, 0.47, 0.46],
        ],
    ],
    # c2[i][j][k] = Cs at (As/Ac[i], Ab/Ac[j], Qb/Qc[k])
    "c2": [
        # As/Ac = 0.50
        [
            [8.65, 1.12, 0.21, 0.05, 0.06, 0.10, 0.15, 0.19, 0.24],
            [7.50, 0.98, 0.19, 0.06, 0.06, 0.10, 0.14, 0.18, 0.22],
            [5.21, 0.68, 0.15, 0.06, 0.07, 0.10, 0.13, 0.16, 0.19],
        ],
        # As/Ac = 0.75
        [
            [19.62, 3.25, 0.86, 0.23, 0.05, 0.02, 0.00, 0.00, 0.05],
            [20.62, 3.24, 0.76, 0.14, -0.03, -0.07, -0.05, -0.01, 0.03],
            [17.01, 2.55, 0.55, 0.07, -0.05, -0.05, -0.02, 0.02, 0.06],
        ],
        # As/Ac = 1.00
        [
            [46.00, 9.50, 3.22, 1.31, 0.52, 0.14, -0.02, -0.05, -0.01],
            [35.34, 6.49, 1.98, 0.69, 0.22, 0.00, -0.04, -0.05, -0.05],
            [38.95, 7.10, 2.15, 0.74, 0.23, 0.03, -0.04, -0.05, -0.04],
        ],
    ],
    "notes": "c1 = Cb (branch path loss coefficient). c2 = Cs (straight/main path). "
             "Ac = common upstream duct area; As = straight downstream area; "
             "Ab = branch area. Qc = total upstream flow; Qb = branch flow. "
             "Condition: As + Ab ≥ Ac. r/Wb = 1.0.",
}

# =============================================================================
# Registry — maps fitting code strings to data dicts
# =============================================================================

FITTING_REGISTRY = {
    "CD3-1":  CD3_1,
    "CD3-5":  CD3_5,
    "CD3-9":  CD3_9,
    "CD3-12": CD3_12,
    "CD3-17": CD3_17,
    "CD9-1":  CD9_1,
    "CD9-3":  CD9_3,
    "ED1-3":  ED1_3,
    "SD1-1":  SD1_1,
    "ED2-1":  ED2_1,
    "CR3-1":  CR3_1,
    "CR3-6":  CR3_6,
    "CR3-9":  CR3_9,
    "CR9-1":  CR9_1,
    "SR4-1":  SR4_1,
    "SR5-1":  SR5_1,
}


def list_fittings() -> list:
    """Return a sorted list of available ASHRAE fitting codes."""
    return sorted(FITTING_REGISTRY.keys())


def get_fitting(code: str) -> dict:
    """
    Retrieve a fitting data dict by ASHRAE code.

    Parameters
    ----------
    code : str
        ASHRAE fitting code, e.g. 'CD3-12', 'CR3-1'.

    Returns
    -------
    dict
        Fitting data dictionary.

    Raises
    ------
    KeyError
        If the code is not found in the registry.
    """
    code = code.upper()
    if code not in FITTING_REGISTRY:
        available = ", ".join(list_fittings())
        raise KeyError(
            f"Fitting code '{code}' not found. Available codes: {available}"
        )
    return FITTING_REGISTRY[code]
