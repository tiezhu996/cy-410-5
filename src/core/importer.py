from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.models.schemas import ImportResult
from src.store.repository import HeritageRepository
from src.utils.validators import normalize_columns, validate_rows


class DataImporter:
    def import_file(self, file: str, db: str, file_format: str | None = None, incremental: bool = True) -> ImportResult:
        path = Path(file)
        if not path.exists():
            raise FileNotFoundError(file)
        detected = file_format or ("excel" if path.suffix.lower() == ".xlsx" else "csv")
        if detected == "excel":
            frame = pd.read_excel(path)
        else:
            frame = pd.read_csv(path)
        frame = normalize_columns(frame)
        valid, invalid = validate_rows(frame)
        inserted = HeritageRepository(db).insert_frame(valid, incremental=incremental)
        return ImportResult(inserted=inserted, invalid_rows=invalid)
