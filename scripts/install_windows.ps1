param(
	[switch]$Open,
	[switch]$NoOpen
)

$ErrorActionPreference = "Stop"

function Resolve-RepoRoot {
	$scriptDir = Split-Path -Parent $PSCommandPath
	$scriptDist = Join-Path (Join-Path $scriptDir "dist") "Narc Recon"
	if (Test-Path -LiteralPath $scriptDist -PathType Container) {
		return (Resolve-Path $scriptDir).Path
	}

	$parentDir = Join-Path $scriptDir ".."
	$parentDist = Join-Path (Join-Path $parentDir "dist") "Narc Recon"
	if (Test-Path -LiteralPath $parentDist -PathType Container) {
		return (Resolve-Path $parentDir).Path
	}

	return (Resolve-Path $parentDir).Path
}

function Get-NarcReconProcesses {
	return @(Get-Process -Name "Narc Recon" -ErrorAction SilentlyContinue)
}

function Stop-NarcReconIfRunning {
	$running = Get-NarcReconProcesses
	if ($running.Count -eq 0) {
		Write-Host "Narc Recon is not currently running."
		return
	}

	Write-Host "Narc Recon is currently running. Attempting graceful close..."
	foreach ($process in $running) {
		$null = $process.CloseMainWindow()
	}
	Start-Sleep -Seconds 3

	$remaining = Get-NarcReconProcesses
	if ($remaining.Count -eq 0) {
		Write-Host "Narc Recon closed before update."
		return
	}

	Write-Warning "Narc Recon is still running."
	$response = Read-Host "Type Y to stop Narc Recon and continue, or press Enter to cancel"
	if ($response -notin @("Y", "y")) {
		throw "Install cancelled. Close Narc Recon and rerun this script."
	}

	foreach ($process in $remaining) {
		Stop-Process -Id $process.Id -Force
	}
	Start-Sleep -Seconds 1

	if ((Get-NarcReconProcesses).Count -gt 0) {
		throw "Narc Recon is still running. Close it manually and rerun this script."
	}

	Write-Host "Narc Recon was stopped before update."
}

function New-DesktopShortcut {
	param(
		[string]$TargetPath,
		[string]$WorkingDirectory
	)

	try {
		$desktop = [Environment]::GetFolderPath("Desktop")
		$shortcutPath = Join-Path $desktop "Narc Recon.lnk"
		$shell = New-Object -ComObject WScript.Shell
		$shortcut = $shell.CreateShortcut($shortcutPath)
		$shortcut.TargetPath = $TargetPath
		$shortcut.WorkingDirectory = $WorkingDirectory
		$shortcut.IconLocation = $TargetPath
		$shortcut.Save()
		Write-Host "Desktop shortcut created/updated:"
		Write-Host "  $shortcutPath"
	} catch {
		Write-Warning "Could not create Desktop shortcut: $($_.Exception.Message)"
	}
}

function Assert-NoUserDataFiles {
	param(
		[string]$Folder,
		[string]$Purpose
	)

	if (-not (Test-Path -LiteralPath $Folder -PathType Container)) {
		return
	}

	$forbiddenNames = @("narc_recon.db", "narc_recon.db-wal", "narc_recon.db-shm", "config.env")
	$matches = @(Get-ChildItem -LiteralPath $Folder -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $forbiddenNames -contains $_.Name })
	if ($matches.Count -eq 0) {
		return
	}

	$joined = ($matches | ForEach-Object { $_.FullName }) -join [Environment]::NewLine
	throw "Refusing to $Purpose because user data or local config was found in the app folder:$([Environment]::NewLine)$joined$([Environment]::NewLine)Move these files into ${env:USERPROFILE}\NarcReconData or back them up, then rerun the installer."
}

function New-RandomSecret {
	$bytes = New-Object byte[] 32
	$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
	try {
		$rng.GetBytes($bytes)
	} finally {
		$rng.Dispose()
	}
	return [Convert]::ToBase64String($bytes)
}

function Write-Utf8NoBomFile {
	param(
		[string]$Path,
		[string]$Content
	)

	$encoding = New-Object System.Text.UTF8Encoding($false)
	[System.IO.File]::WriteAllText($Path, $Content, $encoding)
}

function New-ConfigFileIfMissing {
	param(
		[string]$ConfigPath,
		[string]$DbPath
	)

	if (Test-Path -LiteralPath $ConfigPath -PathType Leaf) {
		Write-Host "Config file already exists; leaving it unchanged:"
		Write-Host "  $ConfigPath"
		return
	}

	$createdAt = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss zzz")
	$pepper = New-RandomSecret
	$configContent = @(
		"# Narc Recon local configuration",
		"# Created by install_windows.ps1 on $createdAt",
		"NARC_RECON_DB_PATH=$DbPath",
		"NARC_RECON_PEPPER=$pepper",
		""
	) -join [Environment]::NewLine

	Write-Utf8NoBomFile -Path $ConfigPath -Content $configContent
	Write-Host "Config file created:"
	Write-Host "  $ConfigPath"
}

$rootDir = Resolve-RepoRoot
$sourceApp = Join-Path (Join-Path $rootDir "dist") "Narc Recon"
$sourceExe = Join-Path $sourceApp "Narc Recon.exe"

if (-not $env:LOCALAPPDATA) {
	throw "LOCALAPPDATA is not set."
}
if (-not $env:USERPROFILE) {
	throw "USERPROFILE is not set."
}

$installParent = Join-Path $env:LOCALAPPDATA "Programs"
$installDir = Join-Path $installParent "Narc Recon"
$installExe = Join-Path $installDir "Narc Recon.exe"
$dataDir = Join-Path $env:USERPROFILE "NarcReconData"
$backupDir = Join-Path $env:USERPROFILE "NarcReconBackups"
$configPath = Join-Path $dataDir "config.env"
$dbPath = Join-Path $dataDir "narc_recon.db"
$processId = [System.Diagnostics.Process]::GetCurrentProcess().Id
$tempInstallDir = Join-Path $installParent ".Narc Recon.tmp.$processId"
$rollbackDir = Join-Path $installParent ".Narc Recon.backup.$processId"
$shouldOpen = -not $NoOpen
if ($Open) {
	$shouldOpen = $true
}

Write-Host "Narc Recon Windows install/update"
Write-Host "Release root:"
Write-Host "  $rootDir"
Write-Host "Source build:"
Write-Host "  $sourceApp"

if (-not (Test-Path -LiteralPath $sourceExe -PathType Leaf)) {
	throw "Expected build output was not found: $sourceExe. Build with PyInstaller first."
}
Assert-NoUserDataFiles -Folder $sourceApp -Purpose "install from the source app folder"
Assert-NoUserDataFiles -Folder $installDir -Purpose "replace the existing app folder"

Stop-NarcReconIfRunning

New-Item -ItemType Directory -Force -Path $installParent | Out-Null
New-Item -ItemType Directory -Force -Path $dataDir | Out-Null
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
New-ConfigFileIfMissing -ConfigPath $configPath -DbPath $dbPath

if (Test-Path -LiteralPath $tempInstallDir) {
	Remove-Item -LiteralPath $tempInstallDir -Recurse -Force
}
if (Test-Path -LiteralPath $rollbackDir) {
	Remove-Item -LiteralPath $rollbackDir -Recurse -Force
}

try {
	Write-Host "Copying app to temporary install path..."
	New-Item -ItemType Directory -Force -Path $tempInstallDir | Out-Null
	Copy-Item -Path (Join-Path $sourceApp "*") -Destination $tempInstallDir -Recurse -Force

	$tempExe = Join-Path $tempInstallDir "Narc Recon.exe"
	if (-not (Test-Path -LiteralPath $tempExe -PathType Leaf)) {
		throw "Temporary app copy is missing Narc Recon.exe: $tempExe"
	}

	if (Test-Path -LiteralPath $installDir) {
		Write-Host "Replacing existing app folder:"
		Write-Host "  $installDir"
		Move-Item -LiteralPath $installDir -Destination $rollbackDir
	}

	Move-Item -LiteralPath $tempInstallDir -Destination $installDir

	if (Test-Path -LiteralPath $rollbackDir) {
		Remove-Item -LiteralPath $rollbackDir -Recurse -Force
	}
} catch {
	if ((-not (Test-Path -LiteralPath $installDir)) -and (Test-Path -LiteralPath $rollbackDir)) {
		Move-Item -LiteralPath $rollbackDir -Destination $installDir
	}
	if (Test-Path -LiteralPath $tempInstallDir) {
		Remove-Item -LiteralPath $tempInstallDir -Recurse -Force
	}
	throw
}

New-DesktopShortcut -TargetPath $installExe -WorkingDirectory $installDir

Write-Host ""
Write-Host "Narc Recon installed at:"
Write-Host "  $installDir"
Write-Host ""
Write-Host "Data directory, never deleted by this script:"
Write-Host "  $dataDir"
Write-Host ""
Write-Host "Backup directory, never deleted by this script:"
Write-Host "  $backupDir"
Write-Host ""
Write-Host "Recommended config file:"
Write-Host "  $configPath"
Write-Host ""
Write-Host "Default database path:"
Write-Host "  $dbPath"
Write-Host ""
Write-Host "The install script creates NARC_RECON_PEPPER once and leaves existing config.env files unchanged."
Write-Host "Do not bundle or copy real database files into the app install folder."

if ($shouldOpen) {
	Write-Host ""
	Write-Host "Opening Narc Recon..."
	Start-Process -FilePath $installExe
} else {
	Write-Host ""
	Write-Host "Launch skipped because -NoOpen was specified."
}
