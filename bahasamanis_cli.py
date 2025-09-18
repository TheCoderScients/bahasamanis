#!/usr/bin/env python3
"""
CLI untuk Bahasa Manis (BM)
Perintah:
  bm run file.bm
  bm transpile file.bm -o file.py
"""
import sys
import argparse
from bahasamanis import Interpreter, transpile_to_python

def cmd_run(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()
    interp = Interpreter()
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

def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(prog='bm', description='BahasaManis CLI')
    parser.add_argument('action', choices=['run','transpile'], help='aksi yang dijalankan')
    parser.add_argument('file', help='file sumber .bm')
    parser.add_argument('--out','-o', help='file output (untuk transpile)')
    args = parser.parse_args(argv)
    if args.action == 'run':
        cmd_run(args.file)
    else:
        cmd_transpile(args.file, args.out)

if __name__ == '__main__':
    main()
