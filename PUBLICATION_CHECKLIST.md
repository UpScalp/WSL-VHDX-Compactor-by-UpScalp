# Publication Checklist

Status: release-quality package candidate; accepted with publication
conditions; not published.

## Current Verification Snapshot

2026-06-17 release-quality validation passed for source tests, source public
audit, clean release-candidate build/audit, duplicate-free tar proof,
PowerShell parse/render-only proof, generated-artifact readback, and local
pre-VET. CODEX-QA accepted the package source/release-candidate quality with
publication conditions. A PO-approved elevated Windows dry run passed from a
real 64-bit Administrator PowerShell session.

Real compaction proof is not claimed. A real compaction run, WSL shutdown,
DiskPart execution, VHDX attach, VHDX compaction, disk mutation, publication,
repository creation, remote mutation, push, tag, upload, or GitHub release still
requires exact PO/release-owner approval.

Exact artifact paths, final SHA-256 hashes, commands, and command output must be
recorded outside the packaged artifact in the release tracker, QA handoff, or
release evidence note. Do not put the tarball's own final hash in this checklist
because editing this file changes the artifact hash.

After any README, checklist, or source edit, rebuild a clean release candidate
from this folder before any transfer, upload, tag, or release action.

This snapshot is not publication approval. PO/release-owner approval remains
open. Windows real-compaction proof remains open only if the release copy will
claim real operational compaction proof.

Required before public release:

- [x] Public-safe package name selected: `wsl-vhdx-compactor`.
- [x] README avoids private local project paths and raw transcript excerpts.
- [x] Script flow requires explicit VHDX path.
- [x] Script flow checks Administrator elevation and 64-bit PowerShell.
- [x] Script flow uses raw ASCII DiskPart script.
- [x] Script flow quotes the DiskPart VHDX path and rejects embedded quote characters.
- [x] Render-only proof covers a VHDX path containing spaces without shutting down WSL.
- [x] Package-local tests cover render-only quoting and embedded quote rejection when `pwsh` is available.
- [x] Script flow records before/after byte counts.
- [x] Script flow does not delete WSL files.
- [x] Clean release candidate builder creates an intended-file tree, tarball, and manifest.
- [x] Clean release candidate tree passes package public-surface audit.
- [x] Release candidate builder refuses overwrite unless explicitly requested.
- [x] Public audit rejects generated cache/build/metadata directories, editable-install metadata, and Python bytecode.
- [x] Clean release candidate builder excludes generated cache/build/metadata directories, editable-install metadata, and Python bytecode.
- [x] Clean release candidate builder does not create source `__pycache__` when run under ordinary Python.
- [x] Clean release candidate tarball has no duplicate members.
- [x] GitHub Actions builds and audits a clean release-candidate tree.
- [x] Script attempts best-effort detach recovery when DiskPart exits non-zero.
- [x] Windows dry-run smoke from a real 64-bit elevated PowerShell.
- [ ] Windows compaction smoke on a disposable or operator-approved VHDX, required only if claiming real operational compaction proof.
- [x] Package-local privacy scan.
- [x] CODEX-QA release-quality review accepted with publication conditions.
- [ ] Final release-owner privacy/public-copy check for any public issue, repository metadata, release notes, or transcript-derived text.
- [ ] PO/release-owner approval.
