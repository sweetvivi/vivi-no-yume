"""打包：把 project1 的游戏文件 + NW.js 运行时复制到 dist，压缩成 Release 包。

用法：
    python tools/package.py 0.2

流程：
  1. 清空 D:\\other\\rpgmakerMZ\\dist\\v<ver>
  2. 复制游戏文件 + NW.js 运行时（排除开发工具）
  3. 压缩成 vivi-no-yume-v<ver>-win64.zip
"""

import shutil
import sys
import zipfile
from pathlib import Path

PROJECT = Path(r"D:\other\rpgmakerMZ\project\project1")
NW = Path(r"D:\other\rpgmakerMZ\RPG.Maker.MZ\nwjs-win")
DIST_ROOT = Path(r"D:\other\rpgmakerMZ\dist")

GAME_DIRS = ["css", "data", "fonts", "icon", "img", "audio", "js", "effects", "movies"]
GAME_FILES = ["index.html", "package.json"]
# 运行时里不需要的开发工具
NW_SKIP = {"nw.exe", "chromedriver.exe", "nwjc.exe", "credits.html", "notification_helper.exe"}


def main() -> int:
    if len(sys.argv) < 2:
        print("用法: python tools/package.py <version>   例如 0.2")
        return 1
    ver = sys.argv[1]

    out = DIST_ROOT / f"v{ver}"
    zip_path = DIST_ROOT / f"vivi-no-yume-v{ver}-win64.zip"

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    if zip_path.exists():
        zip_path.unlink()

    # 1. NW.js 运行时
    n = 0
    for item in NW.iterdir():
        if item.name in NW_SKIP:
            continue
        dst = out / item.name
        if item.is_dir():
            shutil.copytree(item, dst)
        else:
            shutil.copy2(item, dst)
        n += 1
    shutil.copy2(NW / "nw.exe", out / "Game.exe")
    print(f"运行时: {n} 项 + Game.exe")

    # 2. 游戏文件
    for d in GAME_DIRS:
        src = PROJECT / d
        if src.exists():
            shutil.copytree(src, out / d)
    for f in GAME_FILES:
        src = PROJECT / f
        if src.exists():
            shutil.copy2(src, out / f)
    print("游戏文件已复制")

    # 3. 压缩
    count = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in out.rglob("*"):
            if p.is_file():
                z.write(p, Path("VivisDream") / p.relative_to(out))
                count += 1

    size = zip_path.stat().st_size / 1024 / 1024
    print(f"\n压缩完成: {zip_path}")
    print(f"  文件数: {count}")
    print(f"  大小:   {size:.1f} MB")
    print(f"\n下一步：")
    print(f"  1. 创建 Release tag v{ver}")
    print(f"  2. 上传 {zip_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
