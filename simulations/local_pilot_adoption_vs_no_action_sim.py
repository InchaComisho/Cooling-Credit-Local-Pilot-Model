"""
Local Pilot Adoption vs No Action Simulation

This script compares two simplified scenarios:

1. No Action
   - No local Cooling Credit pilots are implemented.
   - No MRV coverage expands.
   - Heat burden grows under a fixed assumed annual pressure.

2. Local Pilot Implementation
   - Pilot sites increase gradually.
   - MRV coverage expands.
   - Local cooling capacity accumulates with maintenance decay.
   - Heat burden is partially reduced by accumulated cooling capacity.

This is not a prediction model.
It is a conceptual comparison model for illustrating the difference between
implementing measurable local cooling pilots and doing nothing.

License: CC BY 4.0
Author: Master / inchacomusho / InchaComisho
"""

from __future__ import annotations

import csv
from pathlib import Path


START_YEAR = 2026
END_YEAR = 2036
INITIAL_HEAT_BURDEN_INDEX = 100.0
ANNUAL_HEAT_PRESSURE_GROWTH = 0.028
INITIAL_PILOT_SITES = 1
SITE_GROWTH_RATE = 1.55
INITIAL_MRV_COVERAGE = 0.15
MRV_COVERAGE_GROWTH = 0.075
MAX_MRV_COVERAGE = 0.90
COOLING_CAPACITY_PER_SITE = 0.09
MAINTENANCE_RETENTION_RATE = 0.92
MAX_HEAT_REDUCTION_BY_LOCAL_COOLING = 22.0


def accumulated_cooling_capacity(year_index: int) -> float:
    """Calculate cumulative local cooling capacity with maintenance decay."""
    capacity = 0.0
    for start_index in range(year_index + 1):
        sites_started = INITIAL_PILOT_SITES * (SITE_GROWTH_RATE ** start_index)
        age = year_index - start_index
        maintenance_factor = MAINTENANCE_RETENTION_RATE ** age
        capacity += sites_started * COOLING_CAPACITY_PER_SITE * maintenance_factor
    return capacity


def generate_rows() -> list[dict[str, float | int | str]]:
    rows: list[dict[str, float | int | str]] = []

    for year_index, year in enumerate(range(START_YEAR, END_YEAR + 1)):
        no_action_heat = INITIAL_HEAT_BURDEN_INDEX * ((1 + ANNUAL_HEAT_PRESSURE_GROWTH) ** year_index)
        no_action_risk_pressure = max(0.0, (no_action_heat - INITIAL_HEAT_BURDEN_INDEX) * 1.8)

        rows.append(
            {
                "year": year,
                "scenario": "No Action",
                "implementation_sites": 0,
                "mrv_coverage_ratio": 0.0,
                "local_cooling_capacity_index": 0.0,
                "local_cooling_points": 0.0,
                "heat_burden_index": round(no_action_heat, 3),
                "risk_reduction_proxy": round(no_action_risk_pressure, 3),
            }
        )

        implementation_sites = round(INITIAL_PILOT_SITES * (SITE_GROWTH_RATE ** year_index))
        mrv_coverage = min(MAX_MRV_COVERAGE, INITIAL_MRV_COVERAGE + MRV_COVERAGE_GROWTH * year_index)
        cooling_capacity = accumulated_cooling_capacity(year_index)
        heat_reduction = min(MAX_HEAT_REDUCTION_BY_LOCAL_COOLING, cooling_capacity * 1.25)
        pilot_heat = max(70.0, no_action_heat - heat_reduction)
        local_cooling_points = cooling_capacity * mrv_coverage * 10
        risk_reduction_proxy = max(0.0, no_action_heat - pilot_heat) * 1.8

        rows.append(
            {
                "year": year,
                "scenario": "Local Pilot Implementation",
                "implementation_sites": implementation_sites,
                "mrv_coverage_ratio": round(mrv_coverage, 3),
                "local_cooling_capacity_index": round(cooling_capacity, 3),
                "local_cooling_points": round(local_cooling_points, 3),
                "heat_burden_index": round(pilot_heat, 3),
                "risk_reduction_proxy": round(risk_reduction_proxy, 3),
            }
        )

    return rows


def write_csv(rows: list[dict[str, float | int | str]], output_path: Path) -> None:
    fieldnames = [
        "year",
        "scenario",
        "implementation_sites",
        "mrv_coverage_ratio",
        "local_cooling_capacity_index",
        "local_cooling_points",
        "heat_burden_index",
        "risk_reduction_proxy",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    output = Path(__file__).with_name("local_pilot_adoption_vs_no_action_results.csv")
    write_csv(generate_rows(), output)
    print(f"Wrote simulation results to {output}")
