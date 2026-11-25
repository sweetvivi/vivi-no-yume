"""压缩 Skills.json 的空槽位，并同步所有引用。

reset_table 留下的空技能对象占着 11..150 这些 id，
导致新技能从 151 开始编号。这个脚本把它们收拢成连续 id。

保留 1（攻击）和 2（防御）在原位——引擎硬编码。
"""

import io
import json

DATA = "data"


def load(name):
    with io.open(f"{DATA}/{name}", encoding="utf-8") as f:
        return json.load(f)


def save(name, obj):
    with io.open(f"{DATA}/{name}", "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))


def main() -> int:
    skills = load("Skills.json")

    # 收集真实技能（名字非空），1 和 2 固定
    real = [e for e in skills if e and e.get("name", "").strip()]
    fixed = [e for e in real if e["id"] in (1, 2)]
    rest = [e for e in real if e["id"] not in (1, 2)]
    rest.sort(key=lambda e: e["id"])

    mapping = {e["id"]: e["id"] for e in fixed}
    next_id = 3
    for e in rest:
        mapping[e["id"]] = next_id
        next_id += 1

    # 重建数组
    new_skills = [None] * next_id
    for e in fixed:
        e["id"] = e["id"]
        new_skills[e["id"]] = e
    for e in rest:
        e["id"] = mapping[e["id"]]
        new_skills[e["id"]] = e

    changed = {old: new for old, new in mapping.items() if old != new}
    print(f"技能 {len(real)} 个，重编号 {len(changed)} 个")

    # 同步引用
    def remap_skill_list(lst, label):
        n = 0
        for item in lst:
            if item and "skillId" in item and item["skillId"] in changed:
                item["skillId"] = changed[item["skillId"]]
                n += 1
        if n:
            print(f"  {label}: 更新 {n} 处")

    classes = load("Classes.json")
    for c in classes:
        if c:
            remap_skill_list(c.get("learnings") or [], f"Classes[{c['id']}]")

    enemies = load("Enemies.json")
    for e in enemies:
        if e:
            remap_skill_list(e.get("actions") or [], f"Enemies[{e['id']}]")

    # 技能/物品里 code 43 = 学习技能
    def remap_effects(container, label):
        n = 0
        for eff in container.get("effects") or []:
            if eff and eff.get("code") == 43 and eff.get("dataId") in changed:
                eff["dataId"] = changed[eff["dataId"]]
                n += 1
        if n:
            print(f"  {label}: 更新 {n} 处")

    for e in new_skills:
        if e:
            remap_effects(e, f"Skills[{e['id']}]")

    items = load("Items.json")
    for i in items:
        if i:
            remap_effects(i, f"Items[{i['id']}]")

    save("Skills.json", new_skills)
    save("Classes.json", classes)
    save("Enemies.json", enemies)
    save("Items.json", items)

    print("\n最终技能表：")
    for e in new_skills:
        if e:
            print(f"  {e['id']:3} {e['name']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
