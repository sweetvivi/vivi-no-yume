"""给 Boss 战前加「同伴插话」。

入队的同伴在 Boss 战前会根据是否在队说不同的话。
用 111 条件分支（type 4 = actor in party）实现。

注意：小冰的代词是「他」（用户指定）。
"""

import io
import json

# (地图, 事件名, [(actorId, 说话人, [台词])])
JOBS = [
    ("data/Map004.json", "祝祝修女", [
        (6, "阿文", [
            "那个修女……",
            "我在洞里听见她说话。",
            "一直在讲「仪式」。",
        ]),
    ]),
    ("data/Map006.json", "科学家", [
        (6, "阿文", [
            "那家伙，我见过。",
            "在我被关着的时候。",
            "他说「再多一点」。",
        ]),
        (7, "花咲", [
            "这里也有便利店吗。",
            "……没有啊。",
            "那我更讨厌他了。",
        ]),
    ]),
    ("data/Map007.json", "超级AI", [
        (7, "花咲", [
            "这个声音……",
            "一直在重复同一句话。",
        ]),
        (18, "白柚", [
            "我被挂起来的时候也听见了。",
            "它说「第四十七次」。",
        ]),
    ]),
    ("data/Map008.json", "小冰", [
        (6, "阿文", [
            "小冰……",
            "群里最话多的就是他。",
            "现在一句话都不说了。",
        ]),
        (7, "花咲", [
            "他上次还问我，便利店有没有进新的零食。",
            "我说没有。",
            "……他有点失望。",
        ]),
    ]),
]

FACES = {
    "阿文": ("AE86_1", 6),
    "花咲": ("AE86_1", 6),
    "白柚": ("AE86_3", 1),
}


def build_block(actor_id: int, speaker: str, lines: list) -> list:
    face, fidx = FACES.get(speaker, ("", 0))
    return [
        {"code": 111, "indent": 0, "parameters": [4, actor_id, 0]},
        {"code": 101, "indent": 1, "parameters": [face, fidx, 0, 2, speaker]},
        *[{"code": 401, "indent": 1, "parameters": [l]} for l in lines],
        {"code": 0, "indent": 1, "parameters": []},
        {"code": 412, "indent": 0, "parameters": []},
    ]


def main() -> int:
    for path, evname, rows in JOBS:
        with io.open(path, encoding="utf-8") as f:
            data = json.load(f)

        ev = next((e for e in data["events"] if e and e.get("name") == evname), None)
        if ev is None:
            print(f"MISS {path} {evname}")
            continue

        lst = ev["pages"][0]["list"]
        if any(c["code"] == 111 and c["parameters"] and c["parameters"][0] == 4 for c in lst):
            print(f"  {evname}: 已有同伴插话，跳过")
            continue

        i301 = next((i for i, c in enumerate(lst) if c["code"] == 301), None)
        if i301 is None:
            print(f"  {evname}: 没找到 301")
            continue

        block = []
        for actor_id, speaker, lines in rows:
            block += build_block(actor_id, speaker, lines)

        lst[i301:i301] = block
        print(f"  {evname}: +{len(rows)} 段同伴插话")

        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
