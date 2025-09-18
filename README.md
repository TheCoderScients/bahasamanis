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

- `bm run file.bm`
- `bm transpile file.bm -o file.py`

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
bm run hello.bm
```

## Fitur Bahasa Singkat

- Kata kunci: `cetak`, `baca`, `jika/elif/lain/akhir`, `selama`, `untuk`, `fungsi/kembali`, `lanjut/henti`
- Boolean: `benar`, `salah`
- Operator logika: `dan`, `atau`, `tidak`
- Interpolasi string: `"Halo, {nama}"` (ekspresi di dalam `{...}` aman & didukung)

## Transpile -> Python

String dengan `{...}` ditranspilasi menjadi f-string Python.

```
# BMcetak "Halo, {1+2}"

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

## Lisensi

MIT
