"""把 RPG Maker MZ 安装目录里的 DLC 素材导入项目。

来源都是本机已购 DLC（随 RPG Maker MZ 安装分发，允许在 RPG Maker 游戏中
使用），全部加上 DF_ 前缀，避免覆盖项目里同名的 RTP 素材。

用法：python tools/import_dlc.py
"""

import shutil
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
DLC = Path(r"D:\other\rpgmakerMZ\RPG.Maker.MZ\dlc")
DF = DLC / "Dark Fantasy Resource Pack" / "samplemap"
EZ = DLC / "Essentials Set Z"
TRINITY = DLC / "MV Trinity Resource Pack"
REMIX = DLC / "MV and MZ Remix Music Pack"
COVER = DLC / "MZ Cover Art Characters Pack"

# (源目录, 项目内目标目录, 前缀, 只取这些文件；None = 全部, 只取 .png/.ogg)
JOBS = [
    (DF / "img" / "enemies", "img/enemies", "DF_", None),
    (DF / "img" / "characters", "img/characters", "DF_", None),
    (DF / "img" / "faces", "img/faces", "DF_", None),
    (DF / "img" / "sv_actors", "img/sv_actors", "DF_", None),
    # 只取 DF_ 开头的暗黑幻想专用 tileset，避免覆盖 RTP 同名图
    (DF / "img" / "tilesets", "img/tilesets", "", "DF_*"),
    (DF / "audio" / "bgm", "audio/bgm", "DF_", None),
    (DF / "audio" / "bgs", "audio/bgs", "DF_", None),
    (DF / "audio" / "me", "audio/me", "DF_", None),
    (DF / "audio" / "se", "audio/se", "DF_", None),
    (REMIX / "bgm", "audio/bgm", "RMX_", None),
    (COVER / "BGM", "audio/bgm", "CV_", None),
    (COVER / "characters", "img/characters", "CV_", None),
    (COVER / "faces", "img/faces", "CV_", None),
    (COVER / "sv_actors", "img/sv_actors", "CV_", None),
    (EZ / "characters", "img/characters", "EZ_", None),
    (EZ / "faces", "img/faces", "EZ_", None),
    (EZ / "enemies", "img/enemies", "EZ_", None),
    (EZ / "se", "audio/se", "EZ_", None),
]

KEEP_EXT = {".png", ".ogg", ".m4a", ".wav", ".webp"}


def main() -> int:
    total = 0
    for src, dst_rel, prefix, only in JOBS:
        if not src.exists():
            print(f"跳过（不存在）：{src}")
            continue
        dst = PROJECT / dst_rel
        dst.mkdir(parents=True, exist_ok=True)
        n = 0
        for f in sorted(src.iterdir()):
            if not f.is_file() or f.suffix.lower() not in KEEP_EXT:
                continue
            if only and not f.name.startswith(only.rstrip("*")):
                continue
            # DF_ 开头的 tileset 不重复加前缀
            name = f.name if f.name.startswith(prefix) and prefix else prefix + f.name
            target = dst / name
            shutil.copy2(f, target)
            n += 1
        total += n
        print(f"{dst_rel:16} +{n:4} 个（前缀 '{prefix}'）")
    print(f"\n共导入 {total} 个文件")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
