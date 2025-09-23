# BahasaManis interpreter + transpiler (v3) - save as bahasamanis.py
from __future__ import annotations
import ast, re, traceback, os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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
class AssignStmt(Stmt):
    def __init__(self, target:str, expr:str, lineno:int): self.target=target; self.expr=expr; self.lineno=lineno
class ReturnStmt(Stmt):
    def __init__(self, expr:Optional[str], lineno:int): self.expr=expr; self.lineno=lineno
class ExprStmt(Stmt):
    def __init__(self, expr:str, lineno:int): self.expr=expr; self.lineno=lineno
class IfStmt(Stmt):
    def __init__(self, branches:List[Tuple[Optional[str], List[Stmt]]], lineno:int):
        self.branches = branches; self.lineno = lineno
class WhileStmt(Stmt):
    def __init__(self, cond:str, body:List[Stmt], lineno:int): self.cond=cond; self.body=body; self.lineno=lineno
class ForStmt(Stmt):
    def __init__(self, var:str, start:str, end:str, body:List[Stmt], lineno:int):
        self.var=var; self.start=start; self.end=end; self.body=body; self.lineno=lineno
class FuncDef(Stmt):
    def __init__(self, name:str, args:List[str], body:List[Stmt], lineno:int):
        self.name=name; self.args=args; self.body=body; self.lineno=lineno

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
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Str, ast.Name, ast.Load,
    ast.Call, ast.Compare, ast.BoolOp, ast.List, ast.Dict, ast.Tuple, ast.Subscript,
    ast.Index, ast.Slice, ast.Constant, ast.Attribute, ast.keyword
}
_ALLOWED_OPERATORS = {
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow, ast.FloorDiv,
    ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
    ast.And, ast.Or, ast.Not, ast.USub, ast.UAdd
}

def _expr_to_python(expr: str) -> str:
    replacements = [
        (r"\bbenar\b", "True"),
        (r"\bsalah\b", "False"),
        (r"\bkosong\b", "None"),
        (r"\bdan\b", " and "),
        (r"\batau\b", " or "),
        (r"\btidak\b", " not "),
    ]
    e = expr
    for pat,repl in replacements:
        e = re.sub(pat, repl, e)
    return e

def _check_ast_nodes(node: ast.AST):
    for n in ast.walk(node):
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
        (r"name '([^']+)' is not defined", r"nama '\1' tidak didefinisikan"),
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
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        inner = s[1:-1]
        if "{" in inner and "}" in inner:
            # Evaluate expressions within {...} safely
            return _interpolate_exprs(inner, env)
        return inner
    pyexpr = _expr_to_python(expr)
    try:
        node = ast.parse(pyexpr, mode="eval")
    except SyntaxError as e:
        raise BMError(f"Kesalahan sintaks pada ekspresi `{expr}`: {_translate_error_message(str(e))}")
    _check_ast_nodes(node)
    safe_globals = {"__builtins__": {"__import__": __import__}}
    return eval(compile(node, "<expr>", "eval"), safe_globals, env)

# --- Parser ---
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
        s = ln.strip()
        if not s or s.startswith("#"): continue
        lines.append((idx,s))
    i=0; n=len(lines)
    def parse_block_from_list(sub_lines):
        src = "\n".join(l for (_,l) in sub_lines)
        return parse_program(src)
    def parse_block(stop_tokens=None):
        nonlocal i
        stmts=[]
        while i<n:
            lineno, line = lines[i]; i+=1
            if stop_tokens and line in stop_tokens:
                return stmts
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
            m = re.match(r"^fungsi\s+([A-Za-z_][A-Za-z0-9_]*)\s*\((.*?)\)\s*$", line)
            if m:
                name=m.group(1); args_str=m.group(2).strip()
                args=[a.strip() for a in args_str.split(",")] if args_str else []
                body = parse_block(stop_tokens=["akhir"])
                stmts.append(FuncDef(name,args,body,lineno)); continue
            if line.startswith("jika "):
                cond = line[len("jika "):].strip()
                if cond.endswith(" maka"): cond = cond[:-len(" maka")].strip()
                collected=[]
                depth = 0
                while i < n:
                    lnno, nxt = lines[i]
                    if nxt.startswith("jika "):
                        depth += 1; collected.append((lnno, nxt)); i += 1; continue
                    if nxt == "akhir" and depth > 0:
                        depth -= 1; collected.append((lnno, nxt)); i += 1; continue
                    if nxt == "akhir" and depth == 0:
                        i += 1; break
                    collected.append((lnno, nxt)); i += 1
                sep_indices = []
                for idxc, (lnno, txt) in enumerate(collected):
                    if txt.startswith("elif ") or txt == "lain":
                        sep_indices.append((idxc, lnno, txt))
                segments = []
                if sep_indices:
                    first_sep_idx = sep_indices[0][0]
                    segments.append(("if", cond, collected[0:first_sep_idx]))
                    for sidx, (idxc, lnno, txt) in enumerate(sep_indices):
                        end_idx = sep_indices[sidx+1][0] if sidx+1 < len(sep_indices) else len(collected)
                        if txt.startswith("elif "):
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
            m = re.match(r"^selama\s+(.*?)\s+maka\s*$", line)
            if m:
                cond = m.group(1).strip()
                body = parse_block(stop_tokens=["akhir"])
                stmts.append(WhileStmt(cond, body, lineno)); continue
            m = re.match(r"^untuk\s+([A-Za-z_][A-Za-z0-9_]*)\s+dari\s+(.*?)\s+sampai\s+(.*?)\s+lakukan\s*$", line)
            if m:
                var=m.group(1); start=m.group(2).strip(); end=m.group(3).strip()
                body = parse_block(stop_tokens=["akhir"])
                stmts.append(ForStmt(var,start,end,body,lineno)); continue
            if line.startswith("cetak "):
                expr=line[len("cetak "):].strip(); stmts.append(PrintStmt(expr, lineno)); continue
            if line.startswith("baca "):
                var=line[len("baca "):].strip(); stmts.append(InputStmt(var, lineno)); continue
            if line.startswith("kembali"):
                rest=line[len("kembali"):].strip(); expr=rest if rest else None; stmts.append(ReturnStmt(expr, lineno)); continue
            if line=="henti":
                stmts.append(ExprStmt("__BM__BREAK__", lineno)); continue
            if line=="lanjut":
                stmts.append(ExprStmt("__BM__CONTINUE__", lineno)); continue
            left,right = _split_eq_outside_quotes(line)
            if right is not None:
                stmts.append(AssignStmt(left,right,lineno)); continue
            stmts.append(ExprStmt(line, lineno))
        return stmts
    i=0
    return parse_block()

# --- Interpreter core ---
class Interpreter:
    def __init__(self):
        self.globals:Dict[str,Any]={}
        self.funcs:Dict[str,FuncDef]={}
        self.builtins:Dict[str,Any] = {
            "len":len, "int":int, "float":float, "str":str, "range":range, "print":print,
            "abs": abs, "min": min, "max": max, "round": round
        }
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
    def _make_callable(self, fdef:FuncDef):
        # Preprocess parameters: support defaults like "nama=nilai"
        # NOTE: we DO NOT evaluate defaults here to avoid any side-effects during import.
        #       Defaults will be evaluated at call-time in the current environment.
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

        def wrapper(*args, **kwargs):
            local = {}
            # Fill from positional, keywords, then defaults
            for i, name in enumerate(param_names):
                if i < len(args):
                    local[name] = args[i]
                elif name in (kwargs or {}):
                    local[name] = kwargs[name]
                elif name in default_exprs:
                    # Evaluate default expression at call-time using current environment
                    try:
                        local[name] = safe_eval(default_exprs[name], self._env(local))
                    except Exception:
                        local[name] = None
                else:
                    local[name] = None
            # Include any extra kwargs
            for k, v in (kwargs or {}).items():
                if k not in local:
                    local[k] = v
            try:
                self._exec_block(fdef.body, local)
            except ReturnException as r:
                return r.value
            return None
        return wrapper
    def load_program(self, src:str):
        stmts = parse_program(src)
        top_level = []
        for s in stmts:
            if isinstance(s, FuncDef):
                self.funcs[s.name] = s
            else:
                top_level.append(s)
        return top_level
    def run(self, src:str):
        top = self.load_program(src)
        try:
            self._exec_block(top, {})
        except BMError as e:
            raise
    def _exec_block(self, stmts:List[Stmt], local:Dict[str,Any]):
        for s in stmts:
            try:
                if isinstance(s, PrintStmt):
                    val = safe_eval(s.expr, self._env(local))
                    print(val, flush=True)
                elif isinstance(s, ImportPkgStmt):
                    try:
                        module = __import__(s.module, fromlist=['*'])
                    except Exception as e:
                        raise BMError(f"Gagal mengimpor paket Python '{s.module}' pada baris {s.lineno}: {e}")
                    self.globals[s.alias] = module
                elif isinstance(s, ImportBMStmt):
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
                elif isinstance(s, AssignStmt):
                    val = safe_eval(s.expr, self._env(local))
                    if "[" in s.target:
                        import re as _re
                        m = _re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*(\[.*\])$", s.target)
                        if m:
                            base = m.group(1)
                            index_expr = m.group(2)
                            base_obj = local.get(base, self.globals.get(base))
                            if base_obj is None:
                                raise BMError(f"Target '{base}' tidak ditemukan untuk penugasan pada baris {s.lineno}")
                            idx = index_expr.strip()[1:-1]
                            idx_val = safe_eval(idx, self._env(local))
                            base_obj[idx_val] = val
                        else:
                            raise BMError(f"Penugasan ke target kompleks belum didukung: {s.target} pada baris {s.lineno}")
                    else:
                        local[s.target] = val
                elif isinstance(s, ExprStmt):
                    if s.expr == "__BM__BREAK__":
                        raise BreakException()
                    if s.expr == "__BM__CONTINUE__":
                        raise ContinueException()
                    safe_eval(s.expr, self._env(local))
                elif isinstance(s, ReturnStmt):
                    if s.expr is None:
                        raise ReturnException(None)
                    val = safe_eval(s.expr, self._env(local))
                    raise ReturnException(val)
                elif isinstance(s, IfStmt):
                    for cond, block in s.branches:
                        if cond is None:
                            self._exec_block(block, local); break
                        if safe_eval(cond, self._env(local)):
                            self._exec_block(block, local); break
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
                elif isinstance(s, FuncDef):
                    self.funcs[s.name] = s
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
        sub = Interpreter()
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
    lines = ["# Transpiled from BahasaManis -> Python", "def __bm_main():"]
    indent = "    "
    def emit_expr_py(expr: str) -> str:
        s = expr.strip()
        # If it's a quoted string, convert `{...}` parts using BM -> Python expr and emit as f-string
        if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
            quote = s[0]
            inner = s[1:-1]
            import re as _re
            def _repl(m):
                inside = m.group(1)
                return '{' + _expr_to_python(inside) + '}'
            inner2 = _re.sub(r"{([^{}]+)}", _repl, inner)
            # Always use double quotes in output for simplicity
            py = f"f\"{inner2}\""
            return py
        # Non-string expression
        return _expr_to_python(expr)
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
            elif isinstance(s, AssignStmt):
                lines.append(f"{pref}{s.target} = {emit_expr_py(s.expr)}")
            elif isinstance(s, ExprStmt):
                if s.expr=="__BM__BREAK__":
                    lines.append(f"{pref}break")
                elif s.expr=="__BM__CONTINUE__":
                    lines.append(f"{pref}continue")
                else:
                    lines.append(f"{pref}{emit_expr_py(s.expr)}")
            elif isinstance(s, ReturnStmt):
                if s.expr is None: lines.append(f"{pref}return")
                else: lines.append(f"{pref}return {emit_expr_py(s.expr)}")
            elif isinstance(s, IfStmt):
                first=True
                for cond, block in s.branches:
                    if cond is None:
                        lines.append(f"{pref}else:")
                    else:
                        if first:
                            lines.append(f"{pref}if {_expr_to_python(cond)}:"); first=False
                        else:
                            lines.append(f"{pref}elif {_expr_to_python(cond)}:")
                    emit(block, level+1)
            elif isinstance(s, WhileStmt):
                lines.append(f"{pref}while {_expr_to_python(s.cond)}:"); emit(s.body, level+1)
            elif isinstance(s, ForStmt):
                lines.append(f"{pref}for {s.var} in range(int({_expr_to_python(s.start)}), int({_expr_to_python(s.end)})+1):"); emit(s.body, level+1)
            elif isinstance(s, FuncDef):
                args = ", ".join(s.args)
                lines.append(f"{pref}def {s.name}({args}):"); emit(s.body, level+1)
            else:
                lines.append(f"{pref}# Unsupported stmt: {type(s)}")
    emit(stmts, 1)
    lines.append("")
    lines.append("if __name__=='__main__':")
    lines.append("    __bm_main()")
    return "\n".join(lines)
