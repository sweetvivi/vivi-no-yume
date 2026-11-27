"""修正陷阱宝箱的 355 脚本（之前被 PowerShell 转义成了 \\$）。"""

import io
import json

MAP = "data/Map003.json"
CORRECT = "$gameVariables.setValue(36, 2);"

with io.open(MAP, encoding="utf-8") as f:
    data = json.load(f)

ev = next(e for e in data["events"] if e and e.get("name") == "奇怪的宝箱")
fixed = 0
for c in ev["pages"][0]["list"]:
    if c["code"] != 355 or not c["parameters"]:
        continue
    s = c["parameters"][0]
    if "setValue(36" in s and s != CORRECT:
        c["parameters"][0] = CORRECT
        fixed += 1
        print(f"  修正: {s!r} -> {CORRECT!r}")

with io.open(MAP, "w", encoding="utf-8", newline="\n") as f:
    json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

print("修正条数:", fixed)
