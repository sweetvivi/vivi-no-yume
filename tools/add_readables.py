"""给各层加可阅读的文档点（终端 / 刻字 / 记录）。

用法：python tools/add_readables.py
"""

import io
import json

# (地图, 名字, x, y, [台词])
POINTS = [
    ("data/Map003.json", "墙上的划痕", 3, 17, [
        "墙上有划痕。",
        "一道，两道，三道……",
        "数不清了。",
        "有人在这里等过很久。",
    ]),
    ("data/Map006.json", "终端 · 样本记录", 3, 4, [
        "【样本记录 017】",
        "祝化进度：完成。",
        "个体仍保有一部分语言能力。",
        "这在理论上不该发生。",
        "——因为它本来就不是我们的技术。",
    ]),
    ("data/Map006.json", "终端 · 观察日志", 21, 8, [
        "【观察日志】",
        "第 47 次循环。",
        "每次都有人走到这里。",
        "每次都留下一个。",
        "我快分不清哪次是真的了。",
    ]),
    ("data/Map006.json", "终端 · 备注", 3, 13, [
        "【备注】",
        "上面那位不喜欢这个数字。",
        "它说数值必须更大。",
        "所以我们一直在加。",
    ]),
    ("data/Map007.json", "记录 · 核心日志", 3, 4, [
        "【核心日志】",
        "它不在这里。",
        "我们从一开始就在替别的东西做事。",
        "那个东西不看我们。",
        "它只看数值。",
    ]),
    ("data/Map007.json", "记录 · 最后的记录", 21, 6, [
        "【最后的记录】",
        "有人问过我，为什么要做这些。",
        "我说不知道。",
        "因为真的不知道。",
    ]),
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


def page(cmds, priority=1):
    return {
        "conditions": blank_conditions(),
        "directionFix": False,
        "image": {
            "characterName": "DF_!Other1", "characterIndex": 0,
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
        "priorityType": priority,
        "stepAnime": False,
        "through": False,
        "trigger": 0,
        "walkAnime": True,
    }


def main() -> int:
    by_map = {}
    for row in POINTS:
        by_map.setdefault(row[0], []).append(row)

    for path, rows in by_map.items():
        with io.open(path, encoding="utf-8") as f:
            data = json.load(f)
        existing = [e for e in data["events"] if e]
        next_id = max([e["id"] for e in existing], default=0) + 1
        occupied = {(e["x"], e["y"]) for e in existing}

        for _, name, x, y, lines in rows:
            if (x, y) in occupied:
                print(f"跳过 {name}")
                continue
            cmds = [{"code": 101, "indent": 0, "parameters": ["", 0, 0, 2, ""]}]
            cmds += [{"code": 401, "indent": 0, "parameters": [ln]} for ln in lines]
            cmds.append({"code": 0, "indent": 0, "parameters": []})
            ev = {
                "id": next_id, "name": name, "note": "",
                "x": x, "y": y, "pages": [page(cmds)],
            }
            while len(data["events"]) <= next_id:
                data["events"].append(None)
            data["events"][next_id] = ev
            occupied.add((x, y))
            print(f"  + {name} (id {next_id}) -> {path}")
            next_id += 1

        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
