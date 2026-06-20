# Data Readiness Report: field_assets

- Status: **PASS**
- Readiness Score: **100/100**
- Driver: GeoJSON
- Feature Count: 3
- CRS: Not available
- Bounds: (-96.4621, 32.9312, -96.4553, 32.9351)

## Geometry Types

- Point: 3

## Fields

- `asset_id` - null/blank values: 0
- `asset_type` - null/blank values: 0
- `owner` - null/blank values: 0
- `status` - null/blank values: 0

## Checks

- **INFO** `schema.fields_present`: Attribute fields were detected.
  - Details: `{"field_count": 4}`
- **INFO** `schema.null_values`: No null or blank attribute values were found.
- **INFO** `spatial.bbox`: Dataset bounds were calculated.
  - Details: `{"bbox": [-96.4621, 32.9312, -96.4553, 32.9351]}`
- **INFO** `config.rules_applied`: Configured required-field and domain checks were applied.
  - Details: `{"rules": ["required:asset_id", "required:asset_type", "required:status", "domain:asset_type", "domain:status"]}`
- **INFO** `geometry.basic_validity`: All geometries passed starter coordinate validation.

## ETL Notes

- Review warning and error checks before loading to PostGIS.
- Confirm the target coordinate reference system and schema mapping with the consuming application.
- Keep this report with the dataset handoff so downstream teams can see known data quality risks.
