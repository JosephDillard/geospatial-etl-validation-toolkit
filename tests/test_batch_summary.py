from pathlib import Path
import shutil
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from spatial_validator.reports import batch_summary_data, render_batch_summary_markdown, write_reports
from spatial_validator.validators import validate_path


class BatchSummaryTests(unittest.TestCase):
    def test_batch_summary_counts_statuses_and_features(self) -> None:
        reports = validate_path(PROJECT_ROOT / "samples" / "valid")
        summary = batch_summary_data(reports)

        self.assertEqual(summary["dataset_count"], 2)
        self.assertEqual(summary["status_counts"]["pass"], 2)
        self.assertEqual(summary["total_features"], 6)

    def test_batch_summary_markdown_contains_dataset_table(self) -> None:
        reports = validate_path(PROJECT_ROOT / "samples" / "valid")
        markdown = render_batch_summary_markdown(reports)

        self.assertIn("# Batch Data Readiness Summary", markdown)
        self.assertIn("| Dataset | Driver | Status | Score | Features | Errors | Warnings |", markdown)
        self.assertIn("field_assets", markdown)

    def test_write_reports_can_include_batch_summary(self) -> None:
        temp_dir = Path(tempfile.mkdtemp())
        try:
            reports = validate_path(PROJECT_ROOT / "samples" / "valid")
            written = write_reports(reports, temp_dir, ["json", "markdown"], include_batch_summary=True)

            self.assertEqual(len(written), 6)
            self.assertTrue((temp_dir / "batch-summary.json").exists())
            self.assertTrue((temp_dir / "batch-summary.md").exists())
        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    unittest.main()
