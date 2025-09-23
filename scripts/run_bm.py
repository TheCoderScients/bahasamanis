from __future__ import annotations
import sys
from bahasamanis import Interpreter


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: run_bm.py <file.bm>", flush=True)
        return 1
    path = sys.argv[1]

    # Pastikan stdout tidak buffering
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    interp = Interpreter()
    # Jangan menunggu input agar contoh tidak macet
    try:
        interp.input_func = lambda: ""
    except Exception:
        pass

    print(f"[RUN] {path}", flush=True)
    try:
        with open(path, "r", encoding="utf-8") as f:
            src = f.read()
        interp.run(src)
    except Exception as e:
        print("[Error]", e, flush=True)
        return 1
    print(f"[DONE] {path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
