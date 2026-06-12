from dataclasses import dataclass
from typing import Any


@dataclass
class ImportResult:
    inserted: int
    invalid_rows: list[dict[str, Any]]


@dataclass
class CleanReport:
    normalized: int
    duplicates_removed: int
    defaults_filled: int
    anomalies_marked: int


@dataclass
class StatsResult:
    headers: list[str]
    rows: list[tuple[Any, ...]]
