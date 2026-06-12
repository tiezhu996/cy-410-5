from pathlib import Path

from src.core.importer import DataImporter


def test_importer_loads_csv(tmp_path: Path) -> None:
    db = tmp_path / "heritage.db"
    result = DataImporter().import_file("tests/fixtures/sample.csv", str(db))
    assert result.inserted == 2
    assert result.invalid_rows == []
