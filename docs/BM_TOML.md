# Format bm.toml

`bm.toml` adalah file konfigurasi proyek Bahasa Manis. File ini disimpan di root
proyek dan dipakai oleh CLI untuk menentukan file utama, folder cek, folder test,
dan output build.

Versi format stabil saat ini: `1`.

## Contoh Lengkap

```toml
[proyek]
format = "1"
nama = "aplikasi_saya"
versi = "0.1.0"
utama = "src/utama.bm"

[cek]
path = "."
ketat = false

[tes]
path = "tests"

[ubah]
output = "build/utama.py"

[bangun]
output = "build/utama.py"
cek = true
ketat = false
```

## Field Wajib

Bagian `[proyek]` wajib ada.

| Field | Wajib | Arti |
| --- | --- | --- |
| `format` | Tidak | Versi format config. Default: `"1"`. |
| `nama` | Ya | Nama proyek. Dipakai oleh `bm info` dan dokumentasi project. |
| `versi` | Ya | Versi aplikasi atau library kamu. |
| `utama` | Ya | File utama `.bm` yang dijalankan dan dibangun. |

## Field Opsional

### `[cek]`

| Field | Default | Arti |
| --- | --- | --- |
| `path` | `"."` | Folder atau file yang diperiksa oleh `bm cek`. |
| `ketat` | `false` | Jika `true`, `bm cek` otomatis memakai mode ketat. |

### `[tes]`

| Field | Default | Arti |
| --- | --- | --- |
| `path` | `"tests"` | Folder test yang dipakai oleh `bm tes`. |

### `[ubah]`

| Field | Default | Arti |
| --- | --- | --- |
| `output` | `"build/utama.py"` | Output default untuk `bm ubah` tanpa `-o`. |

### `[bangun]`

| Field | Default | Arti |
| --- | --- | --- |
| `output` | Nilai `[ubah].output` atau `"build/utama.py"` | Output Python untuk `bm bangun`. |
| `cek` | `true` | Jalankan validasi sebelum build. |
| `ketat` | `false` | Pakai mode ketat saat validasi build. |

## Nilai Boolean

Untuk field boolean, nilai berikut dikenali:

- Benar: `true`, `benar`, `ya`, `yes`
- Salah: `false`, `salah`, `tidak`, `no`

## Perintah Terkait

```bash
bm info
bm cek
bm cek --ketat
bm tes
bm ubah
bm bangun
bm bersih
```

`bm info` menampilkan ringkasan config. Jika ada field wajib yang hilang atau
file utama tidak ditemukan, `bm info` dan `bm cek` akan memberi pesan error.

`bm bangun` membaca `[proyek].utama`, memvalidasi file `.bm`, lalu membuat output
Python sesuai `[bangun].output`.
