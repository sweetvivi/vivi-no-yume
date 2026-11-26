"""给每章地图加「章节标题」演出（首次进入触发一次）。

用法：python tools/add_titles.py
"""

import io
import json

JOBS = [
    ("data/Map003.json", "第一章 · 祝化洞窟", ["……这里也是它造的。"]),
    ("data/Map006.json", "第二章 · 现代层", ["这里是它记忆里的地方。"]),
    ("data/Map007.json", "第三章 · 未来层", ["再往上，就不是记忆了。"]),
    ("data/Map008.json", "第四章 · 王座间", ["……到了。"]),
    ("data/Map009.json", "终章 · 评估之塔", ["这里什么都没有。"]),
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


def make_page(conditions, cmds, trigger, priority=0):
    return {
        "conditions": conditions,
        "directionFix": False,
        "image": {
            "characterName": "", "characterIndex": 0,
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
        "trigger": trigger,
        "walkAnime": True,
    }


def main() -> int:
    for path, title, lines in JOBS:
        with io.open(path, encoding="utf-8") as f:
            data = json.load(f)

        existing = [e for e in data["events"] if e]
        if any(e.get("name") == "章节标题" for e in existing):
            print(f"  {path}: 已存在，跳过")
            continue
        next_id = max([e["id"] for e in existing], default=0) + 1

        show = [
            {"code": 221, "indent": 0, "parameters": []},
            {"code": 230, "indent": 0, "parameters": [20]},
            # 居中大字
            {"code": 101, "indent": 0, "parameters": ["", 0, 0, 1, ""]},
            {"code": 401, "indent": 0, "parameters": [title]},
            {"code": 230, "indent": 0, "parameters": [60]},
        ]
        # 小小薇的一句话
        show.append({"code": 101, "indent": 0, "parameters": ["AE86_1", 4, 0, 2, "小小薇"]})
        show += [{"code": 401, "indent": 0, "parameters": [ln]} for ln in lines]
        show += [
            {"code": 222, "indent": 0, "parameters": []},
            {"code": 123, "indent": 0, "parameters": ["A", 0]},
            {"code": 0, "indent": 0, "parameters": []},
        ]

        cond1 = blank_conditions()
        cond1["selfSwitchValid"] = True
        cond1["selfSwitchCh"] = "A"

        ev = {
            "id": next_id,
            "name": "章节标题",
            "note": "",
            "x": 1,
            "y": 1,
            "pages": [
                make_page(blank_conditions(), show, trigger=3),
                make_page(cond1, [{"code": 0, "indent": 0, "parameters": []}], trigger=0),
            ],
        }
        while len(data["events"]) <= next_id:
            data["events"].append(None)
        data["events"][next_id] = ev
        print(f"  + {path} 「{title}」 (id {next_id})")

        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
