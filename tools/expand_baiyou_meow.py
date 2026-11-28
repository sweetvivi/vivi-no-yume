"""给白柚和喵神补「入队后」的对话（page 1 之前是空的）。"""

import io
import json

JOBS = [
    ("data/Map006.json", "白柚", [
        ("", ["她扶着墙站了一会儿。"]),
        ("self", ["……还晕。"]),
        ("self", ["⑨呢。"]),
        ("vivian", ["他不在这儿。"]),
        ("self", ["哦。"]),
        ("self", ["那算了。"]),
        ("", ["她转过身去。"]),
        ("self", ["……你别死啊。"]),
        ("vivian", ["……？"]),
        ("self", ["我说了什么吗。"]),
    ]),
    ("data/Map007.json", "喵神", [
        ("self", ["饼干。"]),
        ("vivian", ["没有。"]),
        ("self", ["……那算了。"]),
        ("", ["她低下头，把脸埋进膝盖。"]),
        ("self", ["薇薇。"]),
        ("self", ["你有没有想过，为什么我从来不语音。"]),
        ("vivian", ["因为懒？"]),
        ("self", ["嗯。因为懒。"]),
        ("", ["很长的停顿。"]),
        ("self", ["……你就当是懒吧。"]),
    ]),
]

FACES = {
    "白柚": ("AE86_3", 1),
    "喵神": ("AE86_4", 0),
    "薇薇": ("AE86_1", 0),
}


def main() -> int:
    for path, name, steps in JOBS:
        with io.open(path, encoding="utf-8") as f:
            data = json.load(f)

        ev = next((e for e in data["events"] if e and e.get("name") == name), None)
        if ev is None or len(ev["pages"]) < 2:
            print(f"  {name}: 跳过")
            continue

        pg = ev["pages"][1]
        if any(c["code"] == 401 for c in pg["list"]):
            print(f"  {name}: page 1 已有文本，跳过")
            continue

        cmds = []
        for who, lines in steps:
            if who == "self":
                face, fidx = FACES[name]
                speaker = name
            elif who == "vivian":
                face, fidx = FACES["薇薇"]
                speaker = "薇薇"
            else:
                face, fidx = "", 0
                speaker = ""
            cmds.append({"code": 101, "indent": 0,
                         "parameters": [face, fidx, 0, 2, speaker]})
            cmds += [{"code": 401, "indent": 0, "parameters": [l]} for l in lines]
        cmds.append({"code": 0, "indent": 0, "parameters": []})

        pg["list"] = cmds
        # page 1 是入队后的常驻页，不能挡路
        pg["priorityType"] = 0
        pg["through"] = True

        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

        print(f"  {name}: 写入 {len(cmds)} 条")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
