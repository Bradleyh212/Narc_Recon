#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

DIST_APP="$ROOT_DIR/dist/Narc Recon.app"
INSTALL_DIR="/Applications"
DATA_DIR="$HOME/NarcReconData"
INSTALL_APP="$INSTALL_DIR/Narc Recon.app"
TEMP_APP="$INSTALL_DIR/.Narc Recon.app.tmp.$$"
BACKUP_APP="$INSTALL_DIR/.Narc Recon.app.backup.$$"

cleanup() {
	if [ -e "$TEMP_APP" ]; then
		sudo rm -rf "$TEMP_APP" || true
	fi

	if [ -e "$BACKUP_APP" ] && [ ! -e "$INSTALL_APP" ]; then
		sudo mv "$BACKUP_APP" "$INSTALL_APP" || true
	fi
}

trap cleanup EXIT

if [ "$(uname -s)" != "Darwin" ]; then
	echo "This installer is intended for macOS only." >&2
	exit 1
fi

if ! command -v pyinstaller >/dev/null 2>&1; then
	echo "pyinstaller was not found. Activate the project virtual environment and try again." >&2
	exit 1
fi

cd "$ROOT_DIR"

echo "Building Narc Recon with PyInstaller..."
pyinstaller --clean --noconfirm build/narc_recon.spec

if [ ! -d "$DIST_APP" ]; then
	echo "Expected built app was not found: $DIST_APP" >&2
	exit 1
fi

mkdir -p "$DATA_DIR"

echo "Administrator permission may be required to install to $INSTALL_DIR."
sudo -v

sudo rm -rf "$TEMP_APP"
sudo rm -rf "$BACKUP_APP"

echo "Copying app to temporary install path..."
sudo ditto "$DIST_APP" "$TEMP_APP"

if [ ! -d "$TEMP_APP" ]; then
	echo "Temporary app copy failed: $TEMP_APP" >&2
	exit 1
fi

if [ -e "$INSTALL_APP" ]; then
	echo "Replacing existing app at $INSTALL_APP..."
	sudo mv "$INSTALL_APP" "$BACKUP_APP"
fi

sudo mv "$TEMP_APP" "$INSTALL_APP"

if [ -e "$BACKUP_APP" ]; then
	sudo rm -rf "$BACKUP_APP"
fi

trap - EXIT

echo
echo "Narc Recon installed at:"
echo "  $INSTALL_APP"
echo
echo "Data directory:"
echo "  $DATA_DIR"
echo
echo "Recommended environment variables:"
echo "  export NARC_RECON_DB_PATH=\"$HOME/NarcReconData/narc_recon.db\""
echo "  export NARC_RECON_PEPPER=\"<set-a-real-secret>\""
echo
echo "Opening installed app..."
open "$INSTALL_APP"
