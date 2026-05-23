param(
	[string]$OutputPath
)

$ErrorActionPreference = "Stop"

function Resolve-RepoRoot {
	$scriptDir = Split-Path -Parent $PSCommandPath
	return (Resolve-Path (Join-Path $scriptDir "..")).Path
}

function Assert-FileExists {
	param(
		[string]$Path,
		[string]$Description
	)

	if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
		throw "$Description was not found: $Path"
	}
}

function Test-AppResourceExists {
	param(
		[string]$AppDir,
		[string]$RelativePath
	)

	$directPath = Join-Path $AppDir $RelativePath
	$internalPath = Join-Path (Join-Path $AppDir "_internal") $RelativePath
	return (Test-Path -LiteralPath $directPath -PathType Leaf) -or (Test-Path -LiteralPath $internalPath -PathType Leaf)
}

$rootDir = Resolve-RepoRoot
$distDir = Join-Path $rootDir "dist"
$sourceApp = Join-Path $distDir "Narc Recon"
$sourceExe = Join-Path $sourceApp "Narc Recon.exe"
$installer = Join-Path (Join-Path $rootDir "scripts") "install_windows.ps1"
$deploymentDoc = Join-Path (Join-Path $rootDir "docs") "windows-deployment.md"
$stagingDir = Join-Path $distDir "Narc_Recon_windows_release"

if (-not $OutputPath) {
	$OutputPath = Join-Path $distDir "Narc_Recon_windows_release.zip"
}

Write-Host "Packaging Narc Recon Windows release"
Write-Host "Repository root:"
Write-Host "  $rootDir"
Write-Host "Source app:"
Write-Host "  $sourceApp"

if (-not (Test-Path -LiteralPath $sourceApp -PathType Container)) {
	throw "Expected PyInstaller output folder was not found: $sourceApp"
}

Assert-FileExists -Path $sourceExe -Description "Narc Recon executable"
Assert-FileExists -Path $installer -Description "Windows installer script"
Assert-FileExists -Path $deploymentDoc -Description "Windows deployment documentation"

foreach ($resource in @("med_sheet.xlsx", "others\logo_nr.png", "others\logo_nr.ico")) {
	if (-not (Test-AppResourceExists -AppDir $sourceApp -RelativePath $resource)) {
		throw "Required bundled resource was not found in the PyInstaller output: $resource"
	}
}

$forbiddenNames = @("narc_recon.db", "narc_recon.db-wal", "narc_recon.db-shm", "config.env")
$forbiddenFiles = @(Get-ChildItem -LiteralPath $sourceApp -Recurse -File | Where-Object { $forbiddenNames -contains $_.Name })
if ($forbiddenFiles.Count -gt 0) {
	$joined = ($forbiddenFiles | ForEach-Object { $_.FullName }) -join [Environment]::NewLine
	throw "Refusing to package user data or local config from the app folder:$([Environment]::NewLine)$joined"
}

if (Test-Path -LiteralPath $stagingDir) {
	Remove-Item -LiteralPath $stagingDir -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $stagingDir | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $stagingDir "dist") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $stagingDir "docs") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $stagingDir "scripts") | Out-Null

Copy-Item -LiteralPath $sourceApp -Destination (Join-Path $stagingDir "dist") -Recurse
Copy-Item -LiteralPath $installer -Destination (Join-Path $stagingDir "install_windows.ps1")
Copy-Item -LiteralPath $installer -Destination (Join-Path (Join-Path $stagingDir "scripts") "install_windows.ps1")
Copy-Item -LiteralPath $deploymentDoc -Destination (Join-Path (Join-Path $stagingDir "docs") "windows-deployment.md")

if (Test-Path -LiteralPath $OutputPath) {
	Remove-Item -LiteralPath $OutputPath -Force
}

Compress-Archive -Path (Join-Path $stagingDir "*") -DestinationPath $OutputPath -Force
Remove-Item -LiteralPath $stagingDir -Recurse -Force

Write-Host "Windows release package created:"
Write-Host "  $OutputPath"
