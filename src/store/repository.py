from __future__ import annotations

import sqlite3
from typing import Any

import pandas as pd

from src.models.fields import STANDARD_FIELDS
from src.store.database import connect, init_db


class HeritageRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        init_db(db_path)

    def insert_frame(self, frame: pd.DataFrame, incremental: bool = True) -> int:
        if frame.empty:
            return 0
        columns = STANDARD_FIELDS
        placeholders = ", ".join(["?"] * len(columns))
        conflict = "OR IGNORE" if incremental else "OR REPLACE"
        sql = f"INSERT {conflict} INTO items ({', '.join(columns)}) VALUES ({placeholders})"
        rows = [tuple(None if pd.isna(row[col]) else row[col] for col in columns) for _, row in frame.iterrows()]
        with connect(self.db_path) as conn:
            before = conn.total_changes
            conn.executemany(sql, rows)
            return conn.total_changes - before

    def fetch(self, where: list[str] | None = None, order_by: str | None = None, limit: int | None = None) -> list[sqlite3.Row]:
        sql = "SELECT * FROM items"
        params: list[Any] = []
        if where:
            clauses = []
            for expression in where:
                if ">=" in expression:
                    field, value = expression.split(">=", 1)
                    clauses.append(f"{field.strip()} >= ?")
                    params.append(value.strip())
                elif "=" in expression:
                    field, value = expression.split("=", 1)
                    clauses.append(f"{field.strip()} = ?")
                    params.append(value.strip())
                else:
                    raise ValueError(f"不支持的查询条件: {expression}")
            sql += " WHERE " + " AND ".join(clauses)
        if order_by:
            sql += f" ORDER BY {order_by}"
        if limit:
            sql += " LIMIT ?"
            params.append(limit)
        with connect(self.db_path) as conn:
            return conn.execute(sql, params).fetchall()

    def count_by(self, field: str) -> list[tuple[Any, int]]:
        with connect(self.db_path) as conn:
            rows = conn.execute(f"SELECT {field}, COUNT(*) AS total FROM items GROUP BY {field} ORDER BY total DESC").fetchall()
            return [(row[0], row[1]) for row in rows]

    def cross_count(self, left: str, right: str) -> list[tuple[Any, Any, int]]:
        with connect(self.db_path) as conn:
            rows = conn.execute(
                f"SELECT {left}, {right}, COUNT(*) AS total FROM items GROUP BY {left}, {right} ORDER BY total DESC"
            ).fetchall()
            return [(row[0], row[1], row[2]) for row in rows]

    def update_cleaned(self, rows: list[dict[str, Any]]) -> None:
        with connect(self.db_path) as conn:
            for row in rows:
                columns = [key for key in row.keys() if key != "id"]
                assignments = ", ".join(f"{column}=?" for column in columns)
                values = [row[column] for column in columns]
                values.append(row["id"])
                conn.execute(f"UPDATE items SET {assignments}, updated_at=CURRENT_TIMESTAMP WHERE id=?", values)

    def delete_ids(self, ids: list[int]) -> int:
        if not ids:
            return 0
        with connect(self.db_path) as conn:
            before = conn.total_changes
            conn.executemany("DELETE FROM items WHERE id=?", [(item_id,) for item_id in ids])
            return conn.total_changes - before

    def execute_sql(self, sql: str) -> list[sqlite3.Row]:
        with connect(self.db_path) as conn:
            cursor = conn.execute(sql)
            return cursor.fetchall() if cursor.description else []
