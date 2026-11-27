"""给角色补全 gender 标记，用于装备性别限制。

规则（用户设定）：
  女性（gender:f）       —— 可穿通用 + 女性装/饰品
  特殊「女生」（special-f）—— 同上
  女装大佬（crossdress）  —— 两类都可穿
  其余（无标记）          —— 通用 + 男性饰品

女性：薇薇、鱼鱼、喵神、小小薇、cardio、水榕茜、夜夜、汐之宫花见、のの
特殊女生：薰衣草、码字姬、白羽、白白
女装大佬：花咲、狗妹、阿文、久远崎彩祸
"""

import io
import json

FEM = {1, 19, 25, 5, 39, 37, 40, 38, 41}
SPECIAL = {11, 15, 21, 22}

with io.open("data/Actors.json", encoding="utf-8") as f:
    actors = json.load(f)

changed = 0
for a in actors:
    if not a:
        continue
    note = a.get("note", "")
    if "crossdress" in note:
        continue  # 女装大佬不用动
    if "gender:" in note:
        continue  # 已有标记
    aid = a["id"]
    if aid in FEM:
        a["note"] = (note + "|gender:f").strip("|")
        changed += 1
        print(f"  {a['name']:<10} -> gender:f")
    elif aid in SPECIAL:
        a["note"] = (note + "|gender:special-f").strip("|")
        changed += 1
        print(f"  {a['name']:<10} -> gender:special-f")

with io.open("data/Actors.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(actors, f, ensure_ascii=False, separators=(",", ":"))

print(f"\n修改 {changed} 个角色")
