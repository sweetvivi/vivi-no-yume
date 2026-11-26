"""检查 action_button 事件的 priorityType。

有图形的 action_button 事件如果 priorityType 是 0（below），
玩家按确定键不会触发它——这是个静默失败，很难在测试里发现。

用法：
  python tools/check_priority.py          # 只报告
  python tools/check_priority.py --fix    # 自动改成 same
"""

import glob
import io
import json
import sys

FIX = "--fix" in sys.argv


def main() -> int:
    findings = []
    for path in sorted(glob.glob("data/Map[0-9][0-9][0-9].json")):
        with io.open(path, encoding="utf-8") as f:
            data = json.load(f)
        for ev in data.get("events") or []:
            if not ev:
                continue
            changed = False
            for i, pg in enumerate(ev["pages"]):
                if pg.get("trigger") != 0:
                    continue
                if pg.get("priorityType") != 0:
                    continue
                img = pg.get("image") or {}
                if not img.get("characterName") and not img.get("tileId"):
                    continue  # 无图形的隐形触发，可能是故意的
                findings.append((path, ev["id"], ev.get("name", ""), i))
                if FIX:
                    pg["priorityType"] = 1
                    changed = True
            if changed:
                with io.open(path, "w", encoding="utf-8", newline="\n") as f:
                    json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    if not findings:
        print("没问题：所有带图形的 action_button 事件都是 same。")
        return 0

    print(f"发现 {len(findings)} 处：")
    for path, eid, name, pi in findings:
        mark = "已修" if FIX else ""
        print(f"  {path} ev{eid} 「{name}」 page {pi + 1} {mark}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
