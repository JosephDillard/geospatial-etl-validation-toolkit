from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from spatial_validator.config import config_from_mapping, load_validation_config
from spatial_validator.validators import validate_dataset


class ConfigRuleTests(unittest.TestCase):
    def test_sample_config_applies_to_valid_geojson(self) -> None:
        config = load_validation_config(PROJECT_ROOT / "samples" / "validation-rules.json")
        report = validate_dataset(PROJECT_ROOT / "samples" / "valid" / "field_assets.geojson", config)

        self.assertEqual(report.status, "pass")
        check_ids = {check.check_id for check in report.checks}
        self.assertIn("config.rules_applied", check_ids)

    def test_required_field_rule_fails_when_field_is_missing(self) -> None:
        config = config_from_mapping({"required_fields": ["asset_id", "missing_field"]})
        report = validate_dataset(PROJECT_ROOT / "samples" / "valid" / "field_assets.geojson", config)

        self.assertEqual(report.status, "fail")
        check_ids = {check.check_id for check in report.checks}
        self.assertIn("config.required_field.missing", check_ids)

    def test_domain_rule_fails_on_unapproved_values(self) -> None:
        config = config_from_mapping({"domains": {"status": ["active"]}})
        report = validate_dataset(PROJECT_ROOT / "samples" / "valid" / "field_assets.geojson", config)

        self.assertEqual(report.status, "fail")
        check_ids = {check.check_id for check in report.checks}
        self.assertIn("config.domain.invalid_value", check_ids)


if __name__ == "__main__":
    unittest.main()
