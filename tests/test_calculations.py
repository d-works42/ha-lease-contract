"""Unit tests for calculations.py.

These import the module directly by file path so the test suite has no
dependency on Home Assistant being installed - calculations.py is pure
Python by design.
"""
from __future__ import annotations

import importlib.util
import sys
from datetime import date
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parent.parent
    / "custom_components"
    / "lease_contract"
    / "calculations.py"
)
spec = importlib.util.spec_from_file_location("calculations", MODULE_PATH)
calculations = importlib.util.module_from_spec(spec)
sys.modules["calculations"] = calculations
spec.loader.exec_module(calculations)

full_months_between = calculations.full_months_between
compute_contract_result = calculations.compute_contract_result


def test_full_months_between_exact_month():
    assert full_months_between(date(2026, 1, 15), date(2026, 2, 15)) == 1


def test_full_months_between_not_yet_a_full_month():
    assert full_months_between(date(2026, 1, 15), date(2026, 2, 10)) == 0


def test_full_months_between_same_day():
    assert full_months_between(date(2026, 1, 15), date(2026, 1, 15)) == 0


def test_full_months_between_end_before_start():
    assert full_months_between(date(2026, 2, 1), date(2026, 1, 1)) == 0


def test_full_months_between_multi_year():
    assert full_months_between(date(2024, 6, 1), date(2026, 9, 1)) == 27


def test_compute_contract_result_basic():
    result = compute_contract_result(
        start_date=date(2025, 1, 1),
        end_date=date(2027, 1, 1),
        max_km=30000,
        start_odometer=10000,
        current_odometer=20000,
        month_start_odometer=19500,
        today=date(2026, 9, 27),
    )

    assert result.used_km == 10000
    assert result.km_left == 20000
    assert result.monthly_avg_used_km == 500.0
    assert result.full_months_elapsed == 20
    assert result.full_months_remaining == 3
    assert result.monthly_avg_left_km == round(20000 / 3, 1)
    assert result.km_left_current_month == round(20000 / 3 - 500, 1)
    assert result.days_left == 96


def test_compute_contract_result_no_full_months_elapsed_yet():
    result = compute_contract_result(
        start_date=date(2026, 9, 20),
        end_date=date(2028, 9, 20),
        max_km=60000,
        start_odometer=5000,
        current_odometer=5100,
        month_start_odometer=5000,
        today=date(2026, 9, 27),
    )

    assert result.full_months_elapsed == 0
    assert result.monthly_avg_used_km is None
    assert result.used_km == 100


def test_compute_contract_result_contract_ended():
    result = compute_contract_result(
        start_date=date(2024, 1, 1),
        end_date=date(2026, 1, 1),
        max_km=45000,
        start_odometer=0,
        current_odometer=44000,
        month_start_odometer=43000,
        today=date(2026, 9, 27),
    )

    assert result.days_left == 0
    assert result.full_months_remaining == 0
    assert result.monthly_avg_left_km is None
    # Falls back to plain km_left when there are no full months remaining.
    assert result.km_left_current_month == result.km_left - 1000


def test_used_km_never_negative_if_odometer_looks_lower_than_baseline():
    result = compute_contract_result(
        start_date=date(2026, 1, 1),
        end_date=date(2028, 1, 1),
        max_km=30000,
        start_odometer=10000,
        current_odometer=9000,  # e.g. odometer entity briefly glitched
        month_start_odometer=9000,
        today=date(2026, 9, 27),
    )

    assert result.used_km == 0
