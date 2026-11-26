"""往地图里批量插入「群友人设」NPC 事件。

用法：python tools/add_npcs.py
事件 id 从现有最大值 +1 开始分配。
"""

import io
import json

MAP = "data/Map002.json"

# (事件名, x, y, 行走图sheet, 行走图index, [(脸图sheet, 脸图idx, 说话人, [台词...]), ...])
NPCS = [
    (
        "鱼鱼", 5, 5, "AE86_C3", 2,
        [("AE86_3", 2, "鱼鱼", [
            "醒了啊。",
            "我刚才在想，这破地方连个便利店都没有。",
            "……妳笑什么。",
            "钢板怎么了。别看。",
        ])],
    ),
    (
        "码字姬", 7, 13, "AE86_C2", 6,
        [("AE86_2", 6, "码字姬", [
            "……啊，薇薇。",
            "我在想，如果是梦的话，回去还要批作业。",
            "那就别醒了吧。",
            "……开玩笑的。",
        ])],
    ),
    (
        "橙子", 17, 13, "AE86_C2", 0,
        [("AE86_2", 0, "橙子", [
            "我什么都存不下来。",
            "手机在这儿是块砖。",
            "……第一次觉得，存东西这件事挺没用的。",
        ])],
    ),
    (
        "⑨", 19, 6, "AE86_C2", 1,
        [("AE86_2", 1, "⑨", [
            "这地方像不像那个……",
            "算了，说了妳也不懂。",
            "我还挺喜欢这里的。",
            "至少不用抽卡。",
        ])],
    ),
    (
        "白羽", 4, 11, "AE86_C3", 4,
        [("AE86_3", 4, "白羽", [
            "别乱跑。",
            "我数过了，能走的路只有一条。",
            "但习惯改不掉。",
            "总想先把出口都看一遍。",
        ])],
    ),
    (
        "时间の文", 20, 10, "AE86_C3", 7,
        [("AE86_3", 7, "时间の文", [
            "……老婆。",
            "习惯了，改不掉。",
            "群主的位置我早就交出去了。",
            "现在这样反而轻松。",
        ])],
    ),
    (
        "明月光", 8, 15, "AE86_C5", 3,
        [("AE86_5", 3, "明月光", [
            "……",
            "这个地图，做得不错。",
            "如果是我，会在右边加一条岔路。",
            "算了。不是我的游戏。",
        ])],
    ),
    (
        "咸鱼", 16, 4, "AE86_C4", 5,
        [("AE86_4", 5, "咸鱼", [
            "笨笨。",
            "妳也笨笨。",
            "大家都笨笨。",
            "笨笨挺好的。",
        ])],
    ),
]


def blank_conditions() -> dict:
    return {
        "actorId": 1, "actorValid": False,
        "itemId": 1, "itemValid": False,
        "selfSwitchCh": "A", "selfSwitchValid": False,
        "switch1Id": 1, "switch1Valid": False,
        "switch2Id": 1, "switch2Valid": False,
        "variableId": 1, "variableValid": False, "variableValue": 0,
    }


def build_list(blocks) -> list:
    cmds = []
    for face_sheet, face_idx, speaker, lines in blocks:
        cmds.append({
            "code": 101, "indent": 0,
            "parameters": [face_sheet, face_idx, 0, 2, speaker],
        })
        for ln in lines:
            cmds.append({"code": 401, "indent": 0, "parameters": [ln]})
    cmds.append({"code": 0, "indent": 0, "parameters": []})
    return cmds


def build_page(sheet, idx, cmds) -> dict:
    return {
        "conditions": blank_conditions(),
        "directionFix": False,
        "image": {
            "characterName": sheet,
            "characterIndex": idx,
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
    with io.open(MAP, encoding="utf-8") as f:
        data = json.load(f)

    existing = [e for e in data["events"] if e]
    next_id = max([e["id"] for e in existing], default=0) + 1
    occupied = {(e["x"], e["y"]) for e in existing}

    added = 0
    for name, x, y, sheet, idx, blocks in NPCS:
        if (x, y) in occupied:
            print(f"跳过 {name}：({x},{y}) 已被占用")
            continue
        ev = {
            "id": next_id,
            "name": name,
            "note": "",
            "x": x,
            "y": y,
            "pages": [build_page(sheet, idx, build_list(blocks))],
        }
        # 保持 0 号空槽（MZ 的 events 以 id 为索引）
        while len(data["events"]) <= next_id:
            data["events"].append(None)
        data["events"][next_id] = ev
        occupied.add((x, y))
        print(f"  + {name} (id {next_id}) @ ({x},{y})")
        next_id += 1
        added += 1

    with io.open(MAP, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(f"\n共添加 {added} 个 NPC")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
