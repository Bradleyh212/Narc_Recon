# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules


ROOT_DIR = Path(SPECPATH).resolve().parent
SRC_DIR = ROOT_DIR / "src"


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
	icon=None,
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
