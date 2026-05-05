# Template CI Bahasa Manis

CI membantu proyek Bahasa Manis tetap rapi sebelum digabung ke `main`.

## GitHub Actions

Buat file ini di proyek kamu:

```text
.github/workflows/bahasamanis.yml
```

Isi file bisa disalin dari:

```text
docs/templates/github-actions-bahasamanis.yml
```

Versi ringkasnya:

```yaml
name: Bahasa Manis CI

on:
  push:
    branches: [ main, master ]
  pull_request:

jobs:
  cek:
    runs-on: ubuntu-latest
    steps:
      - name: Ambil kode
        uses: actions/checkout@v4

      - name: Siapkan Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Pasang Bahasa Manis
        run: |
          python -m pip install --upgrade pip
          python -m pip install bahasamanis

      - name: Cek format
        run: bm format --cek

      - name: Cek sintaks ketat
        run: bm cek --ketat

      - name: Jalankan test BM
        run: bm tes

      - name: Bangun output Python
        run: bm bangun --ketat
```

## Urutan yang Disarankan

Jalankan urutan ini secara lokal sebelum push:

```bash
bm format --cek
bm cek --ketat
bm tes
bm bangun --ketat
```

Jika `bm format --cek` gagal, jalankan:

```bash
bm format
```

Lalu ulangi ceknya.

## Proyek Tanpa `bm.toml`

Untuk folder biasa tanpa `bm.toml`, panggil path secara eksplisit:

```yaml
- run: bm format --cek src
- run: bm cek --ketat src
- run: bm tes tests
```

Mode proyek dengan `bm.toml` tetap lebih disarankan untuk proyek besar.

