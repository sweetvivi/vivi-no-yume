"""把「薇薇失散」的两个事件用全局开关 30 联动起来。

- 事件 17（数据流·冲散）：末尾开开关 30
- 事件 18（薇薇·找到了）：条件改成开关 30，末尾关开关 30
"""

import io
import json

MAP = "data/Map007.json"
SW = 30


def cond_switch(sw):
    return {
        "actorId": 1, "actorValid": False,
        "itemId": 1, "itemValid": False,
        "selfSwitchCh": "A", "selfSwitchValid": False,
        "switch1Id": sw, "switch1Valid": True,
        "switch2Id": 1, "switch2Valid": False,
        "variableId": 1, "variableValid": False, "variableValue": 0,
    }


with io.open(MAP, encoding="utf-8") as f:
    data = json.load(f)

# 1. 数据流事件：末尾加开开关
ev1 = next(e for e in data["events"] if e and e.get("name") == "数据流·冲散")
lst = ev1["pages"][0]["list"]
if not any(c["code"] == 121 and c["parameters"][0] == SW for c in lst):
    end = next(i for i in range(len(lst) - 1, -1, -1) if lst[i]["code"] == 0)
    lst.insert(end, {"code": 121, "indent": 0, "parameters": [SW, SW, 0]})
    print("数据流事件：已加开开关", SW)

# 2. 找到了事件：改条件 + 末尾关开关
ev2 = next(e for e in data["events"] if e and e.get("name") == "薇薇·找到了")
ev2["pages"][0]["conditions"] = cond_switch(SW)
lst2 = ev2["pages"][0]["list"]
if not any(c["code"] == 121 and c["parameters"][0] == SW for c in lst2):
    end = next(i for i in range(len(lst2) - 1, -1, -1) if lst2[i]["code"] == 0)
    lst2.insert(end, {"code": 121, "indent": 0, "parameters": [SW, SW, 1]})
    print("找到了事件：条件改为开关", SW, "，末尾关开关")

with io.open(MAP, "w", encoding="utf-8", newline="\n") as f:
    json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

# 3. 命名开关
with io.open("data/System.json", encoding="utf-8") as f:
    sys_data = json.load(f)
sw = sys_data["switches"]
while len(sw) <= SW:
    sw.append("")
sw[SW] = "薇薇失散中"
with io.open("data/System.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(sys_data, f, ensure_ascii=False, separators=(",", ":"))

print("完成")
