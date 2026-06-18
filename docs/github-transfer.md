# GitHub Transfer Guide

Status: maintainer packaging guidance.

Transfer only this package folder or a freshly built package tree.

Do not transfer:

- Raw transcripts.
- Local workstation paths.
- Private logs.
- Local app state.
- Credentials, account data, browser profiles, or proprietary project details.

Before import:

```bash
python scripts/audit_public_package.py --root .
python -B -m unittest discover -s tests -p '*test*.py' -v
```

Create a clean package tree from intended package files only:

```bash
python scripts/make_release_candidate.py --root . --out-dir /tmp/wsl-vhdx-compactor-rc --label rc1
```

Then audit the generated package tree printed by the command:

```bash
python scripts/audit_public_package.py --root /tmp/wsl-vhdx-compactor-rc/wsl-vhdx-compactor-rc1
```

```powershell
pwsh -NoProfile -Command '$null = [scriptblock]::Create((Get-Content -Raw "scripts/Test-WslVhdxCompactionReadiness.ps1")); $null = [scriptblock]::Create((Get-Content -Raw "scripts/Invoke-WslVhdxCompaction.ps1")); "PowerShell parse OK"'
```

Prefer importing from the clean package tree:

```bash
mkdir wsl-vhdx-compactor-public
cp -R /tmp/wsl-vhdx-compactor-rc/wsl-vhdx-compactor-rc1/. wsl-vhdx-compactor-public/
cd wsl-vhdx-compactor-public
git init
git add .
git commit -m "Initial WSL VHDX Compactor release"
```
