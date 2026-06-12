from __future__ import annotations

from src.models.schemas import StatsResult
from src.store.repository import HeritageRepository


FIELD_MAP = {
    "category": "category",
    "region": "region_province",
    "batch": "batch",
    "endangerment": "endangerment",
}


class Analyzer:
    def stats_by(self, db: str, by: str) -> StatsResult:
        field = FIELD_MAP.get(by, by)
        rows = HeritageRepository(db).count_by(field)
        return StatsResult(headers=[by, "数量"], rows=rows)

    def cross(self, db: str, left: str, right: str) -> StatsResult:
        left_field = FIELD_MAP.get(left, left)
        right_field = FIELD_MAP.get(right, right)
        rows = HeritageRepository(db).cross_count(left_field, right_field)
        return StatsResult(headers=[left, right, "数量"], rows=rows)

    def inheritor_age(self, db: str) -> StatsResult:
        rows = HeritageRepository(db).fetch()
        buckets = {"30岁以下": 0, "30-44岁": 0, "45-59岁": 0, "60岁及以上": 0, "未知": 0}
        for row in rows:
            age = row["inheritor_age"]
            if age is None:
                buckets["未知"] += 1
            elif age < 30:
                buckets["30岁以下"] += 1
            elif age < 45:
                buckets["30-44岁"] += 1
            elif age < 60:
                buckets["45-59岁"] += 1
            else:
                buckets["60岁及以上"] += 1
        return StatsResult(headers=["年龄段", "数量"], rows=list(buckets.items()))
