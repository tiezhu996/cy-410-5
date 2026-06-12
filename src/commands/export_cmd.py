import click

from src.core.exporter import DataExporter


@click.command(help="导出清洗后的数据")
@click.option("--db", default="heritage.db", show_default=True)
@click.option("--format", "output_format", type=click.Choice(["csv", "excel", "json", "sqlite"]), default="csv", show_default=True)
@click.option("--output", required=True, type=click.Path())
@click.option("--filter", "filters", multiple=True, help="筛选条件，如 category=传统技艺")
def export(db: str, output_format: str, output: str, filters: tuple[str, ...]) -> None:
    count = DataExporter().export(db, output_format, output, list(filters) or None)
    click.echo(f"已导出 {count} 条记录到 {output}")
