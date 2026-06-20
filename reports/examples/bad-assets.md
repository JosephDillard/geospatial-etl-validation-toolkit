# Data Readiness Report: bad_assets

- Status: **FAIL**
- Readiness Score: **42/100**
- Driver: GeoJSON
- Feature Count: 2
- Bounds: (-196.4597, 32.93, -96.45, 32.94)

## Geometry Types

- Point: 1
- Polygon: 1

## Fields

- `asset_id` - null/blank values: 0
- `asset_type` - null/blank values: 0
- `status` - null/blank values: 2

## Checks

- **ERROR** `geometry.invalid`: Feature geometry failed basic coordinate validation.
  - Details: `{"errors": ["One or more coordinates fall outside WGS84 longitude/latitude ranges."], "index": 0}`
- **ERROR** `geometry.invalid`: Feature geometry failed basic coordinate validation.
  - Details: `{"errors": ["Polygon ring 0 must contain at least four positions."], "index": 1}`
- **INFO** `schema.fields_present`: Attribute fields were detected.
  - Details: `{"field_count": 3}`
- **WARNING** `schema.null_values`: One or more fields contain null or blank values.
  - Details: `{"status": 2}`
- **INFO** `spatial.bbox`: Dataset bounds were calculated.
  - Details: `{"bbox": [-196.4597, 32.93, -96.45, 32.94]}`

## ETL Notes

- Review warning and error checks before loading to PostGIS.
- Confirm the target coordinate reference system and schema mapping with the consuming application.
- Keep this report with the dataset handoff so downstream teams can see known data quality risks.
