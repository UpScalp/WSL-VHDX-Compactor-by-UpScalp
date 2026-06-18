# Failure Modes

## Non-Admin PowerShell

Symptom:

- `IsAdmin=False`
- The script's explicit administrator check fails.
- DiskPart cannot attach or compact the VHDX

Fix:

- Open Windows PowerShell with **Run as Administrator**.
- Verify the script reports `IsAdmin=True` before compaction.

## 32-Bit PowerShell

Symptom:

- `Is64BitProcess=False`
- Shell path includes `SysWOW64`

Fix:

- Open the 64-bit PowerShell at
  `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`.

## Held VHDX

Symptom:

- DiskPart cannot attach or detach the VHDX.
- The file appears locked.
- The transcript shows `DetachRecoveryAttempted=True` after a non-zero DiskPart
  exit.

Fix:

- Close WSL terminals, Docker Desktop, editors, and tools using WSL.
- Run `wsl.exe --shutdown`.
- Retry only after the VHDX is no longer held.
- If detach recovery also exits non-zero, reboot Windows before trying again;
  do not keep rerunning compaction against a possibly attached VHDX.

## DiskPart Script Formatting

Symptom:

- DiskPart prints help instead of compacting.
- DiskPart exits non-zero before selecting or attaching the VHDX.

Fix:

- Use an ASCII script file.
- Confirm the script contains:

```text
select vdisk file="<absolute-ext4-vhdx-path>"
attach vdisk readonly
compact vdisk
detach vdisk
exit
```

If the VHDX path contains spaces, the generated DiskPart script must still use
the quoted `select vdisk` syntax. Use `-RenderDiskPartScriptOnly` to inspect the
generated DiskPart script without shutting down WSL or touching the VHDX.

If the main DiskPart run returns non-zero, the script attempts a separate
best-effort detach command and prints `DetachRecoveryExitCode`. A clean Windows
smoke test is still required before claiming real compaction readiness.

## Hyper-V Cmdlets Missing

Symptom:

- `Optimize-VHD`, `Mount-VHD`, or `Dismount-VHD` is unavailable.

Fix:

- Do not rely on Hyper-V fallback. Use DiskPart raw ASCII compaction.

## WSL Deletion Did Not Shrink Windows Disk Usage

Symptom:

- WSL `df` shows free space.
- Windows `C:\` free space does not improve.
- `ext4.vhdx` remains large.

Fix:

- Run Windows-side VHDX compaction after WSL shutdown.

## No Space Reclaimed

Symptom:

- DiskPart succeeds.
- `AfterBytes` equals `BeforeBytes`.

Fix:

- Confirm WSL deletion actually freed filesystem space with `df`.
- Confirm the selected VHDX is the intended distro.
- If both are true, there may be no reclaimable blocks in that VHDX.
