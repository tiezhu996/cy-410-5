import click

from src.commands.clean_cmd import clean
from src.commands.db_cmd import db
from src.commands.export_cmd import export
from src.commands.import_cmd import import_data
from src.commands.query_cmd import query
from src.commands.report_cmd import report
from src.commands.stats_cmd import stats


@click.group(help="非遗项目普查数据处理器")
def cli() -> None:
    pass


cli.add_command(import_data, "import")
cli.add_command(clean)
cli.add_command(stats)
cli.add_command(report)
cli.add_command(export)
cli.add_command(query)
cli.add_command(db)
