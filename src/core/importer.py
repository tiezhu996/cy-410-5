from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.models.schemas import ImportResult
from src.store.repository import HeritageRepository
from src.utils.validators import normalize_columns, validate_rows


def _read_xls_direct(path: Path) -> pd.DataFrame:
    try:
        import xlrd
    except ImportError as exc:
        raise ImportError(
            "读取旧版 .xls 文件需要 xlrd 库（版本 < 2.0）。"
            "请运行：pip install 'xlrd>=1.2,<2.0'"
        ) from exc

    try:
        major = int(xlrd.__version__.split(".")[0])
        if major >= 2:
            raise ImportError(
                f"检测到 xlrd=={xlrd.__version__}（>=2.0 不再支持 .xls）。"
                "请降级：pip install 'xlrd>=1.2,<2.0'"
            )
    except (AttributeError, ValueError):
        pass

    book = xlrd.open_workbook(str(path))
    sheet = book.sheet_by_index(0)
    if sheet.nrows == 0:
        return pd.DataFrame()
    headers = [str(sheet.cell_value(0, col)).strip() for col in range(sheet.ncols)]
    rows = []
    for r in range(1, sheet.nrows):
        row = {}
        for c, header in enumerate(headers):
            if not header:
                continue
            cell = sheet.cell_value(r, c)
            ctype = sheet.cell_type(r, c)
            if ctype == xlrd.XL_CELL_NUMBER and cell == int(cell):
                cell = int(cell)
            row[header] = cell
        rows.append(row)
    return pd.DataFrame(rows, columns=[h for h in headers if h])


def _read_excel(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".xls":
        return _read_xls_direct(path)
    try:
        return pd.read_excel(path, engine="openpyxl")
    except ImportError as exc:
        raise ImportError(
            "读取 .xlsx 文件需要 openpyxl 库。请运行：pip install openpyxl"
        ) from exc


class DataImporter:
    def import_file(self, file: str, db: str, file_format: str | None = None, incremental: bool = True) -> ImportResult:
        path = Path(file)
        if not path.exists():
            raise FileNotFoundError(file)
        detected = file_format or ("excel" if path.suffix.lower() in (".xlsx", ".xls") else "csv")
        if detected == "excel":
            frame = _read_excel(path)
        else:
            frame = pd.read_csv(path)
        frame = normalize_columns(frame)
        valid, invalid = validate_rows(frame)
        inserted = HeritageRepository(db).insert_frame(valid, incremental=incremental)
        return ImportResult(inserted=inserted, invalid_rows=invalid)
