"""按补充设定微调已有 NPC 台词。

- ⑨ 叫白柚「区」（谐音，不解释）
- 喂饱口头禅「乐」
- 白白提到头像（薇薇画的）
"""

import io
import json

MAP = "data/Map002.json"

# 事件名 -> [(页索引, 追加的 401 文本)]
APPEND = {
    "⑨": [(0, ["……对了。", "区呢。", "白柚那家伙，又不知道跑哪去了。"])],
    "喂饱": [(1, ["……乐。"])],
    "白白": [(0, ["……对了。", "你给我画的那张头像，我还留着。"])],
}


def main() -> int:
    with io.open(MAP, encoding="utf-8") as f:
        data = json.load(f)

    by_name = {e["name"]: e for e in data["events"] if e}

    for name, entries in APPEND.items():
        ev = by_name.get(name)
        if ev is None:
            print(f"  跳过 {name}（找不到）")
            continue
        for page_idx, lines in entries:
            lst = ev["pages"][page_idx]["list"]
            # 插到末尾 code 0 之前
            end = len(lst) - 1
            for i in range(len(lst) - 1, -1, -1):
                if lst[i]["code"] == 0:
                    end = i
                    break
            new = [{"code": 401, "indent": 0, "parameters": [l]} for l in lines]
            lst[end:end] = new
            print(f"  {name} page {page_idx}: +{len(lines)} 行")

    with io.open(MAP, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
