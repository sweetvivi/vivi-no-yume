"""第三批群友 NPC。

用法：python tools/add_npcs3.py
"""

import io
import json

NPCS = [
    ("data/Map003.json", "篮子", 21, 14, "AE86_C2", 5, "AE86_2", 5, [
        "这个季度的推荐……",
        "算了，现在也没人能玩了。",
        "我还留着清单。",
        "回去之后再说。",
    ]),
    ("data/Map003.json", "鬼狐", 3, 3, "AE86_C4", 4, "AE86_4", 4, [
        "妳是……薇薇。",
        "太好了。",
        "我以为这里只有我一个。",
        "……我有点害怕。",
    ]),
    ("data/Map006.json", "青花灯影stella", 21, 4, "AE86_C2", 7, "AE86_2", 7, [
        "我看到了很多东西。",
        "都是假的。",
        "这里的墙壁会重复。",
        "你们小心。",
    ]),
    ("data/Map006.json", "星璇猫猫", 3, 15, "AE86_C5", 2, "AE86_5", 2, [
        "……",
        "我只是路过的。",
        "真的。",
        "别问我为什么在这儿。",
    ]),
    ("data/Map007.json", "基世界人", 16, 12, "AE86_C4", 2, "AE86_4", 2, [
        "这张图我刚才发过吧。",
        "不对，是在群里发过。",
        "这里没有群。",
        "……那我发给谁。",
    ]),
    ("data/Map007.json", "晚儿", 8, 12, "AE86_C4", 6, "AE86_4", 6, [
        "啊。",
        "有人来了。",
        "我还以为要一直待在这儿。",
        "……能带我走吗。",
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


def build_page(sheet, index, name, face_sheet, face_idx, lines):
    cmds = [{"code": 101, "indent": 0, "parameters": [face_sheet, face_idx, 0, 2, name]}]
    cmds += [{"code": 401, "indent": 0, "parameters": [ln]} for ln in lines]
    cmds.append({"code": 0, "indent": 0, "parameters": []})
    return {
        "conditions": blank_conditions(),
        "directionFix": False,
        "image": {
            "characterName": sheet,
            "characterIndex": index,
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
        "priorityType": 1,
        "stepAnime": False,
        "through": False,
        "trigger": 0,
        "walkAnime": True,
    }


def main() -> int:
    by_map = {}
    for row in NPCS:
        by_map.setdefault(row[0], []).append(row)

    for path, rows in by_map.items():
        with io.open(path, encoding="utf-8") as f:
            data = json.load(f)
        existing = [e for e in data["events"] if e]
        next_id = max([e["id"] for e in existing], default=0) + 1
        occupied = {(e["x"], e["y"]) for e in existing}

        for _, name, x, y, sheet, idx, fs, fi, lines in rows:
            if (x, y) in occupied:
                print(f"跳过 {name}")
                continue
            ev = {
                "id": next_id,
                "name": name,
                "note": "",
                "x": x,
                "y": y,
                "pages": [build_page(sheet, idx, name, fs, fi, lines)],
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
