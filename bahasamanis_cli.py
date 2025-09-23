#!/usr/bin/env python3
"""
CLI untuk Bahasa Manis (BM)
Perintah:
  bm run|jalankan file.bm
  bm transpile|ubah file.bm -o file.py
  bm repl
"""
import sys
import argparse
from pathlib import Path
from bahasamanis import Interpreter, transpile_to_python

def cmd_run(path: str):
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
    try:
        interp.run(src)
    except Exception as e:
        print('[Error]', e, file=sys.stderr)

def cmd_transpile(path: str, out: str | None = None):
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()
    py = transpile_to_python(src)
    if out:
        with open(out, 'w', encoding='utf-8') as f:
            f.write(py)
        print('Tersimpan ->', out)
    else:
        print(py)

def repl():
    print('BM REPL — ketik "keluar" untuk berhenti. Gunakan kata kunci BM seperti cetak/baca/jika/akhir.')
    interp = Interpreter()
    buffer = []
    def is_block_complete(lines):
        # sederhana: jika jumlah 'akhir' >= jumlah pembuka ('fungsi','jika','selama','untuk')
        opens = 0
        for ln in lines:
            s = ln.strip()
            if s.startswith('fungsi ') or s.startswith('jika ') or s.startswith('selama ') or s.startswith('untuk '):
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

def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(prog='bm', description='BahasaManis CLI')
    parser.add_argument('action', choices=['run','transpile','jalankan','ubah','repl'], help='aksi yang dijalankan')
    parser.add_argument('file', nargs='?', help='file sumber .bm (untuk run/transpile)')
    parser.add_argument('--out','-o', help='file output (untuk transpile/ubah)')
    args = parser.parse_args(argv)
    act = args.action
    if act in ('run','jalankan'):
        if not args.file:
            parser.error('butuh FILE untuk dijalankan')
        cmd_run(args.file)
    elif act in ('transpile','ubah'):
        if not args.file:
            parser.error('butuh FILE untuk diubah')
        cmd_transpile(args.file, args.out)
    else:
        repl()

if __name__ == '__main__':
    main()
