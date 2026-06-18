from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import unittest


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PACKAGE_ROOT / "scripts" / "Invoke-WslVhdxCompaction.ps1"


class PowerShellRenderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.pwsh = shutil.which("pwsh")
        if not self.pwsh:
            self.skipTest("pwsh is not available")

    def _render(self, vhd_path: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                self.pwsh,
                "-NoProfile",
                "-File",
                str(SCRIPT),
                "-VhdPath",
                vhd_path,
                "-RenderDiskPartScriptOnly",
            ],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_render_quotes_vhdx_paths_with_spaces(self) -> None:
        vhd_path = r"C:\Users\Example User\AppData\Local\Packages\ExampleDistro\LocalState\ext4.vhdx"

        result = self._render(vhd_path)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f'select vdisk file="{vhd_path}"', result.stdout)
        self.assertIn("attach vdisk readonly", result.stdout)
        self.assertIn("compact vdisk", result.stdout)
        self.assertIn("detach vdisk", result.stdout)

    def test_render_rejects_embedded_double_quote(self) -> None:
        result = self._render(r'C:\Users\Example User\Bad"Path\ext4.vhdx')

        self.assertNotEqual(result.returncode, 0, result.stdout)
        combined_output = f"{result.stdout}\n{result.stderr}"
        compact_output = " ".join(combined_output.split())
        self.assertIn("double quote", combined_output)
        self.assertIn("cannot be", compact_output)
        self.assertIn("safely emitted", compact_output)


if __name__ == "__main__":
    unittest.main()
