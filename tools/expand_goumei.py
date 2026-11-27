"""给狗妹补一段完整的戏。

她有钱，但在这个世界里钱没用。她想帮忙，只能提供资源。
"""

import io
import json

MAP = "data/Map006.json"
EV_NAME = "狗妹"

EXTRA = [
    ("", [
        "她想了想，把一样东西递过来。",
    ]),
    ("self", [
        "这个给你。",
    ]),
    ("vivian", [
        "……钥匙？",
    ]),
    ("self", [
        "万能钥匙。",
        "我不知道从哪来的。",
        "可能是之前的人留下的。",
    ]),
    ("self", [
        "你们用得比我好。",
    ]),
]

FACE_SELF = ("AE86_1", 3, "狗妹")
FACE_VIVI = ("AE86_1", 0, "薇薇")


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

    ev = next((e for e in data["events"] if e and e.get("name") == EV_NAME), None)
    if ev is None:
        print("找不到狗妹")
        return 1

    lst = ev["pages"][0]["list"]
    if any(c["code"] == 126 for c in lst):
        print("已加过，跳过")
        return 0

    end = next(i for i in range(len(lst) - 1, -1, -1) if lst[i]["code"] == 0)

    block = []
    for who, lines in EXTRA:
        if who == "self":
            face, fidx, name = FACE_SELF
        elif who == "vivian":
            face, fidx, name = FACE_VIVI
        else:
            face, fidx, name = "", 0, ""
        block.append({"code": 101, "indent": 0, "parameters": [face, fidx, 0, 2, name]})
        block += [{"code": 401, "indent": 0, "parameters": [l]} for l in lines]

    # 给万能钥匙
    block.append({"code": 126, "indent": 0, "parameters": [1, 0, 0, 1]})
    block.append({"code": 101, "indent": 0, "parameters": ["", 0, 0, 2, ""]})
    block.append({"code": 401, "indent": 0, "parameters": ["（得到了 万能钥匙 ×1）"]})

    lst[end:end] = block

    with io.open(MAP, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    print(f"狗妹：追加 {len(block)} 条命令（含给钥匙）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
