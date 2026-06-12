import click

from src.core.analyzer import Analyzer
from src.utils.formatters import print_table


@click.command(help="统计分析")
@click.option("--db", default="heritage.db", show_default=True)
@click.option("--by", "by_", type=click.Choice(["category", "region", "batch"]), help="统计维度")
@click.option("--cross", nargs=2, type=str, help="交叉分析维度，如 category region")
@click.option("--inheritor-age", is_flag=True, help="传承人年龄分布")
@click.option("--endangerment", is_flag=True, help="濒危程度分布")
def stats(db: str, by_: str | None, cross: tuple[str, str] | None, inheritor_age: bool, endangerment: bool) -> None:
    analyzer = Analyzer()
    if cross:
        result = analyzer.cross(db, cross[0], cross[1])
    elif inheritor_age:
        result = analyzer.inheritor_age(db)
    elif endangerment:
        result = analyzer.stats_by(db, "endangerment")
    else:
        result = analyzer.stats_by(db, by_ or "category")
    print_table(result.headers, result.rows)
