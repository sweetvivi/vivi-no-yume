"""用 Wayward 模块化素材拼 41 个角色的行走图。

素材：D:\\other\\rpgmakerMZ\\about\\WMG Modular NPCs
授权：Wayward Martian Graphics，可商用、可改，需署名。
      （原始 TOS 禁止用于 AI 训练 / NFT，本项目只是拼图用于游戏，符合。）
输出：img/characters/AE86_C1.png ... AE86_C6.png（每张 576x576，8 个角色）

素材结构：每张 576x576，横向 4 个 block、纵向 2 个 block，
每个 block 是 144x288 = 3 列 x 4 行（每帧 48x72），行序为 下/左/右/上。
"""

import io
from pathlib import Path

from PIL import Image

PROJECT = Path(__file__).resolve().parent.parent
SRC = Path(r"D:\other\rpgmakerMZ\about\WMG Modular NPCs")
OUT = PROJECT / "img" / "characters"

FRAME_W, FRAME_H = 48, 72
BLOCK_W, BLOCK_H = FRAME_W * 3, FRAME_H * 4  # 144 x 288
SHEET_W, SHEET_H = 576, 576
BLOCKS_ACROSS, BLOCKS_DOWN = 4, 2
PER_SHEET = BLOCKS_ACROSS * BLOCKS_DOWN  # 8

ADULT = SRC / "Adult"
UNI = SRC / "Universal Pieces"

# ---------------------------------------------------------------------------
# 每个角色的外观：(底图文件, block序号, 下装, 上装, 后发, 刘海)
#   底图 block 0-7 是不同的肤色/体型变体
#   下装/上装/头发 传文件名（不含 .png），None 表示不用
# ---------------------------------------------------------------------------
F = "Adult/Femme"
M = "Adult/Masc"

# 等级顺序同 设定圣经：薇薇 → A → B → C → F
LOOKS = [
    # 薇薇（主角，法师，浅色）
    (F, 1, "F_Bottom-03", "F_Top-02", "F_Hair-04", "F_Bangs-01"),
    # 无所谓了啊（喂饱）
    (M, 2, "M_Bottom-01", "M_Top-03", "M_Hair-02", "M_Bangs-01"),
    # 皮老智（猫）
    (M, 5, "M_Bottom-04", "M_Top-01", "M_Hair-03", "M_Bangs-01"),
    # 狗妹（女装大佬）
    (M, 0, "F_Bottom-02", "F_Top-04", "F_Hair-02", "F_Bangs-01"),
    # 小小薇（姐姐，女仆感）
    (F, 2, "F_Bottom-05", "F_Top-01", "F_Hair-06", "F_Bangs-01"),
    # 阿文（女装大佬）
    (M, 3, "F_Bottom-01", "F_Top-03", "F_Hair-03", "F_Bangs-01"),
    # 花咲（女装大佬，便利店）
    (M, 4, "F_Bottom-04", "F_Top-05", "F_Hair-05", "F_Bangs-01"),
    # 天辽阔
    (M, 6, "M_Bottom-02", "M_Top-02", "M_Hair-01", "M_Bangs-01"),
    # 橙子
    (M, 1, "M_Bottom-03", "M_Top-04", "M_Hair-04", "M_Bangs-01"),
    # ⑨
    (M, 7, "M_Bottom-05", "M_Top-05", "M_Hair-02", "M_Bangs-01"),
    # 薰衣草（特殊女生）
    (F, 3, "F_Bottom-06", "F_Top-02", "F_Hair-03", "F_Bangs-01"),
    # 灵游
    (M, 2, "M_Bottom-01", "M_Top-01", "M_Hair-03", "M_Bangs-01"),
    # 久远崎彩祸（女装大佬）
    (M, 5, "F_Outfit-02", "F_Top-01", "F_Hair-01", "F_Bangs-01"),
    # 篮子
    (M, 0, "M_Bottom-04", "M_Top-03", "M_Hair-01", "M_Bangs-01"),
    # 码字姬（特殊女生，教师）
    (F, 4, "F_Bottom-02", "F_Top-03", "F_Hair-05", "F_Bangs-01"),
    # 青花灯影stella
    (M, 6, "M_Bottom-02", "M_Top-02", "M_Hair-04", "M_Bangs-01"),
    # 黄狐狸
    (M, 3, "M_Bottom-05", "M_Top-04", "M_Hair-02", "M_Bangs-01"),
    # 白柚
    (F, 5, "F_Bottom-01", "F_Top-04", "F_Hair-02", "F_Bangs-01"),
    # 鱼鱼
    (F, 0, "F_Bottom-03", "F_Top-05", "F_Hair-01", "F_Bangs-01"),
    # 小冰（群主）
    (M, 4, "M_Bottom-03", "M_Top-05", "M_Hair-03", "M_Bangs-01"),
    # 白羽（特殊，警察）
    (F, 6, "F_Outfit-01", "F_Top-02", "F_Hair-06", "F_Bangs-01"),
    # 白白（医生）
    (M, 1, "M_Bottom-01", "M_Top-05", "M_Hair-01", "M_Bangs-01"),
    # 阿百
    (M, 7, "M_Bottom-02", "M_Top-01", "M_Hair-04", "M_Bangs-01"),
    # 时间の文（文妹）
    (F, 2, "F_Bottom-04", "F_Top-01", "F_Hair-03", "F_Bangs-01"),
    # 喵神
    (F, 7, "F_Bottom-05", "F_Top-03", "F_Hair-04", "F_Bangs-01"),
    # 三七
    (M, 3, "M_Bottom-04", "M_Top-02", "M_Hair-02", "M_Bangs-01"),
    # 基世界人
    (M, 6, "M_Bottom-01", "M_Top-04", "M_Hair-01", "M_Bangs-01"),
    # 十三
    (F, 1, "F_Bottom-02", "F_Top-05", "F_Hair-02", "F_Bangs-01"),
    # 鬼狐
    (M, 4, "M_Bottom-03", "M_Top-03", "M_Hair-03", "M_Bangs-01"),
    # 咸鱼
    (M, 0, "M_Bottom-05", "M_Top-01", "M_Hair-04", "M_Bangs-01"),
    # 晚儿
    (F, 5, "F_Bottom-06", "F_Top-04", "F_Hair-05", "F_Bangs-01"),
    # 殇（粉色的祝）
    (F, 3, "F_Bottom-01", "F_Top-02", "F_Hair-03", "F_Bangs-01"),
    # 猹
    (M, 2, "M_Bottom-02", "M_Top-05", "M_Hair-02", "M_Bangs-01"),
    # 初雪
    (F, 4, "F_Bottom-04", "F_Top-01", "F_Hair-06", "F_Bangs-01"),
    # 星璇猫猫
    (F, 6, "F_Bottom-03", "F_Top-03", "F_Hair-04", "F_Bangs-01"),
    # 明月光
    (M, 7, "M_Bottom-01", "M_Top-02", "M_Hair-03", "M_Bangs-01"),
    # 水榕茜
    (F, 0, "F_Outfit-03", "F_Top-02", "F_Hair-01", "F_Bangs-01"),
    # 汐之宫花见
    (F, 2, "F_Outfit-04", "F_Top-05", "F_Hair-02", "F_Bangs-01"),
    # cardio
    (F, 7, "F_Bottom-05", "F_Top-04", "F_Hair-06", "F_Bangs-01"),
    # 夜夜
    (F, 5, "F_Outfit-05", "F_Top-03", "F_Hair-05", "F_Bangs-01"),
    # のの
    (F, 1, "F_Bottom-02", "F_Top-01", "F_Hair-04", "F_Bangs-01"),
]

BASE_FILES = {
    F: ADULT / "Wayward-Bases-Humans.png",
    M: ADULT / "Wayward-Bases-Humans.png",
}
PIECE_DIRS = {F: ADULT / "Femme", M: ADULT / "Masc"}


def load_piece(body: str, name: str | None) -> Image.Image | None:
    if not name:
        return None
    # 下装/上装跟 body，头发刘海在各自目录
    for d in (PIECE_DIRS.get(body), ADULT / "Femme", ADULT / "Masc", UNI):
        p = d / (f"Wayward-Modular-{name}.png")
        if p.exists():
            return Image.open(p).convert("RGBA")
    return None


def compose_block(body: str, skin: int, bottom: str, top: str, hair: str, bangs: str):
    """按行序拼一个 144x288 的 block。

    行序：0=下 1=左 2=右 3=上。
    朝向下的三行：底层 → 后发 → 下装 → 上装 → 刘海
    朝上的那行：  底层 → 刘海 → 下装 → 上装 → 后发
    """
    bx, by = skin % BLOCKS_ACROSS, skin // BLOCKS_ACROSS
    box = (bx * BLOCK_W, by * BLOCK_H, (bx + 1) * BLOCK_W, (by + 1) * BLOCK_H)

    base = Image.open(BASE_FILES[body]).convert("RGBA").crop(box)
    bot = load_piece(body, bottom)
    tp = load_piece(body, top)
    hr = load_piece(body, hair)
    bg = load_piece(body, bangs)

    bot = bot.crop(box) if bot else None
    tp = tp.crop(box) if tp else None
    hr = hr.crop(box) if hr else None
    bg = bg.crop(box) if bg else None

    out = Image.new("RGBA", (BLOCK_W, BLOCK_H), (0, 0, 0, 0))
    for row in range(4):
        strip = (0, row * FRAME_H, BLOCK_W, (row + 1) * FRAME_H)
        cell = base.crop(strip)
        # 朝上的那行后发在最上层（背面看到的是头发），其余三行刘海最上层
        order = [bg, bot, tp, hr] if row == 3 else [hr, bot, tp, bg]
        for layer in order:
            if layer is not None:
                cell.alpha_composite(layer.crop(strip))
        out.paste(cell, (0, row * FRAME_H))
    return out


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    if len(LOOKS) != 41:
        print(f"警告：LOOKS 有 {len(LOOKS)} 条，预期 41")

    mapping = []
    for sheet_no in range((len(LOOKS) + PER_SHEET - 1) // PER_SHEET):
        chunk = LOOKS[sheet_no * PER_SHEET : (sheet_no + 1) * PER_SHEET]
        sheet = Image.new("RGBA", (SHEET_W, SHEET_H), (0, 0, 0, 0))
        for slot, look in enumerate(chunk):
            body, skin, bottom, top, hair, bangs = look
            block = compose_block(body, skin, bottom, top, hair, bangs)
            bx = slot % BLOCKS_ACROSS
            by = slot // BLOCKS_ACROSS
            sheet.alpha_composite(block, (bx * BLOCK_W, by * BLOCK_H))
            mapping.append(
                {
                    "sheet": f"AE86_C{sheet_no + 1}",
                    "index": slot,
                    "actorOrder": sheet_no * PER_SHEET + slot,
                }
            )
        p = OUT / f"AE86_C{sheet_no + 1}.png"
        sheet.save(p, "PNG")
        print(f"写入 {p.name}  ({len(chunk)} 个角色)")

    print(f"\n共 {len(mapping)} 个角色行走图")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
