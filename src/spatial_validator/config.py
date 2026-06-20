from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from spatial_validator.models import DatasetReport


@dataclass(frozen=True)
class DatasetRules:
    required_fields: tuple[str, ...] = ()
    domains: dict[str, tuple[str, ...]] = field(default_factory=dict)

    def merge(self, other: "DatasetRules") -> "DatasetRules":
        required = tuple(dict.fromkeys([*self.required_fields, *other.required_fields]))
        domains = {**self.domains, **other.domains}
        return DatasetRules(required_fields=required, domains=domains)


@dataclass(frozen=True)
class ValidationConfig:
    global_rules: DatasetRules = field(default_factory=DatasetRules)
    dataset_rules: dict[str, DatasetRules] = field(default_factory=dict)

    def rules_for(self, dataset_name: str) -> DatasetRules:
        return self.global_rules.merge(self.dataset_rules.get(dataset_name, DatasetRules()))


def load_validation_config(path: str | Path | None) -> ValidationConfig | None:
    if path is None:
        return None

    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Validation config not found: {config_path}")

    if config_path.suffix.lower() == ".json":
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    elif config_path.suffix.lower() in {".yml", ".yaml"}:
        try:
            import yaml
        except ImportError as exc:
            raise RuntimeError("YAML config files require PyYAML. Use JSON or install PyYAML.") from exc
        payload = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    else:
        raise ValueError("Validation config must be a JSON, YAML, or YML file.")

    if not isinstance(payload, dict):
        raise ValueError("Validation config root must be an object.")
    return config_from_mapping(payload)


def config_from_mapping(payload: dict[str, Any]) -> ValidationConfig:
    global_rules = rules_from_mapping(payload)
    datasets = payload.get("datasets", {})
    if not isinstance(datasets, dict):
        raise ValueError("Validation config 'datasets' value must be an object.")

    dataset_rules = {
        str(dataset_name): rules_from_mapping(dataset_payload or {})
        for dataset_name, dataset_payload in datasets.items()
        if isinstance(dataset_payload, dict)
    }
    return ValidationConfig(global_rules=global_rules, dataset_rules=dataset_rules)


def rules_from_mapping(payload: dict[str, Any]) -> DatasetRules:
    required_fields = tuple(str(field) for field in payload.get("required_fields", []) or [])
    raw_domains = payload.get("domains", {}) or {}
    if not isinstance(raw_domains, dict):
        raise ValueError("Validation config 'domains' value must be an object.")

    domains = {
        str(field): tuple(str(value) for value in values)
        for field, values in raw_domains.items()
        if isinstance(values, list)
    }
    return DatasetRules(required_fields=required_fields, domains=domains)


def apply_attribute_rules(
    report: DatasetReport,
    rows: list[dict[str, Any]],
    config: ValidationConfig | None,
) -> None:
    if config is None:
        return

    rules = config.rules_for(report.dataset_name)
    if not rules.required_fields and not rules.domains:
        return

    applied = []
    field_set = set(report.fields)

    for field in rules.required_fields:
        applied.append(f"required:{field}")
        if field not in field_set:
            report.add_check(
                "config.required_field.missing",
                "error",
                "Configured required field is missing.",
                {"field": field},
            )
            continue

        blank_count = sum(1 for row in rows if is_blank(row.get(field)))
        if blank_count:
            report.add_check(
                "config.required_field.blank",
                "error",
                "Configured required field contains blank values.",
                {"field": field, "blank_count": blank_count},
            )

    for field, allowed_values in rules.domains.items():
        applied.append(f"domain:{field}")
        if field not in field_set:
            report.add_check(
                "config.domain_field.missing",
                "error",
                "Configured domain field is missing.",
                {"field": field},
            )
            continue

        allowed = {normalize_value(value) for value in allowed_values}
        invalid_values: dict[str, int] = {}
        for row in rows:
            value = row.get(field)
            if is_blank(value):
                continue
            normalized = normalize_value(value)
            if normalized not in allowed:
                invalid_values[normalized] = invalid_values.get(normalized, 0) + 1

        if invalid_values:
            report.add_check(
                "config.domain.invalid_value",
                "error",
                "Field contains values outside the configured domain.",
                {"field": field, "invalid_values": invalid_values, "allowed_values": sorted(allowed)},
            )

    report.add_check(
        "config.rules_applied",
        "info",
        "Configured required-field and domain checks were applied.",
        {"rules": applied},
    )


def is_blank(value: Any) -> bool:
    if value is None:
        return True
    try:
        if value != value:
            return True
    except TypeError:
        pass
    if isinstance(value, str):
        return value.strip() == ""
    return False


def normalize_value(value: Any) -> str:
    return str(value).strip()
