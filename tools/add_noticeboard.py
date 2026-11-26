"""村庄留言板：按进度显示下一步该去哪。

MZ 按顺序取第一个条件满足的事件页，所以条件最严格的放最前面，
无条件的那页放最后。

用法：python tools/add_noticeboard.py
"""

import io
import json

MAP = "data/Map002.json"

# 从最严格到最宽松：(开关 id 或 None, 台词)
LINES = [
    (6, ["最上面还有一层。", "塔顶。", "那里才是真正的房间。"]),
    (5, ["王座间之后，还有一扇门。", "往上。"]),
    (4, ["未来层之后，就是最顶层。", "小冰在那里。"]),
    (3, ["现代层之后，是未来层。", "一直往上走。"]),
    (1, ["前哨后面，有一道门。", "门后面不是这个世界。"]),
    (None, ["北边有山路。", "先去看看。"]),
]


def blank_conditions():
    return {
        "actorId": 1, "actorValid": False,
        "itemId": 1, "itemValid": False,
        "selfSwitchCh": "A", "selfSwitchValid": False,
        "switch1Id": 1, "switch1Valid": False,
        "switch2Id": 1, "switch2Valid": False,
        "variableId": 1, "variableValid": False, "variableValue": 0,
    }


def make_page(switch_id, lines):
    cond = blank_conditions()
    if switch_id is not None:
        cond["switch1Id"] = switch_id
        cond["switch1Valid"] = True

    cmds = [{"code": 101, "indent": 0, "parameters": ["", 0, 0, 2, ""]}]
    cmds.append({"code": 401, "indent": 0, "parameters": ["——留言板——"]})
    cmds += [{"code": 401, "indent": 0, "parameters": [ln]} for ln in lines]
    cmds.append({"code": 0, "indent": 0, "parameters": []})

    return {
        "conditions": cond,
        "directionFix": False,
        "image": {
            "characterName": "DF_!Other1", "characterIndex": 1,
            "direction": 2, "pattern": 0, "tileId": 0,
        },
        "list": cmds,
        "moveFrequency": 3,
        "moveRoute": {
            "list": [{"code": 0, "parameters": []}],
            "repeat": True, "skippable": False, "wait": False,
        },
        "moveSpeed": 3,
        "moveType": 0,
        "priorityType": 1,
        "stepAnime": False,
        "through": False,
        "trigger": 0,
        "walkAnime": True,
    }


def main() -> int:
    with io.open(MAP, encoding="utf-8") as f:
        data = json.load(f)

    existing = [e for e in data["events"] if e]
    if any(e.get("name") == "留言板" for e in existing):
        print("已存在，跳过")
        return 0
    occupied = {(e["x"], e["y"]) for e in existing}
    if (12, 12) in occupied:
        print("位置被占")
        return 0

    next_id = max([e["id"] for e in existing], default=0) + 1
    ev = {
        "id": next_id,
        "name": "留言板",
        "note": "",
        "x": 12,
        "y": 12,
        "pages": [make_page(sw, ln) for sw, ln in LINES],
    }
    while len(data["events"]) <= next_id:
        data["events"].append(None)
    data["events"][next_id] = ev

    with io.open(MAP, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    print(f"  + 留言板 (id {next_id}) @ (12,12)，{len(LINES)} 页")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
