from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from spatial_validator.postgis import build_load_plan, load_to_postgis, split_table_name


class PostGISLoaderTests(unittest.TestCase):
    def test_build_load_plan_splits_schema_and_table(self) -> None:
        plan = build_load_plan("samples/valid/field_assets.geojson", "staging.field_assets")

        self.assertEqual(plan.schema, "staging")
        self.assertEqual(plan.table_name, "field_assets")
        self.assertIn("staging.field_assets", plan.summary())

    def test_dry_run_validates_without_database_write(self) -> None:
        result = load_to_postgis(
            PROJECT_ROOT / "samples" / "valid" / "field_assets.geojson",
            "postgresql+psycopg://user:password@localhost:5432/spatial_validator",
            "staging.field_assets",
            dry_run=True,
        )

        self.assertFalse(result.loaded)
        self.assertEqual(result.row_count, 3)
        self.assertIn("Dry run", result.message)

    def test_validation_failure_refuses_postgis_load(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "Validation failed"):
            load_to_postgis(
                PROJECT_ROOT / "samples" / "invalid" / "bad_assets.geojson",
                "postgresql+psycopg://user:password@localhost:5432/spatial_validator",
                "staging.bad_assets",
                dry_run=True,
            )

    def test_split_table_name_allows_table_only(self) -> None:
        schema, table = split_table_name("field_assets")

        self.assertIsNone(schema)
        self.assertEqual(table, "field_assets")


if __name__ == "__main__":
    unittest.main()
