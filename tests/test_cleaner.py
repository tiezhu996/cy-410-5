from pathlib import Path

from src.core.cleaner import DataCleaner
from src.core.importer import DataImporter


def test_cleaner_normalizes_aliases(tmp_path: Path) -> None:
    db = tmp_path / "heritage.db"
    DataImporter().import_file("tests/fixtures/sample.csv", str(db))
    result = DataCleaner().clean(str(db))
    assert result.normalized >= 1
