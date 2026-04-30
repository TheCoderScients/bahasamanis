#!/usr/bin/env python3
from __future__ import annotations

"""
CLI untuk Bahasa Manis (BM)
Perintah:
  bm jalankan file.bm
  bm ubah file.bm -o file.py
  bm interaktif
  bm buat nama_proyek
  bm cek [path]
  bm tes [path]
  bm info
  bm versi
"""
import sys
import argparse
import shutil
from pathlib import Path
from bahasamanis import __version__, Interpreter, parse_program, transpile_to_python

SKIP_DIRS = {'.git', '.hg', '.svn', '.venv', 'venv', '__pycache__', 'dist', 'build'}

def find_project_root(start: Path | None = None) -> Path | None:
    current = (start or Path.cwd()).resolve()
    if current.is_file():
        current = current.parent
    for path in [current, *current.parents]:
        if (path / 'bm.toml').is_file():
            return path
    return None

def parse_bm_toml(path: Path) -> dict[str, dict[str, str]]:
    config: dict[str, dict[str, str]] = {}
    section = ''
    for raw_line in path.read_text(encoding='utf-8').splitlines():
        line = raw_line.split('#', 1)[0].strip()
        if not line:
            continue
        if line.startswith('[') and line.endswith(']'):
            section = line[1:-1].strip()
            config.setdefault(section, {})
            continue
        if '=' not in line:
            continue
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        config.setdefault(section, {})[key] = value
    return config

def load_project(start: Path | None = None) -> tuple[Path, dict[str, dict[str, str]]] | None:
    root = find_project_root(start)
    if root is None:
        return None
    return root, parse_bm_toml(root / 'bm.toml')

def project_value(config: dict[str, dict[str, str]], section: str, key: str, default: str) -> str:
    return config.get(section, {}).get(key, default)

def resolve_project_path(path: str | None, default: str) -> Path:
    if path:
        return Path(path)
    project = load_project()
    if project:
        root, config = project
        return root / default
    return Path(default)

def iter_bm_files(target: Path):
    if target.is_file():
        return [target] if target.suffix == '.bm' else []
    if not target.exists():
        return []
    files = []
    for path in sorted(target.rglob('*.bm')):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        files.append(path)
    return files

def run_bm_file(path: Path):
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()
    interp = Interpreter()
    # Set base_path to the folder of the file for correct 'pakai' resolution
    p = Path(path).resolve()
    interp.base_path = p.parent
    # Include project root (CWD) and file's parent for search paths, preserving existing defaults
    try:
        extra_paths = [interp.base_path, Path.cwd()]
        # preserve order and uniqueness
        seen = set()
        new_list = []
        for pth in [*getattr(interp, 'search_paths', []), *extra_paths]:
            key = str(pth)
            if key not in seen:
                seen.add(key); new_list.append(pth)
        interp.search_paths = new_list
    except Exception:
        pass
    interp.run(src)

def cmd_run(path: str | None = None) -> int:
    if not path:
        project = load_project()
        if not project:
            print("[Error] Butuh FILE untuk dijalankan, atau jalankan dari proyek yang punya bm.toml.", file=sys.stderr)
            return 1
        root, config = project
        path = str(root / project_value(config, 'proyek', 'utama', 'src/utama.bm'))
    try:
        run_bm_file(Path(path))
    except Exception as e:
        print('[Error]', e, file=sys.stderr)
        return 1
    return 0

def cmd_transpile(path: str | None = None, out: str | None = None) -> int:
    if not path:
        project = load_project()
        if not project:
            print("[Error] Butuh FILE untuk diubah, atau jalankan dari proyek yang punya bm.toml.", file=sys.stderr)
            return 1
        root, config = project
        path = str(root / project_value(config, 'proyek', 'utama', 'src/utama.bm'))
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()
    py = transpile_to_python(src)
    if out:
        with open(out, 'w', encoding='utf-8') as f:
            f.write(py)
        print('Tersimpan ->', out)
    else:
        print(py)
    return 0

def cmd_create(name: str, template: str = 'cli') -> int:
    root = Path(name)
    if template != 'cli':
        print(f"[Error] Template '{template}' belum tersedia. Pakai: cli", file=sys.stderr)
        return 1
    if root.exists() and not root.is_dir():
        print(f"[Error] '{root}' sudah ada dan bukan folder.", file=sys.stderr)
        return 1
    if root.exists() and any(root.iterdir()):
        print(f"[Error] Folder '{root}' sudah ada dan tidak kosong.", file=sys.stderr)
        return 1

    root.mkdir(parents=True, exist_ok=True)
    (root / 'src').mkdir(exist_ok=True)
    (root / 'tests').mkdir(exist_ok=True)
    (root / 'bm.toml').write_text(
        '\n'.join([
            '[proyek]',
            f'nama = "{root.name}"',
            'versi = "0.1.0"',
            'utama = "src/utama.bm"',
            '',
            '[cek]',
            'path = "."',
            '',
            '[tes]',
            'path = "tests"',
            '',
        ]),
        encoding='utf-8',
    )
    (root / 'src' / 'utama.bm').write_text(
        '\n'.join([
            f'cetak "{root.name} siap jalan!"',
            '',
            'fungsi sapa(nama)',
            '    kembali "Halo, {nama}!"',
            'akhir',
            '',
            'cetak sapa("Indonesia")',
            '',
        ]),
        encoding='utf-8',
    )
    (root / 'tests' / 'tes_utama.bm').write_text(
        '\n'.join([
            'fungsi tambah(a, b)',
            '    kembali a + b',
            'akhir',
            '',
            'jika tambah(2, 3) != 5',
            '    lempar "Tes tambah gagal"',
            'akhir',
            '',
            'cetak "Tes utama lulus"',
            '',
        ]),
        encoding='utf-8',
    )
    (root / 'README.md').write_text(
        '\n'.join([
            f'# {root.name}',
            '',
            'Proyek Bahasa Manis.',
            '',
            '```bash',
            'bm info',
            'bm jalankan',
            'bm cek',
            'bm tes',
            '```',
            '',
        ]),
        encoding='utf-8',
    )
    (root / '.gitignore').write_text('__pycache__/\n*.pyc\n', encoding='utf-8')
    print(f"Proyek '{root}' dibuat.")
    print(f"Jalankan: cd {root} && bm jalankan")
    return 0

def cmd_check(path: str | None = None) -> int:
    project = load_project()
    if path:
        target = Path(path)
    elif project:
        root, config = project
        target = root / project_value(config, 'cek', 'path', '.')
    else:
        target = Path('.')
    files = iter_bm_files(target)
    if not files:
        print(f"[Error] Tidak ada file .bm di '{target}'.", file=sys.stderr)
        return 1
    failed = 0
    for file in files:
        try:
            src = file.read_text(encoding='utf-8')
            parse_program(src)
            print(f"OK  {file}")
        except Exception as e:
            failed += 1
            print(f"ERR {file}: {e}", file=sys.stderr)
    if failed:
        print(f"{failed} file bermasalah.", file=sys.stderr)
        return 1
    print(f"{len(files)} file BM valid.")
    return 0

def cmd_test(path: str | None = None) -> int:
    project = load_project()
    if path:
        target = Path(path)
    elif project:
        root, config = project
        target = root / project_value(config, 'tes', 'path', 'tests')
    else:
        target = Path('tests')
    if path and target.is_dir() and (target / 'tests').is_dir():
        target = target / 'tests'
    files = iter_bm_files(target)
    if not files:
        print(f"[Error] Tidak ada test .bm di '{target}'.", file=sys.stderr)
        return 1
    failed = 0
    for file in files:
        try:
            run_bm_file(file)
            print(f"LULUS {file}")
        except Exception as e:
            failed += 1
            print(f"GAGAL {file}: {e}", file=sys.stderr)
    if failed:
        print(f"{failed} test gagal.", file=sys.stderr)
        return 1
    print(f"{len(files)} test BM lulus.")
    return 0

def cmd_info() -> int:
    project = load_project()
    if not project:
        print('[Error] bm.toml tidak ditemukan dari folder ini.', file=sys.stderr)
        return 1
    root, config = project
    name = project_value(config, 'proyek', 'nama', root.name)
    version = project_value(config, 'proyek', 'versi', '-')
    main_file = project_value(config, 'proyek', 'utama', 'src/utama.bm')
    check_path = project_value(config, 'cek', 'path', '.')
    test_path = project_value(config, 'tes', 'path', 'tests')
    print(f'Proyek      : {name}')
    print(f'Versi       : {version}')
    print(f'Root        : {root}')
    print(f'File utama  : {main_file}')
    print(f'Cek path    : {check_path}')
    print(f'Test path   : {test_path}')
    return 0

def repl():
    print('BM Interaktif — ketik "keluar" untuk berhenti. Coba: cetak, baca, tanya, jika, pilih, untuk/setiap, ulangi, kelas, coba, asinkron, henti/berhenti, lanjutkan, lewati, akhir.')
    interp = Interpreter()
    buffer = []
    def is_block_complete(lines):
        # sederhana: jika jumlah 'akhir' >= jumlah pembuka blok
        opens = 0
        for ln in lines:
            s = ln.strip()
            if (
                s.startswith('fungsi ')
                or s.startswith('asinkron fungsi ')
                or s.startswith('async fungsi ')
                or s.startswith('jika ')
                or s.startswith('selama ')
                or s.startswith('untuk ')
                or s.startswith('setiap ')
                or s.startswith('ulangi ')
                or s.startswith('pilih ')
                or s.startswith('kelas ')
                or s in ('coba', 'coba maka')
            ):
                opens += 1
            if s == 'akhir':
                opens -= 1
        return opens <= 0
    while True:
        try:
            prompt = '... ' if buffer else 'bm> '
            line = input(prompt)
        except EOFError:
            break
        if line.strip() in ('keluar','exit','quit'):
            break
        buffer.append(line)
        if not is_block_complete(buffer):
            continue
        src = '\n'.join(buffer)
        buffer.clear()
        try:
            interp.run(src)
        except Exception as e:
            print('[Error]', e, file=sys.stderr)

def cmd_diagnose():
    print(f'Bahasa Manis : {__version__}')
    print(f'Perintah bm  : {shutil.which("bm") or "(tidak ditemukan di PATH)"}')
    print(f'Python       : {sys.executable}')
    print(f'Env Python   : {sys.prefix}')
    print(f'Modul CLI    : {Path(__file__).resolve()}')
    print(f'Folder kerja : {Path.cwd()}')
    print('')
    print('Kalau `bm` pernah jalan hanya dari folder repo, pasang ulang paketnya:')
    print('python -m pip install --force-reinstall -e /path/ke/bahasamanis')

def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(prog='bm', description='BahasaManis CLI')
    parser.add_argument('--version', action='version', version=f'Bahasa Manis {__version__}')
    parser.add_argument('action', choices=['jalankan','ubah','interaktif','versi','diagnosa','buat','bikin','cek','tes','info','run','transpile','repl','diagnose','new','check','test'], help='aksi: jalankan, ubah, buat, cek, tes, info, interaktif, versi, atau diagnosa')
    parser.add_argument('file', nargs='?', help='file sumber .bm')
    parser.add_argument('--out','-o', help='file hasil Python untuk perintah ubah')
    parser.add_argument('--template', default='cli', help='template untuk perintah buat (default: cli)')
    args = parser.parse_args(argv)
    act = args.action
    if act in ('run','jalankan'):
        return cmd_run(args.file)
    elif act in ('transpile','ubah'):
        return cmd_transpile(args.file, args.out)
    elif act in ('buat','bikin','new'):
        if not args.file:
            parser.error('butuh NAMA_PROYEK untuk dibuat')
        return cmd_create(args.file, args.template)
    elif act in ('cek','check'):
        return cmd_check(args.file)
    elif act in ('tes','test'):
        return cmd_test(args.file)
    elif act == 'info':
        return cmd_info()
    elif act == 'versi':
        print(f'Bahasa Manis {__version__}')
        return 0
    elif act in ('diagnosa','diagnose'):
        cmd_diagnose()
        return 0
    else:
        repl()
        return 0

if __name__ == '__main__':
    sys.exit(main())
