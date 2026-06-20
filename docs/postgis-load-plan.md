# PostGIS Load Plan

The first release focuses on validation and reporting. The `spatial_validator.postgis` module includes a small load-plan object so the future database workflow has a clear boundary.

## Intended Production Pattern

1. Validate the source dataset.
2. Stop on errors unless the operator explicitly overrides.
3. Map source fields to target table columns.
4. Normalize geometry to the target SRID, usually EPSG:4326 for web mapping or a local projected CRS for analysis.
5. Load into a staging table.
6. Run database checks.
7. Promote from staging to the production schema.

## Example

```python
from spatial_validator.postgis import build_load_plan

plan = build_load_plan(
    source_path="samples/valid/field_assets.geojson",
    table_name="staging.field_assets",
    target_srid=4326,
)

print(plan.summary())
```

The implementation intentionally avoids connecting to a real database until validation, schema mapping, and safety behavior are explicit.
