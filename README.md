# Geospatial ETL Validation Toolkit

A portfolio-ready geospatial data readiness tool for validating incoming datasets before they are loaded into PostGIS, published as map services, or handed to downstream application teams.

The goal is to show practical GIS architecture judgment: data quality, ETL safety, repeatable reporting, and clear communication between GIS, database, cloud, and application teams.

## What It Does Today

- Validates GeoJSON FeatureCollections.
- Validates CSV files with latitude and longitude columns.
- Validates GeoPackage and Shapefile vector datasets through GeoPandas/Pyogrio.
- Inspects GeoTIFF raster metadata for Cloud Optimized GeoTIFF readiness signals.
- Applies configurable required-field and domain checks from JSON or YAML rule files.
- Loads passing vector datasets to PostGIS through an explicit validation gate.
- Reports feature counts, fields, geometry types, bounding boxes, null or blank values, and validation checks.
- Generates Markdown, JSON, and HTML data-readiness reports plus batch handoff summaries.
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

Validate with customer-specific field and domain rules:

```powershell
$env:PYTHONPATH = "src"
python -m spatial_validator validate samples\valid --config samples\validation-rules.json --report-dir reports\generated
```

Run tests:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

Install as an editable package:

```powershell
python -m pip install -e ".[geo,postgis]"
spatial-validator validate samples\valid --report-dir reports\generated
```

Dry-run a PostGIS load plan after validation passes:

```powershell
$env:PYTHONPATH = "src"
python -m spatial_validator load-postgis samples\valid\field_assets.geojson `
  --connection "postgresql+psycopg://spatial_validator:spatial_validator@localhost:5434/spatial_validator" `
  --table staging.field_assets `
  --dry-run
```

## Example Output

```text
field_assets: PASS (100/100, 3 features)
service_locations: PASS (100/100, 3 features)
wrote reports\generated\field-assets.md
wrote reports\generated\field-assets.json
wrote reports\generated\field-assets.html
wrote reports\generated\batch-summary.md
```

## Repository Map

This repo is the validation and handoff layer in the public geospatial stack. It
can be used before the Data Gateway loads a source, before GeoServer publishes a
layer, or before the Status Board depends on customer-provided data.

- `src/spatial_validator/validators.py` - GeoJSON, CSV, GeoPackage, Shapefile, and GeoTIFF validation logic.
- `src/spatial_validator/reports.py` - Markdown, JSON, and HTML report generation.
- `samples/valid` - Datasets expected to pass readiness checks.
- `samples/invalid` - Datasets expected to fail or warn.
- `samples/validation-rules.json` - Example required-field and domain rules.
- `reports/examples` - Committed example reports for reviewers.
- `docs/architecture.md` - Architecture notes and expansion path.
- `docs/postgis-load-plan.md` - PostGIS validation gate and loading workflow.
- `docker-compose.yml` - Optional local PostGIS service for future load testing.
- `.github/workflows/validate.yml` - Continuous validation for tests and passing sample data.

Companion repos:

- [Portfolio site](https://josephdillard.github.io/JosephDillard/)
- [Geospatial ETL Validation Toolkit repo](https://github.com/JosephDillard/geospatial-etl-validation-toolkit)
- [Geospatial Data Gateway](https://github.com/JosephDillard/geospatial-data-gateway)
- [Geospatial Status Board](https://github.com/JosephDillard/geospatial-status-board)
- [GeoAI Asset Detection Platform](https://github.com/JosephDillard/geoai-asset-detection-platform)

## Checks Included

| Area | Starter checks |
|---|---|
| Input | Supported format, parse errors, empty dataset |
| Schema | Field discovery, null or blank value counts, required fields, domain values |
| Geometry | Type counts, coordinate validation, GeoPandas geometry validity checks |
| Spatial | Bounding box calculation, CRS detection |
| Raster | Driver, dimensions, CRS, tiling, overviews, compression, block shapes |
| Loading | PostGIS dry-run planning, validation gate, target SRID, if-exists behavior |
| Reporting | Status, readiness score, check details, ETL notes, batch handoff summaries |

## Fit With The Larger Geospatial Stack

This toolkit can sit in front of a data gateway or operational status board:

1. Validate incoming files.
2. Generate a readiness report.
3. Load clean data to PostGIS.
4. Publish or refresh downstream map services.
5. Notify browser map clients when validated layers change.

That makes it useful as a standalone portfolio project and as a future validation layer for the broader geospatial platform.

## Roadmap

- Add a gateway handoff manifest that can be consumed directly by
  `geospatial-data-gateway`.
- Add optional GeoServer publish-readiness checks after PostGIS load planning.
- Add richer customer handoff templates with remediation notes by data owner,
  source system, and target layer.
