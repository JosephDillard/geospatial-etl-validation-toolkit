# Geospatial ETL Validation Toolkit

A portfolio-ready geospatial data readiness tool for validating incoming datasets before they are loaded into PostGIS, published as map services, or handed to downstream application teams.

The goal is to show practical GIS architecture judgment: data quality, ETL safety, repeatable reporting, and clear communication between GIS, database, cloud, and application teams.

## What It Does Today

- Validates GeoJSON FeatureCollections.
- Validates CSV files with latitude and longitude columns.
- Reports feature counts, fields, geometry types, bounding boxes, null or blank values, and validation checks.
- Generates Markdown, JSON, and HTML data-readiness reports.
- Includes valid and invalid sample datasets for quick review.
- Keeps PostGIS as an optional next step instead of requiring a database for the first run.
- Includes a GitHub Actions workflow that runs unit tests and validates passing sample datasets.

## Why This Matters

Many GIS delivery problems begin with data that is almost ready: missing fields, bad coordinates, invalid geometries, unclear ownership, or schema drift. This toolkit catches those issues early and creates a report that a customer, GIS analyst, developer, or database team can act on.

## Quick Start

Run the validator directly from the source tree:

```powershell
$env:PYTHONPATH = "src"
python -m spatial_validator validate samples\valid --report-dir reports\generated
```

Validate the intentionally bad samples:

```powershell
$env:PYTHONPATH = "src"
python -m spatial_validator validate samples\invalid --report-dir reports\generated
```

Run tests:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

Install as an editable package:

```powershell
python -m pip install -e .
spatial-validator validate samples\valid --report-dir reports\generated
```

## Example Output

```text
field_assets: PASS (100/100, 3 features)
service_locations: PASS (100/100, 3 features)
wrote reports\generated\field-assets.md
wrote reports\generated\field-assets.json
wrote reports\generated\field-assets.html
```

## Repository Map

- `src/spatial_validator/validators.py` - GeoJSON and CSV validation logic.
- `src/spatial_validator/reports.py` - Markdown, JSON, and HTML report generation.
- `samples/valid` - Datasets expected to pass readiness checks.
- `samples/invalid` - Datasets expected to fail or warn.
- `reports/examples` - Committed example reports for reviewers.
- `docs/architecture.md` - Architecture notes and expansion path.
- `docs/postgis-load-plan.md` - Planned PostGIS loading workflow.
- `docker-compose.yml` - Optional local PostGIS service for future load testing.
- `.github/workflows/validate.yml` - Continuous validation for tests and passing sample data.

## Checks Included

| Area | Starter checks |
|---|---|
| Input | Supported format, parse errors, empty dataset |
| Schema | Field discovery, null or blank value counts |
| Geometry | Type counts, basic coordinate validation, coordinate range checks |
| Spatial | Bounding box calculation |
| Reporting | Status, readiness score, check details, ETL notes |

## Fit With The Larger Geospatial Stack

This toolkit can sit in front of a data gateway or operational status board:

1. Validate incoming files.
2. Generate a readiness report.
3. Load clean data to PostGIS.
4. Publish or refresh downstream map services.
5. Notify browser map clients when validated layers change.

That makes it useful as a standalone portfolio project and as a future validation layer for the broader geospatial platform.

## Roadmap

- Add GeoPackage and Shapefile support through optional GeoPandas/Pyogrio dependencies.
- Add configurable required fields, domains, and customer-specific schema rules.
- Add raster metadata validation for COG-oriented workflows.
- Add PostGIS staging-table load execution.
- Add batch summary reports for data handoffs.
- Add GitHub Actions validation for all sample datasets.
