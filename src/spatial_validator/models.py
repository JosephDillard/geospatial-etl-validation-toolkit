from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


SEVERITY_WEIGHT = {
    "info": 0,
    "warning": 8,
    "error": 25,
}


@dataclass(frozen=True)
class CheckResult:
    check_id: str
    severity: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "severity": self.severity,
            "message": self.message,
            "details": self.details,
        }


@dataclass
class DatasetReport:
    path: Path
    dataset_name: str
    driver: str
    feature_count: int = 0
    fields: list[str] = field(default_factory=list)
    geometry_types: dict[str, int] = field(default_factory=dict)
    bbox: tuple[float, float, float, float] | None = None
    null_counts: dict[str, int] = field(default_factory=dict)
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def status(self) -> str:
        severities = {check.severity for check in self.checks}
        if "error" in severities:
            return "fail"
        if "warning" in severities:
            return "warn"
        return "pass"

    @property
    def readiness_score(self) -> int:
        penalty = sum(SEVERITY_WEIGHT.get(check.severity, 0) for check in self.checks)
        return max(0, 100 - penalty)

    def add_check(
        self,
        check_id: str,
        severity: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.checks.append(
            CheckResult(
                check_id=check_id,
                severity=severity,
                message=message,
                details=details or {},
            )
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_name": self.dataset_name,
            "path": str(self.path),
            "driver": self.driver,
            "status": self.status,
            "readiness_score": self.readiness_score,
            "feature_count": self.feature_count,
            "fields": self.fields,
            "geometry_types": self.geometry_types,
            "bbox": self.bbox,
            "null_counts": self.null_counts,
            "checks": [check.to_dict() for check in self.checks],
        }
