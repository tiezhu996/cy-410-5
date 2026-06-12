from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from src.core.analyzer import Analyzer
from src.utils.formatters import write_markdown_table


class Reporter:
    def generate(self, db: str, report_type: str, output: str, charts: bool = False) -> None:
        analyzer = Analyzer()
        category = analyzer.stats_by(db, "category")
        region = analyzer.stats_by(db, "region")
        if report_type == "markdown":
            lines = ["# 非遗项目普查统计报告", "", "## 按类别统计"]
            temp = Path(output)
            write_markdown_table(category.headers, category.rows, output)
            existing = temp.read_text(encoding="utf-8")
            temp.write_text("\n".join(lines) + "\n" + existing, encoding="utf-8")
            return

        env = Environment(loader=FileSystemLoader(Path(__file__).resolve().parents[1] / "templates"))
        template = env.get_template("report.html.j2")
        html = template.render(category=category, region=region, charts=charts)
        Path(output).write_text(html, encoding="utf-8")
