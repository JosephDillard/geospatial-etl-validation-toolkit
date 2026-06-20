from pathlib import Path
import shutil
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from spatial_validator.reports import render_markdown, write_reports
from spatial_validator.validators import validate_dataset


class ReportRenderingTests(unittest.TestCase):
    def test_markdown_report_contains_readiness_summary(self) -> None:
        report = validate_dataset(PROJECT_ROOT / "samples" / "valid" / "field_assets.geojson")
        markdown = render_markdown(report)

        self.assertIn("# Data Readiness Report", markdown)
        self.assertIn("Readiness Score", markdown)
        self.assertIn("ETL Notes", markdown)

    def test_write_reports_creates_selected_formats(self) -> None:
        temp_dir = Path(tempfile.mkdtemp())
        try:
            report = validate_dataset(PROJECT_ROOT / "samples" / "valid" / "field_assets.geojson")
            written = write_reports([report], temp_dir, ["json", "markdown"])

            self.assertEqual(len(written), 2)
            self.assertTrue((temp_dir / "field-assets.json").exists())
            self.assertTrue((temp_dir / "field-assets.md").exists())
        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    unittest.main()
