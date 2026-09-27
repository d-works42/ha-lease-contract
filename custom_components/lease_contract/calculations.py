"""Pure calculation helpers for the Lease Contract integration.

This module has no Home Assistant dependencies, so it can be unit tested
in isolation and re-used by both the coordinator and any future platform.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date


def full_months_between(start: date, end: date) -> int:
    """Return the number of *full* calendar months between two dates.

    A month only counts once the day-of-month of ``end`` has reached the
    day-of-month of ``start`` (e.g. Jan 15 -> Feb 15 is exactly one full
    month, Jan 15 -> Feb 10 is zero full months).
    """
    if end <= start:
        return 0

    months = (end.year - start.year) * 12 + (end.month - start.month)
    if end.day < start.day:
        months -= 1

    return max(months, 0)


def clamp(value: float, minimum: float | None = None, maximum: float | None = None) -> float:
    """Clamp a value between an optional minimum and maximum."""
    if minimum is not None and value < minimum:
        return minimum
    if maximum is not None and value > maximum:
        return maximum
    return value


@dataclass
class ContractResult:
    """The full set of computed values for a single lease contract."""

    used_km: float
    km_left: float
    monthly_avg_used_km: float | None
    monthly_avg_left_km: float | None
    km_left_current_month: float
    days_left: int
    full_months_elapsed: int
    full_months_remaining: int
    current_odometer: float
    start_odometer: float


def compute_contract_result(
    *,
    start_date: date,
    end_date: date,
    max_km: float,
    start_odometer: float,
    current_odometer: float,
    month_start_odometer: float,
    today: date,
) -> ContractResult:
    """Compute all derived sensor values for one contract."""
    used_km = max(current_odometer - start_odometer, 0.0)
    km_left = max_km - used_km

    days_left = max((end_date - today).days, 0)

    full_months_elapsed = full_months_between(start_date, today)
    full_months_remaining = full_months_between(today, end_date)

    monthly_avg_used_km = (
        used_km / full_months_elapsed if full_months_elapsed > 0 else None
    )
    monthly_avg_left_km = (
        km_left / full_months_remaining if full_months_remaining > 0 else None
    )

    km_driven_this_month = max(current_odometer - month_start_odometer, 0.0)
    baseline_for_current_month = (
        monthly_avg_left_km if monthly_avg_left_km is not None else km_left
    )
    km_left_current_month = baseline_for_current_month - km_driven_this_month

    return ContractResult(
        used_km=round(used_km, 1),
        km_left=round(km_left, 1),
        monthly_avg_used_km=(
            round(monthly_avg_used_km, 1) if monthly_avg_used_km is not None else None
        ),
        monthly_avg_left_km=(
            round(monthly_avg_left_km, 1) if monthly_avg_left_km is not None else None
        ),
        km_left_current_month=round(km_left_current_month, 1),
        days_left=days_left,
        full_months_elapsed=full_months_elapsed,
        full_months_remaining=full_months_remaining,
        current_odometer=current_odometer,
        start_odometer=start_odometer,
    )
