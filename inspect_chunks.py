import json
from pathlib import Path

data = json.loads(Path("data/index/chunks.json").read_text(encoding="cp1252"))

# The file may hold a dict of id -> chunk or a plain list; handle both
items = list(data.items()) if isinstance(data, dict) else list(enumerate(data))

for cid, c in items:
    text = c.get("text", "") if isinstance(c, dict) else str(c)
    page = c.get("page", "?") if isinstance(c, dict) else "?"
    source = c.get("source", "?") if isinstance(c, dict) else "?"
    start = " ".join(text.split())[:90]  # collapse whitespace, keep 90 chars
    print(f"[{cid}] p.{page} {len(text):>5} chars | {start}")

print(f"\nTotal: {len(items)} chunks")