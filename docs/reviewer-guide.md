# Reviewer Guide

This repo is meant to be reviewed quickly by hiring managers, GIS architects, and technical leads.

## What To Look At First

- `README.md` explains the business value and commands.
- `samples/valid` and `samples/invalid` show the validation story.
- `samples/validation-rules.json` shows configurable required-field and domain checks.
- `src/spatial_validator/validators.py` contains the GeoJSON, CSV, GeoPackage, Shapefile, and GeoTIFF checks.
- `src/spatial_validator/reports.py` generates Markdown, JSON, and HTML readiness reports.
- `docs/architecture.md` explains how this grows into a production ETL validation layer.

## What The Project Demonstrates

- Practical GIS data quality thinking.
- Customer-specific schema governance through configurable rules.
- Python automation for geospatial ETL.
- Vector validation with GeoPandas/Pyogrio for reviewer-friendly GIS formats.
- Raster metadata inspection for COG-oriented readiness conversations.
- Clear customer-facing reporting.
- A path from raw data to PostGIS-backed map applications.
- Lightweight architecture choices that can grow into heavier GIS dependencies when needed.
