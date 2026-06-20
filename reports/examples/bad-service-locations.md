# Data Readiness Report: bad_service_locations

- Status: **FAIL**
- Readiness Score: **42/100**
- Driver: CSV
- Feature Count: 3
- Bounds: (-96.4612, 32.9329, -96.4612, 32.9329)

## Geometry Types

- Point: 3

## Fields

- `asset_id` - null/blank values: 0
- `asset_type` - null/blank values: 0
- `status` - null/blank values: 1
- `longitude` - null/blank values: 0
- `latitude` - null/blank values: 0
- `priority` - null/blank values: 1

## Checks

- **ERROR** `csv.coordinates.numeric`: Coordinate values must be numeric.
  - Details: `{"lat": "32.9344", "lon": "not-a-number", "row": 3}`
- **ERROR** `csv.coordinates.range`: Coordinate values fall outside valid WGS84 longitude/latitude ranges.
  - Details: `{"lat": 95.0, "lon": -96.4526, "row": 4}`
- **INFO** `schema.fields_present`: Attribute fields were detected.
  - Details: `{"field_count": 6}`
- **WARNING** `schema.null_values`: One or more fields contain null or blank values.
  - Details: `{"priority": 1, "status": 1}`
- **INFO** `spatial.bbox`: Dataset bounds were calculated.
  - Details: `{"bbox": [-96.4612, 32.9329, -96.4612, 32.9329]}`
- **INFO** `csv.coordinates.detected`: Latitude and longitude columns were detected.
  - Details: `{"latitude": "latitude", "longitude": "longitude"}`

## ETL Notes

- Review warning and error checks before loading to PostGIS.
- Confirm the target coordinate reference system and schema mapping with the consuming application.
- Keep this report with the dataset handoff so downstream teams can see known data quality risks.
