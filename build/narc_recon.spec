# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules


ROOT_DIR = Path(SPECPATH).resolve().parent
SRC_DIR = ROOT_DIR / "src"
WINDOWS_ICON = SRC_DIR / "others" / "logo_nr.ico"
MAC_ICON = SRC_DIR / "others" / "logo_nr.icns"
EXE_ICON = str(WINDOWS_ICON) if sys.platform == "win32" and WINDOWS_ICON.exists() else None
APP_ICON = str(MAC_ICON) if sys.platform == "darwin" and MAC_ICON.exists() else None


def collect_optional_submodules(package_name):
	try:
		return collect_submodules(package_name)
	except Exception:
		return [package_name]


hiddenimports = []
for package in (
	"customtkinter",
	"PIL",
	"pandas",
	"openpyxl",
	"reportlab",
	"prettytable",
	"argon2",
	"pytz",
):
	hiddenimports.extend(collect_optional_submodules(package))


a = Analysis(
	[str(SRC_DIR / "narc_recon.pyw")],
	pathex=[str(SRC_DIR)],
	binaries=[],
	datas=[
		(str(SRC_DIR / "med_sheet.xlsx"), "."),
		(str(SRC_DIR / "others" / "logo_nr.png"), "others"),
	],
	hiddenimports=hiddenimports,
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
	[],
	exclude_binaries=True,
	name="Narc Recon",
	debug=False,
	bootloader_ignore_signals=False,
	strip=False,
	upx=True,
	console=False,
	disable_windowed_traceback=False,
	argv_emulation=False,
	target_arch=None,
	codesign_identity=None,
	entitlements_file=None,
	icon=EXE_ICON,
)

coll = COLLECT(
	exe,
	a.binaries,
	a.datas,
	strip=False,
	upx=True,
	upx_exclude=[],
	name="Narc Recon",
)

if sys.platform == "darwin":
	app = BUNDLE(
		coll,
		name="Narc Recon.app",
		icon=APP_ICON,
		bundle_identifier=None,
	)
