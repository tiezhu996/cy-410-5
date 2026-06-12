# 非遗项目普查数据处理器

非遗项目普查数据处理器是一个 Python CLI 工具，用于导入、清洗、统计、查询和导出非遗项目普查数据，支持 CSV、Excel、SQLite、Markdown、JSON 和 HTML 报表。

## 安装方式

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 使用示例

```bash
python main.py db init --db heritage.db
python main.py import --file tests/fixtures/sample.csv --db heritage.db
python main.py clean --db heritage.db --report clean_report.md
python main.py stats --db heritage.db --by category
python main.py stats --db heritage.db --cross category region
python main.py stats --db heritage.db --inheritor-age
python main.py report --db heritage.db --type html --output report.html --charts
python main.py export --db heritage.db --format csv --output cleaned.csv
python main.py query --db heritage.db --where "category=传统技艺" --limit 50
python main.py db sql "SELECT COUNT(*) FROM items" --db heritage.db
```

## 功能列表

- 数据导入：读取 CSV / Excel，自动补齐标准字段，报告格式错误行，支持增量导入。
- 数据清洗：去重、地区和类别归一化、缺失值填充、异常年龄与濒危程度标记。
- 统计分析：按类别、地区、批次、传承人年龄和濒危程度统计，支持类别与地区等交叉分析。
- 报表生成：输出 Markdown 表格或 HTML 报表，HTML 可内嵌 ECharts 图表。
- 数据导出：导出 CSV、Excel、JSON 或 SQLite，支持筛选子集。
- 数据查询：多条件 AND 查询，终端表格或 JSON 输出。
- 数据库管理：初始化数据库、查看表结构、执行原始 SQL。

## 数据字段说明

| 字段 | 说明 |
| --- | --- |
| project_name | 项目名称 |
| project_code | 项目编号 |
| category | 非遗类别 |
| batch | 入选批次 |
| region_province | 所属省份 |
| region_city | 所属城市 |
| region_district | 所属区县 |
| protection_unit | 保护单位 |
| inheritor_name | 代表性传承人 |
| inheritor_age | 传承人年龄 |
| inheritor_gender | 传承人性别 |
| endangerment | 濒危程度 |
| description | 项目简介 |
| declare_year | 公布年份 |

## 技术栈

| 模块 | 技术 |
| --- | --- |
| CLI | Click |
| 数据处理 | pandas |
| Excel | openpyxl |
| 数据库 | SQLite3 |
| 终端输出 | rich |
| HTML 报表 | Jinja2 + ECharts CDN |
| 测试 | pytest |

## 目录结构

```text
src/
├── cli.py
├── commands/
├── core/
├── models/
├── store/
├── templates/
└── utils/
tests/
└── fixtures/
```

## License

MIT
