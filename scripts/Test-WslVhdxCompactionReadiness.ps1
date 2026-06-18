[CmdletBinding()]
param(
  [string]$SearchRoot = "$env:LOCALAPPDATA\Packages"
)

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
$is64Bit = [Environment]::Is64BitProcess
$wslCommand = Get-Command wsl.exe -ErrorAction SilentlyContinue
$diskpartCommand = Get-Command diskpart.exe -ErrorAction SilentlyContinue
$optimizeVhdCommand = Get-Command Optimize-VHD -ErrorAction SilentlyContinue
$mountVhdCommand = Get-Command Mount-VHD -ErrorAction SilentlyContinue
$dismountVhdCommand = Get-Command Dismount-VHD -ErrorAction SilentlyContinue

$vhdx = @()
if (Test-Path -LiteralPath $SearchRoot) {
  $vhdx = Get-ChildItem -LiteralPath $SearchRoot -Filter ext4.vhdx -Recurse -ErrorAction SilentlyContinue |
    ForEach-Object {
      [PSCustomObject]@{
        FullName = $_.FullName
        Length = $_.Length
        LastWriteTime = $_.LastWriteTime
      }
    }
}

[PSCustomObject]@{
  IsAdmin = $isAdmin
  Is64BitProcess = $is64Bit
  PSHome = $PSHOME
  WslExeAvailable = [bool]$wslCommand
  DiskPartAvailable = [bool]$diskpartCommand
  HyperVOptimizeVhdAvailable = [bool]$optimizeVhdCommand
  HyperVMountVhdAvailable = [bool]$mountVhdCommand
  HyperVDismountVhdAvailable = [bool]$dismountVhdCommand
  SearchRoot = $SearchRoot
  CandidateVhdx = $vhdx
} | ConvertTo-Json -Depth 5
