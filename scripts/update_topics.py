#!/usr/bin/env python3
"""Build topics.json for the static radar dashboard.

The dashboard contains a reviewed baseline in index.html. This script extracts
that baseline, adds a small amount of fresh public RSS metadata when available,
and writes a stable JSON snapshot for GitHub Pages.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
OUTPUT = ROOT / "topics.json"


def load_baseline() -> list[dict]:
    html = INDEX.read_text(encoding="utf-8")
    match = re.search(r"(?:const|let) rawTopics\s*=\s*(\[.*?\]);\s*\n\s*// ==================== 状态", html, re.S)
    if not match:
        raise RuntimeError("找不到 index.html 中的 rawTopics 基准数据")
    # The source uses JavaScript object literals (unquoted keys and template-safe
    # strings), so let Node parse it instead of maintaining a fragile Python parser.
    node_program = "const value = %s; process.stdout.write(JSON.stringify(value));" % match.group(1)
    result = subprocess.run(["node", "-e", node_program], check=True, capture_output=True, text=True)
    topics = json.loads(result.stdout)
    if not isinstance(topics, list) or not topics:
        raise RuntimeError("rawTopics 不是非空数组")
    return topics


def fetch_rss_titles() -> list[str]:
    """Fetch optional public RSS titles; network failure is non-fatal."""
    feed_url = os.getenv("TOPIC_RADAR_RSS_URL", "https://hnrss.org/frontpage")
    try:
        request = Request(feed_url, headers={"User-Agent": "laoguo-topic-radar/1.0"})
        with urlopen(request, timeout=12) as response:
            body = response.read().decode("utf-8", errors="replace")
        return re.findall(r"<title><!\[CDATA\[(.*?)\]\]></title>", body, re.S)[:10]
    except Exception as exc:  # noqa: BLE001 - network is optional for this static build
        print(f"提示：RSS 暂时不可用，将保留基准数据：{exc}", file=sys.stderr)
        return []


def build_snapshot() -> dict:
    topics = load_baseline()
    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    rss_titles = fetch_rss_titles()
    return {
        "channel": "老郭的数字生活",
        "lastUpdated": now,
        "source": "index.html 内置基准数据 + 可选公开 RSS",
        "rssSampleTitles": rss_titles,
        "topics": topics,
    }


def main() -> None:
    snapshot = build_snapshot()
    OUTPUT.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"已生成 {OUTPUT}：{len(snapshot['topics'])} 个选题，RSS 标题 {len(snapshot['rssSampleTitles'])} 条")


if __name__ == "__main__":
    main()
