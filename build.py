"""Automated Build Script for MD Editor

Compiles the application into a standalone Windows executable (.exe) using PyInstaller.
"""

import os
import sys
import PyInstaller.__main__


def build_executable():
    """Run PyInstaller build for MD Editor."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(base_dir, "main.py")
    assets_dir = os.path.join(base_dir, "assets")
    icon_path = os.path.join(assets_dir, "icon.ico")

    args = [
        main_script,
        "--name=MD Editor",
        "--onefile",
        "--noconsole",
        "--clean",
    ]

    if os.path.exists(icon_path):
        args.append(f"--icon={icon_path}")

    if os.path.exists(assets_dir):
        # Use Windows path separator ; for --add-data
        args.append(f"--add-data={assets_dir};assets")

    print(f"Starting build for MD Editor with arguments:\n{args}\n")
    PyInstaller.__main__.run(args)

    exe_path = os.path.join(base_dir, "dist", "MD Editor.exe")
    if os.path.exists(exe_path):
        print(f"\n[BUILD SUCCESS] Executable berhasil dibuat di: {exe_path}")
    else:
        print(f"\n[BUILD COMPLETED] Cek folder dist/ untuk file executable.")


if __name__ == "__main__":
    build_executable()
