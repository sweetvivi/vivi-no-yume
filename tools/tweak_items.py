"""给道具描述加点味道。"""

import io
import json

NEW = {
    1: "很旧的钥匙。金属已经发暗。\n能打开任何锁——不知道为什么。",
    2: "常见的草药。\n嚼起来很苦。但有用。",
    3: "蓝色的水。\n喝下去会从喉咙一路凉到胃里。",
}

with io.open("data/Items.json", encoding="utf-8") as f:
    items = json.load(f)

for it in items:
    if not it or it["id"] not in NEW:
        continue
    old = it.get("description", "")
    it["description"] = NEW[it["id"]]
    print(f"  {it['name']}: {old!r} -> {NEW[it['id']]!r}")

with io.open("data/Items.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(items, f, ensure_ascii=False, separators=(",", ":"))

print("完成")
