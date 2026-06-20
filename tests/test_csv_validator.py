from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from spatial_validator.validators import validate_dataset


class CSVValidatorTests(unittest.TestCase):
    def test_valid_csv_detects_coordinates(self) -> None:
        report = validate_dataset(PROJECT_ROOT / "samples" / "valid" / "service_locations.csv")

        self.assertEqual(report.status, "pass")
        self.assertEqual(report.feature_count, 3)
        self.assertEqual(report.geometry_types, {"Point": 3})
        self.assertIsNotNone(report.bbox)

    def test_invalid_csv_fails_on_numeric_and_range_errors(self) -> None:
        report = validate_dataset(PROJECT_ROOT / "samples" / "invalid" / "bad_service_locations.csv")

        self.assertEqual(report.status, "fail")
        check_ids = {check.check_id for check in report.checks}
        self.assertIn("csv.coordinates.numeric", check_ids)
        self.assertIn("csv.coordinates.range", check_ids)
        self.assertIn("schema.null_values", check_ids)


if __name__ == "__main__":
    unittest.main()
