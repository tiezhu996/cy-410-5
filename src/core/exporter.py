from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.store.repository import HeritageRepository


class DataExporter:
    def export(self, db: str, output_format: str, output: str, filters: list[str] | None = None) -> int:
        rows = [dict(row) for row in HeritageRepository(db).fetch(where=filters)]
        frame = pd.DataFrame(rows)
        if output_format == "excel":
            frame.to_excel(output, index=False)
        elif output_format == "json":
            Path(output).write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        elif output_format == "sqlite":
            target = HeritageRepository(output)
            target.insert_frame(frame.drop(columns=["id", "created_at", "updated_at"], errors="ignore"), incremental=False)
        else:
            frame.to_csv(output, index=False)
        return len(rows)
