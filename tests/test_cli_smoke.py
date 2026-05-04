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
    assert "bm.toml v1" in info.stdout
    assert "src/utama.bm" in info.stdout
    assert "build/utama.py" in info.stdout
    assert "Output bangun" in info.stdout

    run_default = run_cli("jalankan", cwd=app)
    assert run_default.returncode == 0
    assert "app_manis siap jalan" in run_default.stdout

    check = run_cli("cek", cwd=app)
    assert check.returncode == 0
    assert "file BM valid" in check.stdout

    test = run_cli("tes", cwd=app)
    assert test.returncode == 0
    assert "Ringkasan tes: 1 lulus, 0 gagal, 1 total." in test.stdout

    transpile = run_cli("ubah", cwd=app)
    assert transpile.returncode == 0
    out = app / "build" / "utama.py"
    assert out.exists()
    assert "def __bm_main():" in out.read_text(encoding="utf-8")

    build = run_cli("bangun", cwd=app)
    assert build.returncode == 0
    assert "Bangun selesai" in build.stdout
    built = subprocess.run(
        [sys.executable, str(app / "build" / "utama.py")],
        text=True,
        capture_output=True,
        check=False,
    )
    assert built.returncode == 0
    assert "app_manis siap jalan" in built.stdout

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

def test_cli_folder_mode_info_run_and_empty_tests(tmp_path):
    app = tmp_path / "folder_biasa"
    app.mkdir()
    (app / "morino_cyber_dungeon.bm").write_text('cetak "jalan dari folder biasa"\n', encoding="utf-8")

    info = run_cli("info", cwd=app)
    assert info.returncode == 0
    assert "folder biasa" in info.stdout
    assert "morino_cyber_dungeon.bm" in info.stdout

    run = run_cli("jalankan", cwd=app)
    assert run.returncode == 0
    assert "jalan dari folder biasa" in run.stdout

    test = run_cli("tes", cwd=app)
    assert test.returncode == 0
    assert "Belum ada test" in test.stdout

def test_cli_folder_mode_finds_test_files(tmp_path):
    app = tmp_path / "folder_tes"
    tests = app / "tests"
    tests.mkdir(parents=True)
    (app / "utama.bm").write_text('cetak "utama"\n', encoding="utf-8")
    (tests / "tes_utama.bm").write_text('cetak "tes folder biasa"\n', encoding="utf-8")

    result = run_cli("tes", cwd=app)
    assert result.returncode == 0
    assert "tes folder biasa" in result.stdout
    assert "Ringkasan tes: 1 lulus, 0 gagal, 1 total." in result.stdout

def test_cli_cek_ketat_reports_style_warnings(tmp_path):
    src = tmp_path / "gaya_lama.bm"
    src.write_text('jika salah maka\n    cetak "x"\nelif benar maka\n    cetak "y"  \nakhir\n', encoding="utf-8")
    result = run_cli("cek", str(src), "--ketat")
    assert result.returncode == 1
    assert "mode ketat" in result.stderr
    assert "lain jika" in result.stderr
    assert "spasi kosong" in result.stderr

def test_cli_cek_ketat_accepts_flag_before_path(tmp_path):
    src = tmp_path / "rapi.bm"
    src.write_text('cetak "aman"\n', encoding="utf-8")
    result = run_cli("cek", "--ketat", str(src))
    assert result.returncode == 0
    assert "file BM valid (ketat)" in result.stdout

def test_cli_cek_ketat_ignores_english_words_inside_strings(tmp_path):
    src = tmp_path / "teks_aman.bm"
    src.write_text('cetak "kata elif dan async cuma teks biasa"\n', encoding="utf-8")
    result = run_cli("cek", "--ketat", str(src))
    assert result.returncode == 0
    assert result.stderr == ""

def test_cli_bangun_uses_custom_output_from_bm_toml(tmp_path):
    app = tmp_path / "app_output"
    assert run_cli("buat", str(app)).returncode == 0
    config = app / "bm.toml"
    config.write_text(
        config.read_text(encoding="utf-8").replace(
            '[bangun]\noutput = "build/utama.py"',
            '[bangun]\noutput = "hasil/aplikasi.py"',
        ),
        encoding="utf-8",
    )

    result = run_cli("bangun", cwd=app)
    assert result.returncode == 0
    assert (app / "hasil" / "aplikasi.py").exists()
    assert "hasil/aplikasi.py" in result.stdout

def test_cli_bangun_ketat_reports_style_warnings(tmp_path):
    app = tmp_path / "app_ketat"
    assert run_cli("buat", str(app)).returncode == 0
    (app / "src" / "utama.bm").write_text('jika salah maka\n    cetak "x"\nelif benar maka\n    cetak "y"\nakhir\n', encoding="utf-8")

    result = run_cli("bangun", "--ketat", cwd=app)
    assert result.returncode == 1
    assert "Bangun dibatalkan" in result.stderr
    assert "lain jika" in result.stderr

def test_cli_project_config_validation_reports_missing_main(tmp_path):
    app = tmp_path / "app_config"
    assert run_cli("buat", str(app)).returncode == 0
    (app / "src" / "utama.bm").unlink()

    result = run_cli("cek", cwd=app)
    assert result.returncode == 1
    assert "file utama tidak ditemukan" in result.stderr

def test_cli_bersih_removes_cache_and_build_dirs(tmp_path):
    app = tmp_path / "app_bersih"
    result = run_cli("buat", str(app))
    assert result.returncode == 0
    (app / "__pycache__").mkdir()
    (app / "__pycache__" / "x.pyc").write_text("cache", encoding="utf-8")
    (app / "contoh.egg-info").mkdir()
    run_cli("ubah", cwd=app)
    assert (app / "build").exists()

    clean = run_cli("bersih", cwd=app)
    assert clean.returncode == 0
    assert "Bersih selesai" in clean.stdout
    assert not (app / "__pycache__").exists()
    assert not (app / "contoh.egg-info").exists()
    assert not (app / "build").exists()
