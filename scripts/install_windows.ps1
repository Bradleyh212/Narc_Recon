param(
	[switch]$Open
)

$ErrorActionPreference = "Stop"

function Resolve-RepoRoot {
	$scriptDir = Split-Path -Parent $PSCommandPath
	return (Resolve-Path (Join-Path $scriptDir "..")).Path
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
$processId = [System.Diagnostics.Process]::GetCurrentProcess().Id
$tempInstallDir = Join-Path $installParent ".Narc Recon.tmp.$processId"
$rollbackDir = Join-Path $installParent ".Narc Recon.backup.$processId"

Write-Host "Narc Recon Windows install/update"
Write-Host "Repository root:"
Write-Host "  $rootDir"
Write-Host "Source build:"
Write-Host "  $sourceApp"

if (-not (Test-Path -LiteralPath $sourceExe -PathType Leaf)) {
	throw "Expected build output was not found: $sourceExe. Build with PyInstaller first."
}

Stop-NarcReconIfRunning

New-Item -ItemType Directory -Force -Path $installParent | Out-Null
New-Item -ItemType Directory -Force -Path $dataDir | Out-Null
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

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
Write-Host "  $(Join-Path $dataDir "config.env")"
Write-Host ""
Write-Host "Default database path:"
Write-Host "  $(Join-Path $dataDir "narc_recon.db")"
Write-Host ""
Write-Host "Set a stable NARC_RECON_PEPPER before creating real accounts."
Write-Host "Do not bundle or copy real database files into the app install folder."

if ($Open) {
	Write-Host ""
	Write-Host "Opening Narc Recon..."
	Start-Process -FilePath $installExe
}
