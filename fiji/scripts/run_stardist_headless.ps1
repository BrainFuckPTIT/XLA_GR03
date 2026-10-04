<#
.SYNOPSIS
Runs the published ImageJ/Fiji StarDist 2D command without the GUI.

.DESCRIPTION
The runner uses the same Maven artifact as the StarDist Fiji/ImageJ plugin.
It intentionally requires Java 8 because StarDist 0.3.0-scijava bundles the
TensorFlow 1.12 ImageJ runtime, whose loader is Java-8 based. The output path
must not already exist: SCIFIO refuses destructive overwrites.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $InputImage,
    [Parameter(Mandatory)] [string] $OutputLabel,
    [Parameter(Mandatory)] [string] $PluginEnvironment,
    [Parameter(Mandatory)] [string] $Java8Home,
    [ValidateRange(1, 999)] [int] $Tiles = 1
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$runner = Join-Path $PSScriptRoot "FijiStarDistRunner.java"
$modules = Join-Path $PluginEnvironment "modules"
$jars = Join-Path $PluginEnvironment "jars"
$patcher = Get-ChildItem $modules -Filter "ij1-patcher-*.jar" | Select-Object -First 1
$javac = Join-Path $Java8Home "bin\\javac.exe"
$java = Join-Path $Java8Home "bin\\java.exe"
$outputDirectory = Split-Path -Parent $OutputLabel

foreach ($path in @($runner, $modules, $jars, $javac, $java, $InputImage)) {
    if (-not (Test-Path -LiteralPath $path)) { throw "Required path not found: $path" }
}
if ($null -eq $patcher) { throw "No ij1-patcher JAR found under $modules" }
if (Test-Path -LiteralPath $OutputLabel) {
    throw "Refusing to overwrite existing label image: $OutputLabel"
}
if ($outputDirectory) { New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null }

$classPath = "$modules\\*;$jars\\*"
& $javac -proc:none -cp $classPath $runner
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $java "-javaagent:$($patcher.FullName)" -cp "$classPath;$PSScriptRoot" `
    FijiStarDistRunner $InputImage $OutputLabel $Tiles
exit $LASTEXITCODE
