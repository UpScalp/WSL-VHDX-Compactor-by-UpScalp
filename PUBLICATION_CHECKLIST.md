# Publication Checklist

Status: release-readiness checklist.

## Current Verification Snapshot

Before a public release, maintainers should verify source tests, package audit,
clean package build, duplicate-free archive contents, PowerShell parse/render
checks, generated-artifact readback, and an elevated Windows dry run from a
64-bit Administrator PowerShell session.

Do not claim real compaction proof unless a maintainer has performed a real
compaction run on a disposable test VHDX and recorded the result.

Record release artifact paths, final SHA-256 hashes, commands, and command
output in release notes or a maintainer release record. Do not put the archive's
own final hash in this checklist because editing this file changes the artifact
hash.

After any README, checklist, or source edit, rebuild a clean package tree before
any transfer, upload, tag, or release action.

Windows real-compaction proof is required only if the release copy claims real
operational compaction proof.

Required before public release:

- [x] Public-safe package name selected: `wsl-vhdx-compactor`.
- [x] README has a clear one-line identity, status, purpose, audience, quick start, safety workflow, docs map, support/security route, contribution route, and license link.
- [x] README uses public-reader language and avoids private local project paths or raw transcript excerpts.
- [x] README uses relative links for package-local docs and maintainer files.
- [x] README does not use unverified or broken external badges.
- [x] `LICENSE` is present.
- [x] `SECURITY.md` is present and linked from README.
- [x] `CONTRIBUTING.md` is present and linked from README.
- [x] Script flow requires explicit VHDX path.
- [x] Script flow checks Administrator elevation and 64-bit PowerShell.
- [x] Script flow uses raw ASCII DiskPart script.
- [x] Script flow quotes the DiskPart VHDX path and rejects embedded quote characters.
- [x] Render-only proof covers a VHDX path containing spaces without shutting down WSL.
- [x] Package-local tests cover render-only quoting and embedded quote rejection when `pwsh` is available.
- [x] Script flow records before/after byte counts.
- [x] Script flow does not delete WSL files.
- [x] Clean package builder creates an intended-file tree, tarball, and manifest.
- [x] Clean package tree passes package public-surface audit.
- [x] Package builder refuses overwrite unless explicitly requested.
- [x] Public audit rejects generated cache/build/metadata directories, editable-install metadata, and Python bytecode.
- [x] Clean package builder excludes generated cache/build/metadata directories, editable-install metadata, and Python bytecode.
- [x] Clean package builder does not create source `__pycache__` when run under ordinary Python.
- [x] Clean package tarball has no duplicate members.
- [x] GitHub Actions builds and audits a clean package tree.
- [x] Script attempts best-effort detach recovery when DiskPart exits non-zero.
- [x] Windows dry-run smoke from a real 64-bit elevated PowerShell.
- [ ] Windows compaction smoke on a disposable test VHDX, required only if claiming real operational compaction proof.
- [x] Package-local privacy scan.
- [ ] Final maintainer privacy/public-copy check for any public issue, repository metadata, release notes, or transcript-derived text.
- [ ] Final maintainer release review.
