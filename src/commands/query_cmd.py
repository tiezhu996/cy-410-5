import click

from src.store.repository import HeritageRepository
from src.utils.formatters import print_table


@click.command(help="按条件查询数据")
@click.option("--db", default="heritage.db", show_default=True)
@click.option("--where", "where_", multiple=True, help="AND 条件，如 category=传统技艺")
@click.option("--limit", default=50, show_default=True)
@click.option("--order-by", help="排序字段")
@click.option("--format", "fmt", type=click.Choice(["table", "json"]), default="table")
def query(db: str, where_: tuple[str, ...], limit: int, order_by: str | None, fmt: str) -> None:
    rows = HeritageRepository(db).fetch(where=list(where_) or None, order_by=order_by, limit=limit)
    if fmt == "json":
        import json

        click.echo(json.dumps([dict(row) for row in rows], ensure_ascii=False, indent=2))
        return
    headers = ["project_name", "project_code", "category", "region_province", "batch", "endangerment"]
    print_table(headers, [tuple(row[header] for header in headers) for row in rows])
