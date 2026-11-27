"""给村庄 NPC 加章节变化对话。

每个 NPC 追加两页：
  page N-1: 开关 1（第一章通关）
  page N  : 开关 4（第三章通关）  ← 最后 = 最高优先级

MZ 的事件页是从后往前找的，所以越靠后优先级越高。
"""

import io
import json

MAP = "data/Map002.json"

# 名字 -> [(开关, [台词...]), (开关, [台词...])]
CHANGES = {
    "鱼鱼": [
        (1, ["你回来了。",
             "洞窟里那个……是阿文吧。",
             "……他变了挺多的。"]),
        (4, ["越往上越不像话。",
             "我不怕。真的。",
             "……你快点。"]),
    ],
    "码字姬": [
        (1, ["我梦到我在批作业。",
             "醒来还在这个村子。"]),
        (4, ["作业本上写满了字。",
             "我一个字都认不出来。"]),
    ],
    "橙子": [
        (1, ["我存下来了一张图。",
             "在这个世界没法看。",
             "但我想留着。"]),
        (4, ["我存的东西越来越多了。",
             "一天存一张。",
             "总有一天能带回去。"]),
    ],
    "⑨": [
        (1, ["这游戏有 bug。",
             "我抽了三十发，什么都没出。"]),
        (4, ["我发现一个 bug。",
             "每次打完那个东西，它都会变强。",
             "……不是我干的。"]),
    ],
    "白羽": [
        (1, ["我数了数。",
             "从村子到洞窟，一共两百三十七步。"]),
        (4, ["我在数还有多少路。",
             "数不清了。"]),
    ],
    "时间の文": [
        (1, ["老婆。",
             "……你还记得我吗。"]),
        (4, ["群主的位置，我一直留着。",
             "虽然已经没人管了。"]),
    ],
    "明月光": [
        (1, ["这个地图的设计，我改主意了。",
             "不需要岔路。"]),
        (4, ["我想了想。",
             "还是需要岔路。"]),
    ],
    "咸鱼": [
        (1, ["笨笨回来了。",
             "笨笨没变。"]),
        (4, ["大家都笨笨。",
             "但笨笨都在往前走。"]),
    ],
}

FACES = {
    "鱼鱼": ("AE86_3", 2),
    "码字姬": ("AE86_2", 6),
    "橙子": ("AE86_2", 0),
    "⑨": ("AE86_2", 1),
    "白羽": ("AE86_3", 4),
    "时间の文": ("AE86_3", 7),
    "明月光": ("AE86_5", 3),
    "咸鱼": ("AE86_4", 5),
}


def cond(switch_id=None):
    c = {
        "actorId": 1, "actorValid": False,
        "itemId": 1, "itemValid": False,
        "selfSwitchCh": "A", "selfSwitchValid": False,
        "switch1Id": 1, "switch1Valid": False,
        "switch2Id": 1, "switch2Valid": False,
        "variableId": 1, "variableValid": False, "variableValue": 0,
    }
    if switch_id is not None:
        c["switch1Id"] = switch_id
        c["switch1Valid"] = True
    return c


def make_page(switch_id, speaker, face, fidx, lines, sheet, sidx):
    cmds = [{"code": 101, "indent": 0, "parameters": [face, fidx, 0, 2, speaker]}]
    cmds += [{"code": 401, "indent": 0, "parameters": [l]} for l in lines]
    cmds.append({"code": 0, "indent": 0, "parameters": []})

    n = len(cmds)
    # 多行文本只保留一个 101
    return {
        "conditions": cond(switch_id),
        "directionFix": False,
        "image": {"characterName": sheet, "characterIndex": sidx,
                  "direction": 2, "pattern": 0, "tileId": 0},
        "list": cmds,
        "moveFrequency": 3,
        "moveRoute": {"list": [{"code": 0, "parameters": []}], "repeat": True,
                      "skippable": False, "wait": False},
        "moveSpeed": 3, "moveType": 0, "priorityType": 1,
        "stepAnime": False, "through": False, "trigger": 0, "walkAnime": True,
    }


def main() -> int:
    with io.open(MAP, encoding="utf-8") as f:
        data = json.load(f)

    by_name = {e["name"]: e for e in data["events"] if e}
    added = 0
    for name, stages in CHANGES.items():
        ev = by_name.get(name)
        if ev is None:
            print(f"  跳过 {name}（找不到）")
            continue
        # 已经有 switch 4 页就跳过
        if any(p["conditions"].get("switch1Id") == 4 and p["conditions"].get("switch1Valid")
               for p in ev["pages"]):
            print(f"  跳过 {name}（已有）")
            continue

        base = ev["pages"][0]
        sheet = base["image"]["characterName"]
        sidx = base["image"]["characterIndex"]
        face, fidx = FACES[name]

        # 按开关升序追加 -> 越后优先级越高
        for sw, lines in sorted(stages, key=lambda x: x[0]):
            ev["pages"].append(make_page(sw, name, face, fidx, lines, sheet, sidx))
        added += 1
        print(f"  {name}: +{len(stages)} 页")

    with io.open(MAP, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    print(f"\n处理 {added} 个 NPC")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
