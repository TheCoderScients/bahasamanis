# Bahasa Manis (BM)

<p align="center">
  <img src="https://raw.githubusercontent.com/TheCoderScients/bahasamanis/main/vscode-bahasamanis/images/icon.png" alt="Bahasa Manis icon" width="128" />
</p>

[![PyPI version](https://img.shields.io/pypi/v/bahasamanis.svg)](https://pypi.org/project/bahasamanis/)

Bahasa pemrograman berbahasa Indonesia dengan interpreter, transpiler, CLI, dan playground web.

PyPI: https://pypi.org/project/bahasamanis/

## Instalasi

Disarankan menggunakan pipx (CLI terisolasi dan langsung tersedia di PATH):

```
pipx ensurepath
pipx install bahasamanis
```

Alternatif (pip + virtualenv):

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows PowerShell
pip install bahasamanis
```

Instalasi dari sumber (pengembangan):

```
pip install -e .
```

Perintah CLI:

- `bm run|jalankan file.bm`
- `bm transpile|ubah file.bm -o file.py`
- `bm repl`

## Playground Web

```
python server.py
# buka http://127.0.0.1:5000
```

## Quickstart

```
cetak "Masukkan nama:"
baca nama
cetak "Halo, {nama}!"
```

Jalankan:

```
bm jalankan hello.bm
# atau
bm run hello.bm
```

## Fitur Bahasa Singkat

- Kata kunci: `cetak`, `baca`, `jika/elif/lain/akhir`, `selama`, `untuk`, `fungsi/kembali`, `lanjut/henti`
- Boolean: `benar`, `salah`
- Operator logika: `dan`, `atau`, `tidak`
- Interpolasi string: `"Halo, {nama}"` (ekspresi di dalam `{...}` aman & didukung)

## Interop Python & Modul BM (paket/pakai)

- Impor modul Python dengan alias Indonesia:

  ```bm
  paket "math" sebagai m
  cetak "akar 16 = {m.sqrt(16)}"
  ```

- Impor modul BM lokal atau pustaka standar berbahasa Indonesia:

  ```bm
  pakai "bm_standar/json" sebagai j
  data = {"nama": "BM", "versi": 1}
  cetak j.bentuk(data, rapi=benar)
  ```

Catatan: Paket `bahasamanis` menyertakan data paket `bahasamanis_data` yang berisi folder `bm_standar/`, sehingga contoh di atas berfungsi langsung setelah instal dari PyPI (tanpa perlu menyalin file .bm secara manual).

## Pustaka Standar BM

Paket `bahasamanis` menyertakan pustaka standar BM yang dapat diimpor menggunakan perintah `pakai`. Pustaka standar ini termasuk:

- `bm_standar/json`: modul untuk bekerja dengan data JSON
- `bm_standar/jaringan`: modul untuk bekerja dengan jaringan
- `bm_standar/waktu`: modul untuk bekerja dengan waktu
- `bm_standar/acak`: modul untuk bekerja dengan bilangan acak

## Transpile -> Python

String dengan `{...}` ditranspilasi menjadi f-string Python.

```
# BM
cetak "Halo, {1+2}"

# Python
print(f"Halo, {1+2}")
```

## Error Berbahasa Indonesia

Pesan kesalahan telah dilokalkan, misalnya:

- `Kesalahan sintaks pada ekspresi ...: tidak ditutup`
- `Kesalahan runtime pada baris N: operator '>' tidak didukung antara tipe 'str' dan 'int'`

## VS Code Extension (lokal)

Folder: `vscode-bahasamanis/`

Cara coba:

1. Buka folder `vscode-bahasamanis/` di VS Code.
2. Tekan `F5` untuk menjalankan Extension Development Host.
3. Buka file `.bm` untuk melihat highlight dan snippet.

## Windows EXE

Rilis menyediakan binary tunggal `bm.exe` di halaman Release GitHub. Unduh `bm.exe`, lalu jalankan:

```
bm.exe jalankan contoh.bm
```

## Changelog ringkas

### 0.1.11
- Interop Python: `paket "modul" sebagai alias`
- Import modul BM: `pakai "path/modul.bm" [sebagai alias]`
- CLI Indonesia: `bm jalankan`, `bm ubah`, `bm repl` (kompatibel dengan `run`/`transpile`)
- Pustaka standar dibundel: `bm_standar/{berkas,json,jaringan,waktu,acak}` via paket data `bahasamanis_data`
- Perbaikan runtime: output `print` di-flush, resolusi `pakai` lebih kuat, default argumen fungsi dievaluasi saat pemanggilan

## Lisensi

MIT
