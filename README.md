# WSL VHDX Compactor

Windows-side tooling for diagnosing and compacting oversized WSL2
`ext4.vhdx` files.

WSL can free space inside Linux before Windows recovers the same space from the
virtual disk file. A common pattern looks like this:

- Large files are deleted inside WSL.
- `df` inside WSL shows the Linux filesystem has more free space.
- Windows still shows low free space because the distro's `ext4.vhdx` file is
  still large.

This package helps with the Windows-side compaction step for that VHDX file.

This is not official Microsoft, OpenAI, or WSL software. It does not delete
files inside WSL, and it does not guarantee that compaction will reclaim space.

## Status

This package is a release-quality candidate accepted with publication
conditions. Source checks, clean release-candidate checks, quote-safe DiskPart
rendering, and an elevated Windows dry run have passed. Real compaction has not
been claimed as package evidence. Publication, repository creation, tagging,
uploading, or release approval remains controlled by the release owner.

## What It Does

- Reports whether the current PowerShell session is elevated and 64-bit.
- Searches for candidate WSL `ext4.vhdx` files under the Windows package
  directory.
- Requires an explicit VHDX path before any compaction flow can run.
- Generates an ASCII DiskPart script with the VHDX path quoted.
- Rejects VHDX paths containing embedded double quotes.
- Supports dry-run output before WSL shutdown or DiskPart execution.
- Can write a PowerShell transcript when `-TranscriptPath` is supplied.
- For a real compaction run, shuts down WSL, attaches the VHDX read-only,
  runs `compact vdisk`, detaches the VHDX, reports byte counts, and warms WSL
  afterward unless `-SkipWarmWsl` is used.
- Attempts a best-effort detach recovery command if DiskPart exits non-zero
  after the main DiskPart flow starts.

## What It Does Not Do

- It does not delete Linux files.
- It does not choose a VHDX automatically for compaction.
- It does not run without an explicit `-VhdPath`.
- It does not back up the VHDX or the WSL distro.
- It does not promise a smaller file after compaction.
- It does not prove that every Windows, WSL, distro, filesystem, or storage
  configuration is safe.

## Safety Model

Use this tool only from a 64-bit Windows PowerShell session opened with
**Run as Administrator**.

The compaction flow is deliberately explicit:

1. Run the readiness check and identify the intended distro VHDX.
2. Run a dry run against the exact VHDX path.
3. Review the generated DiskPart script and transcript.
4. Make sure important WSL data is backed up.
5. Run real compaction only when the selected VHDX path is correct.

During a real compaction run, the script runs `wsl.exe --shutdown`, attaches the
selected VHDX read-only, runs `compact vdisk`, detaches the VHDX, and then
starts WSL again with a lightweight warm-up command unless disabled.

## Quick Start

Open 64-bit Windows PowerShell as Administrator.

From the package root, find candidate WSL VHDX files:

```powershell
.\scripts\Test-WslVhdxCompactionReadiness.ps1
```

Dry run the exact VHDX path:

```powershell
.\scripts\Invoke-WslVhdxCompaction.ps1 `
  -VhdPath 'C:\Users\<WindowsUser>\AppData\Local\Packages\<DistroPackage>\LocalState\ext4.vhdx' `
  -TranscriptPath "$env:TEMP\wsl-vhdx-compact-dry-run.txt" `
  -DryRun
```

Inspect the DiskPart script without shutdown or disk action:

```powershell
.\scripts\Invoke-WslVhdxCompaction.ps1 `
  -VhdPath 'C:\Users\<WindowsUser>\AppData\Local\Packages\<DistroPackage>\LocalState\ext4.vhdx' `
  -RenderDiskPartScriptOnly
```

Run compaction only after the dry run points to the correct VHDX:

```powershell
.\scripts\Invoke-WslVhdxCompaction.ps1 `
  -VhdPath 'C:\Users\<WindowsUser>\AppData\Local\Packages\<DistroPackage>\LocalState\ext4.vhdx' `
  -TranscriptPath "$env:TEMP\wsl-vhdx-compact.txt"
```

## Expected Output

A successful dry run should show:

- `IsAdmin=True`
- `Is64BitProcess=True`
- `BeforeBytes=<number>`
- `DryRun=True`
- a generated DiskPart script containing `select vdisk`, `attach vdisk
  readonly`, `compact vdisk`, `detach vdisk`, and `exit`

A successful real compaction run should additionally show:

- `ShuttingDownWsl=True`
- `RunningDiskPart=True`
- `DiskPartExitCode=0`
- `AfterBytes=<number>`
- `SavedBytes=<number>`
- WSL starts afterward

`SavedBytes` can be `0` even when DiskPart succeeds. That means this run did
not find reclaimable blocks in the selected VHDX.

## When To Stop

Stop and check `docs/failure-modes.md` if:

- the script reports `IsAdmin=False`
- the script reports `Is64BitProcess=False`
- the selected VHDX path is not the intended distro
- DiskPart cannot attach or detach the VHDX
- detach recovery exits non-zero
- `AfterBytes` is the same as `BeforeBytes` and you expected reclaimed space

If detach recovery exits non-zero, reboot Windows before retrying. Do not keep
rerunning compaction against a VHDX that may still be attached or held.

## Privacy

Transcripts and diagnostics can include Windows usernames, machine names, distro
package identifiers, absolute paths, disk sizes, and local tool context.

Do not publish raw transcripts. Redact local usernames, hostnames, absolute
paths, project names, and storage details before opening a public issue.

See `docs/privacy.md`.

## Release Candidate Checks

Before public transfer or upload, rebuild a clean candidate from the package
folder and audit that generated tree:

```bash
python -B -m unittest discover -s tests -p '*test*.py' -v
python scripts/make_release_candidate.py --root . --out-dir /tmp/wsl-vhdx-compactor-rc --label rc1
python scripts/audit_public_package.py --root /tmp/wsl-vhdx-compactor-rc/wsl-vhdx-compactor-rc1
```

The PowerShell render tests skip automatically when `pwsh` is unavailable. When
`pwsh` is available, they check that paths containing spaces are quoted in the
DiskPart script and paths containing embedded double quotes are rejected before
any shutdown or disk action.

Do not publish directly from a dirty parent worktree. Transfer only this package
folder or a freshly rebuilt clean release candidate.

## More Documentation

- Failure modes: `docs/failure-modes.md`
- Privacy guidance: `docs/privacy.md`
- GitHub transfer guide: `docs/github-transfer.md`
- Publication checklist: `PUBLICATION_CHECKLIST.md`
- Changelog: `CHANGELOG.md`
