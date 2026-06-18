# Privacy Guide

Transcripts and diagnostics can reveal:

- Windows usernames.
- Machine names.
- Distro package identifiers.
- Absolute local paths.
- Disk sizes and storage layout.
- Tooling names and process context.

Do not publish raw transcripts. Redact local paths, hostnames, usernames, and
any project-specific directory names before opening a public issue.

Public examples should use placeholders:

```text
C:\Users\<WindowsUser>\AppData\Local\Packages\<DistroPackage>\LocalState\ext4.vhdx
```

The package should not include private production logs, raw Codex transcripts,
credentials, browser profiles, account data, or proprietary project details.
