"""给「位面之外」的 5 个 F 级角色加「进度变化」的第二段。

条件：变量 13（已救回人数）>= 2。
用 111 条件分支内嵌在原 page 0 末尾。
"""

import io
import json

MAP = "data/Map010.json"
VAR = 13

# 事件名 -> [(说话人, 台词)]
EXTRA = {
    "水榕茜": [
        ("水榕茜", ["你带回来的人，越来越多了。"]),
        ("水榕茜", ["我看着他们进来的时候，都不太敢说话。"]),
        ("水榕茜", ["……我也很久没说话了。"]),
        ("薇薇", ["那现在说。"]),
        ("水榕茜", ["……嗯。"]),
    ],
    "汐之宫花见": [
        ("汐之宫花见", ["我试过给他带衣服。"]),
        ("汐之宫花见", ["带不进去。"]),
        ("汐之宫花见", ["他还在那儿。"]),
    ],
    "cardio": [
        ("cardio", ["我看了很多次。"]),
        ("cardio", ["每次都是同一个结局。"]),
        ("cardio", ["……这次不一样了。"]),
        ("cardio", ["别让我看第三遍。"]),
    ],
    "夜夜": [
        ("夜夜", ["我写到你和小冰打架。"]),
        ("夜夜", ["不知道怎么写下去。"]),
        ("夜夜", ["……你告诉我后来怎么样。"]),
    ],
    "のの": [
        ("のの", ["记到第几页了。"]),
        ("のの", ["不知道。"]),
        ("のの", ["纸不够了。"]),
    ],
}

FACES = {
    "水榕茜": ("AE86_5", 0),
    "汐之宫花见": ("AE86_5", 1),
    "cardio": ("AE86_5", 2),
    "夜夜": ("AE86_5", 4),
    "のの": ("AE86_5", 5),
    "薇薇": ("AE86_1", 0),
}


def main() -> int:
    with io.open(MAP, encoding="utf-8") as f:
        data = json.load(f)

    by_name = {e["name"]: e for e in data["events"] if e}
    ok = 0

    for name, steps in EXTRA.items():
        ev = by_name.get(name)
        if ev is None:
            print(f"  跳过 {name}")
            continue

        lst = ev["pages"][0]["list"]
        if any(c["code"] == 111 for c in lst):
            print(f"  {name}: 已有分支，跳过")
            continue

        end = next(i for i in range(len(lst) - 1, -1, -1) if lst[i]["code"] == 0)

        block = [{"code": 111, "indent": 0, "parameters": [1, VAR, 0, 1, 2]}]  # 变量 >= 2
        for who, lines in steps:
            face, fidx = FACES.get(who, ("", 0))
            block.append({"code": 101, "indent": 1,
                          "parameters": [face, fidx, 0, 2, who]})
            block += [{"code": 401, "indent": 1, "parameters": [l]} for l in lines]
        block.append({"code": 0, "indent": 1, "parameters": []})
        block.append({"code": 412, "indent": 0, "parameters": []})

        lst[end:end] = block
        ok += 1
        print(f"  {name}: +{len(block)} 条")

    with io.open(MAP, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    print(f"\n处理 {ok} 个")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
