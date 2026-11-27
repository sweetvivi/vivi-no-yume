"""把「鱼鱼·踩背」改成白羽事件（与鱼鱼相邻），并删除旧的白羽位置。

顺带修正称谓：白羽是特殊「女生」，鱼鱼对白羽用「你」。

- 事件 19 在 (6,5)，改为白羽图形
- 内容包含白羽的 solo（数步数）+ 双人互动
- 删除 (4,11) 的旧白羽事件
"""

import io
import json

MAP = "data/Map002.json"
EV_NAME = "鱼鱼·踩背"

# (说话人, 脸图, 脸图idx, [台词])
SCRIPT = [
    ("白羽", "AE86_3", 4, [
        "别乱跑。",
        "我数过了，能走的路只有一条。",
        "从村子到洞窟，两百三十七步。",
        "但习惯改不掉。",
        "总想先把出口都看一遍。",
    ]),
    ("鱼鱼", "AE86_3", 2, ["白羽。"]),
    ("白羽", "AE86_3", 4, ["……嗯。"]),
    ("鱼鱼", "AE86_3", 2, ["我背还是痛。"]),
    ("白羽", "AE86_3", 4, ["……那不是我让妳踩的。"]),
    ("鱼鱼", "AE86_3", 2, ["可是你没有拒绝。"]),
    ("白羽", "AE86_3", 4, ["……"]),
    ("鱼鱼", "AE86_3", 2, [
        "那天我穿黑丝和伊蕾娜那套。",
        "你说「再重点」。",
    ]),
    ("白羽", "AE86_3", 4, ["……那是字面意思上的。"]),
    ("鱼鱼", "AE86_3", 2, [
        "我知道啊。",
        "……我也没说别的。",
    ]),
    ("白羽", "AE86_3", 4, [
        "别站那么近。",
        "……站那么近干嘛。",
    ]),
    ("鱼鱼", "AE86_3", 2, ["因为这里就我们两个人熟。"]),
]


def main() -> int:
    with io.open(MAP, encoding="utf-8") as f:
        data = json.load(f)

    ev = next((e for e in data["events"] if e and e.get("name") == EV_NAME), None)
    if ev is None:
        print("找不到事件")
        return 1

    cmds = []
    for speaker, face, fidx, lines in SCRIPT:
        cmds.append({"code": 101, "indent": 0,
                     "parameters": [face, fidx, 0, 2, speaker]})
        cmds += [{"code": 401, "indent": 0, "parameters": [l]} for l in lines]
    cmds.append({"code": 0, "indent": 0, "parameters": []})

    page = ev["pages"][0]
    page["list"] = cmds
    page["image"] = {"characterName": "AE86_C3", "characterIndex": 4,
                     "direction": 4, "pattern": 0, "tileId": 0}
    ev["name"] = "白羽"
    print(f"事件 {ev['id']} 改为「白羽」，{len(cmds)} 条命令")

    # 删除旧的白羽（4,11）
    old = [e for e in data["events"]
           if e and e.get("name") == "白羽" and e.get("id") != ev["id"]]
    for e in old:
        print(f"  删除旧白羽: id {e['id']} @ ({e['x']},{e['y']})")
        idx = data["events"].index(e)
        data["events"][idx] = None

    with io.open(MAP, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
