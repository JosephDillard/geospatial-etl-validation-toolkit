# PostGIS Load Plan

The toolkit now includes an explicit PostGIS load path. It validates one vector dataset first, refuses failed datasets, and only writes to PostGIS after the validation gate passes.

## Production Pattern

1. Validate the source dataset.
2. Stop on validation errors.
3. Map source fields to target table columns.
4. Normalize geometry to the target SRID, usually EPSG:4326 for web mapping or a local projected CRS for analysis.
5. Load into a staging table with `GeoDataFrame.to_postgis()`.
6. Run database checks.
7. Promote from staging to the production schema.

## Dry Run Example

```powershell
$env:PYTHONPATH = "src"
python -m spatial_validator load-postgis samples\valid\field_assets.geojson `
  --connection "postgresql+psycopg://spatial_validator:spatial_validator@localhost:5434/spatial_validator" `
  --table staging.field_assets `
  --dry-run
```

## Python Example

```python
from spatial_validator.postgis import load_to_postgis

result = load_to_postgis(
    source_path="samples/valid/field_assets.geojson",
    connection_string="postgresql+psycopg://user:password@localhost:5432/spatial_validator",
    table_name="staging.field_assets",
    target_srid=4326,
    dry_run=True,
)

print(result.plan.summary())
```

Warnings block loading by default. Pass `--allow-warnings` only when the operator has reviewed the warnings and accepts the risk.
