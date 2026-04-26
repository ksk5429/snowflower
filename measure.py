"""Per-post metrics aggregator.

Pulls platform-native analytics for each (episode, platform) pair we have a
post_id for. Sprint 0: scaffold only. Real per-platform metrics queries land
in Sprint 2.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class Metric:
    episode_id: str
    platform: str
    post_id: str
    impressions: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    clicks: int = 0
    fetched_at: datetime = datetime.now()


def aggregate(results_files: list[Path], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    for rf in results_files:
        try:
            data = json.loads(rf.read_text(encoding="utf-8"))
        except Exception:
            continue
        for r in data:
            if not r.get("post_id"):
                continue
            ep_id = rf.stem.replace("_results", "")
            m = Metric(episode_id=ep_id, platform=r["platform"], post_id=r["post_id"])
            rows.append({**asdict(m), "fetched_at": m.fetched_at.isoformat()})
    out_path = out_dir / f"metrics_{datetime.now():%Y%m%d_%H%M%S}.json"
    out_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return out_path
