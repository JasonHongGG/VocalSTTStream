# -*- mode: python ; coding: utf-8 -*-
import os
import site
from PyInstaller.utils.hooks import collect_data_files

# --- 自定義函式：暴力搜尋所有 NVIDIA 相關 DLL ---
def get_nvidia_dlls():
    dlls = []
    # 取得所有 site-packages 路徑
    packages = site.getsitepackages()
    for pkg in packages:
        nvidia_path = os.path.join(pkg, 'nvidia')
        if os.path.exists(nvidia_path):
            print(f"Found NVIDIA directory at: {nvidia_path}")
            # 遞迴搜尋該目錄下所有 .dll
            for root, dirs, files in os.walk(nvidia_path):
                for file in files:
                    if file.endswith(".dll"):
                        source_file = os.path.join(root, file)
                        # 將 DLL 放入 exe 同層目錄 ('.')
                        dlls.append((source_file, '.'))
    return dlls

# 執行搜尋並印出數量 (讓你在 build 過程能看到)
my_nvidia_binaries = get_nvidia_dlls()
print(f"Total NVIDIA DLLs found: {len(my_nvidia_binaries)}")
# ------------------------------------------------

a = Analysis(
    ['app_gui.py'],
    pathex=[],
    binaries=my_nvidia_binaries,  # <--- 使用我們搜到的 DLL 列表
    datas=collect_data_files('faster_whisper'),
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='VocalSTTStream',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    icon='./logo/dog.ico',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)