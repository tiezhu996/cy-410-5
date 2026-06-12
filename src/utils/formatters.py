from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from rich.console import Console
from rich.table import Table


def print_table(headers: list[str], rows: Iterable[tuple]) -> None:
    table = Table(show_header=True, header_style="bold cyan")
    for header in headers:
        table.add_column(header)
    for row in rows:
        table.add_row(*[str(value if value is not None else "") for value in row])
    Console().print(table)


def write_markdown_table(headers: list[str], rows: Iterable[tuple], output: str) -> None:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(value if value is not None else "") for value in row) + " |")
    Path(output).write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_json(rows: list[dict], output: str) -> None:
    Path(output).write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
