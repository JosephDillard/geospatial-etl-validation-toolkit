from __future__ import annotations

import argparse
from pathlib import Path

from spatial_validator.config import load_validation_config
from spatial_validator.postgis import load_to_postgis
from spatial_validator.reports import write_reports
from spatial_validator.validators import validate_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="spatial-validator",
        description="Validate geospatial datasets and generate data readiness reports.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Validate a dataset file or directory.")
    validate.add_argument("path", help="Path to a GeoJSON, JSON, CSV, or directory of supported datasets.")
    validate.add_argument(
        "--report-dir",
        default="reports/generated",
        help="Directory where report files will be written.",
    )
    validate.add_argument(
        "--formats",
        default="markdown,json,html",
        help="Comma-separated output formats: markdown,json,html.",
    )
    validate.add_argument(
        "--config",
        help="Optional JSON/YAML validation rules for required fields and domains.",
    )
    validate.add_argument(
        "--no-batch-summary",
        action="store_true",
        help="Do not write batch-summary reports.",
    )

    load = subparsers.add_parser("load-postgis", help="Validate and load one vector dataset into PostGIS.")
    load.add_argument("path", help="Path to a CSV, GeoJSON, GeoPackage, or Shapefile dataset.")
    load.add_argument("--connection", required=True, help="SQLAlchemy Postgres/PostGIS connection string.")
    load.add_argument("--table", required=True, help="Destination table as table or schema.table.")
    load.add_argument("--config", help="Optional JSON/YAML validation rules.")
    load.add_argument("--target-srid", type=int, default=4326, help="Target SRID for loaded geometry.")
    load.add_argument(
        "--if-exists",
        choices=["fail", "replace", "append"],
        default="replace",
        help="GeoPandas to_postgis if_exists behavior.",
    )
    load.add_argument(
        "--allow-warnings",
        action="store_true",
        help="Allow PostGIS load when validation produced warnings but no errors.",
    )
    load.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and prepare the load plan without writing to the database.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        config = load_validation_config(args.config)
        reports = validate_path(Path(args.path), config)
        formats = [item.strip().lower() for item in args.formats.split(",") if item.strip()]
        written = write_reports(
            reports,
            args.report_dir,
            formats,
            include_batch_summary=not args.no_batch_summary,
        )

        for report in reports:
            print(
                f"{report.dataset_name}: {report.status.upper()} "
                f"({report.readiness_score}/100, {report.feature_count} features)"
            )
        for path in written:
            print(f"wrote {path}")
        return 1 if any(report.status == "fail" for report in reports) else 0

    if args.command == "load-postgis":
        config = load_validation_config(args.config)
        try:
            result = load_to_postgis(
                Path(args.path),
                args.connection,
                args.table,
                config=config,
                target_srid=args.target_srid,
                if_exists=args.if_exists,
                allow_warnings=args.allow_warnings,
                dry_run=args.dry_run,
            )
        except RuntimeError as exc:
            print(f"load-postgis failed: {exc}")
            return 1

        print(result.plan.summary())
        print(result.message)
        print(f"rows: {result.row_count}")
        return 0

    parser.error("Unknown command.")
    return 2
