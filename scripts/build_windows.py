from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import textwrap
import zipfile
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
APP_NAME = "SnapRename"
APP_VERSION = "1.0.0"
FRONTEND_DIR = ROOT / "frontend"
DIST_HTML = FRONTEND_DIR / "dist" / "index.html"
ICON_PNG = ROOT / "biao.png"
BUILD_DIR = ROOT / "build"
PYI_DIST_DIR = BUILD_DIR / "pyinstaller-dist"
PYI_WORK_DIR = BUILD_DIR / "pyinstaller-work"
PYI_SPEC_DIR = BUILD_DIR / "pyinstaller-spec"
RELEASE_DIR = ROOT / "release"
ICON_ICO = BUILD_DIR / "icons" / f"{APP_NAME}.ico"


def npm_command() -> str:
    return "npm.cmd" if os.name == "nt" else "npm"


def run(cmd: list[str], cwd: Path | None = None):
    print(">", " ".join(str(part) for part in cmd))
    subprocess.run(cmd, cwd=cwd or ROOT, check=True)


def ensure_pyinstaller():
    if importlib.util.find_spec("PyInstaller"):
        return
    run([sys.executable, "-m", "pip", "install", "pyinstaller>=6.0"])


def build_frontend():
    if not FRONTEND_DIR.exists():
        return
    run([npm_command(), "run", "build"], cwd=FRONTEND_DIR)
    if not DIST_HTML.exists():
        raise FileNotFoundError(f"前端构建失败，未找到 {DIST_HTML}")


def build_icon():
    if not ICON_PNG.exists():
        raise FileNotFoundError(f"未找到图标文件: {ICON_PNG}")
    ICON_ICO.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(ICON_PNG) as img:
        img.save(ICON_ICO, sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])


def build_exe():
    if PYI_DIST_DIR.exists():
        shutil.rmtree(PYI_DIST_DIR)
    if PYI_WORK_DIR.exists():
        shutil.rmtree(PYI_WORK_DIR)
    PYI_SPEC_DIR.mkdir(parents=True, exist_ok=True)
    run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--clean",
            "--windowed",
            "--name",
            APP_NAME,
            "--icon",
            str(ICON_ICO),
            "--distpath",
            str(PYI_DIST_DIR),
            "--workpath",
            str(PYI_WORK_DIR),
            "--specpath",
            str(PYI_SPEC_DIR),
            "--add-data",
            f"{FRONTEND_DIR / 'dist'};frontend/dist",
            "--add-data",
            f"{ROOT / 'presets'};presets",
            "--collect-submodules",
            "webview",
            "--hidden-import",
            "openpyxl",
            str(ROOT / "main.py"),
        ]
    )


def make_portable_release() -> Path:
    app_dir = PYI_DIST_DIR / APP_NAME
    if not app_dir.exists():
        raise FileNotFoundError(f"未找到绿色版目录: {app_dir}")

    portable_dir = RELEASE_DIR / f"{APP_NAME}-{APP_VERSION}-portable"
    zip_path = RELEASE_DIR / f"{APP_NAME}-{APP_VERSION}-portable.zip"

    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    if zip_path.exists():
        zip_path.unlink()

    shutil.copytree(app_dir, portable_dir)
    (portable_dir / "portable.flag").write_text("", encoding="utf-8")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in portable_dir.rglob("*"):
            zf.write(path, path.relative_to(RELEASE_DIR))
    return portable_dir


def find_iscc() -> Path | None:
    candidates = [
        Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
        Path(r"C:\Program Files\Inno Setup 6\ISCC.exe"),
        Path.home() / "AppData" / "Local" / "Programs" / "Inno Setup 6" / "ISCC.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def write_inno_script(source_dir: Path) -> Path:
    installer_dir = BUILD_DIR / "installer"
    installer_dir.mkdir(parents=True, exist_ok=True)
    iss_path = installer_dir / f"{APP_NAME}.iss"
    app_exe = source_dir / f"{APP_NAME}.exe"
    output_base = f"{APP_NAME}-{APP_VERSION}-Setup"
    script = textwrap.dedent(
        f"""
        #define MyAppName "{APP_NAME}"
        #define MyAppVersion "{APP_VERSION}"
        #define MyAppPublisher "{APP_NAME}"
        #define MyAppExeName "{APP_NAME}.exe"
        #define MySourceDir "{source_dir}"
        #define MyIconFile "{ICON_ICO}"
        #define MyOutputDir "{RELEASE_DIR}"
        #define MyOutputBaseName "{output_base}"

        [Setup]
        AppId={{{{A2ED7D11-667D-4E30-8D52-A08F7D3858BA}}}}
        AppName={{#MyAppName}}
        AppVersion={{#MyAppVersion}}
        AppPublisher={{#MyAppPublisher}}
        DefaultDirName={{autopf}}\\{{#MyAppName}}
        DefaultGroupName={{#MyAppName}}
        DisableProgramGroupPage=yes
        OutputDir={{#MyOutputDir}}
        OutputBaseFilename={{#MyOutputBaseName}}
        SetupIconFile={{#MyIconFile}}
        WizardStyle=modern
        Compression=lzma
        SolidCompression=yes
        ArchitecturesInstallIn64BitMode=x64compatible
        UninstallDisplayIcon={{app}}\\{{#MyAppExeName}}

        [Languages]
        Name: "english"; MessagesFile: "compiler:Default.isl"

        [Tasks]
        Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加任务:"; Flags: unchecked

        [Files]
        Source: "{{#MySourceDir}}\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

        [Icons]
        Name: "{{autoprograms}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"
        Name: "{{autodesktop}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: desktopicon

        [Run]
        Filename: "{{app}}\\{{#MyAppExeName}}"; Description: "启动 {{#MyAppName}}"; Flags: nowait postinstall skipifsilent
        """
    ).strip()
    iss_path.write_text(script, encoding="utf-8")
    if not app_exe.exists():
        raise FileNotFoundError(f"未找到安装目标可执行文件: {app_exe}")
    return iss_path


def build_installer():
    source_dir = PYI_DIST_DIR / APP_NAME
    iss_path = write_inno_script(source_dir)
    iscc = find_iscc()
    if not iscc:
        print(f"Inno Setup 未安装，已生成脚本: {iss_path}")
        return
    run([str(iscc), str(iss_path)])


def main():
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    build_frontend()
    build_icon()
    ensure_pyinstaller()
    build_exe()
    portable_dir = make_portable_release()
    build_installer()
    print(f"绿色版目录: {portable_dir}")
    print(f"发布目录: {RELEASE_DIR}")


if __name__ == "__main__":
    main()
