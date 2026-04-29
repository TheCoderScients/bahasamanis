import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "bahasamanis_cli.py"

def run_cli(*args):
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

def test_cli_versi():
    result = run_cli("versi")
    assert result.returncode == 0
    assert "Bahasa Manis" in result.stdout
    assert "0.2.0b1" in result.stdout

def test_cli_jalankan_example():
    result = run_cli("jalankan", "examples/output_demo.bm")
    assert result.returncode == 0
    assert result.stderr == ""
    assert "Demo Output Cepat" in result.stdout

def test_cli_ubah_outputs_python(tmp_path):
    out = tmp_path / "hello.py"
    result = run_cli("ubah", "examples/output_demo.bm", "-o", str(out))
    assert result.returncode == 0
    assert out.exists()
    assert "def __bm_main():" in out.read_text(encoding="utf-8")
