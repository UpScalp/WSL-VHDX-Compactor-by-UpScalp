from __future__ import annotations

from pathlib import Path
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def _load_release_builder():
    script = PACKAGE_ROOT / "scripts" / "make_release_candidate.py"
    spec = importlib.util.spec_from_file_location("make_release_candidate", script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load release builder from {script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _copy_clean_package_root(destination: Path) -> Path:
    shutil.copytree(
        PACKAGE_ROOT,
        destination,
        ignore=shutil.ignore_patterns(
            "__pycache__",
            "*.pyc",
            "*.pyo",
            ".pytest_cache",
            ".ruff_cache",
            ".mypy_cache",
            "build",
            "dist",
            "*.egg-info",
            "*.dist-info",
        ),
    )
    return destination


def _normal_python_env() -> dict[str, str]:
    env = os.environ.copy()
    env.pop("PYTHONDONTWRITEBYTECODE", None)
    return env


class MakeReleaseCandidateTests(unittest.TestCase):
    def test_builds_clean_candidate_with_manifest_and_archive(self) -> None:
        builder = _load_release_builder()
        with tempfile.TemporaryDirectory() as temp_dir:
            clean_root = _copy_clean_package_root(Path(temp_dir) / "source")
            result = builder.create_release_candidate(clean_root, Path(temp_dir) / "out", label="unit")

            self.assertTrue(result["ok"], result)
            tree = Path(result["tree"])
            archive = Path(result["archive"])
            external_manifest = Path(result["manifest"])
            embedded_manifest = tree / "RELEASE_CANDIDATE_MANIFEST.json"

            self.assertTrue(tree.exists())
            self.assertTrue(archive.exists())
            self.assertTrue(external_manifest.exists())
            self.assertTrue(embedded_manifest.exists())

            manifest = json.loads(embedded_manifest.read_text(encoding="utf-8"))
            paths = {item["path"] for item in manifest["files"]}
            self.assertIn("README.md", paths)
            self.assertIn("scripts/Invoke-WslVhdxCompaction.ps1", paths)
            self.assertIn("scripts/make_release_candidate.py", paths)
            self.assertNotIn("RELEASE_CANDIDATE_MANIFEST.json", paths)
            self.assertEqual(result["source_file_count"], len(paths))

            with tarfile.open(archive, "r:gz") as tar:
                name_list = tar.getnames()
            names = set(name_list)
            self.assertEqual(len(name_list), len(names), "archive should not contain duplicate entries")
            self.assertIn("wsl-vhdx-compactor-unit/README.md", names)
            self.assertIn("wsl-vhdx-compactor-unit/RELEASE_CANDIDATE_MANIFEST.json", names)

    def test_cli_builder_does_not_create_source_pycache_when_run_normally(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            clean_root = _copy_clean_package_root(Path(temp_dir) / "source")
            result = subprocess.run(
                [
                    sys.executable,
                    str(clean_root / "scripts" / "make_release_candidate.py"),
                    "--root",
                    str(clean_root),
                    "--out-dir",
                    str(Path(temp_dir) / "out"),
                    "--label",
                    "normal-python",
                ],
                check=False,
                env=_normal_python_env(),
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse((clean_root / "scripts" / "__pycache__").exists())

    def test_refuses_to_overwrite_without_explicit_flag(self) -> None:
        builder = _load_release_builder()
        with tempfile.TemporaryDirectory() as temp_dir:
            clean_root = _copy_clean_package_root(Path(temp_dir) / "source")
            out_dir = Path(temp_dir) / "out"
            first = builder.create_release_candidate(clean_root, out_dir, label="repeat")
            second = builder.create_release_candidate(clean_root, out_dir, label="repeat")

            self.assertTrue(first["ok"], first)
            self.assertFalse(second["ok"], second)
            self.assertEqual(second["stage"], "output_exists")

    def test_public_audit_rejects_packaging_metadata(self) -> None:
        builder = _load_release_builder()
        audit = builder._load_audit_scan()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            metadata = root / "src" / "example_package.egg-info"
            metadata.mkdir(parents=True)
            (metadata / "PKG-INFO").write_text("Name: example-package\n", encoding="utf-8")

            result = audit(root)

            self.assertFalse(result["ok"], result)
            self.assertEqual(result["failures"][0]["kind"], "generated_artifact")
            self.assertEqual(result["failures"][0]["file"], "src/example_package.egg-info")


if __name__ == "__main__":
    unittest.main()
