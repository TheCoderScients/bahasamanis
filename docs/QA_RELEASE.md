# QA Release

Checklist ini dipakai sebelum membuat tag rilis Bahasa Manis.

## Cek Lokal

```bash
python -m pytest
python -m py_compile bahasamanis.py bahasamanis_cli.py server.py
python -m json.tool vscode-bahasamanis/snippets/bm.json >/tmp/bm_snippets.json
python -m json.tool vscode-bahasamanis/syntaxes/bm.tmLanguage.json >/tmp/bm_syntax.json
bm jalankan examples/run_all_demos.bm
```

## Cek Build Paket

```bash
rm -rf dist build *.egg-info
python -m build
python -m twine check dist/*
```

## Cek CLI

```bash
bm versi
bm jalankan examples/output_demo.bm
bm ubah examples/output_demo.bm -o /tmp/output_demo.py
python /tmp/output_demo.py
bm cek --ketat examples
bm paket examples
bm jalankan examples/env_demo.bm
bm jalankan examples/log_demo.bm
bm jalankan examples/csv_demo.bm
bm jalankan examples/uji_demo.bm
tmpdir=$(mktemp -d)
cd "$tmpdir"
bm buat qa_bangun
cd qa_bangun
bm paket
bm bangun
python build/utama.py
```

## Cek Mode Aman

Program ini harus gagal di mode aman:

```bm
paket "os" sebagai os
```

```bm
tulis_berkas("/tmp/uji.txt", "isi")
```

Program ini harus tetap jalan di mode aman:

```bm
nama = ["Ayu", "Budi"]
setiap item dalam nama lakukan
    cetak besar(item)
akhir
```

## Cek Playground

```bash
python - <<'PY'
from server import app
client = app.test_client()

ok = client.post('/run', json={'code': 'cetak "Halo"', 'inputs': []})
assert ok.status_code == 200
assert 'Halo' in ok.get_json()['output']

blocked = client.post('/run', json={'code': 'paket "os" sebagai os', 'inputs': []})
assert 'mode aman' in blocked.get_json()['output']
PY
```

Untuk cek timeout manual:

```bash
BM_PLAYGROUND_TIMEOUT_SECONDS=1 python server.py
```

Lalu jalankan kode ini di playground:

```bm
selama benar lakukan
    lewati
akhir
```

## Cek Dokumentasi

- [ ] README menyebut status versi saat ini.
- [ ] `CHANGELOG.md` punya catatan rilis.
- [ ] `docs/STABILITAS.md` sesuai kondisi terbaru.
- [ ] `docs/ROADMAP.md` tidak menjanjikan fitur yang belum diputuskan.
- [ ] `docs/PANDUAN_PEMULA.md` bisa diikuti dari nol.
- [ ] `docs/KEAMANAN_PLAYGROUND.md` menjelaskan mode aman.

## Cek GitHub

- [ ] CI hijau di Python 3.9 sampai 3.13.
- [ ] Tidak ada token, file build, atau cache yang ikut commit.
- [ ] Tag rilis sesuai versi di `pyproject.toml` dan `bahasamanis.__version__`.
- [ ] Release notes menyebut breaking change jika ada.
