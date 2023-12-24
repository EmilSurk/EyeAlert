# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('/Users/emilsk/Desktop/alarm_sound.mp3', 'resources'), ('/Users/emilsk/PycharmProjects/pythonProject/dlib-models/shape_predictor_68_face_landmarks.dat', 'dlib-models')],
    hiddenimports=['dlib'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file='/Users/emilsk/Desktop/pythonProject/pythonProject/pythonProject.entitlements',
)
app = BUNDLE(
    exe,
    name='main.app',
    icon=None,
    bundle_identifier='emilsk.pythonProject',
)
