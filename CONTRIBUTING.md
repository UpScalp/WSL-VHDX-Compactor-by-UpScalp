# Contributing

Use synthetic paths and public-safe examples only.

Do not include:

- Raw transcripts.
- Local usernames or machine names.
- Private project paths.
- Production logs.
- Credentials, cookies, tokens, or browser profiles.

Before proposing changes:

```powershell
pwsh -NoProfile -Command '$null = [scriptblock]::Create((Get-Content -Raw "scripts/Test-WslVhdxCompactionReadiness.ps1")); $null = [scriptblock]::Create((Get-Content -Raw "scripts/Invoke-WslVhdxCompaction.ps1")); "PowerShell parse OK"'
```

```bash
python scripts/audit_public_package.py --root .
```
