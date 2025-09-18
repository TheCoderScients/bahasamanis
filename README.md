# Bahasa Manis (BM)

Bahasa pemrograman berbahasa Indonesia dengan interpreter, transpiler, CLI, dan playground web.

## Instalasi (lokal)

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

## Contoh

```
cetak "Masukkan nama:"
baca nama
cetak "Halo, {nama}!"
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
