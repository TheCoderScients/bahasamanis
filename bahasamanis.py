# BahasaManis interpreter + transpiler (v3) - save as bahasamanis.py
from __future__ import annotations
import ast, re, traceback, os, asyncio, inspect
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

__version__ = "0.2.0b1"

# --- Exceptions & statement classes ---
class BMError(Exception): pass
class ReturnException(Exception):
    def __init__(self, value): self.value = value
class BreakException(Exception): pass
class ContinueException(Exception): pass

class Stmt: pass
class PrintStmt(Stmt):
    def __init__(self, expr:str, lineno:int): self.expr=expr; self.lineno=lineno
class InputStmt(Stmt):
    def __init__(self, varname:str, lineno:int): self.varname=varname; self.lineno=lineno
class PromptInputStmt(Stmt):
    def __init__(self, prompt_expr:str, varname:str, lineno:int):
        self.prompt_expr=prompt_expr; self.varname=varname; self.lineno=lineno
class AssignStmt(Stmt):
    def __init__(self, target:str, expr:str, lineno:int): self.target=target; self.expr=expr; self.lineno=lineno
class ReturnStmt(Stmt):
    def __init__(self, expr:Optional[str], lineno:int): self.expr=expr; self.lineno=lineno
class ExprStmt(Stmt):
    def __init__(self, expr:str, lineno:int): self.expr=expr; self.lineno=lineno
class IfStmt(Stmt):
    def __init__(self, branches:List[Tuple[Optional[str], List[Stmt]]], lineno:int):
        self.branches = branches; self.lineno = lineno
class SwitchStmt(Stmt):
    def __init__(self, expr:str, cases:List[Tuple[Optional[str], List[Stmt]]], lineno:int):
        self.expr=expr; self.cases=cases; self.lineno=lineno
class WhileStmt(Stmt):
    def __init__(self, cond:str, body:List[Stmt], lineno:int): self.cond=cond; self.body=body; self.lineno=lineno
class ForStmt(Stmt):
    def __init__(self, var:str, start:str, end:str, body:List[Stmt], lineno:int):
        self.var=var; self.start=start; self.end=end; self.body=body; self.lineno=lineno
class ForEachStmt(Stmt):
    def __init__(self, var:str, iterable:str, body:List[Stmt], lineno:int):
        self.var=var; self.iterable=iterable; self.body=body; self.lineno=lineno
class RepeatStmt(Stmt):
    def __init__(self, count:str, body:List[Stmt], lineno:int):
        self.count=count; self.body=body; self.lineno=lineno
class FuncDef(Stmt):
    def __init__(self, name:str, args:List[str], body:List[Stmt], lineno:int):
        self.name=name; self.args=args; self.body=body; self.lineno=lineno
class AsyncFuncDef(FuncDef): pass
class ClassDef(Stmt):
    def __init__(self, name:str, body:List[Stmt], lineno:int):
        self.name=name; self.body=body; self.lineno=lineno
class TryStmt(Stmt):
    def __init__(self, body:List[Stmt], error_name:Optional[str], catch_body:Optional[List[Stmt]], finally_body:Optional[List[Stmt]], lineno:int):
        self.body=body; self.error_name=error_name; self.catch_body=catch_body; self.finally_body=finally_body; self.lineno=lineno
class RaiseStmt(Stmt):
    def __init__(self, expr:str, lineno:int): self.expr=expr; self.lineno=lineno
class AwaitStmt(Stmt):
    def __init__(self, expr:str, lineno:int): self.expr=expr; self.lineno=lineno
class AwaitAssignStmt(Stmt):
    def __init__(self, target:str, expr:str, lineno:int): self.target=target; self.expr=expr; self.lineno=lineno

class ImportPkgStmt(Stmt):
    """paket "modul.python" sebagai alias"""
    def __init__(self, module:str, alias:str, lineno:int):
        self.module = module; self.alias = alias; self.lineno = lineno

class ImportBMStmt(Stmt):
    """pakai "path/to/modul.bm" [sebagai alias]"""
    def __init__(self, path:str, alias:Optional[str], lineno:int):
        self.path = path; self.alias = alias; self.lineno = lineno

# --- Expression safety using AST ---
_ALLOWED_NODES = {
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Name, ast.Load,
    ast.Call, ast.Compare, ast.BoolOp, ast.List, ast.Dict, ast.Tuple, ast.Subscript,
    ast.Index, ast.Slice, ast.Constant, ast.Attribute, ast.keyword
}
_ALLOWED_OPERATORS = {
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow, ast.FloorDiv,
    ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
    ast.In, ast.NotIn, ast.Is, ast.IsNot,
    ast.And, ast.Or, ast.Not, ast.USub, ast.UAdd
}

def _expr_to_python(expr: str) -> str:
    """Translate BM expression keywords without touching string literals."""
    mapping = {
        "benar": "True",
        "salah": "False",
        "kosong": "None",
        "dan": "and",
        "atau": "or",
        "tidak": "not",
        "dalam": "in",
    }
    try:
        import io, tokenize
        tokens = []
        for tok in tokenize.generate_tokens(io.StringIO(expr).readline):
            if tok.type == tokenize.NAME and tok.string in mapping:
                tok = tokenize.TokenInfo(tok.type, mapping[tok.string], tok.start, tok.end, tok.line)
            tokens.append(tok)
        return tokenize.untokenize(tokens)
    except Exception:
        replacements = [
            (r"\bbenar\b", "True"),
            (r"\bsalah\b", "False"),
            (r"\bkosong\b", "None"),
            (r"\bdan\b", " and "),
            (r"\batau\b", " or "),
            (r"\btidak\b", " not "),
            (r"\bdalam\b", " in "),
        ]
        e = expr
        for pat,repl in replacements:
            e = re.sub(pat, repl, e)
        return e

def _check_ast_nodes(node: ast.AST):
    for n in ast.walk(node):
        if isinstance(n, ast.Name) and n.id.startswith("__"):
            raise BMError(f"Nama khusus Python tidak diizinkan: {n.id}")
        if isinstance(n, ast.Attribute) and n.attr.startswith("__"):
            raise BMError(f"Atribut khusus Python tidak diizinkan: {n.attr}")
        if isinstance(n, ast.operator) and type(n) not in _ALLOWED_OPERATORS:
            raise BMError(f"Operator {type(n).__name__} tidak diizinkan")
        if type(n) not in _ALLOWED_NODES and not isinstance(n, tuple(_ALLOWED_OPERATORS)):
            raise BMError(f"Node AST tidak diizinkan: {type(n).__name__}")

def _translate_error_message(msg: str) -> str:
    """Terjemahkan sebagian besar frase error Python ke Bahasa Indonesia."""
    rules = [
        (r"was never closed", "tidak ditutup"),
        (r"unexpected EOF while parsing", "EOF tak terduga saat parsing"),
        (r"EOF while scanning triple-quoted string literal", "EOF saat memindai string tiga-kutip"),
        (r"unterminated string literal.*", "string tidak diakhiri"),
        (r"invalid syntax", "sintaks tidak valid"),
        (r"invalid literal for int\(\)\s*with base\s*\d+", "nilai tidak valid untuk int()"),
        (r"division or modulo by zero", "pembagian atau modulo dengan nol"),
        (r"division by zero", "pembagian dengan nol"),
        (r"name '([^']+)' is not defined", r"Variabel '\1' belum dibuat. Buat dulu dengan `\1 = ...`, `baca \1`, atau `tanya \"...\" sebagai \1`."),
        (r"unsupported operand type\(s\) for ([^:]+): '([^']+)' and '([^']+)'", r"tipe operan tidak didukung untuk \1: '\2' dan '\3'"),
        (r"'([^']+)' not supported between instances of '([^']+)' and '([^']+)'", r"operator '\1' tidak didukung antara tipe '\2' dan '\3'"),
        (r"object of type '([^']+)' has no len\(\)", r"objek bertipe '\1' tidak memiliki panjang"),
        (r"'([^']+)' object is not subscriptable", r"objek '\1' tidak bisa diindeks"),
        (r"list index out of range", "indeks daftar di luar jangkauan"),
    ]
    out = msg
    for pat, repl in rules:
        out = re.sub(pat, repl, out, flags=re.IGNORECASE)
    return out

def _friendly_value(value: Any) -> str:
    text = str(value)
    if len(text) > 60:
        text = text[:57] + "..."
    return text

def _interpolate_exprs(inner: str, env: Dict[str,Any]) -> str:
    """Interpolate {...} segments by safely evaluating each expression.
    Supports variables and expressions (including allowed function calls).
    """
    pattern = re.compile(r"{([^{}]+)}")
    def repl(m):
        expr = m.group(1)
        pyexpr = _expr_to_python(expr)
        try:
            node = ast.parse(pyexpr, mode="eval")
            _check_ast_nodes(node)
            safe_globals = {"__builtins__": {"__import__": __import__}}
            val = eval(compile(node, "<interp>", "eval"), safe_globals, env)
            return str(val)
        except SyntaxError:
            # Treat as literal (e.g., JSON fragments inside text)
            return '{' + expr + '}'
        except Exception as e:
            raise BMError(f"Kesalahan interpolasi string: {_translate_error_message(str(e))}")
    return pattern.sub(repl, inner)

def safe_eval(expr: str, env: Dict[str,Any]):
    s = expr.strip()
    pyexpr = _expr_to_python(expr)
    try:
        node = ast.parse(pyexpr, mode="eval")
    except SyntaxError as e:
        raise BMError(f"Kesalahan sintaks pada ekspresi `{expr}`: {_translate_error_message(str(e))}")
    _check_ast_nodes(node)
    if isinstance(node.body, ast.Constant) and isinstance(node.body.value, str):
        inner = node.body.value
        if "{" in inner and "}" in inner:
            # Evaluate expressions within {...} safely
            return _interpolate_exprs(inner, env)
        return inner
    safe_globals = {"__builtins__": {"__import__": __import__}}
    return eval(compile(node, "<expr>", "eval"), safe_globals, env)

def _bm_rapikan(nilai: Any) -> str:
    return str(nilai).strip()

def _bm_kecil(nilai: Any) -> str:
    return str(nilai).lower()

def _bm_besar(nilai: Any) -> str:
    return str(nilai).upper()

def _bm_angka(nilai: Any) -> int:
    try:
        return int(nilai)
    except Exception:
        raise BMError(f"angka() gagal: '{_friendly_value(nilai)}' bukan bilangan bulat")

def _bm_pecahan(nilai: Any) -> float:
    try:
        return float(nilai)
    except Exception:
        raise BMError(f"pecahan() gagal: '{_friendly_value(nilai)}' bukan bilangan pecahan")

def _bm_ganti(teks: Any, lama: Any, baru: Any) -> str:
    return str(teks).replace(str(lama), str(baru))

def _bm_pisah(teks: Any, pemisah: Any = None):
    if pemisah is None:
        return str(teks).split()
    return str(teks).split(str(pemisah))

def _bm_gabung(kumpulan: Any, pemisah: Any = "") -> str:
    return str(pemisah).join(kumpulan)

def _bm_mulai_dengan(teks: Any, awalan: Any) -> bool:
    return str(teks).startswith(str(awalan))

def _bm_berakhir_dengan(teks: Any, akhiran: Any) -> bool:
    return str(teks).endswith(str(akhiran))

def _bm_cari(teks: Any, bagian: Any) -> int:
    return str(teks).find(str(bagian))

def _bm_tambah(kumpulan: Any, nilai: Any):
    kumpulan.append(nilai)
    return kumpulan

def _bm_daftar(nilai: Any = None):
    if nilai is None:
        return []
    return list(nilai)

def _bm_kamus(nilai: Any = None):
    if nilai is None:
        return {}
    return dict(nilai)

def _bm_berisi(kumpulan: Any, nilai: Any) -> bool:
    return nilai in kumpulan

def _bm_ambil(kumpulan: Any, kunci: Any, bawaan: Any = None):
    if isinstance(kumpulan, dict):
        return kumpulan.get(kunci, bawaan)
    try:
        return kumpulan[kunci]
    except Exception:
        return bawaan

def _bm_atur(kumpulan: Any, kunci: Any, nilai: Any):
    kumpulan[kunci] = nilai
    return kumpulan

def _bm_hapus(kumpulan: Any, nilai: Any):
    if isinstance(kumpulan, dict):
        kumpulan.pop(nilai, None)
        return kumpulan
    try:
        kumpulan.remove(nilai)
    except ValueError:
        pass
    return kumpulan

def _bm_urutkan(kumpulan: Any):
    return sorted(kumpulan)

def _bm_balik(kumpulan: Any):
    if isinstance(kumpulan, str):
        return kumpulan[::-1]
    return list(reversed(kumpulan))

def _bm_kunci(kamus: Any):
    return list(kamus.keys())

def _bm_nilai(kamus: Any):
    return list(kamus.values())

def _bm_pasangan(kamus: Any):
    return list(kamus.items())

def _bm_salin(nilai: Any):
    if hasattr(nilai, "copy"):
        return nilai.copy()
    return nilai

def _bm_baca_berkas(path: Any) -> str:
    return Path(str(path)).read_text(encoding="utf-8")

def _bm_baca_baris(path: Any):
    return Path(str(path)).read_text(encoding="utf-8").splitlines()

def _bm_tulis_berkas(path: Any, isi: Any) -> str:
    Path(str(path)).write_text(str(isi), encoding="utf-8")
    return str(path)

def _bm_tambah_berkas(path: Any, isi: Any) -> str:
    with Path(str(path)).open("a", encoding="utf-8") as f:
        f.write(str(isi))
    return str(path)

def _bm_ada_berkas(path: Any) -> bool:
    return Path(str(path)).exists()

def _bm_hapus_berkas(path: Any) -> bool:
    p = Path(str(path))
    if p.exists() and p.is_file():
        p.unlink()
        return True
    return False

def _bm_daftar_berkas(path: Any = "."):
    return [p.name for p in Path(str(path)).iterdir()]

def _bm_fitur_dinonaktifkan(nama: str):
    def _inner(*args, **kwargs):
        raise BMError(f"Fitur '{nama}' dimatikan di mode aman")
    return _inner

class BMClass:
    def __init__(self, interpreter: "Interpreter", name: str, methods: Dict[str, FuncDef]):
        self.interpreter = interpreter
        self.name = name
        self.methods = methods

    def __call__(self, *args, **kwargs):
        instance = BMInstance(self)
        initializer = self.methods.get("mulai")
        if initializer:
            result = self.interpreter._call_method(initializer, instance, args, kwargs)
            if inspect.isawaitable(result):
                asyncio.run(result)
        return instance

    def __repr__(self):
        return f"<kelas {self.name}>"

class BMInstance:
    def __init__(self, bm_class: BMClass):
        object.__setattr__(self, "_bm_class", bm_class)
        object.__setattr__(self, "_bm_attrs", {})

    def __getattr__(self, name: str):
        attrs = object.__getattribute__(self, "_bm_attrs")
        if name in attrs:
            return attrs[name]
        bm_class = object.__getattribute__(self, "_bm_class")
        if name in bm_class.methods:
            fdef = bm_class.methods[name]
            def bound(*args, **kwargs):
                return bm_class.interpreter._call_method(fdef, self, args, kwargs)
            return bound
        raise AttributeError(f"atribut '{name}' tidak ditemukan")

    def __setattr__(self, name: str, value: Any):
        object.__getattribute__(self, "_bm_attrs")[name] = value

    def __repr__(self):
        bm_class = object.__getattribute__(self, "_bm_class")
        return f"<objek {bm_class.name}>"

# --- Parser ---
def _strip_inline_comment(line: str) -> str:
    inq = False
    qchar = None
    escaped = False
    for i, ch in enumerate(line):
        if escaped:
            escaped = False
            continue
        if ch == "\\" and inq:
            escaped = True
            continue
        if ch in "\"'":
            if inq and ch == qchar:
                inq = False
                qchar = None
            elif not inq:
                inq = True
                qchar = ch
            continue
        if ch == "#" and not inq:
            return line[:i]
    return line

def _split_eq_outside_quotes(s:str):
    depth=0; inq=False; qchar=None
    for i,ch in enumerate(s):
        if ch in "\"'":
            if inq and ch==qchar:
                inq=False; qchar=None
            elif not inq:
                inq=True; qchar=ch
            continue
        if inq: continue
        if ch in "([{": depth+=1
        elif ch in ")]}": depth-=1
        elif ch=="=" and depth==0:
            if i+1<len(s) and s[i+1]=="=": continue
            left=s[:i].strip(); right=s[i+1:].strip(); return left,right
    return s.strip(), None

def parse_program(src:str):
    raw_lines = src.splitlines()
    lines=[]
    for idx,ln in enumerate(raw_lines, start=1):
        s = _strip_inline_comment(ln).strip()
        if not s or s.startswith("#"): continue
        lines.append((idx,s))
    i=0; n=len(lines)
    def is_elif_line(txt: str) -> bool:
        return txt.startswith("elif ") or txt.startswith("lain jika ")
    def is_block_start(txt: str) -> bool:
        return (
            txt.startswith("fungsi ")
            or txt.startswith("fungsi asinkron ")
            or txt.startswith("fungsi async ")
            or txt.startswith("asinkron fungsi ")
            or txt.startswith("async fungsi ")
            or txt.startswith("kelas ")
            or txt == "coba"
            or txt == "coba maka"
            or txt.startswith("jika ")
            or txt.startswith("pilih ")
            or txt.startswith("selama ")
            or txt.startswith("untuk ")
            or txt.startswith("setiap ")
            or txt.startswith("ulangi ")
        )
    def collect_until_akhir(block_name: str = "blok", opener_line: Optional[int] = None):
        nonlocal i
        collected=[]
        depth = 0
        closed = False
        while i < n:
            lnno, nxt = lines[i]
            if nxt == "akhir" and depth == 0:
                i += 1; closed = True; break
            collected.append((lnno, nxt)); i += 1
            if nxt == "akhir" and depth > 0:
                depth -= 1; continue
            if is_block_start(nxt):
                depth += 1; continue
        if not closed:
            info_baris = f" pada baris {opener_line}" if opener_line is not None else ""
            raise BMError(f"Blok `{block_name}`{info_baris} belum ditutup dengan `akhir`")
        return collected
    def top_level_separator_indices(collected, predicate):
        sep_indices = []
        depth = 0
        for idxc, (lnno, txt) in enumerate(collected):
            if txt == "akhir" and depth > 0:
                depth -= 1
                continue
            if depth == 0 and predicate(txt):
                sep_indices.append((idxc, lnno, txt))
                continue
            if is_block_start(txt):
                depth += 1
        return sep_indices
    def parse_block_from_list(sub_lines):
        src = "\n".join(l for (_,l) in sub_lines)
        return parse_program(src)
    def parse_block(stop_tokens=None, opener_name: Optional[str] = None, opener_line: Optional[int] = None):
        nonlocal i
        stmts=[]
        while i<n:
            lineno, line = lines[i]; i+=1
            if stop_tokens and line in stop_tokens:
                return stmts
            if line == "akhir":
                raise BMError(f"`akhir` pada baris {lineno} tidak punya pembuka blok")
            if line == "lain" or is_elif_line(line):
                raise BMError(f"`{line}` pada baris {lineno} harus berada di dalam blok `jika`")
            if line.startswith("saat ") or line == "bawaan":
                raise BMError(f"`{line}` pada baris {lineno} harus berada di dalam blok `pilih`")
            if line.startswith("tangkap") or line == "akhirnya":
                raise BMError(f"`{line}` pada baris {lineno} harus berada di dalam blok `coba`")
            # paket "modul" (sebagai alias)?
            m = re.match(r'^paket\s+(["\"][^"\"]+["\"])\s*(?:sebagai|as)\s*([A-Za-z_][A-Za-z0-9_]*)\s*$', line)
            if m:
                mod = m.group(1)[1:-1]
                alias = m.group(2)
                stmts.append(ImportPkgStmt(mod, alias, lineno)); continue
            m = re.match(r'^paket\s+(["\"][^"\"]+["\"])\s*$', line)
            if m:
                mod = m.group(1)[1:-1]
                alias = mod.split('.')[-1]
                stmts.append(ImportPkgStmt(mod, alias, lineno)); continue
            # pakai "file.bm" (sebagai alias)?
            m = re.match(r'^pakai\s+(["\"][^"\"]+["\"])\s*(?:(sebagai|as)\s*([A-Za-z_][A-Za-z0-9_]*))?\s*$', line)
            if m:
                path = m.group(1)[1:-1]
                alias = m.group(3) if m.group(2) else None
                stmts.append(ImportBMStmt(path, alias, lineno)); continue
            m = re.match(r"^(?:fungsi\s+(?:asinkron|async)|(?:asinkron|async)\s+fungsi)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\((.*?)\)\s*$", line)
            if m:
                name=m.group(1); args_str=m.group(2).strip()
                args=[a.strip() for a in args_str.split(",")] if args_str else []
                body = parse_block(stop_tokens=["akhir"], opener_name=f"asinkron fungsi {name}", opener_line=lineno)
                stmts.append(AsyncFuncDef(name,args,body,lineno)); continue
            m = re.match(r"^fungsi\s+([A-Za-z_][A-Za-z0-9_]*)\s*\((.*?)\)\s*$", line)
            if m:
                name=m.group(1); args_str=m.group(2).strip()
                args=[a.strip() for a in args_str.split(",")] if args_str else []
                body = parse_block(stop_tokens=["akhir"], opener_name=f"fungsi {name}", opener_line=lineno)
                stmts.append(FuncDef(name,args,body,lineno)); continue
            m = re.match(r"^kelas\s+([A-Za-z_][A-Za-z0-9_]*)\s*$", line)
            if m:
                name=m.group(1)
                body = parse_block(stop_tokens=["akhir"], opener_name=f"kelas {name}", opener_line=lineno)
                stmts.append(ClassDef(name,body,lineno)); continue
            if line == "coba" or line == "coba maka":
                collected = collect_until_akhir("coba", lineno)
                sep_indices = top_level_separator_indices(
                    collected,
                    lambda txt: txt.startswith("tangkap") or txt == "akhirnya"
                )
                error_name = None
                catch_body = None
                finally_body = None
                if sep_indices:
                    first_sep_idx = sep_indices[0][0]
                    body_slice = collected[0:first_sep_idx]
                    for sidx, (idxc, lnno, txt) in enumerate(sep_indices):
                        end_idx = sep_indices[sidx+1][0] if sidx+1 < len(sep_indices) else len(collected)
                        body_part = collected[idxc+1:end_idx]
                        if txt == "akhirnya":
                            finally_body = parse_block_from_list(body_part)
                        else:
                            m_catch = re.match(r"^tangkap(?:\s+(?:sebagai\s+)?([A-Za-z_][A-Za-z0-9_]*))?\s*$", txt)
                            error_name = m_catch.group(1) if m_catch and m_catch.group(1) else "error"
                            catch_body = parse_block_from_list(body_part)
                    body = parse_block_from_list(body_slice)
                else:
                    body = parse_block_from_list(collected)
                stmts.append(TryStmt(body,error_name,catch_body,finally_body,lineno)); continue
            if line.startswith("jika "):
                cond = line[len("jika "):].strip()
                if cond.endswith(" maka"): cond = cond[:-len(" maka")].strip()
                collected=collect_until_akhir("jika", lineno)
                sep_indices = top_level_separator_indices(
                    collected,
                    lambda txt: is_elif_line(txt) or txt == "lain"
                )
                segments = []
                if sep_indices:
                    first_sep_idx = sep_indices[0][0]
                    segments.append(("if", cond, collected[0:first_sep_idx]))
                    for sidx, (idxc, lnno, txt) in enumerate(sep_indices):
                        end_idx = sep_indices[sidx+1][0] if sidx+1 < len(sep_indices) else len(collected)
                        if is_elif_line(txt):
                            if txt.startswith("lain jika "):
                                c = txt[len("lain jika "):].strip()
                            else:
                                c = txt[len("elif "):].strip()
                            if c.endswith(" maka"): c = c[:-len(" maka")].strip()
                            body_slice = collected[idxc+1:end_idx]
                            segments.append(("elif", c, body_slice))
                        else:
                            body_slice = collected[idxc+1:end_idx]
                            segments.append(("else", None, body_slice))
                    branches = []
                    for kind, c, body_slice in segments:
                        body_stmts = parse_block_from_list(body_slice)
                        if kind in ("if","elif"):
                            branches.append((c, body_stmts))
                        else:
                            branches.append((None, body_stmts))
                    stmts.append(IfStmt(branches, lineno)); continue
                else:
                    then_block = parse_block_from_list(collected)
                    stmts.append(IfStmt([(cond, then_block)], lineno)); continue
            if line.startswith("pilih "):
                expr = line[len("pilih "):].strip()
                if expr.endswith(" maka"): expr = expr[:-len(" maka")].strip()
                collected=collect_until_akhir("pilih", lineno)
                sep_indices = top_level_separator_indices(
                    collected,
                    lambda txt: txt.startswith("saat ") or txt == "bawaan"
                )
                cases = []
                if sep_indices:
                    for sidx, (idxc, lnno, txt) in enumerate(sep_indices):
                        end_idx = sep_indices[sidx+1][0] if sidx+1 < len(sep_indices) else len(collected)
                        body_slice = collected[idxc+1:end_idx]
                        if txt == "bawaan":
                            cases.append((None, parse_block_from_list(body_slice)))
                        else:
                            case_expr = txt[len("saat "):].strip()
                            if case_expr.endswith(" maka"): case_expr = case_expr[:-len(" maka")].strip()
                            cases.append((case_expr, parse_block_from_list(body_slice)))
                stmts.append(SwitchStmt(expr,cases,lineno)); continue
            m = re.match(r"^selama\s+(.*?)\s+(?:maka|lakukan)\s*$", line)
            if m:
                cond = m.group(1).strip()
                body = parse_block(stop_tokens=["akhir"], opener_name="selama", opener_line=lineno)
                stmts.append(WhileStmt(cond, body, lineno)); continue
            m = re.match(r"^setiap\s+([A-Za-z_][A-Za-z0-9_]*)\s+(?:dalam|di)\s+(.*?)\s+lakukan\s*$", line)
            if m:
                var=m.group(1); iterable=m.group(2).strip()
                body = parse_block(stop_tokens=["akhir"], opener_name="setiap", opener_line=lineno)
                stmts.append(ForEachStmt(var,iterable,body,lineno)); continue
            m = re.match(r"^untuk\s+([A-Za-z_][A-Za-z0-9_]*)\s+(?:dalam|di)\s+(.*?)\s+lakukan\s*$", line)
            if m:
                var=m.group(1); iterable=m.group(2).strip()
                body = parse_block(stop_tokens=["akhir"], opener_name="untuk", opener_line=lineno)
                stmts.append(ForEachStmt(var,iterable,body,lineno)); continue
            m = re.match(r"^untuk\s+([A-Za-z_][A-Za-z0-9_]*)\s+dari\s+(.*?)\s+sampai\s+(.*?)\s+lakukan\s*$", line)
            if m:
                var=m.group(1); start=m.group(2).strip(); end=m.group(3).strip()
                body = parse_block(stop_tokens=["akhir"], opener_name="untuk", opener_line=lineno)
                stmts.append(ForStmt(var,start,end,body,lineno)); continue
            m = re.match(r"^ulangi\s+(.*?)\s+kali\s+lakukan\s*$", line)
            if m:
                count=m.group(1).strip()
                body = parse_block(stop_tokens=["akhir"], opener_name="ulangi", opener_line=lineno)
                stmts.append(RepeatStmt(count,body,lineno)); continue
            if line.startswith("cetak "):
                expr=line[len("cetak "):].strip(); stmts.append(PrintStmt(expr, lineno)); continue
            m = re.match(r"^tanya\s+(.+?)\s+sebagai\s+([A-Za-z_][A-Za-z0-9_]*)\s*$", line)
            if m:
                prompt_expr=m.group(1).strip(); varname=m.group(2)
                stmts.append(PromptInputStmt(prompt_expr,varname,lineno)); continue
            if line.startswith("baca "):
                var=line[len("baca "):].strip(); stmts.append(InputStmt(var, lineno)); continue
            if line.startswith("kembali"):
                rest=line[len("kembali"):].strip(); expr=rest if rest else None; stmts.append(ReturnStmt(expr, lineno)); continue
            if line.startswith("lempar "):
                expr=line[len("lempar "):].strip(); stmts.append(RaiseStmt(expr, lineno)); continue
            if line.startswith("gagal "):
                expr=line[len("gagal "):].strip(); stmts.append(RaiseStmt(expr, lineno)); continue
            if line.startswith("tunggu "):
                expr=line[len("tunggu "):].strip(); stmts.append(AwaitStmt(expr, lineno)); continue
            if line in ("henti", "berhenti"):
                stmts.append(ExprStmt("__BM__BREAK__", lineno)); continue
            if line in ("lanjut", "lanjutkan"):
                stmts.append(ExprStmt("__BM__CONTINUE__", lineno)); continue
            if line == "lewati":
                stmts.append(ExprStmt("__BM__PASS__", lineno)); continue
            left,right = _split_eq_outside_quotes(line)
            if right is not None:
                if right.startswith("tunggu "):
                    stmts.append(AwaitAssignStmt(left,right[len("tunggu "):].strip(),lineno)); continue
                stmts.append(AssignStmt(left,right,lineno)); continue
            stmts.append(ExprStmt(line, lineno))
        if stop_tokens:
            info_baris = f" pada baris {opener_line}" if opener_line is not None else ""
            nama = opener_name or "blok"
            raise BMError(f"Blok `{nama}`{info_baris} belum ditutup dengan `akhir`")
        return stmts
    i=0
    return parse_block()

# --- Interpreter core ---
class Interpreter:
    def __init__(self, aman: bool = False, allow_imports: Optional[bool] = None, allow_file_access: Optional[bool] = None):
        self.aman = bool(aman)
        self.allow_imports = (not self.aman) if allow_imports is None else bool(allow_imports)
        self.allow_file_access = (not self.aman) if allow_file_access is None else bool(allow_file_access)
        self.globals:Dict[str,Any]={}
        self.funcs:Dict[str,FuncDef]={}
        file_builtins = {
            "baca_berkas": _bm_baca_berkas, "baca_file": _bm_baca_berkas,
            "baca_baris": _bm_baca_baris,
            "tulis_berkas": _bm_tulis_berkas, "tulis_file": _bm_tulis_berkas,
            "tambah_berkas": _bm_tambah_berkas, "tambah_file": _bm_tambah_berkas,
            "ada_berkas": _bm_ada_berkas, "ada_file": _bm_ada_berkas,
            "hapus_berkas": _bm_hapus_berkas, "hapus_file": _bm_hapus_berkas,
            "daftar_berkas": _bm_daftar_berkas, "daftar_file": _bm_daftar_berkas,
        }
        if not self.allow_file_access:
            file_builtins = {name: _bm_fitur_dinonaktifkan(name) for name in file_builtins}
        self.builtins:Dict[str,Any] = {
            "len":len, "int":int, "float":float, "str":str, "range":range, "print":print,
            "abs": abs, "min": min, "max": max, "round": round,
            "panjang": len, "angka": _bm_angka, "pecahan": _bm_pecahan, "teks": str, "rentang": range,
            "mutlak": abs, "terkecil": min, "terbesar": max, "bulatkan": round,
            "rapikan": _bm_rapikan, "kecil": _bm_kecil, "besar": _bm_besar,
            "ganti": _bm_ganti, "pisah": _bm_pisah, "gabung": _bm_gabung,
            "mulai_dengan": _bm_mulai_dengan, "berakhir_dengan": _bm_berakhir_dengan,
            "cari": _bm_cari, "tambah": _bm_tambah,
            "daftar": _bm_daftar, "kamus": _bm_kamus, "berisi": _bm_berisi,
            "ambil": _bm_ambil, "atur": _bm_atur, "hapus": _bm_hapus,
            "urutkan": _bm_urutkan, "balik": _bm_balik, "kunci": _bm_kunci,
            "nilai": _bm_nilai, "pasangan": _bm_pasangan, "salin": _bm_salin,
            "jeda": asyncio.sleep,
        }
        self.builtins.update(file_builtins)
        # Input provider can be overridden (e.g., by web server) to supply inputs from request
        self.input_func = input
        # Root path for 'pakai' resolution
        self.base_path = Path.cwd()
        # Additional search paths for resolving 'pakai' modules (propagated to child interpreters)
        self.search_paths: List[Path] = [self.base_path]
        # Try to include installed package data for bm_standar if available
        try:
            import bahasamanis_data as _bmdata
            # data_pkg_root points to .../bahasamanis_data
            data_pkg_root = Path(_bmdata.__file__).parent
            if data_pkg_root.exists():
                # We add the parent that contains the 'bm_standar' folder.
                self.search_paths.append(data_pkg_root)
        except Exception:
            pass
    def _env(self, local:Optional[Dict[str,Any]]=None):
        env = {}
        env.update(self.builtins)
        env.update(self.globals)
        if local: env.update(local)
        for name,fdef in self.funcs.items():
            env[name] = self._make_callable(fdef)
        return env
    def _prepare_call_local(self, fdef:FuncDef, args, kwargs, initial:Optional[Dict[str,Any]]=None):
        local = dict(initial or {})
        param_names: List[str] = []
        default_exprs: Dict[str, str] = {}
        for raw in (fdef.args or []):
            raw = (raw or '').strip()
            if not raw:
                continue
            if '=' in raw:
                name, defexpr = raw.split('=', 1)
                name = name.strip(); defexpr = defexpr.strip()
                param_names.append(name)
                default_exprs[name] = defexpr
            else:
                param_names.append(raw)
        for i, name in enumerate(param_names):
            if name in local:
                continue
            if i < len(args):
                local[name] = args[i]
            elif name in (kwargs or {}):
                local[name] = kwargs[name]
            elif name in default_exprs:
                try:
                    local[name] = safe_eval(default_exprs[name], self._env(local))
                except Exception:
                    local[name] = None
            else:
                local[name] = None
        for k, v in (kwargs or {}).items():
            if k not in local:
                local[k] = v
        return local
    def _make_callable(self, fdef:FuncDef):
        if isinstance(fdef, AsyncFuncDef):
            async def async_wrapper(*args, **kwargs):
                local = self._prepare_call_local(fdef, args, kwargs)
                try:
                    await self._exec_block_async(fdef.body, local)
                except ReturnException as r:
                    return r.value
                return None
            return async_wrapper
        def wrapper(*args, **kwargs):
            local = self._prepare_call_local(fdef, args, kwargs)
            try:
                self._exec_block(fdef.body, local)
            except ReturnException as r:
                return r.value
            return None
        return wrapper
    def _call_method(self, fdef:FuncDef, instance:BMInstance, args, kwargs):
        initial = {"ini": instance, "self": instance}
        if isinstance(fdef, AsyncFuncDef):
            async def async_method():
                local = self._prepare_call_local(fdef, args, kwargs, initial=initial)
                try:
                    await self._exec_block_async(fdef.body, local)
                except ReturnException as r:
                    return r.value
                return None
            return async_method()
        local = self._prepare_call_local(fdef, args, kwargs, initial=initial)
        try:
            self._exec_block(fdef.body, local)
        except ReturnException as r:
            return r.value
        return None
    def _make_class(self, cdef:ClassDef):
        methods = {}
        for item in cdef.body:
            if isinstance(item, (FuncDef, AsyncFuncDef)):
                methods[item.name] = item
        return BMClass(self, cdef.name, methods)
    def load_program(self, src:str):
        stmts = parse_program(src)
        top_level = []
        for s in stmts:
            if isinstance(s, (FuncDef, AsyncFuncDef)):
                self.funcs[s.name] = s
            elif isinstance(s, ClassDef):
                self.globals[s.name] = self._make_class(s)
            else:
                top_level.append(s)
        return top_level
    def run(self, src:str):
        top = self.load_program(src)
        try:
            self._exec_block(top, {})
        except BMError as e:
            raise
    def _await_value_sync(self, value):
        if inspect.isawaitable(value):
            return asyncio.run(value)
        return value
    async def _await_value_async(self, value):
        if inspect.isawaitable(value):
            return await value
        return value
    def _set_target(self, target:str, val:Any, local:Dict[str,Any], lineno:int):
        if "[" in target:
            import re as _re
            m = _re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*(\[.*\])$", target)
            if m:
                base = m.group(1)
                index_expr = m.group(2)
                base_obj = local.get(base, self.globals.get(base))
                if base_obj is None:
                    raise BMError(f"Target '{base}' tidak ditemukan untuk penugasan pada baris {lineno}")
                idx = index_expr.strip()[1:-1]
                idx_val = safe_eval(idx, self._env(local))
                base_obj[idx_val] = val
                return
            raise BMError(f"Penugasan ke target kompleks belum didukung: {target} pada baris {lineno}")
        if "." in target:
            parts = [p.strip() for p in target.split(".")]
            base_name = parts[0]
            obj = local.get(base_name, self.globals.get(base_name))
            if obj is None and base_name == "ini":
                obj = local.get("self")
            if obj is None:
                raise BMError(f"Target '{base_name}' tidak ditemukan untuk penugasan pada baris {lineno}")
            for attr in parts[1:-1]:
                obj = getattr(obj, attr)
            setattr(obj, parts[-1], val)
            return
        local[target] = val
    def _exec_try_stmt(self, s:TryStmt, local:Dict[str,Any]):
        try:
            try:
                self._exec_block(s.body, local)
            except (ReturnException, BreakException, ContinueException):
                raise
            except Exception as e:
                if s.catch_body is None:
                    raise
                local[s.error_name or "error"] = str(e)
                self._exec_block(s.catch_body, local)
        finally:
            if s.finally_body is not None:
                self._exec_block(s.finally_body, local)
    async def _exec_try_stmt_async(self, s:TryStmt, local:Dict[str,Any]):
        try:
            try:
                await self._exec_block_async(s.body, local)
            except (ReturnException, BreakException, ContinueException):
                raise
            except Exception as e:
                if s.catch_body is None:
                    raise
                local[s.error_name or "error"] = str(e)
                await self._exec_block_async(s.catch_body, local)
        finally:
            if s.finally_body is not None:
                await self._exec_block_async(s.finally_body, local)
    def _exec_block(self, stmts:List[Stmt], local:Dict[str,Any]):
        for s in stmts:
            try:
                if isinstance(s, PrintStmt):
                    val = safe_eval(s.expr, self._env(local))
                    print(val, flush=True)
                elif isinstance(s, ImportPkgStmt):
                    if not self.allow_imports:
                        raise BMError(f"Impor paket Python '{s.module}' dimatikan di mode aman")
                    try:
                        module = __import__(s.module, fromlist=['*'])
                    except Exception as e:
                        raise BMError(f"Gagal mengimpor paket Python '{s.module}' pada baris {s.lineno}: {e}")
                    self.globals[s.alias] = module
                elif isinstance(s, ImportBMStmt):
                    if not self.allow_imports:
                        raise BMError(f"Impor modul BM '{s.path}' dimatikan di mode aman")
                    mod_obj = self._import_bm_module(s.path)
                    if s.alias:
                        self.globals[s.alias] = mod_obj
                    else:
                        # merge into current env
                        for name, val in vars(mod_obj).items():
                            if name.startswith('_'): continue
                            if callable(val):
                                # treat as function -> register into funcs via a wrapper
                                self.globals[name] = val
                            else:
                                self.globals[name] = val
                elif isinstance(s, InputStmt):
                    v = self.input_func()
                    local[s.varname] = v
                elif isinstance(s, PromptInputStmt):
                    prompt = safe_eval(s.prompt_expr, self._env(local))
                    print(prompt, end="", flush=True)
                    local[s.varname] = self.input_func()
                elif isinstance(s, AssignStmt):
                    val = safe_eval(s.expr, self._env(local))
                    self._set_target(s.target, val, local, s.lineno)
                elif isinstance(s, AwaitAssignStmt):
                    val = safe_eval(s.expr, self._env(local))
                    val = self._await_value_sync(val)
                    self._set_target(s.target, val, local, s.lineno)
                elif isinstance(s, AwaitStmt):
                    val = safe_eval(s.expr, self._env(local))
                    self._await_value_sync(val)
                elif isinstance(s, ExprStmt):
                    if s.expr == "__BM__BREAK__":
                        raise BreakException()
                    if s.expr == "__BM__CONTINUE__":
                        raise ContinueException()
                    if s.expr == "__BM__PASS__":
                        continue
                    safe_eval(s.expr, self._env(local))
                elif isinstance(s, ReturnStmt):
                    if s.expr is None:
                        raise ReturnException(None)
                    val = safe_eval(s.expr, self._env(local))
                    raise ReturnException(val)
                elif isinstance(s, RaiseStmt):
                    val = safe_eval(s.expr, self._env(local))
                    raise BMError(str(val))
                elif isinstance(s, TryStmt):
                    self._exec_try_stmt(s, local)
                elif isinstance(s, IfStmt):
                    for cond, block in s.branches:
                        if cond is None:
                            self._exec_block(block, local); break
                        if safe_eval(cond, self._env(local)):
                            self._exec_block(block, local); break
                elif isinstance(s, SwitchStmt):
                    value = safe_eval(s.expr, self._env(local))
                    default_block = None
                    matched = False
                    for case_expr, block in s.cases:
                        if case_expr is None:
                            default_block = block
                            continue
                        if value == safe_eval(case_expr, self._env(local)):
                            self._exec_block(block, local)
                            matched = True
                            break
                    if not matched and default_block is not None:
                        self._exec_block(default_block, local)
                elif isinstance(s, WhileStmt):
                    while True:
                        condv = safe_eval(s.cond, self._env(local))
                        if not condv: break
                        try:
                            self._exec_block(s.body, local)
                        except ContinueException:
                            continue
                        except BreakException:
                            break
                elif isinstance(s, ForStmt):
                    start = int(safe_eval(s.start, self._env(local)))
                    end = int(safe_eval(s.end, self._env(local)))
                    for v in range(start, end+1):
                        local[s.var] = v
                        try:
                            self._exec_block(s.body, local)
                        except ContinueException:
                            continue
                        except BreakException:
                            break
                elif isinstance(s, ForEachStmt):
                    iterable = safe_eval(s.iterable, self._env(local))
                    for v in iterable:
                        local[s.var] = v
                        try:
                            self._exec_block(s.body, local)
                        except ContinueException:
                            continue
                        except BreakException:
                            break
                elif isinstance(s, RepeatStmt):
                    count = int(safe_eval(s.count, self._env(local)))
                    for _ in range(count):
                        try:
                            self._exec_block(s.body, local)
                        except ContinueException:
                            continue
                        except BreakException:
                            break
                elif isinstance(s, FuncDef):
                    self.funcs[s.name] = s
                elif isinstance(s, AsyncFuncDef):
                    self.funcs[s.name] = s
                elif isinstance(s, ClassDef):
                    local[s.name] = self._make_class(s)
                else:
                    raise BMError(f"Pernyataan tidak dikenali pada baris {getattr(s,'lineno','?')}")
            except BMError:
                raise
            except ReturnException:
                raise
            except BreakException:
                raise
            except ContinueException:
                raise
            except Exception as e:
                raise BMError(f"Kesalahan runtime pada baris {getattr(s,'lineno','?')}: {_translate_error_message(str(e))}")

    async def _exec_block_async(self, stmts:List[Stmt], local:Dict[str,Any]):
        for s in stmts:
            try:
                if isinstance(s, PrintStmt):
                    val = safe_eval(s.expr, self._env(local))
                    print(val, flush=True)
                elif isinstance(s, ImportPkgStmt):
                    if not self.allow_imports:
                        raise BMError(f"Impor paket Python '{s.module}' dimatikan di mode aman")
                    try:
                        module = __import__(s.module, fromlist=['*'])
                    except Exception as e:
                        raise BMError(f"Gagal mengimpor paket Python '{s.module}' pada baris {s.lineno}: {e}")
                    self.globals[s.alias] = module
                elif isinstance(s, ImportBMStmt):
                    if not self.allow_imports:
                        raise BMError(f"Impor modul BM '{s.path}' dimatikan di mode aman")
                    mod_obj = self._import_bm_module(s.path)
                    if s.alias:
                        self.globals[s.alias] = mod_obj
                    else:
                        for name, val in vars(mod_obj).items():
                            if name.startswith('_'): continue
                            self.globals[name] = val
                elif isinstance(s, InputStmt):
                    v = self.input_func()
                    local[s.varname] = v
                elif isinstance(s, PromptInputStmt):
                    prompt = safe_eval(s.prompt_expr, self._env(local))
                    print(prompt, end="", flush=True)
                    local[s.varname] = self.input_func()
                elif isinstance(s, AssignStmt):
                    val = safe_eval(s.expr, self._env(local))
                    self._set_target(s.target, val, local, s.lineno)
                elif isinstance(s, AwaitAssignStmt):
                    val = safe_eval(s.expr, self._env(local))
                    val = await self._await_value_async(val)
                    self._set_target(s.target, val, local, s.lineno)
                elif isinstance(s, AwaitStmt):
                    val = safe_eval(s.expr, self._env(local))
                    await self._await_value_async(val)
                elif isinstance(s, ExprStmt):
                    if s.expr == "__BM__BREAK__":
                        raise BreakException()
                    if s.expr == "__BM__CONTINUE__":
                        raise ContinueException()
                    if s.expr == "__BM__PASS__":
                        continue
                    safe_eval(s.expr, self._env(local))
                elif isinstance(s, ReturnStmt):
                    if s.expr is None:
                        raise ReturnException(None)
                    val = safe_eval(s.expr, self._env(local))
                    raise ReturnException(val)
                elif isinstance(s, RaiseStmt):
                    val = safe_eval(s.expr, self._env(local))
                    raise BMError(str(val))
                elif isinstance(s, TryStmt):
                    await self._exec_try_stmt_async(s, local)
                elif isinstance(s, IfStmt):
                    for cond, block in s.branches:
                        if cond is None:
                            await self._exec_block_async(block, local); break
                        if safe_eval(cond, self._env(local)):
                            await self._exec_block_async(block, local); break
                elif isinstance(s, SwitchStmt):
                    value = safe_eval(s.expr, self._env(local))
                    default_block = None
                    matched = False
                    for case_expr, block in s.cases:
                        if case_expr is None:
                            default_block = block
                            continue
                        if value == safe_eval(case_expr, self._env(local)):
                            await self._exec_block_async(block, local)
                            matched = True
                            break
                    if not matched and default_block is not None:
                        await self._exec_block_async(default_block, local)
                elif isinstance(s, WhileStmt):
                    while True:
                        condv = safe_eval(s.cond, self._env(local))
                        if not condv: break
                        try:
                            await self._exec_block_async(s.body, local)
                        except ContinueException:
                            continue
                        except BreakException:
                            break
                elif isinstance(s, ForStmt):
                    start = int(safe_eval(s.start, self._env(local)))
                    end = int(safe_eval(s.end, self._env(local)))
                    for v in range(start, end+1):
                        local[s.var] = v
                        try:
                            await self._exec_block_async(s.body, local)
                        except ContinueException:
                            continue
                        except BreakException:
                            break
                elif isinstance(s, ForEachStmt):
                    iterable = safe_eval(s.iterable, self._env(local))
                    for v in iterable:
                        local[s.var] = v
                        try:
                            await self._exec_block_async(s.body, local)
                        except ContinueException:
                            continue
                        except BreakException:
                            break
                elif isinstance(s, RepeatStmt):
                    count = int(safe_eval(s.count, self._env(local)))
                    for _ in range(count):
                        try:
                            await self._exec_block_async(s.body, local)
                        except ContinueException:
                            continue
                        except BreakException:
                            break
                elif isinstance(s, (FuncDef, AsyncFuncDef)):
                    self.funcs[s.name] = s
                elif isinstance(s, ClassDef):
                    local[s.name] = self._make_class(s)
                else:
                    raise BMError(f"Pernyataan tidak dikenali pada baris {getattr(s,'lineno','?')}")
            except BMError:
                raise
            except ReturnException:
                raise
            except BreakException:
                raise
            except ContinueException:
                raise
            except Exception as e:
                raise BMError(f"Kesalahan runtime pada baris {getattr(s,'lineno','?')}: {_translate_error_message(str(e))}")

    # --- Module helpers ---
    def _import_bm_module(self, path_str: str):
        """Load a .bm file and return a simple module-like object exposing its functions & globals.
        Resolution order:
        - Absolute path as provided (ensure .bm)
        - Relative to current interpreter base_path
        - Relative to any paths in self.search_paths (in order)
        """
        p_raw = Path(path_str)
        def with_suffix(p: Path) -> Path:
            return p if p.suffix == '.bm' else p.with_suffix('.bm')

        candidates: List[Path] = []
        if p_raw.is_absolute():
            candidates.append(with_suffix(p_raw))
        else:
            # base_path first
            candidates.append(with_suffix((self.base_path / p_raw).resolve()))
            # then inherited search paths
            for sp in self.search_paths:
                try:
                    candidates.append(with_suffix((Path(sp) / p_raw).resolve()))
                except Exception:
                    continue
        # de-duplicate while preserving order
        seen = set(); ordered: List[Path] = []
        for c in candidates:
            key = str(c).lower()
            if key not in seen:
                seen.add(key); ordered.append(c)

        target: Optional[Path] = None
        for c in ordered:
            if c.exists():
                target = c; break
        if target is None:
            raise BMError(f"File BM untuk 'pakai' tidak ditemukan: {(self.base_path / p_raw).with_suffix('.bm').resolve()}")

        src = target.read_text(encoding='utf-8')
        sub = Interpreter(aman=self.aman, allow_imports=self.allow_imports, allow_file_access=self.allow_file_access)
        sub.base_path = target.parent
        # Propagate and extend search paths so nested modules can resolve to project roots
        sub.search_paths = list({*(p for p in self.search_paths), self.base_path, target.parent})
        # Preserve the same input function behavior
        sub.input_func = self.input_func
        # run submodule
        sub.run(src)
        # Build module-like object
        class _BMModule: pass
        mod = _BMModule()
        # expose functions
        for name,fdef in sub.funcs.items():
            setattr(mod, name, sub._make_callable(fdef))
        # expose globals
        for name,val in sub.globals.items():
            if name.startswith('_'): continue
            setattr(mod, name, val)
        # convenience: path attribute
        setattr(mod, '__file__', str(target))
        return mod

def transpile_to_python(src:str) -> str:
    stmts = parse_program(src)
    lines = ["# Transpiled from BahasaManis -> Python", "import asyncio", "from pathlib import Path", "async def __bm_main():"]
    indent = "    "
    indonesian_aliases = [
        "jeda = asyncio.sleep",
        "panjang = len",
        "def angka(nilai):",
        "    try: return int(nilai)",
        "    except Exception: raise ValueError(f\"angka() gagal: '{nilai}' bukan bilangan bulat\")",
        "def pecahan(nilai):",
        "    try: return float(nilai)",
        "    except Exception: raise ValueError(f\"pecahan() gagal: '{nilai}' bukan bilangan pecahan\")",
        "teks = str",
        "rentang = range",
        "mutlak = abs",
        "terkecil = min",
        "terbesar = max",
        "bulatkan = round",
        "def rapikan(nilai): return str(nilai).strip()",
        "def kecil(nilai): return str(nilai).lower()",
        "def besar(nilai): return str(nilai).upper()",
        "def ganti(teks, lama, baru): return str(teks).replace(str(lama), str(baru))",
        "def pisah(teks, pemisah=None): return str(teks).split() if pemisah is None else str(teks).split(str(pemisah))",
        "def gabung(kumpulan, pemisah=''): return str(pemisah).join(kumpulan)",
        "def mulai_dengan(teks, awalan): return str(teks).startswith(str(awalan))",
        "def berakhir_dengan(teks, akhiran): return str(teks).endswith(str(akhiran))",
        "def cari(teks, bagian): return str(teks).find(str(bagian))",
        "def tambah(kumpulan, nilai): kumpulan.append(nilai); return kumpulan",
        "def daftar(nilai=None): return [] if nilai is None else list(nilai)",
        "def kamus(nilai=None): return {} if nilai is None else dict(nilai)",
        "def berisi(kumpulan, nilai): return nilai in kumpulan",
        "def ambil(kumpulan, kunci, bawaan=None): return kumpulan.get(kunci, bawaan) if isinstance(kumpulan, dict) else (kumpulan[kunci] if kunci < len(kumpulan) else bawaan)",
        "def atur(kumpulan, kunci, nilai): kumpulan[kunci] = nilai; return kumpulan",
        "def hapus(kumpulan, nilai): kumpulan.pop(nilai, None) if isinstance(kumpulan, dict) else (kumpulan.remove(nilai) if nilai in kumpulan else None); return kumpulan",
        "def urutkan(kumpulan): return sorted(kumpulan)",
        "def balik(kumpulan): return kumpulan[::-1] if isinstance(kumpulan, str) else list(reversed(kumpulan))",
        "def kunci(kamus): return list(kamus.keys())",
        "def nilai(kamus): return list(kamus.values())",
        "def pasangan(kamus): return list(kamus.items())",
        "def salin(nilai): return nilai.copy() if hasattr(nilai, 'copy') else nilai",
        "def baca_berkas(path): return Path(str(path)).read_text(encoding='utf-8')",
        "baca_file = baca_berkas",
        "def baca_baris(path): return Path(str(path)).read_text(encoding='utf-8').splitlines()",
        "def tulis_berkas(path, isi): Path(str(path)).write_text(str(isi), encoding='utf-8'); return str(path)",
        "tulis_file = tulis_berkas",
        "def tambah_berkas(path, isi): p=Path(str(path)); p.write_text((p.read_text(encoding='utf-8') if p.exists() else '') + str(isi), encoding='utf-8'); return str(path)",
        "tambah_file = tambah_berkas",
        "def ada_berkas(path): return Path(str(path)).exists()",
        "ada_file = ada_berkas",
        "def hapus_berkas(path): p=Path(str(path)); ok=p.exists() and p.is_file(); p.unlink() if ok else None; return ok",
        "hapus_file = hapus_berkas",
        "def daftar_berkas(path='.'): return [p.name for p in Path(str(path)).iterdir()]",
        "daftar_file = daftar_berkas",
    ]
    for alias in indonesian_aliases:
        lines.append(f"{indent}{alias}")
    lines.append("")
    def expr_to_python_transpile(expr: str) -> str:
        pyexpr = _expr_to_python(expr)
        try:
            import io, tokenize
            tokens = []
            for tok in tokenize.generate_tokens(io.StringIO(pyexpr).readline):
                if tok.type == tokenize.NAME and tok.string == "ini":
                    tok = tokenize.TokenInfo(tok.type, "self", tok.start, tok.end, tok.line)
                tokens.append(tok)
            return tokenize.untokenize(tokens)
        except Exception:
            return re.sub(r"\bini\b", "self", pyexpr)
    def emit_expr_py(expr: str) -> str:
        s = expr.strip()
        # If it's a quoted string, convert `{...}` parts using BM -> Python expr and emit as f-string
        if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
            quote = s[0]
            inner = s[1:-1]
            if "{" not in inner or "}" not in inner:
                return s
            import re as _re
            def _repl(m):
                inside = m.group(1)
                return '{' + expr_to_python_transpile(inside) + '}'
            inner2 = _re.sub(r"{([^{}]+)}", _repl, inner)
            # Always use double quotes in output for simplicity
            py = f"f\"{inner2}\""
            return py
        # Non-string expression
        return expr_to_python_transpile(expr)
    def emit_target_py(target: str) -> str:
        return re.sub(r"\bini\b", "self", target)
    switch_counter = [0]
    def emit(stmt_list, level):
        for s in stmt_list:
            pref = indent*level
            if isinstance(s, PrintStmt):
                lines.append(f"{pref}print({emit_expr_py(s.expr)})")
            elif isinstance(s, ImportPkgStmt):
                # import module as alias
                lines.append(f"{pref}import {s.module} as {s.alias}")
            elif isinstance(s, ImportBMStmt):
                # For now, 'pakai' is not supported in transpile mode: leave a note
                lines.append(f"{pref}# NOTE: 'pakai {s.path}' tidak didukung saat transpile (gunakan interpreter)")
            elif isinstance(s, InputStmt):
                lines.append(f"{pref}{s.varname} = input()")
            elif isinstance(s, PromptInputStmt):
                lines.append(f"{pref}print({emit_expr_py(s.prompt_expr)}, end='')")
                lines.append(f"{pref}{s.varname} = input()")
            elif isinstance(s, AssignStmt):
                lines.append(f"{pref}{emit_target_py(s.target)} = {emit_expr_py(s.expr)}")
            elif isinstance(s, AwaitAssignStmt):
                lines.append(f"{pref}{emit_target_py(s.target)} = await {emit_expr_py(s.expr)}")
            elif isinstance(s, AwaitStmt):
                lines.append(f"{pref}await {emit_expr_py(s.expr)}")
            elif isinstance(s, ExprStmt):
                if s.expr=="__BM__BREAK__":
                    lines.append(f"{pref}break")
                elif s.expr=="__BM__CONTINUE__":
                    lines.append(f"{pref}continue")
                elif s.expr=="__BM__PASS__":
                    lines.append(f"{pref}pass")
                else:
                    lines.append(f"{pref}{emit_expr_py(s.expr)}")
            elif isinstance(s, ReturnStmt):
                if s.expr is None: lines.append(f"{pref}return")
                else: lines.append(f"{pref}return {emit_expr_py(s.expr)}")
            elif isinstance(s, RaiseStmt):
                lines.append(f"{pref}raise Exception({emit_expr_py(s.expr)})")
            elif isinstance(s, TryStmt):
                lines.append(f"{pref}try:")
                emit(s.body, level+1)
                if s.catch_body is not None:
                    lines.append(f"{pref}except Exception as {s.error_name or 'error'}:")
                    emit(s.catch_body, level+1)
                if s.finally_body is not None:
                    lines.append(f"{pref}finally:")
                    emit(s.finally_body, level+1)
            elif isinstance(s, ClassDef):
                lines.append(f"{pref}class {s.name}:")
                methods = [item for item in s.body if isinstance(item, (FuncDef, AsyncFuncDef))]
                if not methods:
                    lines.append(f"{pref}{indent}pass")
                for item in methods:
                    method_name = "__init__" if item.name == "mulai" else item.name
                    args = ", ".join(["self", *item.args])
                    if isinstance(item, AsyncFuncDef):
                        lines.append(f"{pref}{indent}async def {method_name}({args}):")
                    else:
                        lines.append(f"{pref}{indent}def {method_name}({args}):")
                    emit(item.body, level+2)
            elif isinstance(s, IfStmt):
                first=True
                for cond, block in s.branches:
                    if cond is None:
                        lines.append(f"{pref}else:")
                    else:
                        if first:
                            lines.append(f"{pref}if {expr_to_python_transpile(cond)}:"); first=False
                        else:
                            lines.append(f"{pref}elif {expr_to_python_transpile(cond)}:")
                    emit(block, level+1)
            elif isinstance(s, SwitchStmt):
                switch_counter[0] += 1
                temp_name = f"__bm_pilih_{switch_counter[0]}"
                lines.append(f"{pref}{temp_name} = {emit_expr_py(s.expr)}")
                first=True
                default_block=None
                for case_expr, block in s.cases:
                    if case_expr is None:
                        default_block = block
                        continue
                    keyword = "if" if first else "elif"
                    lines.append(f"{pref}{keyword} {temp_name} == {emit_expr_py(case_expr)}:")
                    emit(block, level+1)
                    first=False
                if default_block is not None:
                    if first:
                        emit(default_block, level)
                    else:
                        lines.append(f"{pref}else:")
                        emit(default_block, level+1)
            elif isinstance(s, WhileStmt):
                lines.append(f"{pref}while {expr_to_python_transpile(s.cond)}:"); emit(s.body, level+1)
            elif isinstance(s, ForStmt):
                lines.append(f"{pref}for {s.var} in range(int({expr_to_python_transpile(s.start)}), int({expr_to_python_transpile(s.end)})+1):"); emit(s.body, level+1)
            elif isinstance(s, ForEachStmt):
                lines.append(f"{pref}for {s.var} in {expr_to_python_transpile(s.iterable)}:"); emit(s.body, level+1)
            elif isinstance(s, RepeatStmt):
                lines.append(f"{pref}for _ in range(int({expr_to_python_transpile(s.count)})):"); emit(s.body, level+1)
            elif isinstance(s, AsyncFuncDef):
                args = ", ".join(s.args)
                lines.append(f"{pref}async def {s.name}({args}):"); emit(s.body, level+1)
            elif isinstance(s, FuncDef):
                args = ", ".join(s.args)
                lines.append(f"{pref}def {s.name}({args}):"); emit(s.body, level+1)
            else:
                lines.append(f"{pref}# Unsupported stmt: {type(s)}")
    emit(stmts, 1)
    lines.append("")
    lines.append("if __name__=='__main__':")
    lines.append("    asyncio.run(__bm_main())")
    return "\n".join(lines)
