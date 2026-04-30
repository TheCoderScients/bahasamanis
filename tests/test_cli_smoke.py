import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "bahasamanis_cli.py"

def run_cli(*args, cwd=ROOT):
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )

def test_cli_versi():
    result = run_cli("versi")
    assert result.returncode == 0
    assert "Bahasa Manis" in result.stdout
    assert "0.2.0b1" in result.stdout

def test_cli_diagnosa():
    result = run_cli("diagnosa")
    assert result.returncode == 0
    assert "Bahasa Manis" in result.stdout
    assert "Perintah bm" in result.stdout
    assert "Modul CLI" in result.stdout

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

def test_cli_jalankan_returns_error_code_for_runtime_error(tmp_path):
    src = tmp_path / "gagal.bm"
    src.write_text('lempar "meledak"\n', encoding="utf-8")
    result = run_cli("jalankan", str(src))
    assert result.returncode == 1
    assert "meledak" in result.stderr

def test_cli_buat_cek_tes_project(tmp_path):
    app = tmp_path / "app_manis"
    result = run_cli("buat", str(app))
    assert result.returncode == 0
    assert (app / "bm.toml").exists()
    assert (app / "src" / "utama.bm").exists()
    assert (app / "tests" / "tes_utama.bm").exists()

    info = run_cli("info", cwd=app)
    assert info.returncode == 0
    assert "app_manis" in info.stdout
    assert "src/utama.bm" in info.stdout

    run_default = run_cli("jalankan", cwd=app)
    assert run_default.returncode == 0
    assert "app_manis siap jalan" in run_default.stdout

    check = run_cli("cek", cwd=app)
    assert check.returncode == 0
    assert "file BM valid" in check.stdout

    test = run_cli("tes", cwd=app)
    assert test.returncode == 0
    assert "test BM lulus" in test.stdout

    nested_info = run_cli("info", cwd=app / "src")
    assert nested_info.returncode == 0
    assert str(app) in nested_info.stdout

def test_cli_cek_reports_syntax_error(tmp_path):
    bad = tmp_path / "bad.bm"
    bad.write_text('jika benar\n    cetak "lupa akhir"\n', encoding="utf-8")
    result = run_cli("cek", str(bad))
    assert result.returncode == 1
    assert "belum ditutup" in result.stderr

def test_cli_jalankan_without_file_needs_project():
    result = run_cli("jalankan")
    assert result.returncode == 1
    assert "Butuh FILE" in result.stderr
