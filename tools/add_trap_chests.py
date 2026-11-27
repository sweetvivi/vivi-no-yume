"""把陷阱宝箱复制到现代层和未来层。

复用洞窟「奇怪的宝箱」的事件结构，只改位置、敌人和文案。
"""

import io
import json
import copy

SRC_MAP = "data/Map003.json"
SRC_NAME = "奇怪的宝箱"

# (地图, x, y, troopId, 敌人名, 台词覆盖)
JOBS = [
    ("data/Map006.json", 12, 13, 14, "机械蜈蚣",
     ["箱子是冷的。", "像金属。"]),
    ("data/Map007.json", 12, 10, 23, "影子",
     ["箱子没有影子。", "不对——", "影子在里面。"]),
]


def main() -> int:
    with io.open(SRC_MAP, encoding="utf-8") as f:
        src = json.load(f)
    src_ev = next(e for e in src["events"] if e and e.get("name") == SRC_NAME)

    for path, x, y, troop, enemy, hint in JOBS:
        with io.open(path, encoding="utf-8") as f:
            data = json.load(f)

        if any(e and e.get("name") == "奇怪的宝箱" for e in data["events"]):
            print(f"  {path}: 已存在，跳过")
            continue

        occupied = {(e["x"], e["y"]) for e in data["events"] if e}
        if (x, y) in occupied:
            print(f"  {path}: ({x},{y}) 被占用")
            continue

        ev = copy.deepcopy(src_ev)
        ev["id"] = max([e["id"] for e in data["events"] if e], default=0) + 1
        ev["x"] = x
        ev["y"] = y

        # 改战斗目标 + 开头两句
        for c in ev["pages"][0]["list"]:
            if c["code"] == 301:
                c["parameters"][1] = troop
            if c["code"] == 401 and c["parameters"]:
                t = c["parameters"][0]
                if t == "一个宝箱。":
                    c["parameters"][0] = hint[0]
                elif t == "看起来和别的不太一样。":
                    c["parameters"][0] = hint[1] if len(hint) > 1 else "看起来不太对。"

        while len(data["events"]) <= ev["id"]:
            data["events"].append(None)
        data["events"][ev["id"]] = ev

        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

        print(f"  {path}: 陷阱宝箱 id {ev['id']} @ ({x},{y}) -> troop {troop} ({enemy})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
