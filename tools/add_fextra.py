"""位面之外彩蛋房间：5 个 F 级角色 + 往返的门。

用法：python tools/add_fextra.py
"""

import io
import json

MAP = "data/Map010.json"

NPCS = [
    ("水榕茜", 3, 4, "AE86_C5", 4, "AE86_5", 4, [
        "薇薇。",
        "你终于来了。",
        "我在这儿等了好久。",
        "这里没有时间。",
        "所以也不算久。",
    ]),
    ("汐之宫花见", 7, 3, "AE86_C5", 5, "AE86_5", 5, [
        "……你的衣服。",
        "在这个世界里，好像会自己变。",
        "我试过。",
        "下次给你带几件。",
    ]),
    ("cardio", 11, 4, "AE86_C5", 6, "AE86_5", 6, [
        "我一直在看。",
        "从上面看，像在玩一个游戏。",
        "你现在是主角。",
        "……别死啊。",
    ]),
    ("夜夜", 5, 7, "AE86_C5", 7, "AE86_5", 7, [
        "我在写。",
        "写你们的故事。",
        "写到一半，卡住了。",
        "因为我不知道结局。",
        "……你帮我写完吧。",
    ]),
    ("のの", 9, 7, "AE86_C6", 0, "AE86_6", 0, [
        "我什么都记下来了。",
        "从小冰说那句话开始。",
        "等你回来，要看吗。",
        "……不看也行。",
    ]),
]

# 返回群聊的门
RETURN_DOOR = ("回群聊", 12, 8, 10, 1, 14, 3)


def blank_conditions():
    return {
        "actorId": 1, "actorValid": False,
        "itemId": 1, "itemValid": False,
        "selfSwitchCh": "A", "selfSwitchValid": False,
        "switch1Id": 1, "switch1Valid": False,
        "switch2Id": 1, "switch2Valid": False,
        "variableId": 1, "variableValid": False, "variableValue": 0,
    }


def page(image_name, image_idx, cmds, priority=1):
    return {
        "conditions": blank_conditions(),
        "directionFix": False,
        "image": {
            "characterName": image_name,
            "characterIndex": image_idx,
            "direction": 2,
            "pattern": 0,
            "tileId": 0,
        },
        "list": cmds,
        "moveFrequency": 3,
        "moveRoute": {
            "list": [{"code": 0, "parameters": []}],
            "repeat": True,
            "skippable": False,
            "wait": False,
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
    with io.open(MAP, encoding="utf-8") as f:
        data = json.load(f)
    existing = [e for e in data["events"] if e]
    next_id = max([e["id"] for e in existing], default=0) + 1
    occupied = {(e["x"], e["y"]) for e in existing}

    def add(name, x, y, pages):
        nonlocal next_id
        ev = {"id": next_id, "name": name, "note": "", "x": x, "y": y, "pages": pages}
        while len(data["events"]) <= next_id:
            data["events"].append(None)
        data["events"][next_id] = ev
        occupied.add((x, y))
        print(f"  + {name} (id {next_id}) @ ({x},{y})")
        next_id += 1

    # 开场旁白（并行事件，进图时触发一次）
    intro = [
        {"code": 101, "indent": 0, "parameters": ["", 0, 0, 2, ""]},
        {"code": 401, "indent": 0, "parameters": ["这里没有风。"]},
        {"code": 401, "indent": 0, "parameters": ["也没有声音。"]},
        {"code": 401, "indent": 0, "parameters": ["只有一个房间，和门外的一段走廊。"]},
        {"code": 101, "indent": 0, "parameters": ["AE86_1", 4, 0, 2, "小小薇"]},
        {"code": 401, "indent": 0, "parameters": ["……这里不受影响。"]},
        {"code": 401, "indent": 0, "parameters": ["但也不能久留。"]},
        {"code": 123, "indent": 0, "parameters": ["A", 0]},
        {"code": 0, "indent": 0, "parameters": []},
    ]
    intro_page = page("", 0, intro, priority=0)
    intro_page["trigger"] = 3  # autorun
    intro_page["conditions"]["selfSwitchValid"] = True
    # page 1 不能自锁，改成：page0 无条件 autorun，page1 用 selfSwitchA
    intro_page["conditions"] = blank_conditions()
    intro_page["trigger"] = 3

    end_page = page("", 0, [{"code": 0, "indent": 0, "parameters": []}], priority=0)
    end_page["conditions"] = blank_conditions()
    end_page["conditions"]["selfSwitchValid"] = True
    end_page["conditions"]["selfSwitchCh"] = "A"
    add("开场", 1, 2, [intro_page, end_page])

    for name, x, y, sheet, idx, fs, fi, lines in NPCS:
        if (x, y) in occupied:
            print(f"跳过 {name}")
            continue
        cmds = [{"code": 101, "indent": 0, "parameters": [fs, fi, 0, 2, name]}]
        cmds += [{"code": 401, "indent": 0, "parameters": [ln]} for ln in lines]
        cmds.append({"code": 0, "indent": 0, "parameters": []})
        add(name, x, y, [page(sheet, idx, cmds)])

    # 返回门
    name, x, y, tmap, tx, ty_, _ = RETURN_DOOR
    door_cmds = [
        {"code": 201, "indent": 0, "parameters": [0, tmap, tx, ty_, 2, 0]},
        {"code": 0, "indent": 0, "parameters": []},
    ]
    add(name, 7, 8, [page("!Door1", 0, door_cmds)])

    with io.open(MAP, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
