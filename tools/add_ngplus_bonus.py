"""二周目特典：序章设开关 31，评估之塔的「最后的话」里加一段二周目专属对话。"""

import io
import json

MAP1 = "data/Map001.json"   # 序章
MAP9 = "data/Map009.json"   # 评估之塔
SW = 31


def main() -> int:
    # 1. 序章：二周目分支里开开关 31
    with io.open(MAP1, encoding="utf-8") as f:
        d1 = json.load(f)
    ev = next(e for e in d1["events"] if e and e.get("name") == "序章·开场")
    lst = ev["pages"][0]["list"]
    if not any(c["code"] == 121 and c["parameters"][0] == SW for c in lst):
        # 找到 126（给钥匙）之前插入
        i126 = next((i for i, c in enumerate(lst) if c["code"] == 126), None)
        if i126 is None:
            print("序章：没找到 126")
        else:
            lst[i126:i126] = [{"code": 121, "indent": 1, "parameters": [SW, SW, 0]}]
            print("序章：已加开开关", SW)
    with io.open(MAP1, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d1, f, ensure_ascii=False, separators=(",", ":"))

    # 2. 最后的话：在「那，走吧。」之前插入二周目分支
    with io.open(MAP9, encoding="utf-8") as f:
        d9 = json.load(f)
    ev9 = next(e for e in d9["events"] if e and e.get("name") == "最后的话")
    lst9 = ev9["pages"][0]["list"]
    if any(c["code"] == 111 and c["parameters"] and c["parameters"][0] == 0
           and c["parameters"][1] == SW for c in lst9):
        print("最后的话：已有二周目分支")
    else:
        idx = next((i for i, c in enumerate(lst9)
                    if c["code"] == 401 and c["parameters"]
                    and "那，走吧" in c["parameters"][0]), None)
        if idx is None:
            print("最后的话：没找到插入点")
        else:
            block = [
                {"code": 111, "indent": 0, "parameters": [0, SW, 0]},
                {"code": 101, "indent": 1, "parameters": ["AE86_1", 4, 0, 2, "小小薇"]},
                {"code": 401, "indent": 1, "parameters": ["……薇薇。"]},
                {"code": 401, "indent": 1, "parameters": ["上一次，我们也走到这里。"]},
                {"code": 230, "indent": 1, "parameters": [30]},
                {"code": 101, "indent": 1, "parameters": ["AE86_1", 0, 0, 2, "薇薇"]},
                {"code": 401, "indent": 1, "parameters": ["……嗯。"]},
                {"code": 101, "indent": 1, "parameters": ["AE86_1", 4, 0, 2, "小小薇"]},
                {"code": 401, "indent": 1, "parameters": ["你没上去。"]},
                {"code": 230, "indent": 1, "parameters": [30]},
                {"code": 401, "indent": 1, "parameters": ["这一次，能。"]},
                {"code": 0, "indent": 1, "parameters": []},
                {"code": 412, "indent": 0, "parameters": []},
            ]
            # 插在「那，走吧」那个 101 之前（要退到它前面的 101）
            j = idx
            while j > 0 and lst9[j]["code"] != 101:
                j -= 1
            lst9[j:j] = block
            print(f"最后的话：插入 {len(block)} 条")

    with io.open(MAP9, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d9, f, ensure_ascii=False, separators=(",", ":"))

    # 3. 命名开关
    with io.open("data/System.json", encoding="utf-8") as f:
        sysd = json.load(f)
    sws = sysd["switches"]
    while len(sws) <= SW:
        sws.append("")
    sws[SW] = "二周目模式"
    with io.open("data/System.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(sysd, f, ensure_ascii=False, separators=(",", ":"))

    print("完成")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
