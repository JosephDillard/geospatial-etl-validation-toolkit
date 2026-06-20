from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from spatial_validator.models import DatasetReport


SUPPORTED_SUFFIXES = {".geojson", ".json", ".csv"}
LON_NAMES = {"lon", "lng", "long", "longitude", "x"}
LAT_NAMES = {"lat", "latitude", "y"}


def validate_path(path: str | Path) -> list[DatasetReport]:
    target = Path(path)
    if target.is_dir():
        files = sorted(
            item for item in target.rglob("*") if item.is_file() and item.suffix.lower() in SUPPORTED_SUFFIXES
        )
        if not files:
            report = DatasetReport(target, target.name, "directory")
            report.add_check("input.no_supported_files", "error", "No supported GeoJSON, JSON, or CSV files were found.")
            return [report]
        return [validate_dataset(file_path) for file_path in files]
    return [validate_dataset(target)]


def validate_dataset(path: Path) -> DatasetReport:
    suffix = path.suffix.lower()
    if suffix in {".geojson", ".json"}:
        return validate_geojson(path)
    if suffix == ".csv":
        return validate_csv(path)

    report = DatasetReport(path, path.stem, "unsupported")
    report.add_check(
        "input.unsupported_format",
        "error",
        "Unsupported file type. Supported starter formats are GeoJSON, JSON, and CSV.",
        {"suffix": suffix},
    )
    return report


def validate_geojson(path: Path) -> DatasetReport:
    report = DatasetReport(path=path, dataset_name=path.stem, driver="GeoJSON")

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        report.add_check("geojson.parse", "error", "GeoJSON could not be parsed.", {"error": str(exc)})
        return report

    if payload.get("type") != "FeatureCollection":
        report.add_check(
            "geojson.type",
            "error",
            "GeoJSON input should be a FeatureCollection for ETL readiness checks.",
            {"type": payload.get("type")},
        )
        return report

    features = payload.get("features")
    if not isinstance(features, list):
        report.add_check("geojson.features", "error", "FeatureCollection features must be a list.")
        return report

    report.feature_count = len(features)
    if report.feature_count == 0:
        report.add_check("dataset.empty", "error", "Dataset contains zero features.")

    field_names: set[str] = set()
    geometry_counter: Counter[str] = Counter()
    null_counter: Counter[str] = Counter()
    coordinate_values: list[tuple[float, float]] = []
    invalid_geometry_count = 0

    for index, feature in enumerate(features):
        if not isinstance(feature, dict) or feature.get("type") != "Feature":
            report.add_check("geojson.feature.type", "error", "Each item must be a GeoJSON Feature.", {"index": index})
            continue

        properties = feature.get("properties") or {}
        if not isinstance(properties, dict):
            report.add_check(
                "geojson.properties",
                "warning",
                "Feature properties should be an object.",
                {"index": index},
            )
            properties = {}

        field_names.update(properties.keys())
        for key, value in properties.items():
            if value in (None, ""):
                null_counter[key] += 1

        geometry = feature.get("geometry")
        geometry_type = geometry.get("type") if isinstance(geometry, dict) else "None"
        geometry_counter[str(geometry_type)] += 1
        geometry_errors, coordinates = inspect_geometry(geometry)
        coordinate_values.extend(coordinates)
        if geometry_errors:
            invalid_geometry_count += 1
            report.add_check(
                "geometry.invalid",
                "error",
                "Feature geometry failed basic coordinate validation.",
                {"index": index, "errors": geometry_errors},
            )

    report.fields = sorted(field_names)
    report.geometry_types = dict(sorted(geometry_counter.items()))
    report.null_counts = dict(sorted(null_counter.items()))
    report.bbox = calculate_bbox(coordinate_values)

    add_common_checks(report)
    if invalid_geometry_count == 0 and report.feature_count > 0:
        report.add_check("geometry.basic_validity", "info", "All geometries passed starter coordinate validation.")

    return report


def validate_csv(path: Path) -> DatasetReport:
    report = DatasetReport(path=path, dataset_name=path.stem, driver="CSV")

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
            fieldnames = reader.fieldnames or []
    except UnicodeDecodeError as exc:
        report.add_check("csv.encoding", "error", "CSV could not be read as UTF-8.", {"error": str(exc)})
        return report

    report.fields = list(fieldnames)
    report.feature_count = len(rows)

    if not fieldnames:
        report.add_check("csv.header", "error", "CSV is missing a header row.")
        return report

    if report.feature_count == 0:
        report.add_check("dataset.empty", "error", "Dataset contains zero records.")

    lon_field, lat_field = detect_coordinate_fields(fieldnames)
    if not lon_field or not lat_field:
        report.add_check(
            "csv.coordinates.missing",
            "error",
            "CSV needs recognizable latitude and longitude columns.",
            {"latitude_names": sorted(LAT_NAMES), "longitude_names": sorted(LON_NAMES)},
        )
    else:
        report.geometry_types = {"Point": report.feature_count}

    null_counter: Counter[str] = Counter()
    coordinate_values: list[tuple[float, float]] = []

    for row_number, row in enumerate(rows, start=2):
        for key, value in row.items():
            if value in (None, ""):
                null_counter[key] += 1

        if lon_field and lat_field:
            lon_raw = row.get(lon_field, "")
            lat_raw = row.get(lat_field, "")
            try:
                lon = float(lon_raw)
                lat = float(lat_raw)
            except ValueError:
                report.add_check(
                    "csv.coordinates.numeric",
                    "error",
                    "Coordinate values must be numeric.",
                    {"row": row_number, "lon": lon_raw, "lat": lat_raw},
                )
                continue

            if not (-180 <= lon <= 180 and -90 <= lat <= 90):
                report.add_check(
                    "csv.coordinates.range",
                    "error",
                    "Coordinate values fall outside valid WGS84 longitude/latitude ranges.",
                    {"row": row_number, "lon": lon, "lat": lat},
                )
                continue
            coordinate_values.append((lon, lat))

    report.null_counts = dict(sorted(null_counter.items()))
    report.bbox = calculate_bbox(coordinate_values)
    add_common_checks(report)

    if lon_field and lat_field and report.bbox:
        report.add_check(
            "csv.coordinates.detected",
            "info",
            "Latitude and longitude columns were detected.",
            {"longitude": lon_field, "latitude": lat_field},
        )

    return report


def detect_coordinate_fields(fieldnames: Iterable[str]) -> tuple[str | None, str | None]:
    lowered = {field.lower().strip(): field for field in fieldnames}
    lon = next((lowered[name] for name in LON_NAMES if name in lowered), None)
    lat = next((lowered[name] for name in LAT_NAMES if name in lowered), None)
    return lon, lat


def inspect_geometry(geometry: Any) -> tuple[list[str], list[tuple[float, float]]]:
    errors: list[str] = []
    coordinates: list[tuple[float, float]] = []

    if not isinstance(geometry, dict):
        return ["Geometry is missing or not an object."], coordinates

    geometry_type = geometry.get("type")
    raw_coordinates = geometry.get("coordinates")
    if geometry_type is None or raw_coordinates is None:
        return ["Geometry type or coordinates are missing."], coordinates

    if geometry_type == "Point":
        point = parse_position(raw_coordinates)
        if point is None:
            errors.append("Point coordinates are invalid.")
        else:
            coordinates.append(point)
    elif geometry_type == "LineString":
        line = [parse_position(item) for item in raw_coordinates or []]
        if len(line) < 2 or any(point is None for point in line):
            errors.append("LineString must contain at least two valid positions.")
        coordinates.extend(point for point in line if point is not None)
    elif geometry_type == "Polygon":
        rings = raw_coordinates or []
        if not rings:
            errors.append("Polygon must contain at least one ring.")
        for ring_index, ring in enumerate(rings):
            parsed_ring = [parse_position(item) for item in ring or []]
            valid_ring = [point for point in parsed_ring if point is not None]
            if len(valid_ring) < 4:
                errors.append(f"Polygon ring {ring_index} must contain at least four positions.")
            elif valid_ring[0] != valid_ring[-1]:
                errors.append(f"Polygon ring {ring_index} is not closed.")
            if len(valid_ring) != len(parsed_ring):
                errors.append(f"Polygon ring {ring_index} contains invalid positions.")
            coordinates.extend(valid_ring)
    elif geometry_type in {"MultiPoint", "MultiLineString", "MultiPolygon"}:
        flattened = flatten_positions(raw_coordinates)
        if not flattened:
            errors.append(f"{geometry_type} does not contain valid positions.")
        coordinates.extend(flattened)
    else:
        errors.append(f"Unsupported geometry type for starter validator: {geometry_type}.")

    out_of_range = [point for point in coordinates if not (-180 <= point[0] <= 180 and -90 <= point[1] <= 90)]
    if out_of_range:
        errors.append("One or more coordinates fall outside WGS84 longitude/latitude ranges.")

    return errors, coordinates


def parse_position(value: Any) -> tuple[float, float] | None:
    if not isinstance(value, list | tuple) or len(value) < 2:
        return None
    try:
        lon = float(value[0])
        lat = float(value[1])
    except (TypeError, ValueError):
        return None
    return lon, lat


def flatten_positions(value: Any) -> list[tuple[float, float]]:
    positions: list[tuple[float, float]] = []
    point = parse_position(value)
    if point is not None:
        return [point]
    if isinstance(value, list):
        for item in value:
            positions.extend(flatten_positions(item))
    return positions


def calculate_bbox(coordinates: list[tuple[float, float]]) -> tuple[float, float, float, float] | None:
    if not coordinates:
        return None
    lon_values = [point[0] for point in coordinates]
    lat_values = [point[1] for point in coordinates]
    return min(lon_values), min(lat_values), max(lon_values), max(lat_values)


def add_common_checks(report: DatasetReport) -> None:
    if report.fields:
        report.add_check("schema.fields_present", "info", "Attribute fields were detected.", {"field_count": len(report.fields)})
    else:
        report.add_check("schema.no_fields", "warning", "No attribute fields were detected.")

    if report.null_counts:
        report.add_check("schema.null_values", "warning", "One or more fields contain null or blank values.", report.null_counts)
    else:
        report.add_check("schema.null_values", "info", "No null or blank attribute values were found.")

    if report.bbox:
        report.add_check("spatial.bbox", "info", "Dataset bounds were calculated.", {"bbox": report.bbox})
    else:
        report.add_check("spatial.bbox", "warning", "Dataset bounds could not be calculated.")
