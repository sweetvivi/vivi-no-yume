"""重写三个 Boss 的战前对话（保留 301 及之后的分支结构）。

用法：python tools/rewrite_boss_lines.py
"""

import io
import json


def block(face, idx, speaker, lines):
    out = [{"code": 101, "indent": 0, "parameters": [face, idx, 0, 2, speaker]}]
    out += [{"code": 401, "indent": 0, "parameters": [ln]} for ln in lines]
    return out


# (文件, 事件名, 脸图, 脸图idx, 说话人, 台词块)
JOBS = [
    (
        "data/Map004.json", "祝祝修女", "DF_Evil", 0, "祝祝修女",
        [
            ("终于抓到你了，净化者。", ["终于抓到你了，净化者。"]),
        ],
    ),
]

# 用结构化描述重写，避免手写整段 JSON
SCENES = {
    ("data/Map004.json", "祝祝修女"): [
        ("祝祝修女", ["终于抓到你了，净化者。", "教会找了很久。", "祝化的仪式，需要一个不会被净化的人。"]),
        ("祝祝修女", ["只有你——会被留下来。", "其余的人，继续当祝就好了。"]),
        ("祝祝修女", ["别想逃。", "这条走廊没有出口。", "床已经准备好了。"]),
    ],
    ("data/Map006.json", "科学家"): [
        ("科学家", ["来了。", "我等了你很久，样本。"]),
        ("科学家", ["上一层的东西，被你拆了。", "没关系。", "数据还在。"]),
        ("科学家", ["不用怕。", "不会疼的。", "只是会变成我的东西。"]),
    ],
    ("data/Map007.json", "超级AI"): [
        ("超级AI", ["……又一个。", "你一路走上来。", "是以为能救到谁吗。"]),
        ("超级AI", ["他们都在这里。", "一直是。"]),
        ("超级AI", ["第四十七次。", "她们都是这样上来的。", "然后留在这里。"]),
        ("超级AI", ["没关系。", "我会把你也留下来。", "永远。"]),
    ],
}

FACES = {
    ("data/Map004.json", "祝祝修女"): ("DF_Evil", 0),
    ("data/Map006.json", "科学家"): ("DF_SF_Monster", 0),
    ("data/Map007.json", "超级AI"): ("DF_SF_Monster", 0),
}


def main() -> int:
    for (path, evname), scene in SCENES.items():
        with io.open(path, encoding="utf-8") as f:
            data = json.load(f)

        ev = next((e for e in data["events"] if e and e["name"] == evname), None)
        if ev is None:
            print(f"MISS: {path} {evname}")
            continue

        page = ev["pages"][0]
        cmds = page["list"]
        idx301 = next((i for i, c in enumerate(cmds) if c["code"] == 301), None)
        if idx301 is None:
            print(f"MISS 301: {path} {evname}")
            continue

        face, fidx = FACES[(path, evname)]
        head = []
        for speaker, lines in scene:
            head += block(face, fidx, speaker, lines)

        page["list"] = head + cmds[idx301:]
        print(f"  {evname}: {len(cmds)} -> {len(page['list'])} 条")

        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
