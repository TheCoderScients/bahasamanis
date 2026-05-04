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
  bm bangun [path]
  bm paket [path]
  bm bersih [path]
  bm info
  bm versi
"""
import sys
import argparse
import shutil
import re
from pathlib import Path
from bahasamanis import __version__, Interpreter, parse_program, transpile_to_python

SKIP_DIRS = {'.git', '.hg', '.svn', '.venv', 'venv', '__pycache__', 'dist', 'build'}
MAIN_FILE_NAMES = ('utama.bm', 'main.bm', 'app.bm', 'program.bm')
BM_TOML_FORMAT = '1'
KNOWN_CONFIG_SECTIONS = {'proyek', 'cek', 'tes', 'ubah', 'bangun'}
KNOWN_CONFIG_KEYS = {
    'proyek': {'format', 'nama', 'versi', 'utama'},
    'cek': {'path', 'ketat'},
    'tes': {'path'},
    'ubah': {'output'},
    'bangun': {'output', 'cek', 'ketat'},
}
CLEAN_DIRS = {'__pycache__', '.pytest_cache', 'build', 'dist'}
CLEAN_DIR_SUFFIXES = ('.egg-info',)
CLEAN_SUFFIXES = {'.pyc', '.pyo'}

def find_project_root(start: Path | None = None) -> Path | None:
    current = (start or Path.cwd()).resolve()
    if current.is_file():
        current = current.parent
    for path in [current, *current.parents]:
        if (path / 'bm.toml').is_file():
            return path
    return None

def parse_config_value(value: str) -> object:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    lowered = value.lower()
    if lowered in ('true', 'benar', 'ya', 'yes'):
        return True
    if lowered in ('false', 'salah', 'tidak', 'no'):
        return False
    return value

def parse_bm_toml(path: Path) -> dict[str, dict[str, object]]:
    config: dict[str, dict[str, object]] = {}
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
        config.setdefault(section, {})[key] = parse_config_value(value)
    return config

def load_project(start: Path | None = None) -> tuple[Path, dict[str, dict[str, object]]] | None:
    root = find_project_root(start)
    if root is None:
        return None
    return root, parse_bm_toml(root / 'bm.toml')

def project_value(config: dict[str, dict[str, object]], section: str, key: str, default: str) -> str:
    return str(config.get(section, {}).get(key, default))

def project_bool(config: dict[str, dict[str, object]], section: str, key: str, default: bool) -> bool:
    value = config.get(section, {}).get(key, default)
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in ('1', 'true', 'benar', 'ya', 'yes'):
        return True
    if text in ('0', 'false', 'salah', 'tidak', 'no'):
        return False
    return default

def validate_project_config(root: Path, config: dict[str, dict[str, object]]):
    errors: list[str] = []
    warnings: list[str] = []
    project_config = config.get('proyek', {})
    for key in ('nama', 'versi', 'utama'):
        if not project_config.get(key):
            errors.append(f"bm.toml: [proyek].{key} wajib diisi.")
    fmt = project_value(config, 'proyek', 'format', BM_TOML_FORMAT)
    if fmt != BM_TOML_FORMAT:
        errors.append(f"bm.toml: format '{fmt}' belum didukung. Pakai format \"{BM_TOML_FORMAT}\".")
    main_path = root / project_value(config, 'proyek', 'utama', 'src/utama.bm')
    if project_config.get('utama') and not main_path.is_file():
        errors.append(f"bm.toml: file utama tidak ditemukan: {rel_display(main_path, root)}")
    for section, values in config.items():
        if section not in KNOWN_CONFIG_SECTIONS:
            warnings.append(f"bm.toml: section [{section}] belum dikenal dan akan diabaikan.")
            continue
        for key in values:
            if key not in KNOWN_CONFIG_KEYS[section]:
                warnings.append(f"bm.toml: field [{section}].{key} belum dikenal dan akan diabaikan.")
    return errors, warnings

def print_project_config_notes(root: Path, config: dict[str, dict[str, object]]) -> bool:
    errors, warnings = validate_project_config(root, config)
    for warning in warnings:
        print(f"WARN {warning}", file=sys.stderr)
    for error in errors:
        print(f"ERR  {error}", file=sys.stderr)
    return not errors

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

def is_test_file(path: Path) -> bool:
    name = path.name.lower()
    return (
        name.startswith('tes_')
        or name.startswith('test_')
        or name.endswith('_tes.bm')
        or name.endswith('_test.bm')
    )

def iter_test_files(target: Path):
    if target.is_file():
        return [target] if target.suffix == '.bm' and is_test_file(target) else []
    if not target.exists():
        return []
    files = []
    tests_dir = target / 'tests'
    if tests_dir.is_dir():
        files.extend(iter_bm_files(tests_dir))
    files.extend(path for path in iter_bm_files(target) if is_test_file(path))
    seen = set()
    unique = []
    for path in files:
        key = str(path.resolve())
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique

def infer_main_file(root: Path | None = None) -> Path | None:
    root = (root or Path.cwd()).resolve()
    for name in MAIN_FILE_NAMES:
        candidate = root / name
        if candidate.is_file():
            return candidate
    for name in MAIN_FILE_NAMES:
        candidate = root / 'src' / name
        if candidate.is_file():
            return candidate
    top_level = sorted(path for path in root.glob('*.bm') if path.is_file())
    if len(top_level) == 1:
        return top_level[0]
    return None

def rel_display(path: Path, root: Path | None = None) -> str:
    base = (root or Path.cwd()).resolve()
    try:
        return str(path.resolve().relative_to(base))
    except ValueError:
        return str(path)

def strip_comment(line: str) -> str:
    out = []
    inq = False
    quote = ''
    escaped = False
    for ch in line:
        if escaped:
            escaped = False
            out.append(' ' if inq else ch)
            continue
        if ch == '\\' and inq:
            escaped = True
            out.append(' ')
            continue
        if ch in "\"'":
            if inq and ch == quote:
                inq = False
                quote = ''
            elif not inq:
                inq = True
                quote = ch
            out.append(' ')
            continue
        if ch == '#' and not inq:
            break
        out.append(' ' if inq else ch)
    return ''.join(out)

def strict_warnings(file: Path, src: str):
    warnings = []
    for lineno, raw in enumerate(src.splitlines(), start=1):
        code = strip_comment(raw)
        if raw.rstrip() != raw:
            warnings.append((lineno, 'hapus spasi kosong di akhir baris'))
        if re.search(r'\belif\b', code):
            warnings.append((lineno, 'pakai `lain jika`, bukan alias Inggris `elif`'))
        if re.search(r'\basync\b', code):
            warnings.append((lineno, 'pakai `asinkron`, bukan alias Inggris `async`'))
    return warnings

def keep_code_before_comment(line: str) -> str:
    out = []
    inq = False
    quote = ''
    escaped = False
    for ch in line:
        if escaped:
            escaped = False
            out.append(ch)
            continue
        if ch == '\\' and inq:
            escaped = True
            out.append(ch)
            continue
        if ch in "\"'":
            if inq and ch == quote:
                inq = False
                quote = ''
            elif not inq:
                inq = True
                quote = ch
            out.append(ch)
            continue
        if ch == '#' and not inq:
            break
        out.append(ch)
    return ''.join(out)

def scan_package_usage(file: Path):
    usage = []
    pkg_re = re.compile(r'^paket\s+(["\'])([^"\']+)\1\s*(?:(?:sebagai|as)\s*([A-Za-z_][A-Za-z0-9_]*))?\s*$')
    bm_re = re.compile(r'^pakai\s+(["\'])([^"\']+)\1\s*(?:(?:sebagai|as)\s*([A-Za-z_][A-Za-z0-9_]*))?\s*$')
    for lineno, raw in enumerate(file.read_text(encoding='utf-8').splitlines(), start=1):
        line = keep_code_before_comment(raw).strip()
        if not line:
            continue
        match_pkg = pkg_re.match(line)
        if match_pkg:
            module = match_pkg.group(2)
            alias = match_pkg.group(3) or module.split('.')[-1]
            usage.append(('python', module, alias, file, lineno))
            continue
        match_bm = bm_re.match(line)
        if match_bm:
            module = match_bm.group(2)
            alias = match_bm.group(3) or ''
            usage.append(('bm', module, alias, file, lineno))
    return usage

def bm_module_kind(name: str) -> str:
    if name.startswith('bm_standar/'):
        return 'standar'
    if name.startswith('.') or '/' in name or name.endswith('.bm'):
        return 'lokal'
    return 'modul'

def print_package_group(title: str, records, root: Path, is_bm: bool):
    print(title)
    if not records:
        print('- tidak ada')
        return
    grouped = {}
    for _, module, alias, file, lineno in records:
        item = grouped.setdefault(module, {'aliases': set(), 'locations': []})
        if alias:
            item['aliases'].add(alias)
        item['locations'].append((file, lineno))
    for module in sorted(grouped):
        item = grouped[module]
        alias_text = ''
        if item['aliases']:
            alias_text = ' alias: ' + ', '.join(sorted(item['aliases']))
        kind_text = f" ({bm_module_kind(module)})" if is_bm else ''
        print(f"- {module}{kind_text}{alias_text} - {len(item['locations'])} pemakaian")
        for file, lineno in item['locations'][:5]:
            print(f"  di {rel_display(file, root)}:{lineno}")
        if len(item['locations']) > 5:
            print(f"  dan {len(item['locations']) - 5} lokasi lain")

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
        if project:
            root, config = project
            path = str(root / project_value(config, 'proyek', 'utama', 'src/utama.bm'))
        else:
            inferred = infer_main_file()
            if not inferred:
                print("[Error] Butuh FILE untuk dijalankan, atau sediakan satu file utama seperti utama.bm/main.bm.", file=sys.stderr)
                return 1
            path = str(inferred)
    try:
        run_bm_file(Path(path))
    except Exception as e:
        print('[Error]', e, file=sys.stderr)
        return 1
    return 0

def cmd_transpile(path: str | None = None, out: str | None = None) -> int:
    project = None
    if not path:
        project = load_project()
        if project:
            root, config = project
            path = str(root / project_value(config, 'proyek', 'utama', 'src/utama.bm'))
        else:
            inferred = infer_main_file()
            if not inferred:
                print("[Error] Butuh FILE untuk diubah, atau sediakan satu file utama seperti utama.bm/main.bm.", file=sys.stderr)
                return 1
            path = str(inferred)
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()
    py = transpile_to_python(src)
    if out is None and project:
        root, config = project
        default_out = 'build/' + Path(path).with_suffix('.py').name
        out = str(root / project_value(config, 'ubah', 'output', default_out))
    if out:
        out_path = Path(out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(py)
        print('Tersimpan ->', out_path)
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
            f'format = "{BM_TOML_FORMAT}"',
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
            '[ubah]',
            'output = "build/utama.py"',
            '',
            '[bangun]',
            'output = "build/utama.py"',
            'cek = true',
            'ketat = false',
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
            'bm ubah',
            'bm bangun',
            'bm paket',
            '```',
            '',
        ]),
        encoding='utf-8',
    )
    (root / '.gitignore').write_text('__pycache__/\n*.pyc\n.pytest_cache/\nbuild/\ndist/\n', encoding='utf-8')
    print(f"Proyek '{root}' dibuat.")
    print(f"Jalankan: cd {root} && bm jalankan")
    return 0

def cmd_check(path: str | None = None, strict: bool = False) -> int:
    project = load_project()
    if path:
        target = Path(path)
    elif project:
        root, config = project
        if not print_project_config_notes(root, config):
            return 1
        if project_bool(config, 'cek', 'ketat', False):
            strict = True
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
            warnings = strict_warnings(file, src) if strict else []
            if warnings:
                failed += 1
                print(f"ERR {file}: mode ketat menemukan {len(warnings)} peringatan", file=sys.stderr)
                for lineno, message in warnings:
                    print(f"  baris {lineno}: {message}", file=sys.stderr)
                continue
            print(f"OK  {file}")
        except Exception as e:
            failed += 1
            print(f"ERR {file}: {e}", file=sys.stderr)
    if failed:
        print(f"{failed} file bermasalah.", file=sys.stderr)
        return 1
    mode = "ketat" if strict else "normal"
    print(f"{len(files)} file BM valid ({mode}).")
    return 0

def cmd_test(path: str | None = None) -> int:
    project = load_project()
    if path:
        target = Path(path)
    elif project:
        root, config = project
        target = root / project_value(config, 'tes', 'path', 'tests')
    else:
        target = Path.cwd()
    if path and target.is_dir() and (target / 'tests').is_dir():
        target = target / 'tests'
    files = iter_bm_files(target) if project or path else iter_test_files(target)
    if not files:
        if project or path:
            print(f"[Error] Tidak ada test .bm di '{target}'.", file=sys.stderr)
            return 1
        print("Belum ada test .bm di folder ini. Buat tests/tes_utama.bm atau pakai `bm cek` untuk validasi cepat.")
        return 0
    failed = 0
    passed = 0
    for file in files:
        try:
            run_bm_file(file)
            passed += 1
            print(f"LULUS {file}")
        except Exception as e:
            failed += 1
            print(f"GAGAL {file}: {e}", file=sys.stderr)
    if failed:
        print(f"Ringkasan tes: {passed} lulus, {failed} gagal, {len(files)} total.", file=sys.stderr)
        return 1
    print(f"Ringkasan tes: {passed} lulus, 0 gagal, {len(files)} total.")
    return 0

def cmd_build(path: str | None = None, out: str | None = None, strict: bool = False) -> int:
    project = load_project(Path(path)) if path and Path(path).is_dir() else load_project()
    config: dict[str, dict[str, object]] = {}
    root = Path.cwd().resolve()
    if project:
        root, config = project
    if path and Path(path).is_file():
        main_path = Path(path)
    elif project:
        if not print_project_config_notes(root, config):
            return 1
        main_path = root / project_value(config, 'proyek', 'utama', 'src/utama.bm')
    else:
        inferred = infer_main_file(root)
        if not inferred:
            print("[Error] Butuh FILE atau proyek bm.toml untuk dibangun.", file=sys.stderr)
            return 1
        main_path = inferred

    if not main_path.is_file():
        print(f"[Error] File utama tidak ditemukan: {main_path}", file=sys.stderr)
        return 1

    run_check = project_bool(config, 'bangun', 'cek', True) if project else True
    strict = strict or (project_bool(config, 'bangun', 'ketat', False) if project else False)
    if run_check:
        check_target = root / project_value(config, 'cek', 'path', '.') if project else main_path
        files = iter_bm_files(check_target)
        failed = 0
        for file in files:
            try:
                src = file.read_text(encoding='utf-8')
                parse_program(src)
                warnings = strict_warnings(file, src) if strict else []
                if warnings:
                    failed += 1
                    print(f"ERR {file}: mode ketat menemukan {len(warnings)} peringatan", file=sys.stderr)
                    for lineno, message in warnings:
                        print(f"  baris {lineno}: {message}", file=sys.stderr)
                    continue
            except Exception as e:
                failed += 1
                print(f"ERR {file}: {e}", file=sys.stderr)
        if failed:
            print(f"Bangun dibatalkan: {failed} file bermasalah.", file=sys.stderr)
            return 1
        mode = "ketat" if strict else "normal"
        print(f"Cek build lulus: {len(files)} file BM valid ({mode}).")

    default_output = 'build/' + main_path.with_suffix('.py').name
    if project:
        default_output = project_value(config, 'bangun', 'output', project_value(config, 'ubah', 'output', default_output))
    output_path = Path(out) if out else root / default_output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    src = main_path.read_text(encoding='utf-8')
    output_path.write_text(transpile_to_python(src), encoding='utf-8')
    print(f"Bangun selesai -> {output_path}")
    print(f"Jalankan hasil: python {output_path}")
    return 0

def cmd_package(path: str | None = None) -> int:
    project = load_project(Path(path)) if path and Path(path).is_dir() else load_project()
    root = Path.cwd().resolve()
    config: dict[str, dict[str, object]] = {}
    if project:
        root, config = project
    if path:
        target = Path(path)
    elif project:
        if not print_project_config_notes(root, config):
            return 1
        target = root / project_value(config, 'cek', 'path', '.')
    else:
        target = root
    files = iter_bm_files(target)
    if not files:
        print(f"[Error] Tidak ada file .bm di '{target}'.", file=sys.stderr)
        return 1

    records = []
    failed = 0
    for file in files:
        try:
            records.extend(scan_package_usage(file))
        except Exception as e:
            failed += 1
            print(f"ERR {file}: {e}", file=sys.stderr)
    if failed:
        print(f"{failed} file gagal dibaca.", file=sys.stderr)
        return 1

    bm_records = [record for record in records if record[0] == 'bm']
    py_records = [record for record in records if record[0] == 'python']
    name = project_value(config, 'proyek', 'nama', root.name) if project else rel_display(target, root)
    print('Paket Bahasa Manis')
    print(f'Proyek      : {name}')
    print(f'Target      : {rel_display(target, root)}')
    print(f'File BM     : {len(files)}')
    print_package_group('Modul BM:', bm_records, root, True)
    print_package_group('Paket Python:', py_records, root, False)
    print(f"Ringkasan   : {len(set(record[1] for record in bm_records))} modul BM, {len(set(record[1] for record in py_records))} paket Python")
    return 0

def cmd_clean(path: str | None = None) -> int:
    project = load_project()
    if path:
        root = Path(path)
    elif project:
        root = project[0]
    else:
        root = Path.cwd()
    if not root.exists():
        print(f"[Error] Path '{root}' tidak ditemukan.", file=sys.stderr)
        return 1
    removed = 0
    for target in sorted(root.rglob('*'), key=lambda p: len(p.parts), reverse=True):
        if target.is_dir() and (target.name in CLEAN_DIRS or target.name.endswith(CLEAN_DIR_SUFFIXES)):
            shutil.rmtree(target)
            print(f"Hapus folder: {target}")
            removed += 1
        elif target.is_file() and target.suffix in CLEAN_SUFFIXES:
            target.unlink()
            print(f"Hapus file: {target}")
            removed += 1
    print(f"Bersih selesai. {removed} item dihapus.")
    return 0

def cmd_info() -> int:
    project = load_project()
    if not project:
        root = Path.cwd().resolve()
        files = iter_bm_files(root)
        tests = iter_test_files(root)
        main_file = infer_main_file(root)
        print('Mode        : folder biasa (tanpa bm.toml)')
        print(f'Folder      : {root}')
        print(f'File BM     : {len(files)}')
        if main_file:
            print(f'File utama  : {rel_display(main_file, root)}')
            print('Jalankan    : bm jalankan')
        else:
            print('File utama  : belum tertebak')
            print('Jalankan    : bm jalankan nama_file.bm')
        print(f'Test BM     : {len(tests)}')
        print('Cek         : bm cek')
        print('Catatan     : buat bm.toml dengan `bm buat nama_proyek` untuk mode proyek penuh.')
        return 0
    root, config = project
    config_ok = print_project_config_notes(root, config)
    format_version = project_value(config, 'proyek', 'format', BM_TOML_FORMAT)
    name = project_value(config, 'proyek', 'nama', root.name)
    version = project_value(config, 'proyek', 'versi', '-')
    main_file = project_value(config, 'proyek', 'utama', 'src/utama.bm')
    check_path = project_value(config, 'cek', 'path', '.')
    test_path = project_value(config, 'tes', 'path', 'tests')
    output_path = project_value(config, 'ubah', 'output', 'build/utama.py')
    build_path = project_value(config, 'bangun', 'output', output_path)
    build_check = 'ya' if project_bool(config, 'bangun', 'cek', True) else 'tidak'
    build_strict = 'ya' if project_bool(config, 'bangun', 'ketat', False) else 'tidak'
    print(f'Proyek      : {name}')
    print(f'Versi       : {version}')
    print(f'Format      : bm.toml v{format_version}')
    print(f'Root        : {root}')
    print(f'File utama  : {main_file}')
    print(f'Cek path    : {check_path}')
    print(f'Test path   : {test_path}')
    print(f'Output ubah : {output_path}')
    print(f'Output bangun: {build_path}')
    print(f'Cek bangun  : {build_check}')
    print(f'Ketat bangun: {build_strict}')
    return 0 if config_ok else 1

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
    parser.add_argument('action', choices=['jalankan','ubah','interaktif','versi','diagnosa','buat','bikin','cek','tes','bangun','paket','bersih','info','run','transpile','repl','diagnose','new','check','test','build','package','packages','deps','clean'], help='aksi: jalankan, ubah, buat, cek, tes, bangun, paket, bersih, info, interaktif, versi, atau diagnosa')
    parser.add_argument('file', nargs='?', help='file sumber .bm')
    parser.add_argument('--out','-o', help='file hasil Python untuk perintah ubah')
    parser.add_argument('--template', default='cli', help='template untuk perintah buat (default: cli)')
    parser.add_argument('--ketat', '--strict', action='store_true', help='mode cek ketat untuk CI')
    args = parser.parse_intermixed_args(argv)
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
        return cmd_check(args.file, args.ketat)
    elif act in ('tes','test'):
        return cmd_test(args.file)
    elif act in ('bangun','build'):
        return cmd_build(args.file, args.out, args.ketat)
    elif act in ('paket','package','packages','deps'):
        return cmd_package(args.file)
    elif act in ('bersih','clean'):
        return cmd_clean(args.file)
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
