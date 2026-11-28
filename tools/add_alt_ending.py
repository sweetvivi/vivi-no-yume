"""第二个结局版本：救回人数不足 3 人时，好结局多一段孤独的结语。

插在观者胜利分支「回标题」之前。
变量 13 = 已救回人数。
"""

import io
import json

MAP = "data/Map009.json"

BLOCK = [
    {"code": 111, "indent": 1, "parameters": [1, 13, 0, 2, 2]},  # 变量13 <= 2
    {"code": 101, "indent": 2, "parameters": ["", 0, 0, 2, ""]},
    {"code": 401, "indent": 2, "parameters": ["（你赢了。）"]},
    {"code": 230, "indent": 2, "parameters": [40]},
    {"code": 101, "indent": 2, "parameters": ["", 0, 0, 2, ""]},
    {"code": 401, "indent": 2, "parameters": ["（但塔下还有很多人在等你。）"]},
    {"code": 401, "indent": 2, "parameters": ["（你没有带他们回来。）"]},
    {"code": 230, "indent": 2, "parameters": [40]},
    {"code": 101, "indent": 2, "parameters": ["", 0, 0, 2, ""]},
    {"code": 401, "indent": 2, "parameters": ["（群里的人数，还是那么多。）"]},
    {"code": 401, "indent": 2, "parameters": ["（只是不会再有人说话了。）"]},
    {"code": 0, "indent": 2, "parameters": []},
    {"code": 412, "indent": 1, "parameters": []},
]


def main() -> int:
    with io.open(MAP, encoding="utf-8") as f:
        data = json.load(f)

    ev = next(e for e in data["events"] if e and e.get("name") == "观者")
    lst = ev["pages"][0]["list"]

    if any(c["code"] == 111 and c["parameters"] and c["parameters"][0] == 1
           and c["parameters"][1] == 13 for c in lst):
        print("已存在，跳过")
        return 0

    # 找到 victory 分支里 localStorage 那行（索引 44 附近）
    idx = None
    for i, c in enumerate(lst):
        if c["code"] == 355 and "localStorage" in str(c["parameters"]):
            idx = i
            break
    if idx is None:
        print("没找到 localStorage 行")
        return 1

    lst[idx:idx] = BLOCK
    print(f"已插入 {len(BLOCK)} 条（位置 {idx}）")

    with io.open(MAP, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
