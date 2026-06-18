[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)]
  [string]$VhdPath,

  [string]$TranscriptPath,

  [switch]$DryRun,

  [switch]$RenderDiskPartScriptOnly,

  [switch]$SkipWarmWsl
)

function Test-IsAdministrator {
  $principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
  return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function New-DiskPartScript {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Path,
    [Parameter(Mandatory = $true)]
    [string]$OutFile
  )

  if ($Path.Contains('"')) {
    throw 'Stop: VHDX path contains a double quote character, which cannot be safely emitted into a DiskPart script.'
  }

  $quotedPath = '"' + $Path + '"'

  $scriptText = @"
select vdisk file=$quotedPath
attach vdisk readonly
compact vdisk
detach vdisk
exit
"@
  $scriptText | Set-Content -Path $OutFile -Encoding ASCII -ErrorAction Stop
}

function New-DiskPartScriptText {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Path
  )

  if ($Path.Contains('"')) {
    throw 'Stop: VHDX path contains a double quote character, which cannot be safely emitted into a DiskPart script.'
  }

  $quotedPath = '"' + $Path + '"'

@"
select vdisk file=$quotedPath
attach vdisk readonly
compact vdisk
detach vdisk
exit
"@
}

function New-DiskPartDetachScript {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Path,
    [Parameter(Mandatory = $true)]
    [string]$OutFile
  )

  if ($Path.Contains('"')) {
    throw 'Stop: VHDX path contains a double quote character, which cannot be safely emitted into a DiskPart script.'
  }

  $quotedPath = '"' + $Path + '"'

  $scriptText = @"
select vdisk file=$quotedPath
detach vdisk
exit
"@
  $scriptText | Set-Content -Path $OutFile -Encoding ASCII -ErrorAction Stop
}

$transcriptStarted = $false
$diskPartScript = $null
$detachRecoveryScript = $null
$diskPartExit = $null
$diskPartWasRun = $false
if ($TranscriptPath) {
  Start-Transcript -Path $TranscriptPath | Out-Null
  $transcriptStarted = $true
}

try {
  if ($RenderDiskPartScriptOnly) {
    New-DiskPartScriptText -Path $VhdPath
    return
  }

  $isAdmin = Test-IsAdministrator
  $is64Bit = [Environment]::Is64BitProcess
  Write-Host "IsAdmin=$isAdmin"
  Write-Host "Is64BitProcess=$is64Bit"
  Write-Host "PSHOME=$PSHOME"

  if (-not $isAdmin) {
    throw "Stop: this PowerShell session is not running as Administrator."
  }
  if (-not $is64Bit) {
    throw "Stop: this is not a 64-bit PowerShell process."
  }
  if (-not (Test-Path -LiteralPath $VhdPath -PathType Leaf)) {
    throw "Stop: VHDX not found: $VhdPath"
  }
  if (-not (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
    throw "Stop: wsl.exe was not found."
  }
  if (-not (Get-Command diskpart.exe -ErrorAction SilentlyContinue)) {
    throw "Stop: diskpart.exe was not found."
  }

  $before = (Get-Item -LiteralPath $VhdPath).Length
  $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
  $diskPartScript = Join-Path $env:TEMP "wsl-vhdx-compact-$stamp.txt"
  $detachRecoveryScript = Join-Path $env:TEMP "wsl-vhdx-detach-recovery-$stamp.txt"
  New-DiskPartScript -Path $VhdPath -OutFile $diskPartScript
  New-DiskPartDetachScript -Path $VhdPath -OutFile $detachRecoveryScript

  Write-Host "BeforeBytes=$before"
  Write-Host "DiskPartScript=$diskPartScript"
  Write-Host "DiskPart script:"
  Get-Content -Path $diskPartScript
  Write-Host "DetachRecoveryScript=$detachRecoveryScript"

  if ($DryRun) {
    Write-Host "DryRun=True"
    return
  }

  Write-Host "ShuttingDownWsl=True"
  wsl.exe --shutdown

  Write-Host "RunningDiskPart=True"
  $diskPartWasRun = $true
  diskpart.exe /s $diskPartScript
  $diskPartExit = $LASTEXITCODE
  Write-Host "DiskPartExitCode=$diskPartExit"
  if ($diskPartExit -ne 0) {
    throw "DiskPart failed with exit code $diskPartExit."
  }

  $afterItem = Get-Item -LiteralPath $VhdPath
  $after = $afterItem.Length
  $saved = $before - $after
  Write-Host "AfterBytes=$after"
  Write-Host "SavedBytes=$saved"
  Write-Host ("SavedGiB={0:N2}" -f ($saved / 1GB))

  if (-not $SkipWarmWsl) {
    Write-Host "WarmingWsl=True"
    wsl.exe -e true
  }

  [PSCustomObject]@{
    Ok = $true
    VhdPath = $VhdPath
    BeforeBytes = $before
    AfterBytes = $after
    SavedBytes = $saved
    DiskPartExitCode = $diskPartExit
  } | ConvertTo-Json -Depth 3
}
finally {
  if ($diskPartWasRun -and $diskPartExit -ne 0 -and $detachRecoveryScript) {
    Write-Host "DetachRecoveryAttempted=True"
    diskpart.exe /s $detachRecoveryScript
    $detachRecoveryExit = $LASTEXITCODE
    Write-Host "DetachRecoveryExitCode=$detachRecoveryExit"
  }
  if ($diskPartScript) {
    Remove-Item -LiteralPath $diskPartScript -Force -ErrorAction SilentlyContinue
  }
  if ($detachRecoveryScript) {
    Remove-Item -LiteralPath $detachRecoveryScript -Force -ErrorAction SilentlyContinue
  }
  if ($transcriptStarted) {
    Stop-Transcript | Out-Null
  }
}
