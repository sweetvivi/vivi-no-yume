"""二周目：在序章开场末尾检测通关标记，给隐藏奖励。

标记存在 localStorage（NW.js 的 profile 里），不受「新游戏」重置影响。
MZ 没有跨存档的全局变量，所以只能走 localStorage。
"""

import io
import json

MAP = "data/Map001.json"

DETECT_JS = (
    'try{$gameVariables.setValue(35, localStorage.getItem("ae86_clear")==="1"?1:0);}'
    "catch(e){$gameVariables.setValue(35,0);}"
)


def main() -> int:
    with io.open(MAP, encoding="utf-8") as f:
        data = json.load(f)

    ev = next((e for e in data["events"] if e and e.get("name") == "序章·开场"), None)
    if ev is None:
        print("找不到序章·开场")
        return 1

    lst = ev["pages"][0]["list"]
    if any(c["code"] == 355 and "ae86_clear" in str(c["parameters"]) for c in lst):
        print("已存在二周目检测")
        return 0

    # 插在末尾（code 0 之前）
    end = len(lst) - 1
    for i in range(len(lst) - 1, -1, -1):
        if lst[i]["code"] == 0:
            end = i
            break

    block = [
        {"code": 355, "indent": 0, "parameters": [DETECT_JS]},
        {"code": 111, "indent": 0, "parameters": [1, 35, 0, 1, 0, 0, 0, 0, 0]},
        {"code": 101, "indent": 1, "parameters": ["", 0, 0, 2, ""]},
        {"code": 401, "indent": 1, "parameters": ["这个梦，你好像已经做过一次。"]},
        {"code": 101, "indent": 1, "parameters": ["AE86_1", 4, 0, 2, "小小薇"]},
        {"code": 401, "indent": 1, "parameters": ["……妳也记得？"]},
        {"code": 101, "indent": 1, "parameters": ["AE86_1", 0, 0, 2, "薇薇"]},
        {"code": 401, "indent": 1, "parameters": ["我记得。"]},
        {"code": 101, "indent": 1, "parameters": ["AE86_1", 4, 0, 2, "小小薇"]},
        {"code": 401, "indent": 1, "parameters": ["那就好。"]},
        {"code": 401, "indent": 1, "parameters": ["这次我们走得快一点。"]},
        {"code": 126, "indent": 1, "parameters": [1, 0, 0, 1]},
        {"code": 101, "indent": 1, "parameters": ["", 0, 0, 2, ""]},
        {"code": 401, "indent": 1, "parameters": ["（得到了 万能钥匙 ×1）"]},
        {"code": 0, "indent": 1, "parameters": []},
        {"code": 412, "indent": 0, "parameters": []},
    ]

    lst[end:end] = block

    with io.open(MAP, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    print("序章已加二周目检测 + 奖励")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
