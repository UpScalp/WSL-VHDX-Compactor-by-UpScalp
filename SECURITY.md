# Security Policy

This tool can shut down WSL and compact a VHDX when run by an elevated Windows
operator. Treat that as a privileged local maintenance action.

Report security issues privately to the maintainers. Do not include raw
transcripts or unredacted local paths in public issues.

The tool should never:

- Delete files inside WSL.
- Guess a VHDX path for mutation.
- Run compaction without Administrator and 64-bit PowerShell checks.
- Publish local usernames, machine names, project paths, transcripts, or
  credentials.
