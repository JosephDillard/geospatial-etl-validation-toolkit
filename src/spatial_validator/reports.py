from __future__ import annotations

import html
import json
from pathlib import Path

from spatial_validator.models import DatasetReport


def write_reports(
    reports: list[DatasetReport],
    output_dir: str | Path,
    formats: list[str] | None = None,
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

    return written


def render_markdown(report: DatasetReport) -> str:
    lines = [
        f"# Data Readiness Report: {report.dataset_name}",
        "",
        f"- Status: **{report.status.upper()}**",
        f"- Readiness Score: **{report.readiness_score}/100**",
        f"- Driver: {report.driver}",
        f"- Feature Count: {report.feature_count}",
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
        <p><strong>Bounds:</strong> {html.escape(str(report.bbox if report.bbox else "Not available"))}</p>
      </section>
      <h2>Geometry Types</h2>
      <ul>{geometry_items}</ul>
      <h2>Fields</h2>
      <ul>{field_items}</ul>
      <h2>Checks</h2>
      <table>
        <thead><tr><th>Severity</th><th>Check</th><th>Message</th></tr></thead>
        <tbody>{check_rows}</tbody>
      </table>
    </main>
  </body>
</html>
"""


def slugify(value: str) -> str:
    cleaned = "".join(char.lower() if char.isalnum() else "-" for char in value)
    parts = [part for part in cleaned.split("-") if part]
    return "-".join(parts) or "dataset-report"
