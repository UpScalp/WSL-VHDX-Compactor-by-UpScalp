# WSL VHDX Compactor

WSL2 stores each Linux distro in a virtual disk file (`ext4.vhdx`) on your Windows drive. That file grows as you use WSL. However, it never shrinks when you delete files inside Linux. 

This tool reclaims that wasted space with a safe, dry-run-first workflow.

> **Not official Microsoft or WSL software.** Compaction does not always reclaim space — `SavedBytes` can be 0 even on a successful run.

We recommend using your Codex agent to help you apply this tool. Share the repo with them and ask them to guide you through the process.

---

## Quick Start

Open 64-bit Windows PowerShell as Administrator from the package root.

**1. Find candidate WSL VHDX files:**

```powershell
.\scripts\Test-WslVhdxCompactionReadiness.ps1
```

**2. Run a dry run against your VHDX path:**

```powershell
.\scripts\Invoke-WslVhdxCompaction.ps1 `
  -VhdPath 'C:\Users\<WindowsUser>\AppData\Local\Packages\<DistroPackage>\LocalState\ext4.vhdx' `
  -TranscriptPath "$env:TEMP\wsl-vhdx-compact-dry-run.txt" `
  -DryRun
```

**3. Inspect the DiskPart script without any WSL or disk action:**

```powershell
.\scripts\Invoke-WslVhdxCompaction.ps1 `
  -VhdPath 'C:\Users\<WindowsUser>\AppData\Local\Packages\<DistroPackage>\LocalState\ext4.vhdx' `
  -RenderDiskPartScriptOnly
```

**4. Run real compaction only after the dry run points to the correct VHDX:**

```powershell
.\scripts\Invoke-WslVhdxCompaction.ps1 `
  -VhdPath 'C:\Users\<WindowsUser>\AppData\Local\Packages\<DistroPackage>\LocalState\ext4.vhdx' `
  -TranscriptPath "$env:TEMP\wsl-vhdx-compact.txt"
```

Replace `<WindowsUser>` and `<DistroPackage>` with your own values. The typical path pattern is:

```
C:\Users\<WindowsUser>\AppData\Local\Packages\<DistroPackage>\LocalState\ext4.vhdx
```

---

## Safety Workflow

Follow these steps in order before running real compaction.

1. Run the readiness check.
2. Identify the intended distro VHDX.
3. Back up important data inside the distro.
4. Run the dry run.
5. Read the generated DiskPart script.
6. Confirm the path is the intended `ext4.vhdx`.
7. Close WSL terminals, Docker Desktop, editors, and other tools using WSL.
8. Run real compaction only after all checks above pass.

During a real compaction run, the script runs `wsl.exe --shutdown`, attaches the selected VHDX read-only, runs `compact vdisk`, detaches the VHDX, then starts WSL again with a lightweight warm-up command unless `-SkipWarmWsl` is used.

---

## Requirements

- Windows with WSL2
- 64-bit Windows PowerShell
- Administrator PowerShell (required for dry-run validation and real compaction)
- `wsl.exe` and `diskpart.exe` available on PATH
- A known WSL2 `ext4.vhdx` path — this tool requires you to identify it yourself
- A current backup of any important distro data

---

## What It Does

- Checks whether PowerShell is running as Administrator and as a 64-bit process
- Lists candidate WSL `ext4.vhdx` files under the Windows package directory
- Requires an explicit `-VhdPath` before any compaction flow can run
- Generates an ASCII DiskPart script with the VHDX path quoted
- Rejects VHDX paths containing embedded double quotes
- Supports a dry run before WSL shutdown or DiskPart execution
- Writes a PowerShell transcript when `-TranscriptPath` is supplied
- For a real run: shuts down WSL, attaches the VHDX read-only, runs `compact vdisk`, detaches the VHDX, reports byte counts, and warms WSL afterward unless `-SkipWarmWsl` is used
- Attempts a best-effort detach recovery command if DiskPart exits non-zero after the main DiskPart flow starts

---

## Expected Output

A successful dry run should show:

```
IsAdmin=True
Is64BitProcess=True
BeforeBytes=<number>
DryRun=True
```

It should also show a generated DiskPart script containing `select vdisk`, `attach vdisk readonly`, `compact vdisk`, `detach vdisk`, and `exit`.

A successful real compaction run should additionally show:

```
ShuttingDownWsl=True
RunningDiskPart=True
DiskPartExitCode=0
AfterBytes=<number>
SavedBytes=<number>
```

WSL starts afterward. 

**`SavedBytes` can be 0 even when DiskPart succeeds**. This means the run found no reclaimable blocks in the selected VHDX.

---

## Stop Conditions

Stop and read [failure modes](docs/failure-modes.md) if:

- The script reports `IsAdmin=False`
- The script reports `Is64BitProcess=False`
- The selected VHDX path is not the intended distro
- DiskPart cannot attach or detach the VHDX
- Detach recovery exits non-zero
- `AfterBytes` equals `BeforeBytes` and you expected reclaimed space

If detach recovery exits non-zero, **reboot Windows before retrying**. Do not keep rerunning compaction against a VHDX that may still be attached or held.

---

## Limitations

- Does not delete files inside WSL
- Does not select a VHDX automatically — you must supply `-VhdPath`
- Does not back up the VHDX or distro
- Does not guarantee a smaller file after compaction
- Has not been tested against every Windows, WSL, distro, filesystem, or storage configuration

---

## Privacy

Transcripts and diagnostics can include Windows usernames, machine names, distro package identifiers, absolute paths, disk sizes, and local tool context.

Do not publish raw transcripts. Redact local usernames, hostnames, absolute paths, project names, and storage details before opening a public issue.

See [privacy guidance](docs/privacy.md).

---

## Security

This tool can shut down WSL and run DiskPart when used for real compaction. Treat that as a privileged local maintenance action.

Report security issues privately to the maintainers. Do not include raw transcripts, unredacted local paths, credentials, cookies, browser profiles, or account data in public issues.

See [SECURITY.md](SECURITY.md).

---

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

The PowerShell render tests skip automatically when `pwsh` is unavailable. When `pwsh` is available, they check that paths containing spaces are quoted in the DiskPart script and paths containing embedded double quotes are rejected before any shutdown or disk action.

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution and public-safety rules.

---

## Repository Map

| File | Purpose |
|---|---|
| `scripts/Test-WslVhdxCompactionReadiness.ps1` | Readiness check and candidate VHDX diagnostics |
| `scripts/Invoke-WslVhdxCompaction.ps1` | Dry-run, render-only, and compaction workflow |
| `docs/failure-modes.md` | Common failures and what to do next |
| `docs/privacy.md` | Transcript and path-redaction guidance |
| `CHANGELOG.md` | Package changes |
| `CONTRIBUTING.md` | Contribution and public-safety rules |
| `SECURITY.md` | Security-reporting guidance |

---

## License

This tool uses an MIT license. See [LICENSE](LICENSE) for more details.
