from __future__ import annotations

import argparse
from pathlib import Path

from spatial_validator.config import load_validation_config
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
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        config = load_validation_config(args.config)
        reports = validate_path(Path(args.path), config)
        formats = [item.strip().lower() for item in args.formats.split(",") if item.strip()]
        written = write_reports(reports, args.report_dir, formats)

        for report in reports:
            print(
                f"{report.dataset_name}: {report.status.upper()} "
                f"({report.readiness_score}/100, {report.feature_count} features)"
            )
        for path in written:
            print(f"wrote {path}")
        return 1 if any(report.status == "fail" for report in reports) else 0

    parser.error("Unknown command.")
    return 2
