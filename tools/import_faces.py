"""把 素材/ 下的头像切成 RPG Maker MZ 的脸图（img/faces/）。

MZ 脸图规格：576x288，4 列 x 2 行，每格 144x144，一张放 8 个角色。

用法：python tools/import_faces.py
输出：img/faces/AE86_1.png ... AE86_6.png，以及 tools/face_map.json
"""

import json
import sys
from pathlib import Path

from PIL import Image

PROJECT = Path(__file__).resolve().parent.parent
SRC = PROJECT.parent / "素材"
OUT = PROJECT / "img" / "faces"

CELL = 144
COLS, ROWS = 4, 2
PER_SHEET = COLS * ROWS

# 按 设定圣经 的顺序排：主人公 → A → B → C → F
# (素材文件名, 角色名, 等级)
ORDER = [
    ("薇薇（管理员，故事的主人公）", "薇薇", "SSS7"),
    ("无所谓了啊（管理员）", "无所谓了啊", "A5"),
    ("皮老智", "皮老智", "A8"),
    ("狗妹", "狗妹", "A7"),
    ("小小薇", "小小薇", "A6"),
    ("小马宝莉衣上绣（阿文）", "阿文", "B10"),
    ("花が咲く", "花咲", "B9"),
    ("天辽阔", "天辽阔", "B9"),
    ("橙子", "橙子", "B8"),
    ("⑨", "⑨", "B8"),
    ("薰衣草", "薰衣草", "B8"),
    ("灵游", "灵游", "B7"),
    ("久远崎彩祸", "久远崎彩祸", "B7"),
    ("篮子", "篮子", "B7"),
    ("码字姬", "码字姬", "B6"),
    ("青花灯影stella", "青花灯影stella", "B6"),
    ("黄狐狸", "黄狐狸", "B5"),
    ("白袖", "白柚", "B4"),  # 素材里叫白袖，设定集叫白柚，同一人
    ("鱼鱼", "鱼鱼", "B3"),
    ("小冰（群主）", "小冰", "B3"),
    ("白羽（管理员）", "白羽", "B2"),
    ("白白", "白白", "B2"),
    ("阿百（管理员）", "阿百", "B2"),
    ("时间の文（管理员）", "时间の文", "B2"),
    ("喵神", "喵神", "B1"),
    ("三七", "三七", "B1"),
    ("基世界人", "基世界人", "C7"),
    ("十三", "十三", "C6"),
    ("喜欢涩涩的鬼狐", "鬼狐", "C5"),
    ("咸鱼", "咸鱼", "C5"),
    ("晚儿", "晚儿", "C4"),
    ("殇", "殇", "C4"),
    ("只偷保熟的瓜的猹", "猹", "C3"),
    ("初雪", "初雪", "C3"),
    ("星璇猫猫", "星璇猫猫", "C2"),
    ("明月光（管理员）", "明月光", "C2"),
    ("水榕茜", "水榕茜", "F10"),
    ("汐之宫花见", "汐之宫花见", "F7"),
    ("cardio", "cardio", "F6"),
    ("夜夜", "夜夜", "F5"),
    ("のの", "のの", "F5"),
]

EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def find_source(stem: str) -> Path | None:
    for ext in EXTS:
        for candidate in (SRC / f"{stem}{ext}", SRC / f"{stem}{ext.upper()}"):
            if candidate.exists():
                return candidate
    return None


def to_cell(path: Path) -> Image.Image:
    """读图 → 居中裁成正方形 → 缩放到 144x144 → RGB。"""
    img = Image.open(path).convert("RGB")
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))
    return img.resize((CELL, CELL), Image.LANCZOS)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    missing = [stem for stem, _, _ in ORDER if find_source(stem) is None]
    if missing:
        print("找不到这些素材：", missing, file=sys.stderr)
        return 1

    mapping = []
    for sheet_no in range((len(ORDER) + PER_SHEET - 1) // PER_SHEET):
        chunk = ORDER[sheet_no * PER_SHEET : (sheet_no + 1) * PER_SHEET]
        sheet = Image.new("RGB", (CELL * COLS, CELL * ROWS), (0, 0, 0))
        for slot, (stem, name, grade) in enumerate(chunk):
            src = find_source(stem)
            assert src is not None
            col, row = slot % COLS, slot // COLS
            sheet.paste(to_cell(src), (col * CELL, row * CELL))
            mapping.append(
                {
                    "name": name,
                    "grade": grade,
                    "faceName": f"AE86_{sheet_no + 1}",
                    "faceIndex": slot,
                    "source": src.name,
                }
            )
        out_path = OUT / f"AE86_{sheet_no + 1}.png"
        sheet.save(out_path, "PNG")
        print(f"写入 {out_path.name}  ({len(chunk)} 个角色)")

    map_path = Path(__file__).resolve().parent / "face_map.json"
    map_path.write_text(
        json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n共 {len(mapping)} 个角色，映射表 → {map_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
