from __future__ import annotations

from pathlib import Path
import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import shutil
import sys
import tarfile


PACKAGE_NAME = "wsl-vhdx-compactor"
PACKAGE_VERSION = "0.1.0"
sys.dont_write_bytecode = True

SKIP_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
}
SKIP_DIR_SUFFIXES = (".egg-info", ".dist-info")
SKIP_FILE_SUFFIXES = {".pyc", ".pyo"}
SKIP_FILES = {"RELEASE_CANDIDATE_MANIFEST.json"}


def _load_audit_scan():
    sibling = Path(__file__).resolve().with_name("audit_public_package.py")
    spec = importlib.util.spec_from_file_location("audit_public_package", sibling)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load audit helper from {sibling}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.scan


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _iter_source_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        rel_parts = path.relative_to(root).parts
        if any(part in SKIP_DIRS or part.endswith(SKIP_DIR_SUFFIXES) for part in rel_parts):
            continue
        if path.is_file() and path.name not in SKIP_FILES and path.suffix not in SKIP_FILE_SUFFIXES:
            files.append(path)
    return sorted(files, key=lambda candidate: candidate.relative_to(root).as_posix())


def create_release_candidate(
    root: Path,
    out_dir: Path,
    *,
    label: str | None = None,
    overwrite: bool = False,
) -> dict[str, object]:
    root = root.resolve()
    out_dir = out_dir.resolve()
    if not root.exists():
        raise FileNotFoundError(root)

    audit = _load_audit_scan()(root)
    if not audit["ok"]:
        return {"ok": False, "stage": "public_surface_audit", "audit": audit}

    safe_label = label or f"v{PACKAGE_VERSION}"
    candidate_name = f"{PACKAGE_NAME}-{safe_label}"
    tree = out_dir / candidate_name
    archive = out_dir / f"{candidate_name}.tar.gz"
    manifest_path = out_dir / f"{candidate_name}-manifest.json"
    if tree.exists() or archive.exists() or manifest_path.exists():
        if not overwrite:
            return {
                "ok": False,
                "stage": "output_exists",
                "tree": str(tree),
                "archive": str(archive),
                "manifest": str(manifest_path),
            }
        if tree.exists():
            shutil.rmtree(tree)
        archive.unlink(missing_ok=True)
        manifest_path.unlink(missing_ok=True)

    out_dir.mkdir(parents=True, exist_ok=True)
    tree.mkdir(parents=True)

    copied: list[dict[str, object]] = []
    for source in _iter_source_files(root):
        relative = source.relative_to(root)
        target = tree / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append(
            {
                "path": relative.as_posix(),
                "bytes": source.stat().st_size,
                "sha256": _sha256(source),
            }
        )

    manifest = {
        "package": PACKAGE_NAME,
        "version": PACKAGE_VERSION,
        "candidate": candidate_name,
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "source_file_count": len(copied),
        "files": copied,
    }
    (tree / "RELEASE_CANDIDATE_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    tree_audit = _load_audit_scan()(tree)
    if not tree_audit["ok"]:
        return {"ok": False, "stage": "candidate_tree_audit", "audit": tree_audit}

    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with tarfile.open(archive, "w:gz") as tar:
        for path in sorted(tree.rglob("*"), key=lambda candidate: candidate.relative_to(tree).as_posix()):
            if path.is_file():
                tar.add(path, arcname=f"{candidate_name}/{path.relative_to(tree).as_posix()}")

    return {
        "ok": True,
        "tree": str(tree),
        "archive": str(archive),
        "manifest": str(manifest_path),
        "archive_sha256": _sha256(archive),
        "source_file_count": len(copied),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="make_release_candidate.py")
    parser.add_argument("--root", default=".", help="Package root to copy from")
    parser.add_argument(
        "--out-dir",
        default="/tmp/wsl-vhdx-compactor-release-candidates",
        help="Output directory for clean tree and tarball",
    )
    parser.add_argument("--label", default=None, help="Release candidate label, for example rc1")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing candidate with the same name")
    args = parser.parse_args(argv)

    result = create_release_candidate(Path(args.root), Path(args.out_dir), label=args.label, overwrite=args.overwrite)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
