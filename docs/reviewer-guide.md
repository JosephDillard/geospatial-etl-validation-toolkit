# Reviewer Guide

This repo is meant to be reviewed quickly by hiring managers, GIS architects, and technical leads.

## What To Look At First

- `README.md` explains the business value and commands.
- `samples/valid` and `samples/invalid` show the validation story.
- `src/spatial_validator/validators.py` contains the starter GeoJSON and CSV checks.
- `src/spatial_validator/reports.py` generates Markdown, JSON, and HTML readiness reports.
- `docs/architecture.md` explains how this grows into a production ETL validation layer.

## What The Project Demonstrates

- Practical GIS data quality thinking.
- Python automation for geospatial ETL.
- Clear customer-facing reporting.
- A path from raw data to PostGIS-backed map applications.
- Lightweight architecture choices that can grow into heavier GIS dependencies when needed.
