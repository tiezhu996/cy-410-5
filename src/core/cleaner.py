from __future__ import annotations

from pathlib import Path

from src.models.schemas import CleanReport
from src.store.repository import HeritageRepository
from src.utils.constants import CATEGORY_ALIASES, ENDANGERMENT_LEVELS, PROVINCE_ALIASES


class DataCleaner:
    def clean(self, db: str, report_path: str | None = None) -> CleanReport:
        repo = HeritageRepository(db)
        rows = [dict(row) for row in repo.fetch()]
        seen_codes: set[str] = set()
        duplicates: list[int] = []
        updates: list[dict] = []
        normalized = defaults_filled = anomalies = 0

        for row in rows:
            if row["project_code"] in seen_codes:
                duplicates.append(row["id"])
                continue
            seen_codes.add(row["project_code"])

            original = row.copy()
            row["category"] = CATEGORY_ALIASES.get(row["category"], row["category"])
            row["region_province"] = PROVINCE_ALIASES.get(row["region_province"], row["region_province"])
            if not row.get("endangerment"):
                row["endangerment"] = "一般"
                defaults_filled += 1
            if row.get("inheritor_age") and (int(row["inheritor_age"]) <= 0 or int(row["inheritor_age"]) >= 120):
                row["is_anomaly"] = 1
                anomalies += 1
            if row.get("endangerment") not in ENDANGERMENT_LEVELS:
                row["is_anomaly"] = 1
                anomalies += 1
            if row != original:
                normalized += 1
                updates.append(row)

        repo.update_cleaned(updates)
        removed = repo.delete_ids(duplicates)
        result = CleanReport(normalized=normalized, duplicates_removed=removed, defaults_filled=defaults_filled, anomalies_marked=anomalies)
        if report_path:
            Path(report_path).write_text(
                "\n".join(
                    [
                        "# 数据清洗报告",
                        f"- 标准化记录：{result.normalized}",
                        f"- 删除重复：{result.duplicates_removed}",
                        f"- 填充默认值：{result.defaults_filled}",
                        f"- 标记异常：{result.anomalies_marked}",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
        return result
