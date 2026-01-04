import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_servers.stellarium_server import (
    gregorian_to_julian,
    BIBLICAL_LOCATIONS,
    PROPHETIC_EVENTS,
)


class TestJulianDateConversion:
    def test_gregorian_to_julian_modern_date(self):
        jd = gregorian_to_julian(2017, 9, 23, 12.0)
        assert abs(jd - 2458019.5) < 1.5

    def test_gregorian_to_julian_j2000_epoch(self):
        jd = gregorian_to_julian(2000, 1, 1, 12.0)
        assert abs(jd - 2451545.0) < 1.0

    def test_gregorian_to_julian_bc_date(self):
        jd = gregorian_to_julian(-2, 9, 14, 12.0)
        assert jd > 0
        assert jd < 2000000

    def test_gregorian_to_julian_midnight_vs_noon(self):
        jd_noon = gregorian_to_julian(2020, 1, 1, 12.0)
        jd_midnight = gregorian_to_julian(2020, 1, 1, 0.0)
        assert abs(jd_noon - jd_midnight - 0.5) < 0.01


class TestBiblicalLocations:
    def test_jerusalem_coordinates(self):
        loc = BIBLICAL_LOCATIONS["jerusalem"]
        assert loc["lat"] == pytest.approx(31.7781, abs=0.01)
        assert loc["lon"] == pytest.approx(35.2353, abs=0.01)
        assert loc["name"] == "Jerusalem"

    def test_babylon_coordinates(self):
        loc = BIBLICAL_LOCATIONS["babylon"]
        assert loc["lat"] == pytest.approx(32.539, abs=0.01)
        assert loc["lon"] == pytest.approx(44.4208, abs=0.01)

    def test_all_locations_have_required_fields(self):
        required_fields = {"lat", "lon", "alt", "name"}
        for key, loc in BIBLICAL_LOCATIONS.items():
            for field in required_fields:
                assert field in loc, f"Location {key} missing {field}"

    def test_latitude_range(self):
        for key, loc in BIBLICAL_LOCATIONS.items():
            assert -90 <= loc["lat"] <= 90, f"{key} latitude out of range"

    def test_longitude_range(self):
        for key, loc in BIBLICAL_LOCATIONS.items():
            assert -180 <= loc["lon"] <= 180, f"{key} longitude out of range"


class TestPropheticEvents:
    def test_revelation_12_sign_exists(self):
        assert "revelation_12_sign" in PROPHETIC_EVENTS

    def test_revelation_12_sign_date(self):
        event = PROPHETIC_EVENTS["revelation_12_sign"]
        assert event["julian_date"] == pytest.approx(2458019.5, abs=1.0)
        assert "2017-09-23" in event["iso_date"]

    def test_star_of_bethlehem_bc_date(self):
        event = PROPHETIC_EVENTS["star_of_bethlehem_conjunction"]
        assert event["julian_date"] < 2000000
        assert "-0002" in event["iso_date"] or "-002" in event["iso_date"]

    def test_all_events_have_required_fields(self):
        required_fields = {"description", "julian_date", "iso_date", "location"}
        for key, event in PROPHETIC_EVENTS.items():
            for field in required_fields:
                assert field in event, f"Event {key} missing {field}"

    def test_all_events_reference_valid_location(self):
        for key, event in PROPHETIC_EVENTS.items():
            location = event["location"]
            assert location in BIBLICAL_LOCATIONS, f"Event {key} has invalid location {location}"


class TestJulianDateEdgeCases:
    def test_leap_year(self):
        jd1 = gregorian_to_julian(2020, 2, 29, 12.0)
        jd2 = gregorian_to_julian(2020, 3, 1, 12.0)
        assert abs(jd2 - jd1 - 1.0) < 0.01

    def test_year_boundary(self):
        jd1 = gregorian_to_julian(2019, 12, 31, 12.0)
        jd2 = gregorian_to_julian(2020, 1, 1, 12.0)
        assert abs(jd2 - jd1 - 1.0) < 0.01

    def test_february_boundary_non_leap_year(self):
        jd1 = gregorian_to_julian(2019, 2, 28, 12.0)
        jd2 = gregorian_to_julian(2019, 3, 1, 12.0)
        assert abs(jd2 - jd1 - 1.0) < 0.01
