# Reviewer Guide

This repo is meant to be reviewed quickly by hiring managers, GIS architects, and technical leads.

## What To Look At First

- `README.md` explains the business value and commands.
- `samples/valid` and `samples/invalid` show the validation story.
- `samples/validation-rules.json` shows configurable required-field and domain checks.
- `src/spatial_validator/validators.py` contains the GeoJSON, CSV, GeoPackage, Shapefile, and GeoTIFF checks.
- `src/spatial_validator/reports.py` generates Markdown, JSON, and HTML readiness reports.
- `reports/examples/batch-summary.md` shows the customer handoff view across multiple datasets.
- `src/spatial_validator/postgis.py` validates and loads passing vector data to PostGIS.
- `docs/architecture.md` explains how this grows into a production ETL validation layer.

## What The Project Demonstrates

- Practical GIS data quality thinking.
- Customer-specific schema governance through configurable rules.
- Python automation for geospatial ETL.
- Vector validation with GeoPandas/Pyogrio for reviewer-friendly GIS formats.
- Raster metadata inspection for COG-oriented readiness conversations.
- Clear customer-facing reporting.
- Batch summaries for large data handoffs.
- A path from raw data to PostGIS-backed map applications.
- PostGIS loading guarded by validation results instead of blind ingestion.
- Lightweight architecture choices that can grow into heavier GIS dependencies when needed.
