"""评估之塔入口的「最后的话」。

打观者之前，队伍里每个人说一句。用 111 条件分支按「是否在队」显示。
"""

import io
import json

MAP = "data/Map009.json"
X, Y = 9, 9
EV_NAME = "最后的话"

# (actorId 或 None = 必定出现, 说话人, 脸图, 脸图idx, 台词)
STEPS = [
    (None, "", "", 0, ["再往上，就是最后的房间了。"]),
    (None, "小小薇", "AE86_1", 4, ["……准备好了吗。"]),
    (6, "阿文", "AE86_1", 6, ["我在这儿。"]),
    (7, "花咲", "AE86_1", 6, ["我有零食。", "真的。"]),
    (18, "白柚", "AE86_3", 1, ["我帮你看着后面。"]),
    (25, "喵神", "AE86_4", 0, ["……嗯。"]),
    (None, "小小薇", "AE86_1", 4, ["那，走吧。"]),
    (None, "薇薇", "AE86_1", 0, ["嗯。"]),
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


def main() -> int:
    with io.open(MAP, encoding="utf-8") as f:
        data = json.load(f)

    if any(e and e.get("name") == EV_NAME for e in data["events"]):
        print("已存在，跳过")
        return 0

    occupied = {(e["x"], e["y"]) for e in data["events"] if e}
    if (X, Y) in occupied:
        print(f"({X},{Y}) 被占用")
        return 1

    cmds = []
    for actor_id, speaker, face, fidx, lines in STEPS:
        body = [{"code": 101, "indent": 0, "parameters": [face, fidx, 0, 2, speaker]}]
        body += [{"code": 401, "indent": 0, "parameters": [l]} for l in lines]

        if actor_id is None:
            cmds += body
        else:
            cmds.append({"code": 111, "indent": 0, "parameters": [4, actor_id, 0]})
            for c in body:
                c = dict(c)
                c["indent"] = 1
                cmds.append(c)
            cmds.append({"code": 0, "indent": 1, "parameters": []})
            cmds.append({"code": 412, "indent": 0, "parameters": []})

    cmds.append({"code": 123, "indent": 0, "parameters": ["A", 0]})
    cmds.append({"code": 0, "indent": 0, "parameters": []})

    page = {
        "conditions": blank_conditions(),
        "directionFix": False,
        "image": {"characterName": "", "characterIndex": 0,
                  "direction": 2, "pattern": 0, "tileId": 0},
        "list": cmds,
        "moveFrequency": 3,
        "moveRoute": {"list": [{"code": 0, "parameters": []}], "repeat": True,
                      "skippable": False, "wait": False},
        "moveSpeed": 3, "moveType": 0, "priorityType": 1,
        "stepAnime": False, "through": False, "trigger": 0, "walkAnime": True,
    }
    page2 = json.loads(json.dumps(page))
    page2["conditions"]["selfSwitchValid"] = True
    page2["conditions"]["selfSwitchCh"] = "A"
    page2["list"] = [{"code": 0, "indent": 0, "parameters": []}]
    page2["priorityType"] = 0
    page2["through"] = True

    next_id = max([e["id"] for e in data["events"] if e], default=0) + 1
    ev = {"id": next_id, "name": EV_NAME, "note": "", "x": X, "y": Y,
          "pages": [page, page2]}
    while len(data["events"]) <= next_id:
        data["events"].append(None)
    data["events"][next_id] = ev

    with io.open(MAP, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    print(f"「{EV_NAME}」已创建: id {next_id} @ ({X},{Y})，{len(cmds)} 条命令")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
