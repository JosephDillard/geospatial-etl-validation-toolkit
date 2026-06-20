from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PostGISLoadPlan:
    table_name: str
    source_path: str
    target_srid: int = 4326
    if_exists: str = "replace"

    def summary(self) -> str:
        return (
            f"Load {self.source_path} into PostGIS table {self.table_name} "
            f"with SRID {self.target_srid} using if_exists={self.if_exists}."
        )


def build_load_plan(source_path: str, table_name: str, target_srid: int = 4326) -> PostGISLoadPlan:
    """Return a PostGIS load plan without connecting to a database yet."""
    return PostGISLoadPlan(source_path=source_path, table_name=table_name, target_srid=target_srid)
