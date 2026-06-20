from pathlib import Path
import shutil
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

try:
    import numpy as np
    import rasterio
    from rasterio.transform import from_origin
except ImportError:
    np = None
    rasterio = None
    from_origin = None

from spatial_validator.validators import validate_dataset


@unittest.skipUnless(rasterio is not None and np is not None, "Rasterio and NumPy are not installed")
class RasterValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_geotiff_metadata_and_cog_readiness_checks_are_reported(self) -> None:
        raster_path = self.temp_dir / "sample.tif"
        data = np.ones((1, 32, 32), dtype="uint8")

        with rasterio.open(
            raster_path,
            "w",
            driver="GTiff",
            height=32,
            width=32,
            count=1,
            dtype="uint8",
            crs="EPSG:4326",
            transform=from_origin(-96.5, 32.95, 0.01, 0.01),
        ) as dataset:
            dataset.write(data)

        report = validate_dataset(raster_path)

        self.assertEqual(report.driver, "GTiff")
        self.assertEqual(report.status, "warn")
        self.assertEqual(report.metadata["width"], 32)
        self.assertEqual(report.metadata["height"], 32)
        self.assertEqual(report.geometry_types, {"Raster": 1})
        check_ids = {check.check_id for check in report.checks}
        self.assertIn("cog.tiling", check_ids)
        self.assertIn("cog.overviews", check_ids)
        self.assertIn("cog.compression", check_ids)


if __name__ == "__main__":
    unittest.main()
