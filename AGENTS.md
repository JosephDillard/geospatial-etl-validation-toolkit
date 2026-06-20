# Agent Guide

This repo is the data-readiness and validation layer in the companion
geospatial stack. It checks incoming datasets before they are loaded into
PostGIS, published as map services, or handed to downstream application teams.

## Suggested GitHub Description

Python geospatial ETL validation toolkit for checking GeoJSON, CSV, GeoPackage, Shapefile, and GeoTIFF inputs before PostGIS load or handoff.

## Stack Context

Related sibling repos:

- `geospatial-data-gateway` can consume validated inputs and load clean layers
  into PostGIS.
- `geospatial-status-board` visualizes published PostGIS/GeoServer layers and
  benefits from reliable source schemas.
- `geoai-asset-detection-platform` can produce or consume GIS-ready datasets
  that should be validated before handoff.
- `geospatial-mcp-services` may use validated map layers as assistant context.

When changing cross-repo docs, prefer full GitHub URLs for links that point
outside this repo.

## What This Repo Owns

- Validator package: `src/spatial_validator/`
- Unit tests: `tests/`
- Valid and invalid sample data: `samples/`
- Example reports: `reports/examples/`
- Architecture and load notes: `docs/`
- Optional local PostGIS service: `docker-compose.yml`
- CI validation workflow: `.github/workflows/validate.yml`

The main workflow is inspect, validate, report, and optionally plan or execute a
PostGIS load after validation passes.

## Development Notes

- Keep PostGIS optional for the first-run validation path. Users should be able
  to run sample validation without a database.
- Use structured geospatial readers such as GeoPandas/Pyogrio/Rasterio instead
  of ad hoc parsing when format support exists.
- Keep reports deterministic enough for tests and portfolio review.
- Treat required-field and domain checks as configurable customer/project rules,
  not hard-coded global assumptions.
- Keep generated reports under ignored output folders unless they are intentional
  examples in `reports/examples/`.

## Useful Commands

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
python -m spatial_validator validate samples\valid --report-dir reports\generated
python -m spatial_validator validate samples\invalid --report-dir reports\generated
Remove-Item Env:PYTHONPATH
```

Editable install:

```powershell
python -m pip install -e ".[geo,postgis]"
spatial-validator validate samples\valid --report-dir reports\generated
```

## Before Finishing Changes

- Run unit tests after validator, report, config, or PostGIS-load changes.
- Run a sample validation when changing CLI behavior or report output.
- Update `README.md`, `docs/architecture.md`, or
  `docs/postgis-load-plan.md` when checks, supported formats, report contracts,
  or load behavior change.
