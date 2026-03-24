# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-24

### Added
- Initial release of the `hvac_pressure` library.
- Darcy-Weisbach friction loss calculation for straight ducts (round, rectangular, flat oval).
- Built-in ASHRAE fitting loss coefficient database (15 common fittings).
- 1D, 2D, and 3D linear interpolation engine for ASHRAE tables.
- Filter and damper element calculation modules.
- `System` class for chaining elements and generating pressure drop reports.
- Comprehensive unit conversion module (SI ↔ Imperial).
- Full test suite with 79 passing tests.
