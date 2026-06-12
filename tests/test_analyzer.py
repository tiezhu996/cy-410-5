from pathlib import Path

from src.core.analyzer import Analyzer
from src.core.importer import DataImporter


def test_analyzer_counts_category(tmp_path: Path) -> None:
    db = tmp_path / "heritage.db"
    DataImporter().import_file("tests/fixtures/sample.csv", str(db))
    result = Analyzer().stats_by(str(db), "category")
    assert result.headers == ["category", "数量"]
    assert len(result.rows) == 2
