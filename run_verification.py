import subprocess
import sys
import os
import sqlite3
import json
from datetime import datetime

CWD = os.path.dirname(os.path.abspath(__file__))
LOGFILE = os.path.join(CWD, f"verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
LOG_LINES = []

PYTHON = sys.executable


def log(msg=""):
    print(msg)
    LOG_LINES.append(msg)


def save_log():
    with open(LOGFILE, "w", encoding="utf-8") as f:
        f.write("\n".join(LOG_LINES) + "\n")
    print(f"\n[日志已保存到: {LOGFILE}]")


def run(args, **kw):
    if isinstance(args, str):
        args = args.split()
    cmd = [PYTHON] + args
    log("$ " + " ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.stdout:
        for line in r.stdout.strip().splitlines():
            log(f"  {line}")
    if r.stderr:
        for line in r.stderr.strip().splitlines():
            log(f"  [err] {line}")
    if r.returncode != 0:
        log(f"  [exit {r.returncode}]")
    return r


log("============================================================")
log("  非遗普查数据Bug修复 端到端验证报告")
log(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log(f"  Python: {PYTHON}")
log(f"  版本: {sys.version}")
log("============================================================")

log("\n[环境检查]")
log("------------------------------------------------------------")
run(["-c", "import xlrd; print('xlrd版本:', xlrd.__version__, '(需要>=1.2,<2.0)')"])
run(["-c", "import openpyxl; print('openpyxl版本:', openpyxl.__version__)"])
run(["-c", "import pandas; print('pandas版本:', pandas.__version__)"])

log("\n[清理旧数据]")
log("------------------------------------------------------------")
for p in ["/tmp/test_heritage.db", "/tmp/export_target.db", "/tmp/test_xlsx.db"]:
    if os.path.exists(p):
        os.remove(p)
log("已清理临时数据库")

log("\n[验证1: 导入真实 BIFF8 .xls 文件]")
log("------------------------------------------------------------")
XLS = os.path.join(CWD, "tests/fixtures/sample.xls")
log(f"文件: {XLS}")
log(f"大小: {os.path.getsize(XLS)} 字节")
with open(XLS, "rb") as f:
    magic = f.read(8).hex()
ok = magic == "d0cf11e0a1b11ae1"
log(f"文件头魔数: {magic} -> {'PASS (真实OLE2/BIFF8格式)' if ok else 'FAIL'}")
assert ok, "文件格式不对"
r = run(["main.py", "import", "--file", XLS, "--db", "/tmp/test_heritage.db"], cwd=CWD)
assert r.returncode == 0, "导入命令失败"
assert "新增 3 条" in r.stdout, f"未导入3条, 输出: {r.stdout}"
log("==> 验证1 [PASS] xls导入成功 (3条)")

log("\n[验证2: 查询确认3条数据均入库]")
log("------------------------------------------------------------")
r = run(["main.py", "query", "--db", "/tmp/test_heritage.db", "--limit", "10", "--format", "table"], cwd=CWD)
conn = sqlite3.connect("/tmp/test_heritage.db")
total = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
log(f"数据库记录总数: {total}")
assert total == 3, f"应为3条, 实际{total}"

log("\n[验证3: 清洗数据 - 120岁传承人不应被标异常]")
log("------------------------------------------------------------")
r = run(["main.py", "clean", "--db", "/tmp/test_heritage.db"], cwd=CWD)
row = conn.execute('SELECT inheritor_name, inheritor_age, is_anomaly FROM items WHERE inheritor_name="王五"').fetchone()
log(f"查询结果: 姓名={row[0]}, 年龄={row[1]}, 异常标记={row[2]}")
assert row[2] in (None, 0), f"120岁不应异常, 实际={row[2]}"
log("==> 验证3 [PASS] 120岁未被标异常")

log("\n[验证4: declare_year>=2006 边界条件 - 应返回全部3条]")
log("------------------------------------------------------------")
r = run(["main.py", "query", "--db", "/tmp/test_heritage.db", "--where", "declare_year>=2006", "--format", "json"], cwd=CWD)
data = json.loads(r.stdout)
log(f"查询结果数量: {len(data)} (期望 3)")
assert len(data) == 3, f"应为3条, 实际{len(data)}"
codes = sorted(d["project_code"] for d in data)
log(f"包含记录: {codes}")
log("==> 验证4 [PASS] >=边界条件正确包含2006年记录")

log("\n[验证5: declare_year>=2008 - 应返回1条(H001)]")
log("------------------------------------------------------------")
r = run(["main.py", "query", "--db", "/tmp/test_heritage.db", "--where", "declare_year>=2008", "--format", "json"], cwd=CWD)
data = json.loads(r.stdout)
log(f"查询结果数量: {len(data)} (期望 1)")
assert len(data) == 1, f"应为1条, 实际{len(data)}"
assert data[0]["project_code"] == "H001"
log(f"记录: {data[0]['project_code']} ({data[0]['declare_year']}年)")
log("==> 验证5 [PASS]")

log("\n[验证6: SQLite重复导出 - 旧数据应被刷新(OR REPLACE)]")
log("------------------------------------------------------------")
log("--- 第一次导出到 /tmp/export_target.db ---")
r = run(["main.py", "export", "--db", "/tmp/test_heritage.db", "--format", "sqlite", "--output", "/tmp/export_target.db"], cwd=CWD)
conn2 = sqlite3.connect("/tmp/export_target.db")
rows = conn2.execute("SELECT project_code, description FROM items ORDER BY project_code").fetchall()
for code, desc in rows:
    log(f"  {code}: {desc}")
log(f"首次导出总数: {len(rows)}")
conn2.close()

log("\n--- 修改源数据库 description 字段 ---")
conn.execute('UPDATE items SET description="UPDATED_青瓷" WHERE project_code="H001"')
conn.commit()
row = conn.execute('SELECT project_code, description FROM items WHERE project_code="H001"').fetchone()
log(f"源数据库已更新: {row[0]} -> {row[1]}")

log("\n--- 第二次导出到同一个 /tmp/export_target.db (验证刷新) ---")
r = run(["main.py", "export", "--db", "/tmp/test_heritage.db", "--format", "sqlite", "--output", "/tmp/export_target.db"], cwd=CWD)
conn2 = sqlite3.connect("/tmp/export_target.db")
row = conn2.execute('SELECT project_code, description FROM items WHERE project_code="H001"').fetchone()
log(f"目标数据库H001描述: {row[1]}")
assert row[1] == "UPDATED_青瓷", f"数据未刷新! 实际={row[1]}"
conn2.close()
log("==> 验证6 [PASS] 重复导出已刷新旧数据")

log("\n[验证7: xlsx文件仍正常工作]")
log("------------------------------------------------------------")
import pandas as pd
df = pd.read_csv(os.path.join(CWD, "tests/fixtures/sample.csv"))
df.to_excel("/tmp/sample.xlsx", index=False, engine="openpyxl")
log("生成 /tmp/sample.xlsx")
r = run(["main.py", "import", "--file", "/tmp/sample.xlsx", "--db", "/tmp/test_xlsx.db"], cwd=CWD)
assert r.returncode == 0, "xlsx导入失败"
assert "新增 2 条" in r.stdout
log("==> 验证7 [PASS] xlsx仍正常")

log("\n[验证8: 测试缺xlrd时的友好错误提示]")
log("------------------------------------------------------------")
log("(仅检查代码中存在ImportError捕获逻辑和直接xlrd读取实现)")
with open(os.path.join(CWD, "src/core/importer.py"), encoding="utf-8") as f:
    importer_src = f.read()
assert "xlrd>=1.2,<2.0" in importer_src
assert "ImportError" in importer_src
assert "_read_xls_direct" in importer_src
assert "xlrd.open_workbook" in importer_src
assert "engine=\"openpyxl\"" in importer_src
log("==> 验证8 [PASS] 代码实现直接xlrd读取并含友好提示")

conn.close()
log("\n============================================================")
log(f"  全部8项验证通过! 日志文件: {LOGFILE}")
log("============================================================")
save_log()
