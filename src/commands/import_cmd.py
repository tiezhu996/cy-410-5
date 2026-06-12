import click

from src.core.importer import DataImporter


@click.command(help="导入 CSV 或 Excel 普查数据")
@click.option("--file", "file_", required=True, type=click.Path(exists=True), help="输入文件路径")
@click.option("--db", default="heritage.db", show_default=True, help="SQLite 数据库路径")
@click.option("--format", "file_format", type=click.Choice(["csv", "excel"]), help="文件格式")
@click.option("--incremental/--replace", default=True, show_default=True, help="增量导入或覆盖同编号记录")
def import_data(file_: str, db: str, file_format: str | None, incremental: bool) -> None:
    result = DataImporter().import_file(file_, db, file_format, incremental)
    click.echo(f"导入完成：新增 {result.inserted} 条，错误 {len(result.invalid_rows)} 行")
    for invalid in result.invalid_rows[:10]:
        click.echo(f"第 {invalid['row']} 行：{'; '.join(invalid['errors'])}")
