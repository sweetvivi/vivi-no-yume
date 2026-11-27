"""把 CG 图鉴改成每个条目一个变量、一行一个 401。

原因：MZ 的 Show Text（401）不支持 \\n 换行，一行必须是一条 401。
"""

import io
import json

MAP = "data/Map002.json"

JS = (
    "var n=0;"
    'var d=[["CG-B-01","教会前廊"],["CG-B-02","实验室"],'
    '["CG-B-03","未来层核心"],["CG-B-04","王座间"]];'
    "for(var i=0;i<4;i++){"
    "if($gameSwitches.value(20+i)){n++;"
    '$gameVariables.setValue(31+i,d[i][0]+" \\u2713 "+d[i][1]);}'
    'else{$gameVariables.setValue(31+i,d[i][0]+" \\u2715 \\uff1f\\uff1f\\uff1f");}}'
    '$gameVariables.setValue(30,n+"/4");'
)


def main() -> int:
    # 1. 扩容变量表到 34
    p_sys = "data/System.json"
    sys_data = json.load(io.open(p_sys, encoding="utf-8"))
    v = sys_data["variables"]
    while len(v) <= 34:
        v.append("")
    v[30] = "图鉴-已解锁数"
    for i in range(4):
        v[31 + i] = f"图鉴-{i + 1:02d}"
    io.open(p_sys, "w", encoding="utf-8", newline="\n").write(
        json.dumps(sys_data, ensure_ascii=False, separators=(",", ":")))
    print(f"variables 长度: {len(v)}")

    # 2. 重写图鉴事件
    p = MAP
    data = json.load(io.open(p, encoding="utf-8"))
    ev = next((e for e in data["events"] if e and e.get("name") == "CG图鉴"), None)
    if ev is None:
        print("找不到 CG图鉴")
        return 1

    cmds = [
        {"code": 101, "indent": 0, "parameters": ["", 0, 0, 2, ""]},
        {"code": 401, "indent": 0, "parameters": ["—— 图鉴 · 记忆碎片 ——"]},
        {"code": 355, "indent": 0, "parameters": [JS]},
        {"code": 101, "indent": 0, "parameters": ["", 0, 0, 2, ""]},
        {"code": 401, "indent": 0, "parameters": ["已收集 \\V[30]"]},
        {"code": 401, "indent": 0, "parameters": ["\\V[31]"]},
        {"code": 401, "indent": 0, "parameters": ["\\V[32]"]},
        {"code": 401, "indent": 0, "parameters": ["\\V[33]"]},
        {"code": 401, "indent": 0, "parameters": ["\\V[34]"]},
        {"code": 101, "indent": 0, "parameters": ["", 0, 0, 2, ""]},
        {"code": 401, "indent": 0, "parameters": ["（还没收集到的会显示成问号。）"]},
        {"code": 401, "indent": 0, "parameters": ["（那些是失败才会看到的东西。）"]},
        {"code": 0, "indent": 0, "parameters": []},
    ]
    ev["pages"][0]["list"] = cmds

    io.open(p, "w", encoding="utf-8", newline="\n").write(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    print("图鉴事件已重写")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
