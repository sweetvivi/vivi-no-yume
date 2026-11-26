"""给每个 Boss 战配置专属战斗 BGM。

MZ 的战斗 BGM 取 `$gameSystem.battleBgm()`：
    return this._battleBgm || $dataSystem.battleBgm;
所以临时设置 `_battleBgm` 就能覆盖，战斗结束后置 null 还原。

用法：python tools/boss_bgm.py
"""

import io
import json

# (文件, 事件名, BGM 名)
JOBS = [
    ("data/Map004.json", "祝祝修女", "DF_Battle2"),
    ("data/Map006.json", "科学家", "DF_Battle4"),
    ("data/Map007.json", "超级AI", "DF_Battle6"),
    ("data/Map008.json", "小冰", "DF_Battle7"),
    ("data/Map009.json", "观者", "DF_Battle8"),
]


def set_cmd(name):
    return {
        "code": 355,
        "indent": 0,
        "parameters": [
            f'$gameSystem._battleBgm = {{name:"{name}", volume:90, pitch:100, pan:0}};'
        ],
    }


def restore_cmd():
    return {
        "code": 355,
        "indent": 0,
        "parameters": ["$gameSystem._battleBgm = null;"],
    }


def main() -> int:
    for path, evname, bgm in JOBS:
        with io.open(path, encoding="utf-8") as f:
            data = json.load(f)
        ev = next((e for e in data["events"] if e and e.get("name") == evname), None)
        if ev is None:
            print(f"MISS {path} {evname}")
            continue

        page = ev["pages"][0]
        cmds = page["list"]

        if any(c["code"] == 355 and "_battleBgm" in str(c["parameters"]) for c in cmds):
            print(f"  {evname}: 已有配置，跳过")
            continue

        i301 = next((i for i, c in enumerate(cmds) if c["code"] == 301), None)
        if i301 is None:
            print(f"  {evname}: 没有 301")
            continue

        cmds.insert(i301, set_cmd(bgm))

        # 末尾（code 0 之前）还原
        i0 = len(cmds) - 1
        for i in range(len(cmds) - 1, -1, -1):
            if cmds[i]["code"] == 0:
                i0 = i
                break
        cmds.insert(i0, restore_cmd())

        print(f"  {evname}: {bgm}")

        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
