from __future__ import annotations

import html
import json
from pathlib import Path

from spatial_validator.models import DatasetReport, json_safe


def write_reports(
    reports: list[DatasetReport],
    output_dir: str | Path,
    formats: list[str] | None = None,
    include_batch_summary: bool = False,
) -> list[Path]:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    selected_formats = formats or ["markdown", "json", "html"]
    written: list[Path] = []

    for report in reports:
        slug = slugify(report.dataset_name)
        if "json" in selected_formats:
            path = destination / f"{slug}.json"
            path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
            written.append(path)
        if "markdown" in selected_formats or "md" in selected_formats:
            path = destination / f"{slug}.md"
            path.write_text(render_markdown(report), encoding="utf-8")
            written.append(path)
        if "html" in selected_formats:
            path = destination / f"{slug}.html"
            path.write_text(render_html(report), encoding="utf-8")
            written.append(path)

    if include_batch_summary:
        written.extend(write_batch_summary(reports, destination, selected_formats))

    return written


def write_batch_summary(
    reports: list[DatasetReport],
    output_dir: str | Path,
    formats: list[str] | None = None,
) -> list[Path]:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    selected_formats = formats or ["markdown", "json", "html"]
    written: list[Path] = []

    if "json" in selected_formats:
        path = destination / "batch-summary.json"
        path.write_text(json.dumps(batch_summary_data(reports), indent=2), encoding="utf-8")
        written.append(path)
    if "markdown" in selected_formats or "md" in selected_formats:
        path = destination / "batch-summary.md"
        path.write_text(render_batch_summary_markdown(reports), encoding="utf-8")
        written.append(path)
    if "html" in selected_formats:
        path = destination / "batch-summary.html"
        path.write_text(render_batch_summary_html(reports), encoding="utf-8")
        written.append(path)

    return written


def render_markdown(report: DatasetReport) -> str:
    lines = [
        f"# Data Readiness Report: {report.dataset_name}",
        "",
        f"- Status: **{report.status.upper()}**",
        f"- Readiness Score: **{report.readiness_score}/100**",
        f"- Driver: {report.driver}",
        f"- Feature Count: {report.feature_count}",
        f"- CRS: {report.crs if report.crs else 'Not available'}",
        f"- Bounds: {report.bbox if report.bbox else 'Not available'}",
        "",
        "## Geometry Types",
        "",
    ]

    if report.geometry_types:
        for geometry_type, count in report.geometry_types.items():
            lines.append(f"- {geometry_type}: {count}")
    else:
        lines.append("- None detected")

    lines.extend(["", "## Fields", ""])
    if report.fields:
        for field in report.fields:
            null_count = report.null_counts.get(field, 0)
            lines.append(f"- `{field}` - null/blank values: {null_count}")
    else:
        lines.append("- None detected")

    if report.metadata:
        lines.extend(["", "## Metadata", ""])
        for key, value in sorted(report.metadata.items()):
            lines.append(f"- `{key}`: `{json.dumps(json_safe(value), sort_keys=True)}`")

    lines.extend(["", "## Checks", ""])
    for check in report.checks:
        lines.append(f"- **{check.severity.upper()}** `{check.check_id}`: {check.message}")
        if check.details:
            lines.append(f"  - Details: `{json.dumps(check.details, sort_keys=True)}`")

    lines.extend(
        [
            "",
            "## ETL Notes",
            "",
            "- Review warning and error checks before loading to PostGIS.",
            "- Confirm the target coordinate reference system and schema mapping with the consuming application.",
            "- Keep this report with the dataset handoff so downstream teams can see known data quality risks.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_html(report: DatasetReport) -> str:
    check_rows = "\n".join(
        f"<tr><td>{html.escape(check.severity.upper())}</td><td>{html.escape(check.check_id)}</td><td>{html.escape(check.message)}</td></tr>"
        for check in report.checks
    )
    field_items = "\n".join(
        f"<li><code>{html.escape(field)}</code> - null/blank values: {report.null_counts.get(field, 0)}</li>"
        for field in report.fields
    ) or "<li>None detected</li>"
    geometry_items = "\n".join(
        f"<li>{html.escape(geometry_type)}: {count}</li>" for geometry_type, count in report.geometry_types.items()
    ) or "<li>None detected</li>"
    metadata_rows = "\n".join(
        f"<tr><td>{html.escape(str(key))}</td><td><code>{html.escape(json.dumps(json_safe(value), sort_keys=True))}</code></td></tr>"
        for key, value in sorted(report.metadata.items())
    ) or "<tr><td colspan=\"2\">None available</td></tr>"

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Data Readiness Report: {html.escape(report.dataset_name)}</title>
    <style>
      body {{ font-family: Arial, sans-serif; color: #17211f; margin: 2rem; line-height: 1.55; }}
      main {{ max-width: 960px; margin: 0 auto; }}
      .summary {{ border: 1px solid #d7e0dd; border-left: 6px solid #2f7d64; padding: 1rem; }}
      table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
      th, td {{ border: 1px solid #d7e0dd; padding: 0.55rem; text-align: left; vertical-align: top; }}
      th {{ background: #f4f8f7; }}
      code {{ background: #f4f8f7; padding: 0.1rem 0.25rem; }}
    </style>
  </head>
  <body>
    <main>
      <h1>Data Readiness Report: {html.escape(report.dataset_name)}</h1>
      <section class="summary">
        <p><strong>Status:</strong> {html.escape(report.status.upper())}</p>
        <p><strong>Readiness Score:</strong> {report.readiness_score}/100</p>
        <p><strong>Driver:</strong> {html.escape(report.driver)}</p>
        <p><strong>Feature Count:</strong> {report.feature_count}</p>
        <p><strong>CRS:</strong> {html.escape(str(report.crs if report.crs else "Not available"))}</p>
        <p><strong>Bounds:</strong> {html.escape(str(report.bbox if report.bbox else "Not available"))}</p>
      </section>
      <h2>Geometry Types</h2>
      <ul>{geometry_items}</ul>
      <h2>Fields</h2>
      <ul>{field_items}</ul>
      <h2>Metadata</h2>
      <table>
        <thead><tr><th>Name</th><th>Value</th></tr></thead>
        <tbody>{metadata_rows}</tbody>
      </table>
      <h2>Checks</h2>
      <table>
        <thead><tr><th>Severity</th><th>Check</th><th>Message</th></tr></thead>
        <tbody>{check_rows}</tbody>
      </table>
    </main>
  </body>
</html>
"""


def batch_summary_data(reports: list[DatasetReport]) -> dict[str, object]:
    status_counts = {"pass": 0, "warn": 0, "fail": 0}
    rows = []
    for report in reports:
        status_counts[report.status] = status_counts.get(report.status, 0) + 1
        rows.append(
            {
                "dataset_name": report.dataset_name,
                "path": str(report.path),
                "driver": report.driver,
                "status": report.status,
                "readiness_score": report.readiness_score,
                "feature_count": report.feature_count,
                "error_count": sum(1 for check in report.checks if check.severity == "error"),
                "warning_count": sum(1 for check in report.checks if check.severity == "warning"),
            }
        )

    total_features = sum(report.feature_count for report in reports)
    average_score = round(
        sum(report.readiness_score for report in reports) / len(reports),
        1,
    ) if reports else 0

    return {
        "dataset_count": len(reports),
        "status_counts": status_counts,
        "total_features": total_features,
        "average_readiness_score": average_score,
        "datasets": rows,
    }


def render_batch_summary_markdown(reports: list[DatasetReport]) -> str:
    summary = batch_summary_data(reports)
    lines = [
        "# Batch Data Readiness Summary",
        "",
        f"- Dataset Count: **{summary['dataset_count']}**",
        f"- Total Features: **{summary['total_features']}**",
        f"- Average Readiness Score: **{summary['average_readiness_score']}/100**",
        f"- Pass/Warn/Fail: **{summary['status_counts']['pass']} / {summary['status_counts']['warn']} / {summary['status_counts']['fail']}**",
        "",
        "## Dataset Results",
        "",
        "| Dataset | Driver | Status | Score | Features | Errors | Warnings |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]

    for row in summary["datasets"]:
        lines.append(
            "| {dataset_name} | {driver} | {status} | {readiness_score} | {feature_count} | {error_count} | {warning_count} |".format(
                **row
            )
        )

    lines.extend(
        [
            "",
            "## Handoff Notes",
            "",
            "- Failed datasets should not be loaded until errors are resolved.",
            "- Warning datasets need reviewer sign-off before loading or publishing.",
            "- Keep individual dataset reports with the batch summary for auditability.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_batch_summary_html(reports: list[DatasetReport]) -> str:
    summary = batch_summary_data(reports)
    rows = "\n".join(
        "<tr><td>{dataset_name}</td><td>{driver}</td><td>{status}</td><td>{readiness_score}</td><td>{feature_count}</td><td>{error_count}</td><td>{warning_count}</td></tr>".format(
            **{key: html.escape(str(value)) for key, value in row.items()}
        )
        for row in summary["datasets"]
    )
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Batch Data Readiness Summary</title>
    <style>
      body {{ font-family: Arial, sans-serif; color: #17211f; margin: 2rem; line-height: 1.55; }}
      main {{ max-width: 1040px; margin: 0 auto; }}
      .summary {{ border: 1px solid #d7e0dd; border-left: 6px solid #315f9f; padding: 1rem; }}
      table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
      th, td {{ border: 1px solid #d7e0dd; padding: 0.55rem; text-align: left; vertical-align: top; }}
      th {{ background: #f4f8f7; }}
    </style>
  </head>
  <body>
    <main>
      <h1>Batch Data Readiness Summary</h1>
      <section class="summary">
        <p><strong>Dataset Count:</strong> {summary["dataset_count"]}</p>
        <p><strong>Total Features:</strong> {summary["total_features"]}</p>
        <p><strong>Average Readiness Score:</strong> {summary["average_readiness_score"]}/100</p>
        <p><strong>Pass/Warn/Fail:</strong> {summary["status_counts"]["pass"]} / {summary["status_counts"]["warn"]} / {summary["status_counts"]["fail"]}</p>
      </section>
      <h2>Dataset Results</h2>
      <table>
        <thead><tr><th>Dataset</th><th>Driver</th><th>Status</th><th>Score</th><th>Features</th><th>Errors</th><th>Warnings</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </main>
  </body>
</html>
"""


def slugify(value: str) -> str:
    cleaned = "".join(char.lower() if char.isalnum() else "-" for char in value)
    parts = [part for part in cleaned.split("-") if part]
    return "-".join(parts) or "dataset-report"
