import click

from src.core.cleaner import DataCleaner


@click.command(help="清洗并标准化数据")
@click.option("--db", default="heritage.db", show_default=True)
@click.option("--report", "report_path", type=click.Path(), help="清洗报告输出路径")
def clean(db: str, report_path: str | None) -> None:
    result = DataCleaner().clean(db, report_path)
    click.echo(
        f"清洗完成：标准化 {result.normalized}，删除重复 {result.duplicates_removed}，"
        f"填充默认值 {result.defaults_filled}，标记异常 {result.anomalies_marked}"
    )
