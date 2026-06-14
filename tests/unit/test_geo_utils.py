import pytest

from app.utils.geo import haversine_distance


class TestHaversineDistance:
    def test_same_point_returns_zero(self):
        assert haversine_distance(4.0, -74.0, 4.0, -74.0) == pytest.approx(0.0, abs=1e-6)

    def test_known_distance_barranquilla_bogota(self):
        # Barranquilla -> Bogotá: ~960 km
        dist = haversine_distance(10.9639, -74.7964, 4.7110, -74.0721)
        assert 950_000 < dist < 970_000

    def test_within_validation_radius(self):
        # 25 metres apart — should be within 30m radius
        lat1, lon1 = 10.9639, -74.7964
        # ~25m north
        lat2 = lat1 + (25 / 111_320)
        dist = haversine_distance(lat1, lon1, lat2, lon1)
        assert dist < 30.0

    def test_outside_validation_radius(self):
        lat1, lon1 = 10.9639, -74.7964
        # ~100m north
        lat2 = lat1 + (100 / 111_320)
        dist = haversine_distance(lat1, lon1, lat2, lon1)
        assert dist > 30.0

    def test_symmetry(self):
        d1 = haversine_distance(10.0, -74.0, 11.0, -75.0)
        d2 = haversine_distance(11.0, -75.0, 10.0, -74.0)
        assert d1 == pytest.approx(d2, rel=1e-9)
