from __future__ import annotations

import pandas as pd

from src.models.fields import INTEGER_FIELDS, REQUIRED_FIELDS, STANDARD_FIELDS


def normalize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    rename = {column: str(column).strip() for column in frame.columns}
    frame = frame.rename(columns=rename)
    for field in STANDARD_FIELDS:
        if field not in frame.columns:
            frame[field] = None
    return frame[STANDARD_FIELDS]


def validate_rows(frame: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    valid_rows = []
    invalid_rows = []
    for index, row in frame.iterrows():
        errors = []
        for field in REQUIRED_FIELDS:
            if pd.isna(row.get(field)) or str(row.get(field)).strip() == "":
                errors.append(f"{field} 不能为空")
        for field in INTEGER_FIELDS:
            value = row.get(field)
            if pd.notna(value) and str(value).strip() != "":
                try:
                    int(float(value))
                except ValueError:
                    errors.append(f"{field} 必须是数字")
        if errors:
            invalid_rows.append({"row": int(index) + 2, "errors": errors})
        else:
            valid_rows.append(row.to_dict())
    return pd.DataFrame(valid_rows, columns=STANDARD_FIELDS), invalid_rows
