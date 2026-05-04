import re
import pytest
from bahasamanis import BMError, Interpreter, transpile_to_python

def test_print_smoke(capsys):
    src = 'cetak "Halo"'
    it = Interpreter()
    it.run(src)
    captured = capsys.readouterr()
    assert "Halo" in captured.out

def test_transpile_smoke():
    src = 'cetak "Halo, {1+2}"'
    py = transpile_to_python(src)
    assert "def __bm_main():" in py
    # pastikan interpolasi menjadi f-string
    assert 'print(f"Halo, {1+2}")' in py

def test_expression_keywords_do_not_change_string_literals(capsys):
    src = 'teks = ["direct dan indirect", "jawaban benar"]\ncetak teks[0]\ncetak teks[1]'
    it = Interpreter()
    it.run(src)
    captured = capsys.readouterr()
    assert "direct dan indirect" in captured.out
    assert "jawaban benar" in captured.out

def test_string_concatenation_can_start_and_end_with_literals(capsys):
    src = 'nama = "BM"\nteks = "Halo, " + nama + "!"\ncetak teks'
    it = Interpreter()
    it.run(src)
    captured = capsys.readouterr()
    assert "Halo, BM!" in captured.out

def test_inline_comments_do_not_break_strings(capsys):
    src = '''
nama = "Ayu # tetap teks" # komentar di luar string
cetak nama # komentar setelah perintah
'''
    it = Interpreter()
    it.run(src)
    captured = capsys.readouterr()
    assert "Ayu # tetap teks" in captured.out
    assert "komentar" not in captured.out

def test_nested_if_inside_if_branch(capsys):
    src = '''
nilai = 2
jika nilai > 0 maka
    jika nilai == 2 maka
        cetak "dua"
    lain
        cetak "positif"
    akhir
lain
    cetak "nol"
akhir
'''
    it = Interpreter()
    it.run(src)
    captured = capsys.readouterr()
    assert "dua" in captured.out

def test_for_loop_inside_if_branch(capsys):
    src = '''
jika benar maka
    untuk i dari 1 sampai 3 lakukan
        cetak "{i}"
    akhir
lain
    cetak "salah"
akhir
'''
    it = Interpreter()
    it.run(src)
    captured = capsys.readouterr()
    assert "1" in captured.out
    assert "3" in captured.out
    assert "salah" not in captured.out

def test_lain_jika_alias(capsys):
    src = '''
nilai = 80
jika nilai >= 90 maka
    cetak "A"
lain jika nilai >= 75 maka
    cetak "B"
lain
    cetak "C"
akhir
'''
    it = Interpreter()
    it.run(src)
    captured = capsys.readouterr()
    assert "B" in captured.out

def test_friendly_beginner_syntax_sugar(capsys):
    src = '''
cetak Halo, Indonesia!

fungsi halo
    kembali "Halo dari fungsi"
akhir

cetak halo()

nilai = 0
jika benar lakukan
    cetak Cabang benar
akhir

selama nilai < 2
    nilai = nilai + 1
akhir

data = ["A", "B"]
setiap item dalam data
    cetak item
akhir

ulangi 2
    cetak ulang lagi
akhir
'''
    it = Interpreter()
    it.run(src)
    captured = capsys.readouterr()
    assert "Halo, Indonesia!" in captured.out
    assert "Halo dari fungsi" in captured.out
    assert "Cabang benar" in captured.out
    assert "A" in captured.out
    assert "B" in captured.out
    assert captured.out.count("ulang lagi") == 2

def test_friendly_tanya_prompt_without_quotes(capsys):
    src = '''
tanya Nama kamu: sebagai nama
cetak "Halo, {nama}"
'''
    it = Interpreter()
    it.input_func = lambda: "Sari"
    it.run(src)
    captured = capsys.readouterr()
    assert "Nama kamu: Halo, Sari" in captured.out

def test_indonesian_builtin_aliases(capsys):
    src = '''
nama = rapikan("  Budi  ")
kata = kecil("HALO")
daftar = pisah("apel,jeruk", ",")
tambah(daftar, "mangga")
cetak "Nama: {nama}"
cetak "Kata: {kata}"
cetak "Jumlah: {panjang(daftar)}"
cetak "Angka: {angka('12') + 3}"
cetak "Pecahan: {pecahan('2.5') + 1}"
cetak "Gabung: {gabung(daftar, ' | ')}"
'''
    it = Interpreter()
    it.run(src)
    captured = capsys.readouterr()
    assert "Nama: Budi" in captured.out
    assert "Kata: halo" in captured.out
    assert "Jumlah: 3" in captured.out
    assert "Angka: 15" in captured.out
    assert "Pecahan: 3.5" in captured.out
    assert "apel | jeruk | mangga" in captured.out

def test_transpile_includes_indonesian_aliases():
    src = '''
jika panjang("abc") == 3 maka
    cetak "ok"
lain jika angka("1") == 1 maka
    cetak "lain"
akhir
pastikan_sama(1, 1)
pastikan_benar(benar)
'''
    py = transpile_to_python(src)
    assert "panjang = len" in py
    assert "elif angka(\"1\") == 1:" in py
    assert "def pastikan_sama" in py
    assert "sama = pastikan_sama" in py
    assert "pastikan_benar(True)" in py

def test_exception_handling_coba_tangkap_akhirnya(capsys):
    src = '''
coba
    angka("bukan angka")
tangkap error
    cetak "Tertangkap"
    cetak error
akhirnya
    cetak "Selesai"
akhir
'''
    it = Interpreter()
    it.run(src)
    captured = capsys.readouterr()
    assert "Tertangkap" in captured.out
    assert "angka() gagal" in captured.out
    assert "Selesai" in captured.out

def test_test_helpers_pastikan_and_aliases(capsys):
    src = '''
pastikan(2 + 3 == 5, "matematika dasar")
pastikan_sama("BM", "BM")
sama(angka("5"), 5)
pastikan_tidak_sama("BM", "Python")
tidak_sama(1, 2)
pastikan_benar(berisi(["BM"], "BM"))
pastikan_salah(berisi(["BM"], "Python"))

pakai "bm_standar/uji" sebagai uji
uji.sama(10, 10)
uji.tidak_sama(10, 11)
uji.pastikan_benar(benar)
uji.pastikan_salah(salah)

cetak "helper uji lulus"
'''
    it = Interpreter()
    it.run(src)
    captured = capsys.readouterr()
    assert "helper uji lulus" in captured.out

def test_test_helpers_report_friendly_errors():
    it = Interpreter()
    with pytest.raises(BMError, match="Pastikan sama gagal"):
        it.run('pastikan_sama(1, 2)')

    with pytest.raises(BMError, match="pesan custom"):
        it.run('pastikan_salah(benar, "pesan custom")')

def test_friendly_name_and_number_errors():
    it = Interpreter()
    with pytest.raises(BMError, match="Variabel 'nama' belum dibuat"):
        it.run('cetak nama')

    with pytest.raises(BMError, match="angka\\(\\) gagal"):
        it.run('nilai = angka("abc")')

    with pytest.raises(BMError, match="pecahan\\(\\) gagal"):
        it.run('nilai = pecahan("abc")')

def test_friendly_block_errors():
    it = Interpreter()
    with pytest.raises(BMError, match="Blok `jika` pada baris 1 belum ditutup dengan `akhir`"):
        it.run('jika benar maka\n    cetak "lupa akhir"')

    with pytest.raises(BMError, match="`akhir` pada baris 1 tidak punya pembuka blok"):
        it.run('akhir')

    with pytest.raises(BMError, match="harus berada di dalam blok `jika`"):
        it.run('lain\n    cetak "salah tempat"')

def test_class_and_ini_methods(capsys):
    src = '''
kelas Siswa
    fungsi mulai(nama, nilai)
        ini.nama = nama
        ini.nilai = nilai
    akhir

    fungsi info()
        kembali "{ini.nama}: {ini.nilai}"
    akhir
akhir

s = Siswa("Budi", 88)
cetak s.info()
cetak s.nama
'''
    it = Interpreter()
    it.run(src)
    captured = capsys.readouterr()
    assert "Budi: 88" in captured.out
    assert captured.out.strip().splitlines()[-1] == "Budi"

def test_ini_can_still_be_regular_variable_outside_class(capsys):
    src = '''
ini = "variabel biasa"
cetak ini
'''
    it = Interpreter()
    it.run(src)
    captured = capsys.readouterr()
    assert "variabel biasa" in captured.out

def test_async_function_tunggu_jeda(capsys):
    src = '''
asinkron fungsi ambil_pesan(nama)
    tunggu jeda(0)
    kembali "Halo, {nama}"
akhir

pesan = tunggu ambil_pesan("BM")
cetak pesan
'''
    it = Interpreter()
    it.run(src)
    captured = capsys.readouterr()
    assert "Halo, BM" in captured.out

def test_foreach_repeat_and_data_helpers(capsys):
    src = '''
nama = ["Sari", "Budi", "Ayu"]
hasil = []

untuk item dalam nama lakukan
    tambah(hasil, besar(item))
akhir

ulangi 2 kali lakukan
    tambah(hasil, "ULANG")
akhir

profil = kamus()
atur(profil, "kelas", "XI")
atur(profil, "jumlah", panjang(hasil))

jika "SARI" dalam hasil dan berisi(profil, "kelas") maka
    cetak gabung(hasil, ", ")
    cetak ambil(profil, "kelas")
    cetak ambil(profil, "tidak_ada", "aman")
akhir
'''
    it = Interpreter()
    it.run(src)
    captured = capsys.readouterr()
    assert "SARI, BUDI, AYU, ULANG, ULANG" in captured.out
    assert "XI" in captured.out
    assert "aman" in captured.out

def test_loop_control_aliases_and_lewati(capsys):
    src = '''
data = ["Ayu", "Budi", "Citra", "Dina"]

jika benar maka
    lewati
akhir

untuk item dalam data lakukan
    jika item == "Budi" maka
        lanjutkan
    akhir
    cetak item
    jika item == "Citra" maka
        berhenti
    akhir
akhir
'''
    it = Interpreter()
    it.run(src)
    captured = capsys.readouterr()
    assert "Ayu" in captured.out
    assert "Citra" in captured.out
    assert "Budi" not in captured.out
    assert "Dina" not in captured.out

def test_setiap_alias_and_selama_lakukan(capsys):
    src = '''
data = ["a", "b"]
jumlah = 0

setiap item dalam data lakukan
    cetak item
akhir

selama jumlah < 2 lakukan
    jumlah = jumlah + 1
akhir

cetak "Jumlah: {jumlah}"
'''
    it = Interpreter()
    it.run(src)
    captured = capsys.readouterr()
    assert "a" in captured.out
    assert "b" in captured.out
    assert "Jumlah: 2" in captured.out

def test_file_helpers(tmp_path, capsys):
    file_path = tmp_path / "catatan.txt"
    src = f'''
path = "{file_path}"
tulis_berkas(path, "Baris 1\\n")
tambah_berkas(path, "Baris 2")

jika ada_berkas(path) maka
    cetak baca_berkas(path)
    baris = baca_baris(path)
    cetak "Jumlah baris: {{panjang(baris)}}"
akhir

cetak berisi(daftar_berkas("{tmp_path}"), "catatan.txt")
hapus_berkas(path)
cetak ada_berkas(path)
'''
    it = Interpreter()
    it.run(src)
    captured = capsys.readouterr()
    assert "Baris 1" in captured.out
    assert "Baris 2" in captured.out
    assert "Jumlah baris: 2" in captured.out
    assert "True" in captured.out
    assert captured.out.strip().endswith("False")

def test_safe_mode_blocks_imports_and_file_helpers(tmp_path):
    it = Interpreter(aman=True)
    with pytest.raises(BMError, match="mode aman"):
        it.run('paket "os" sebagai os')

    with pytest.raises(BMError, match="mode aman"):
        it.run('pakai "bm_standar/json" sebagai j')

    file_path = tmp_path / "tidak_boleh.txt"
    with pytest.raises(BMError, match="mode aman"):
        it.run(f'tulis_berkas("{file_path}", "isi")')
    assert not file_path.exists()

def test_standard_modules_env_log_csv(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("BM_TEST_MODE", raising=False)
    csv_path = tmp_path / "nilai.csv"
    src = f'''
pakai "bm_standar/env" sebagai env
pakai "bm_standar/log" sebagai log
pakai "bm_standar/csv" sebagai csv

env.atur("BM_TEST_MODE", "produksi")
env.atur("BM_TEST_PORT", "8080")
env.atur("BM_TEST_DEBUG", "ya")

cetak "Mode: {{env.ambil('BM_TEST_MODE')}}"
cetak "Port: {{env.ambil_angka('BM_TEST_PORT') + 1}}"
cetak "Debug: {{env.ambil_bool('BM_TEST_DEBUG')}}"
cetak "Ada: {{env.ada('BM_TEST_MODE')}}"

log.atur("INFO", "%(levelname)s:%(message)s")
log.info("modul log jalan")

data = [{{"nama": "Ayu", "nilai": "90"}}, {{"nama": "Budi", "nilai": "88"}}]
teks = csv.bentuk(data, ["nama", "nilai"])
baris = csv.urai(teks)
cetak "CSV: {{baris[0]['nama']}}/{{baris[1]['nilai']}}"

csv.tulis("{csv_path}", data, ["nama", "nilai"])
dari_file = csv.baca("{csv_path}")
cetak "File CSV: {{dari_file[1]['nama']}}"

env.hapus("BM_TEST_MODE")
env.hapus("BM_TEST_PORT")
env.hapus("BM_TEST_DEBUG")
'''
    it = Interpreter()
    it.run(src)
    captured = capsys.readouterr()
    assert "Mode: produksi" in captured.out
    assert "Port: 8081" in captured.out
    assert "Debug: True" in captured.out
    assert "Ada: True" in captured.out
    assert "INFO:modul log jalan" in captured.out
    assert "CSV: Ayu/88" in captured.out
    assert "File CSV: Budi" in captured.out
    assert csv_path.exists()

def test_env_wajib_reports_missing_variable(monkeypatch):
    monkeypatch.delenv("BM_TIDAK_ADA", raising=False)
    it = Interpreter()
    with pytest.raises(BMError, match="Environment variable belum ada"):
        it.run('pakai "bm_standar/env" sebagai env\nenv.wajib("BM_TIDAK_ADA")')

def test_expression_eval_does_not_expose_python_import():
    it = Interpreter()
    with pytest.raises(BMError, match="__import__|tidak didefinisikan"):
        it.run('cetak __import__("os").getcwd()')

def test_safe_mode_can_still_run_basic_program(capsys):
    src = '''
nama = ["Ayu", "Budi"]
setiap item dalam nama lakukan
    cetak besar(item)
akhir
'''
    it = Interpreter(aman=True)
    it.run(src)
    captured = capsys.readouterr()
    assert "AYU" in captured.out
    assert "BUDI" in captured.out

def test_tanya_prompt_input(capsys):
    src = '''
tanya "Nama kamu: " sebagai nama
cetak "Halo, {nama}"
'''
    it = Interpreter()
    it.input_func = lambda: "Sari"
    it.run(src)
    captured = capsys.readouterr()
    assert "Nama kamu: Halo, Sari" in captured.out

def test_pilih_saat_bawaan(capsys):
    src = '''
menu = "2"
pilih menu
    saat "1"
        cetak "Tambah"
    saat "2"
        cetak "Lihat"
    bawaan
        cetak "Keluar"
akhir
'''
    it = Interpreter()
    it.run(src)
    captured = capsys.readouterr()
    assert "Lihat" in captured.out
    assert "Tambah" not in captured.out
    assert "Keluar" not in captured.out

def test_transpile_advanced_features():
    src = '''
kelas Siswa
    fungsi mulai(nama)
        ini.nama = nama
    akhir
akhir

asinkron fungsi halo()
    tunggu jeda(0)
    kembali "ok"
akhir

coba
    lempar "gagal"
tangkap error
    cetak error
akhir
'''
    py = transpile_to_python(src)
    assert "class Siswa:" in py
    assert "def __init__(self, nama):" in py
    assert "self.nama" in py
    assert "async def halo():" in py
    assert "await jeda(0)" in py
    assert "except Exception as error:" in py

def test_transpile_foreach_repeat_helpers():
    src = '''
data = ["a", "b"]
untuk item dalam data lakukan
    cetak item
akhir
ulangi 2 kali lakukan
    cetak "lagi"
akhir
'''
    py = transpile_to_python(src)
    assert "for item in data:" in py
    assert "for _ in range(int(2)):" in py
    assert "def daftar(nilai=None):" in py

def test_transpile_loop_control_aliases():
    src = '''
untuk item dalam ["a"] lakukan
    lewati
    lanjutkan
    berhenti
akhir
'''
    py = transpile_to_python(src)
    assert "pass" in py
    assert "continue" in py
    assert "break" in py

def test_transpile_file_helpers_and_setiap():
    src = '''
tulis_berkas("/tmp/bm-test.txt", "isi")
setiap item dalam baca_baris("/tmp/bm-test.txt") lakukan
    cetak item
akhir
'''
    py = transpile_to_python(src)
    assert "from pathlib import Path" in py
    assert "def baca_berkas(path):" in py
    assert "def tulis_berkas(path, isi):" in py
    assert "for item in baca_baris" in py

def test_transpile_tanya_and_pilih():
    src = '''
tanya "Pilih: " sebagai menu
pilih menu
    saat "1"
        cetak "Satu"
    bawaan
        cetak "Lain"
akhir
'''
    py = transpile_to_python(src)
    assert "print(\"Pilih: \", end='')" in py
    assert "menu = input()" in py
    assert "__bm_pilih_" in py
    assert "== \"1\":" in py

def test_transpile_friendly_beginner_syntax():
    src = '''
cetak Halo dunia!
fungsi halo
    kembali "ok"
akhir
selama benar
    berhenti
akhir
'''
    py = transpile_to_python(src)
    assert "print(" in py
    assert "Halo dunia!" in py
    assert "def halo():" in py
    assert "while True:" in py
