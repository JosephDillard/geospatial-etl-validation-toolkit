from pathlib import Path
import shutil
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

try:
    import geopandas as gpd
    from shapely.geometry import Point, Polygon
except ImportError:
    gpd = None
    Point = None
    Polygon = None

from spatial_validator.validators import validate_dataset


@unittest.skipUnless(gpd is not None, "GeoPandas is not installed")
class VectorValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp())
        self.gdf = gpd.GeoDataFrame(
            {
                "asset_id": ["GPKG-1", "GPKG-2"],
                "status": ["active", "maintenance"],
            },
            geometry=[Point(-96.45, 32.93), Point(-96.46, 32.94)],
            crs="EPSG:4326",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_geopackage_validation_reads_metadata(self) -> None:
        gpkg_path = self.temp_dir / "assets.gpkg"
        self.gdf.to_file(gpkg_path, layer="assets", driver="GPKG")

        report = validate_dataset(gpkg_path)

        self.assertEqual(report.status, "pass")
        self.assertEqual(report.driver, "GeoPackage")
        self.assertEqual(report.feature_count, 2)
        self.assertEqual(report.crs, "EPSG:4326")
        self.assertIn("layers", report.metadata)

    def test_shapefile_validation_reads_geometry(self) -> None:
        shp_path = self.temp_dir / "assets.shp"
        self.gdf.to_file(shp_path)

        report = validate_dataset(shp_path)

        self.assertEqual(report.status, "pass")
        self.assertEqual(report.driver, "ESRI Shapefile")
        self.assertEqual(report.geometry_types, {"Point": 2})
        self.assertIsNotNone(report.bbox)

    def test_invalid_vector_geometry_fails(self) -> None:
        bad_gdf = gpd.GeoDataFrame(
            {"asset_id": ["BAD-GEOM"]},
            geometry=[Polygon([(0, 0), (1, 1), (1, 0), (0, 1), (0, 0)])],
            crs="EPSG:4326",
        )
        gpkg_path = self.temp_dir / "bad_assets.gpkg"
        bad_gdf.to_file(gpkg_path, layer="bad_assets", driver="GPKG")

        report = validate_dataset(gpkg_path)

        self.assertEqual(report.status, "fail")
        check_ids = {check.check_id for check in report.checks}
        self.assertIn("geometry.invalid", check_ids)


if __name__ == "__main__":
    unittest.main()
