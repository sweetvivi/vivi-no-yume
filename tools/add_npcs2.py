"""往多张地图批量插入群友 NPC。

用法：python tools/add_npcs2.py
"""

import io
import json

# (map, 名字, x, y, 行走图sheet, index, 脸图sheet, faceIdx, [台词...])
NPCS = [
    # --- 祝化洞窟 ---
    ("data/Map003.json", "灵游", 20, 4, "AE86_C2", 3, "AE86_2", 3, [
        "这地图的引导做得太烂了。",
        "不，我不是在挑刺。",
        "……好吧，我是在挑刺。",
        "换我早就通关了。",
    ]),
    ("data/Map003.json", "猹", 21, 5, "AE86_C5", 0, "AE86_5", 0, [
        "灵处呢。",
        "刚才还在这儿。",
        "算了，他跑不远的。",
        "这地方就这么大。",
    ]),
    ("data/Map003.json", "黄狐狸", 4, 15, "AE86_C3", 0, "AE86_3", 0, [
        "……",
        "我本来是来找薰衣草的。",
        "结果先找到妳。",
        "她应该还在上面。",
    ]),
    # --- 现代层 ---
    ("data/Map006.json", "狗妹", 18, 8, "AE86_C1", 3, "AE86_1", 3, [
        "薇薇。",
        "我很有钱。",
        "但在这地方，钱好像没用。",
        "……第一次有这种感觉。",
    ]),
    ("data/Map006.json", "久远崎彩祸", 5, 12, "AE86_C2", 4, "AE86_2", 4, [
        "别这么看我。",
        "我知道这身衣服很奇怪。",
        "在这里没得选。",
        "……回去之后我会换掉的。",
    ]),
    ("data/Map006.json", "十三", 20, 12, "AE86_C4", 3, "AE86_4", 3, [
        "阿百呢。",
        "我在找他。",
        "他总是一个人走在前面。",
        "我得跟上。",
    ]),
    # --- 未来层 ---
    ("data/Map007.json", "天辽阔", 18, 6, "AE86_C1", 7, "AE86_1", 7, [
        "有没有……",
        "算了，都这个时候了。",
        "我就是问问。",
        "习惯了。",
    ]),
    ("data/Map007.json", "初雪", 5, 5, "AE86_C5", 1, "AE86_5", 1, [
        "薇薇！",
        "我一直想跟你们一起玩。",
        "这次终于……",
        "虽然场合不太对。",
    ]),
    ("data/Map007.json", "殇", 20, 10, "AE86_C4", 7, "AE86_4", 7, [
        "看我。",
        "我是粉色的。",
        "其他祝都是灰的。",
        "……我不知道为什么。",
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

        for _, name, x, y, sheet, idx, face_sheet, face_idx, lines in rows:
            if (x, y) in occupied:
                print(f"跳过 {name}：({x},{y}) 被占")
                continue
            ev = {
                "id": next_id,
                "name": name,
                "note": "",
                "x": x,
                "y": y,
                "pages": [build_page(sheet, idx, name, face_sheet, face_idx, lines)],
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
