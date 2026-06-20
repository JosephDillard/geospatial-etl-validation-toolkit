from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from spatial_validator.config import ValidationConfig
from spatial_validator.models import DatasetReport
from spatial_validator.validators import detect_coordinate_fields, validate_path


@dataclass(frozen=True)
class PostGISLoadPlan:
    table_name: str
    source_path: str
    target_srid: int = 4326
    if_exists: str = "replace"
    schema: str | None = None

    def summary(self) -> str:
        target = f"{self.schema}.{self.table_name}" if self.schema else self.table_name
        return (
            f"Load {self.source_path} into PostGIS table {target} "
            f"with SRID {self.target_srid} using if_exists={self.if_exists}."
        )


@dataclass(frozen=True)
class PostGISLoadResult:
    plan: PostGISLoadPlan
    reports: list[DatasetReport] = field(default_factory=list)
    loaded: bool = False
    row_count: int = 0
    message: str = ""


def build_load_plan(
    source_path: str,
    table_name: str,
    target_srid: int = 4326,
    if_exists: str = "replace",
) -> PostGISLoadPlan:
    """Return a PostGIS load plan without connecting to a database yet."""
    schema, table = split_table_name(table_name)
    return PostGISLoadPlan(
        source_path=source_path,
        table_name=table,
        schema=schema,
        target_srid=target_srid,
        if_exists=if_exists,
    )


def load_to_postgis(
    source_path: str | Path,
    connection_string: str,
    table_name: str,
    *,
    config: ValidationConfig | None = None,
    target_srid: int = 4326,
    if_exists: str = "replace",
    allow_warnings: bool = False,
    dry_run: bool = False,
) -> PostGISLoadResult:
    plan = build_load_plan(str(source_path), table_name, target_srid=target_srid, if_exists=if_exists)
    reports = validate_path(source_path, config)
    validate_load_gate(reports, allow_warnings=allow_warnings)

    if dry_run:
        return PostGISLoadResult(
            plan=plan,
            reports=reports,
            loaded=False,
            row_count=sum(report.feature_count for report in reports),
            message="Dry run passed validation; no database write was attempted.",
        )

    gdf = read_source_as_geodataframe(Path(source_path), target_srid=target_srid)

    try:
        from sqlalchemy import create_engine
    except ImportError as exc:
        raise RuntimeError("PostGIS loading requires SQLAlchemy. Install the postgis optional dependencies.") from exc

    try:
        engine = create_engine(connection_string)
        gdf.to_postgis(
            name=plan.table_name,
            con=engine,
            schema=plan.schema,
            if_exists=if_exists,
            index=False,
        )
    except Exception as exc:
        raise RuntimeError(f"PostGIS load failed: {exc}") from exc

    return PostGISLoadResult(
        plan=plan,
        reports=reports,
        loaded=True,
        row_count=int(len(gdf)),
        message="Dataset loaded to PostGIS.",
    )


def validate_load_gate(reports: list[DatasetReport], *, allow_warnings: bool = False) -> None:
    if not reports:
        raise RuntimeError("No validation reports were produced; refusing to load PostGIS.")
    if len(reports) > 1:
        raise RuntimeError("PostGIS load currently accepts one dataset at a time.")
    if any(report.has_errors for report in reports):
        raise RuntimeError("Validation failed; refusing to load PostGIS.")
    if not allow_warnings and any(report.has_warnings for report in reports):
        raise RuntimeError("Validation produced warnings; pass allow_warnings to load anyway.")


def read_source_as_geodataframe(path: Path, *, target_srid: int = 4326):
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return csv_to_geodataframe(path, target_srid=target_srid)
    if suffix in {".geojson", ".json", ".gpkg", ".shp"}:
        try:
            import geopandas as gpd
        except ImportError as exc:
            raise RuntimeError("Vector loading requires GeoPandas.") from exc

        gdf = gpd.read_file(path)
        if gdf.crs is None:
            raise RuntimeError("Vector dataset CRS is missing; assign a CRS before loading to PostGIS.")
        if target_srid:
            gdf = gdf.to_crs(epsg=target_srid)
        return gdf

    raise RuntimeError("PostGIS load supports CSV, GeoJSON, GeoPackage, and Shapefile inputs.")


def csv_to_geodataframe(path: Path, *, target_srid: int = 4326):
    try:
        import geopandas as gpd
        import pandas as pd
    except ImportError as exc:
        raise RuntimeError("CSV PostGIS loading requires GeoPandas and Pandas.") from exc

    df = pd.read_csv(path)
    lon_field, lat_field = detect_coordinate_fields(df.columns)
    if not lon_field or not lat_field:
        raise RuntimeError("CSV load requires recognizable latitude and longitude columns.")

    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df[lon_field], df[lat_field]),
        crs="EPSG:4326",
    )
    if target_srid:
        gdf = gdf.to_crs(epsg=target_srid)
    return gdf


def split_table_name(table_name: str) -> tuple[str | None, str]:
    parts = [part.strip() for part in table_name.split(".") if part.strip()]
    if not parts:
        raise ValueError("PostGIS table name is required.")
    if len(parts) == 1:
        return None, parts[0]
    if len(parts) == 2:
        return parts[0], parts[1]
    raise ValueError("PostGIS table name should be table or schema.table.")
