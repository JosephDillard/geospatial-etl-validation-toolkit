from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from spatial_validator.validators import validate_dataset


class GeoJSONValidatorTests(unittest.TestCase):
    def test_valid_geojson_passes_with_bbox_and_fields(self) -> None:
        report = validate_dataset(PROJECT_ROOT / "samples" / "valid" / "field_assets.geojson")

        self.assertEqual(report.status, "pass")
        self.assertEqual(report.feature_count, 3)
        self.assertEqual(report.geometry_types, {"Point": 3})
        self.assertIn("asset_id", report.fields)
        self.assertIsNotNone(report.bbox)

    def test_invalid_geojson_fails_on_bad_coordinates_and_ring(self) -> None:
        report = validate_dataset(PROJECT_ROOT / "samples" / "invalid" / "bad_assets.geojson")

        self.assertEqual(report.status, "fail")
        self.assertLess(report.readiness_score, 100)
        check_ids = {check.check_id for check in report.checks}
        self.assertIn("geometry.invalid", check_ids)
        self.assertIn("schema.null_values", check_ids)


if __name__ == "__main__":
    unittest.main()
