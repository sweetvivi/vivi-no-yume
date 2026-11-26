"""批量插入「净化」事件（参照洞窟阿文的写法）。

用法：python tools/add_purify.py
"""

import io
import json

JOBS = [
    {
        "map": "data/Map003.json",
        "x": 17, "y": 6,
        "name": "花咲",
        "sheet": "AE86_C1", "index": 6,
        "actorId": 7,
        "switchId": 7,
        "face": ("AE86_1", 6),
        "scene": [
            ("", [
                "一个圆鼓鼓的影子缩在角落里。",
                "还在发抖。",
            ]),
            ("small", [
                "……花咲。",
            ]),
            ("vivian", [
                "花咲？",
            ]),
            ("small", [
                "一天能水五千条的那个。",
                "所以也变成这样了。",
            ]),
            ("", [
                "光落下去。",
            ]),
            ("", [
                "诅咒一层层褪开。",
            ]),
            ("self", [
                "……啊。",
                "我的零食还在吗。",
            ]),
            ("vivian", [
                "……在群里。",
            ]),
            ("self", [
                "那就好。",
                "我还以为，我把它们弄丢了。",
            ]),
        ],
        "after": [
            ("self", [
                "店里那台咖啡机，我还没擦。",
                "回去要挨骂了。",
            ]),
        ],
    },
    {
        "map": "data/Map006.json",
        "x": 6, "y": 9,
        "name": "白柚",
        "sheet": "AE86_C3", "index": 1,
        "actorId": 18,
        "switchId": 8,
        "face": ("AE86_3", 1),
        "scene": [
            ("", [
                "一只机械臂把她吊在半空。",
                "还在滴滴地响。",
            ]),
            ("small", [
                "白柚。",
            ]),
            ("vivian", [
                "被挂在那种东西上……",
            ]),
            ("", [
                "光顺着机械臂爬上去。",
                "关节一个接一个松开。",
            ]),
            ("self", [
                "……下来了。",
                "我以为我要一直转下去。",
            ]),
            ("vivian", [
                "你没事吧。",
            ]),
            ("self", [
                "没事。",
                "就是有点晕。",
            ]),
            ("self", [
                "对了，⑨呢。",
            ]),
        ],
        "after": [
            ("self", [
                "说好一起打那个新副本的。",
                "再不回去，就过期了。",
            ]),
        ],
    },
    {
        "map": "data/Map007.json",
        "x": 6, "y": 8,
        "name": "喵神",
        "sheet": "AE86_C4", "index": 0,
        "actorId": 25,
        "switchId": 9,
        "face": ("AE86_4", 0),
        "scene": [
            ("", [
                "她蹲在最高的台阶上，抱着膝盖。",
                "像是一直在等谁。",
            ]),
            ("small", [
                "喵神。",
                "出没最少的那个。",
            ]),
            ("vivian", [
                "所以祝化最浅……",
            ]),
            ("small", [
                "几乎没有。",
            ]),
            ("", [
                "一层薄薄的灰，从她身上剥下来。",
            ]),
            ("self", [
                "……薇薇。",
                "我等你好久了。",
            ]),
            ("vivian", [
                "等我？",
            ]),
            ("self", [
                "嗯。",
                "因为我知道，你会来的。",
            ]),
            ("self", [
                "……有饼干吗。",
            ]),
        ],
        "after": [
            ("self", [
                "没有也没关系。",
                "我先记着。",
            ]),
        ],
    },
]

WHO = {
    "vivian": ("AE86_1", 0, "薇薇"),
    "small": ("AE86_1", 4, "小小薇"),
}


def blank_conditions(switch_id=None):
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


def line_cmds(speaker, lines, self_face, self_name):
    if speaker == "self":
        face, idx, name = self_face[0], self_face[1], self_name
    elif speaker == "":
        face, idx, name = "", 0, ""
    else:
        face, idx, name = WHO[speaker]
    out = [{"code": 101, "indent": 0, "parameters": [face, idx, 0, 2, name]}]
    out += [{"code": 401, "indent": 0, "parameters": [ln]} for ln in lines]
    return out


def build_page(conditions, sheet, index, cmds, trigger=0, priority=1):
    return {
        "conditions": conditions,
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
        "priorityType": priority,
        "stepAnime": False,
        "through": False,
        "trigger": trigger,
        "walkAnime": True,
    }


def main() -> int:
    by_map = {}
    for job in JOBS:
        by_map.setdefault(job["map"], []).append(job)

    for path, jobs in by_map.items():
        with io.open(path, encoding="utf-8") as f:
            data = json.load(f)
        existing = [e for e in data["events"] if e]
        next_id = max([e["id"] for e in existing], default=0) + 1
        occupied = {(e["x"], e["y"]) for e in existing}

        for job in jobs:
            if (job["x"], job["y"]) in occupied:
                print(f"跳过 {job['name']}：位置被占")
                continue

            # --- 第 1 页：净化演出 ---
            cmds = []
            for speaker, lines in job["scene"]:
                if speaker == "" and lines and lines[0].startswith("光"):
                    cmds.append({"code": 224, "indent": 0,
                                 "parameters": [[255, 255, 255, 180], 90, True]})
                    cmds.append({"code": 230, "indent": 0, "parameters": [30]})
                cmds += line_cmds(speaker, lines, job["face"], job["name"])
            cmds += [
                {"code": 129, "indent": 0, "parameters": [job["actorId"], 0, 0]},
                {"code": 121, "indent": 0, "parameters": [job["switchId"], job["switchId"], 0]},
                {"code": 123, "indent": 0, "parameters": ["A", 0]},
                {"code": 0, "indent": 0, "parameters": []},
            ]
            page0 = build_page(blank_conditions(), job["sheet"], job["index"], cmds)

            # --- 第 2 页：已净化 ---
            after = []
            for speaker, lines in job["after"]:
                after += line_cmds(speaker, lines, job["face"], job["name"])
            after.append({"code": 0, "indent": 0, "parameters": []})
            cond1 = blank_conditions()
            cond1["selfSwitchValid"] = True
            cond1["selfSwitchCh"] = "A"
            page1 = build_page(cond1, job["sheet"], job["index"], after)

            ev = {
                "id": next_id,
                "name": job["name"],
                "note": "",
                "x": job["x"],
                "y": job["y"],
                "pages": [page0, page1],
            }
            while len(data["events"]) <= next_id:
                data["events"].append(None)
            data["events"][next_id] = ev
            occupied.add((job["x"], job["y"]))
            print(f"  + {job['name']} (id {next_id}) -> {path}")
            next_id += 1

        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
