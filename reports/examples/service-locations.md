# Data Readiness Report: service_locations

- Status: **PASS**
- Readiness Score: **100/100**
- Driver: CSV
- Feature Count: 3
- CRS: Not available
- Bounds: (-96.4612, 32.9329, -96.4526, 32.9361)

## Geometry Types

- Point: 3

## Fields

- `asset_id` - null/blank values: 0
- `asset_type` - null/blank values: 0
- `status` - null/blank values: 0
- `longitude` - null/blank values: 0
- `latitude` - null/blank values: 0
- `priority` - null/blank values: 0

## Checks

- **INFO** `schema.fields_present`: Attribute fields were detected.
  - Details: `{"field_count": 6}`
- **INFO** `schema.null_values`: No null or blank attribute values were found.
- **INFO** `spatial.bbox`: Dataset bounds were calculated.
  - Details: `{"bbox": [-96.4612, 32.9329, -96.4526, 32.9361]}`
- **INFO** `config.rules_applied`: Configured required-field and domain checks were applied.
  - Details: `{"rules": ["required:asset_id", "required:asset_type", "required:status", "domain:asset_type", "domain:status"]}`
- **INFO** `csv.coordinates.detected`: Latitude and longitude columns were detected.
  - Details: `{"latitude": "latitude", "longitude": "longitude"}`

## ETL Notes

- Review warning and error checks before loading to PostGIS.
- Confirm the target coordinate reference system and schema mapping with the consuming application.
- Keep this report with the dataset handoff so downstream teams can see known data quality risks.
