import json
from pathlib import Path
from app.dependencies import get_embedding_model

model = get_embedding_model().model
print("model limit:", model.max_seq_length, "tokens")

data = json.loads(Path("data/index/chunks.json").read_text(encoding="utf-8"))
for cid, c in data.items():
    n = len(model.tokenizer.encode(c["text"]))
    print(f"[{cid}] {n:>4} tokens  {len(c['text']):>5} chars")