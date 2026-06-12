import click

from src.store.database import init_db
from src.store.repository import HeritageRepository
from src.utils.formatters import print_table


@click.group(help="数据库管理")
def db() -> None:
    pass


@db.command(help="初始化数据库")
@click.option("--db", "db_path", default="heritage.db", show_default=True)
def init(db_path: str) -> None:
    init_db(db_path)
    click.echo(f"数据库已初始化：{db_path}")


@db.command(help="查看表结构")
@click.option("--db", "db_path", default="heritage.db", show_default=True)
def schema(db_path: str) -> None:
    rows = HeritageRepository(db_path).execute_sql("PRAGMA table_info(items)")
    print_table(["cid", "name", "type", "notnull", "default", "pk"], [tuple(row) for row in rows])


@db.command(help="执行原始 SQL")
@click.argument("sql")
@click.option("--db", "db_path", default="heritage.db", show_default=True)
def sql(sql: str, db_path: str) -> None:
    rows = HeritageRepository(db_path).execute_sql(sql)
    if rows:
        print_table(list(rows[0].keys()), [tuple(row) for row in rows])
    else:
        click.echo("SQL 已执行")
