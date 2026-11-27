"""弱点系统：给不同敌人加属性弱点/抗性。

属性 ID（System.elements）：
  1 物理  2 火  3 冰  4 雷  5 水  6 土  7 风  8 光  9 暗

设计：
- 祝类（史莱姆/修女/鸦/群友/史莱姆王/母体/树）→ 光 ×1.6（净化系克制）
- 机械类（哨兵/无人机/蜈蚣/守卫机/猎杀者）→ 雷 ×1.6，水 ×0.6
- 数据类（超级AI/影子/雾怪/雕像）→ 雷 ×1.4，暗 ×0.7
- 宝箱怪 → 火 ×1.5（烧掉）
- Boss：修女/小冰 → 光 ×1.3（但仍很硬）；观者 → 全属性 ×1.0（无弱点）

trait: code 11 = 元素倍率, dataId = 元素 ID, value = 倍率
"""

import io
import json

# 敌人 id -> {元素: 倍率}
WEAK = {
    # 祝类
    1: {8: 1.6},    # 祝·史莱姆
    2: {8: 1.3},    # 祝祝修女（Boss，克制但不多）
    3: {8: 1.6},    # 祝·鸦
    10: {8: 1.6},   # 祝·群友
    11: {8: 1.6},   # 祝·史莱姆王
    15: {8: 1.5},   # 祝·母体
    20: {8: 1.6},   # 祝·树
    # 机械类
    4: {4: 1.6, 5: 0.6},    # 机械·哨兵
    6: {4: 1.5, 5: 0.6},    # 机械·猎杀者
    12: {4: 1.6, 5: 0.6},   # 安保无人机
    13: {4: 1.6, 5: 0.6},   # 机械蜈蚣
    14: {4: 1.5, 5: 0.6},   # 守卫机
    21: {4: 1.6, 5: 0.6},   # 侦察无人机
    # 数据类
    7: {4: 1.4, 9: 0.7},    # 超级AI
    19: {4: 1.4, 9: 0.7},   # 旧日雕像
    22: {4: 1.4, 9: 0.7},   # 影子
    17: {4: 1.4, 9: 0.7},   # 雾怪
    # 宝箱怪
    23: {2: 1.5},           # 宝箱怪
    # Boss
    8: {8: 1.3},            # 小冰
    9: {},                  # 观者无弱点
}

with io.open("data/Enemies.json", encoding="utf-8") as f:
    enemies = json.load(f)

for e in enemies:
    if not e:
        continue
    if e["id"] not in WEAK:
        continue
    table = WEAK[e["id"]]
    # 清掉旧的元素倍率 trait
    e["traits"] = [t for t in e.get("traits", []) if t.get("code") != 11]
    for el, rate in table.items():
        e["traits"].append({"code": 11, "dataId": el, "value": rate})
    if table:
        print(f"  {e['name']:<12} " + ", ".join(f"元素{k}×{v}" for k, v in table.items()))
    else:
        print(f"  {e['name']:<12} 无弱点")

with io.open("data/Enemies.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(enemies, f, ensure_ascii=False, separators=(",", ":"))

print("完成")
