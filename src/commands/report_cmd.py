import click

from src.core.reporter import Reporter


@click.command(help="生成 Markdown 或 HTML 报表")
@click.option("--db", default="heritage.db", show_default=True)
@click.option("--type", "report_type", type=click.Choice(["markdown", "html"]), default="markdown", show_default=True)
@click.option("--output", required=True, type=click.Path())
@click.option("--charts", is_flag=True, help="HTML 报表内嵌 ECharts 图表")
def report(db: str, report_type: str, output: str, charts: bool) -> None:
    Reporter().generate(db, report_type, output, charts)
    click.echo(f"报表已生成：{output}")
