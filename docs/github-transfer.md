# GitHub Transfer Guide

Status: candidate. Do not publish until QA and release-owner approval.

Transfer only `public_packages/wsl-vhdx-compactor/`.

Do not transfer:

- The parent private repository.
- Raw transcripts.
- Local workstation paths.
- Production logs.
- Codex sessions or app state.
- Credentials, account data, browser profiles, or proprietary project details.

Before import:

```bash
python scripts/audit_public_package.py --root .
python -B -m unittest discover -s tests -p '*test*.py' -v
```

Create a clean release candidate from intended package files only:

```bash
python scripts/make_release_candidate.py --root . --out-dir /tmp/wsl-vhdx-compactor-rc --label rc1
```

Then audit the generated candidate tree printed by the command:

```bash
python scripts/audit_public_package.py --root /tmp/wsl-vhdx-compactor-rc/wsl-vhdx-compactor-rc1
```

```powershell
pwsh -NoProfile -Command '$null = [scriptblock]::Create((Get-Content -Raw "scripts/Test-WslVhdxCompactionReadiness.ps1")); $null = [scriptblock]::Create((Get-Content -Raw "scripts/Invoke-WslVhdxCompaction.ps1")); "PowerShell parse OK"'
```

Create a clean repository only after approval. Prefer importing from the clean
release candidate tree, not from the private parent worktree:

```bash
mkdir wsl-vhdx-compactor-public
cp -R /tmp/wsl-vhdx-compactor-rc/wsl-vhdx-compactor-rc1/. wsl-vhdx-compactor-public/
cd wsl-vhdx-compactor-public
git init
git add .
git commit -m "Initial WSL VHDX Compactor candidate"
```

Add a remote only after the release owner approves the exact destination.
