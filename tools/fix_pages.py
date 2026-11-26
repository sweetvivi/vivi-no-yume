"""扫描并修复地图事件页的失效条件。

问题：用 `selfSwitchA: true` 建出来的第 2 页事件，
conditions 里会同时有 `selfSwitchA: true` 和 `selfSwitchValid: false`。
MZ 只看 `selfSwitchValid`，所以那一页条件恒成立、永远优先于第 1 页。

修法：把 `selfSwitchA: true` 转成 `selfSwitchValid: true` + `selfSwitchCh: 'A'`。

用法：python tools/fix_pages.py [--dry]
"""

import glob
import io
import json
import sys

dry = "--dry" in sys.argv


def fix_map(path: str) -> int:
    with io.open(path, encoding="utf-8") as f:
        data = json.load(f)

    fixed = 0
    for ev in data.get("events") or []:
        if not ev:
            continue
        for pg in ev.get("pages") or []:
            cond = pg.get("conditions") or {}
            if cond.get("selfSwitchA") and not cond.get("selfSwitchValid"):
                cond["selfSwitchValid"] = True
                cond["selfSwitchCh"] = "A"
                cond.pop("selfSwitchA", None)
                fixed += 1
                print(f"  {path} ev{ev['id']} 「{ev.get('name','')}」 selfSwitchA 已修")
            # 顺手检查：条件字段存在但 Valid 为假的，提示但不自动改
            for key, valid in (
                ("switch1Id", "switch1Valid"),
                ("switch2Id", "switch2Valid"),
                ("variableId", "variableValid"),
                ("actorId", "actorValid"),
            ):
                if cond.get(valid) and key not in cond:
                    print(f"  ! {path} ev{ev['id']} {valid}=true 但缺 {key}")

    if fixed and not dry:
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    return fixed


def main() -> int:
    total = 0
    for path in sorted(glob.glob("data/Map[0-9][0-9][0-9].json")):
        total += fix_map(path)
    print(f"\n{'[dry] ' if dry else ''}共修复 {total} 处")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
