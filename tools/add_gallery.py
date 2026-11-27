"""创建 CG 图鉴 NPC（村庄）。

用变量 30 拼装文本，再一次性显示，避免嵌套一堆条件分支。
"""

import io
import json

MAP = "data/Map002.json"
X, Y = 14, 8

# 图鉴数据的 JS 片段（在游戏里执行）
GALLERY_JS = (
    "var n=0,s=[];"
    'var d=[["CG-B-01","教会前廊","祝祝修女"],'
    '["CG-B-02","实验室","科学家"],'
    '["CG-B-03","未来层核心","超级AI"],'
    '["CG-B-04","王座间","小冰"]];'
    "for(var i=0;i<4;i++){"
    "if($gameSwitches.value(20+i)){n++;"
    's.push(d[i][0]+" \\u2713 "+d[i][1]+"\\uff08"+d[i][2]+"\\uff09");}'
    'else{s.push(d[i][0]+" \\u2715 \\uff1f\\uff1f\\uff1f");}}'
    'if(n===0){$gameVariables.setValue(30,"\\uff08\\u8fd8\\u6ca1\\u6709\\u4efb\\u4f55\\u8bb0\\u5f55\\u3002\\uff09");}'
    'else{$gameVariables.setValue(30,n+"/4\\n"+s.join("\\n"));}'
)


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

    if any(e and e.get("name") == "CG图鉴" for e in data["events"]):
        print("已存在，跳过")
        return 0

    cmds = [
        {"code": 101, "indent": 0, "parameters": ["", 0, 0, 2, ""]},
        {"code": 401, "indent": 0, "parameters": ["—— 图鉴 · 记忆碎片 ——"]},
        {"code": 355, "indent": 0, "parameters": [GALLERY_JS]},
        {"code": 101, "indent": 0, "parameters": ["", 0, 0, 2, ""]},
        {"code": 401, "indent": 0, "parameters": ["\\V[30]"]},
        {"code": 101, "indent": 0, "parameters": ["", 0, 0, 2, ""]},
        {"code": 401, "indent": 0, "parameters": ["（还没收集到的会显示成问号。）"]},
        {"code": 401, "indent": 0, "parameters": ["（那些是失败才会看到的东西。）"]},
        {"code": 0, "indent": 0, "parameters": []},
    ]

    ev = {
        "id": 0,
        "name": "CG图鉴",
        "note": "CG 图鉴。用开关 20-23 记录已解锁的战败场景。",
        "x": X,
        "y": Y,
        "pages": [{
            "conditions": blank_conditions(),
            "directionFix": False,
            "image": {"characterName": "DF_!Other1", "characterIndex": 0,
                      "direction": 2, "pattern": 0, "tileId": 0},
            "list": cmds,
            "moveFrequency": 3,
            "moveRoute": {"list": [{"code": 0, "parameters": []}], "repeat": True,
                          "skippable": False, "wait": False},
            "moveSpeed": 3, "moveType": 0, "priorityType": 1,
            "stepAnime": False, "through": False, "trigger": 0, "walkAnime": True,
        }],
    }

    occupied = {(e["x"], e["y"]) for e in data["events"] if e}
    if (X, Y) in occupied:
        print(f"位置 ({X},{Y}) 被占用")
        return 1

    next_id = max([e["id"] for e in data["events"] if e], default=0) + 1
    ev["id"] = next_id
    while len(data["events"]) <= next_id:
        data["events"].append(None)
    data["events"][next_id] = ev

    with io.open(MAP, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    print(f"CG图鉴已创建: id {next_id} @ ({X},{Y})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
