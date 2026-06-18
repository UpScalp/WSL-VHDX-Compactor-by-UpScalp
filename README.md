# WSL VHDX Compactor

Shrink a WSL2 distro's `ext4.vhdx` from Windows after deleting files inside
Linux.

WSL can show free space inside the Linux filesystem while Windows still shows a
large virtual disk file. This package helps you find the right WSL VHDX, inspect
the exact DiskPart commands that would run, and compact the selected VHDX with a
dry-run-first workflow.

This is not official Microsoft or WSL software. It does not delete Linux files,
does not choose a VHDX for you, and does not guarantee that compaction will
reclaim space.

## Status

`0.1.0`

This is a local maintenance utility. Use the dry run and render-only modes
before running real compaction, and keep a current backup of important distro
data.

## Why This Exists

After large files are removed inside WSL, the Linux filesystem can report more
free space, but the Windows-side `ext4.vhdx` file can remain large. Windows disk
usage improves only after the virtual disk is compacted.

This tool is for that Windows-side maintenance step.

## Who Should Use It

Use this package if you:

- use WSL2 on Windows;
- can identify the distro VHDX you want to compact;
- are comfortable running an elevated 64-bit PowerShell session;
- have backed up anything important inside the distro;
- want a dry run before any WSL shutdown or DiskPart action.

Do not use it if you are unsure which VHDX belongs to the distro you care about.

## What It Does

- Checks whether PowerShell is running as Administrator and as a 64-bit process.
- Lists candidate WSL `ext4.vhdx` files under the Windows package directory.
- Requires an explicit `-VhdPath` before any compaction flow can run.
- Generates an ASCII DiskPart script with the VHDX path quoted.
- Rejects VHDX paths containing embedded double quotes.
- Supports a dry run before WSL shutdown or DiskPart execution.
- Writes a PowerShell transcript when `-TranscriptPath` is supplied.
- For a real run, shuts down WSL, attaches the VHDX read-only, runs
  `compact vdisk`, detaches the VHDX, reports byte counts, and warms WSL
  afterward unless `-SkipWarmWsl` is used.
- Attempts a best-effort detach recovery command if DiskPart exits non-zero
  after the main DiskPart flow starts.

## What It Does Not Do

- It does not delete files inside WSL.
- It does not select a VHDX automatically for compaction.
- It does not run compaction without an explicit `-VhdPath`.
- It does not back up the VHDX or distro.
- It does not promise a smaller file after compaction.
- It does not prove every Windows, WSL, distro, filesystem, or storage setup is
  safe.

## Requirements

- Windows with WSL2.
- 64-bit Windows PowerShell.
- Administrator PowerShell for dry-run validation and real compaction.
- `wsl.exe` and `diskpart.exe` available on `PATH`.
- A known WSL2 `ext4.vhdx` path.
- A current backup for any important distro data.

The examples below use placeholders. Replace them with your own Windows user
and distro package path.

```text
C:\Users\<WindowsUser>\AppData\Local\Packages\<DistroPackage>\LocalState\ext4.vhdx
```

## Quick Start

Open **64-bit Windows PowerShell as Administrator** from the package root.

Find candidate WSL VHDX files:

```powershell
.\scripts\Test-WslVhdxCompactionReadiness.ps1
```

Run a dry run against the exact VHDX path:

```powershell
.\scripts\Invoke-WslVhdxCompaction.ps1 `
  -VhdPath 'C:\Users\<WindowsUser>\AppData\Local\Packages\<DistroPackage>\LocalState\ext4.vhdx' `
  -TranscriptPath "$env:TEMP\wsl-vhdx-compact-dry-run.txt" `
  -DryRun
```

Inspect the DiskPart script without WSL shutdown or disk action:

```powershell
.\scripts\Invoke-WslVhdxCompaction.ps1 `
  -VhdPath 'C:\Users\<WindowsUser>\AppData\Local\Packages\<DistroPackage>\LocalState\ext4.vhdx' `
  -RenderDiskPartScriptOnly
```

Run real compaction only after the dry run points to the correct VHDX:

```powershell
.\scripts\Invoke-WslVhdxCompaction.ps1 `
  -VhdPath 'C:\Users\<WindowsUser>\AppData\Local\Packages\<DistroPackage>\LocalState\ext4.vhdx' `
  -TranscriptPath "$env:TEMP\wsl-vhdx-compact.txt"
```

## Safety Workflow

1. Run the readiness check.
2. Identify the intended distro VHDX.
3. Back up important data inside the distro.
4. Run the dry run.
5. Read the generated DiskPart script.
6. Confirm the path is the intended `ext4.vhdx`.
7. Close WSL terminals, Docker Desktop, editors, and other tools using WSL.
8. Run real compaction only after the checks above pass.

During a real compaction run, the script runs `wsl.exe --shutdown`, attaches the
selected VHDX read-only, runs `compact vdisk`, detaches the VHDX, then starts
WSL again with a lightweight warm-up command unless disabled.

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

`SavedBytes` can be `0` even when DiskPart succeeds. That means this run did not
find reclaimable blocks in the selected VHDX.

## Stop Conditions

Stop and read [failure modes](docs/failure-modes.md) if:

- the script reports `IsAdmin=False`;
- the script reports `Is64BitProcess=False`;
- the selected VHDX path is not the intended distro;
- DiskPart cannot attach or detach the VHDX;
- detach recovery exits non-zero;
- `AfterBytes` is the same as `BeforeBytes` and you expected reclaimed space.

If detach recovery exits non-zero, reboot Windows before retrying. Do not keep
rerunning compaction against a VHDX that may still be attached or held.

## Privacy

Transcripts and diagnostics can include Windows usernames, machine names, distro
package identifiers, absolute paths, disk sizes, and local tool context.

Do not publish raw transcripts. Redact local usernames, hostnames, absolute
paths, project names, and storage details before opening a public issue.

See [privacy guidance](docs/privacy.md).

## Development

Run the package tests:

```bash
python -B -m unittest discover -s tests -p '*test*.py' -v
```

Audit the public package surface:

```bash
python -B scripts/audit_public_package.py --root .
```

Build and audit a clean package tree:

```bash
python -B scripts/make_release_candidate.py --root . --out-dir /tmp/wsl-vhdx-compactor-build --label local
python -B scripts/audit_public_package.py --root /tmp/wsl-vhdx-compactor-build/wsl-vhdx-compactor-local
```

The PowerShell render tests skip automatically when `pwsh` is unavailable. When
`pwsh` is available, they check that paths containing spaces are quoted in the
DiskPart script and paths containing embedded double quotes are rejected before
any shutdown or disk action.

## Repository Map

- [`scripts/Test-WslVhdxCompactionReadiness.ps1`](scripts/Test-WslVhdxCompactionReadiness.ps1): readiness and candidate-VHDX diagnostics.
- [`scripts/Invoke-WslVhdxCompaction.ps1`](scripts/Invoke-WslVhdxCompaction.ps1): dry-run, render-only, and compaction workflow.
- [`docs/failure-modes.md`](docs/failure-modes.md): common failures and what to do next.
- [`docs/privacy.md`](docs/privacy.md): transcript and path-redaction guidance.
- [`CHANGELOG.md`](CHANGELOG.md): package changes.
- [`CONTRIBUTING.md`](CONTRIBUTING.md): contribution and public-safety rules.
- [`SECURITY.md`](SECURITY.md): security-reporting guidance.

## Security

This tool can shut down WSL and run DiskPart when used for real compaction. Treat
that as a privileged local maintenance action.

Report security issues privately to the maintainers. Do not include raw
transcripts, unredacted local paths, credentials, cookies, browser profiles, or
account data in public issues.

See [SECURITY.md](SECURITY.md).

## Contributing

Contributions must use synthetic paths and public-safe examples only. Before
proposing changes, run the tests and package audit above.

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).
