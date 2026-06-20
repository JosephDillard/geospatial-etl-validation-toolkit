# Architecture

The toolkit is designed as a small but credible geospatial data-readiness workflow.

## Current Flow

1. A GIS analyst, data engineer, or application team points the validator at a dataset or folder.
2. The validator runs format-specific checks for GeoJSON, CSV, GeoPackage, and Shapefile.
3. The report model normalizes feature counts, fields, geometry types, CRS, bounds, null counts, check results, status, and readiness score.
4. The report writer emits Markdown, JSON, and HTML artifacts.
5. A reviewer can decide whether the dataset is ready for PostGIS loading or needs cleanup.

## Why This Helps A GIS Architecture Conversation

Data readiness problems often appear late in GIS projects: unknown coordinate systems, blank key fields, invalid geometries, inconsistent schemas, and downstream map-service failures. This project makes those risks visible before production loading.

## Planned Expansion

- Add raster metadata inspection for Cloud Optimized GeoTIFF readiness.
- Add configurable required-field and domain checks.
- Add PostGIS load execution after validation passes.
- Add a batch summary report for large customer handoffs.
- Add GitHub Actions so every sample dataset is validated automatically.
