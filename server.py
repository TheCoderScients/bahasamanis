# server.py - Flask server for BahasaManis playground
from flask import Flask, request, jsonify
import io, os, sys
import multiprocessing as mp
import queue
from bahasamanis import Interpreter, transpile_to_python

app = Flask(__name__, static_folder='static')
# Disable static caching so UI updates are reflected without stale cache
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

PLAYGROUND_UNSAFE = os.environ.get("BM_PLAYGROUND_UNSAFE") == "1"
MAX_CODE_CHARS = int(os.environ.get("BM_PLAYGROUND_MAX_CODE_CHARS", "20000"))
MAX_OUTPUT_CHARS = int(os.environ.get("BM_PLAYGROUND_MAX_OUTPUT_CHARS", "20000"))
RUN_TIMEOUT_SECONDS = float(os.environ.get("BM_PLAYGROUND_TIMEOUT_SECONDS", "5"))

class _LimitedOutput:
    def __init__(self, limit: int):
        self.limit = max(0, int(limit))
        self.buf = io.StringIO()
        self.truncated = False
        self.size = 0

    def write(self, text):
        text = str(text)
        remaining = self.limit - self.size
        if remaining > 0:
            chunk = text[:remaining]
            self.buf.write(chunk)
            self.size += len(chunk)
        if len(text) > max(remaining, 0):
            self.truncated = True
        return len(text)

    def flush(self):
        pass

    def getvalue(self):
        out = self.buf.getvalue()
        if self.truncated:
            out += "\n[Output dipotong agar playground tetap stabil]\n"
        return out

def _trim_output(text: str) -> str:
    if len(text) <= MAX_OUTPUT_CHARS:
        return text
    return text[:MAX_OUTPUT_CHARS] + "\n[Output dipotong agar playground tetap stabil]\n"

def _make_request_interpreter(inputs, unsafe=None):
    input_queue = [str(x) for x in inputs] if isinstance(inputs, list) else []
    use_unsafe = PLAYGROUND_UNSAFE if unsafe is None else bool(unsafe)
    interp = Interpreter(aman=not use_unsafe)
    interp.globals['user'] = 'Fatal'

    def _web_input_provider():
        return input_queue.pop(0) if input_queue else ""

    interp.input_func = _web_input_provider
    return interp

def _run_code_worker(result_queue, code, inputs, unsafe, max_output_chars):
    old_stdout = sys.stdout
    writer = _LimitedOutput(max_output_chars)
    sys.stdout = writer
    try:
        interp = _make_request_interpreter(inputs, unsafe=unsafe)
        interp.run(code)
    except Exception as e:
        print(f"[Error] {e}")
    finally:
        sys.stdout = old_stdout
    result_queue.put({'output': writer.getvalue()})

def _mp_context():
    methods = mp.get_all_start_methods()
    if "fork" in methods:
        return mp.get_context("fork")
    return mp.get_context("spawn")

def _run_code_isolated(code, inputs):
    ctx = _mp_context()
    result_queue = ctx.Queue(maxsize=1)
    proc = ctx.Process(
        target=_run_code_worker,
        args=(result_queue, code, inputs, PLAYGROUND_UNSAFE, MAX_OUTPUT_CHARS),
    )
    proc.start()
    proc.join(RUN_TIMEOUT_SECONDS)
    if proc.is_alive():
        proc.terminate()
        proc.join(1)
        if proc.is_alive() and hasattr(proc, "kill"):
            proc.kill()
            proc.join(1)
        return {
            'output': f'[Error] Eksekusi melewati batas waktu {RUN_TIMEOUT_SECONDS:g} detik dan dihentikan.\n'
        }, 408
    try:
        return result_queue.get_nowait(), 200
    except queue.Empty:
        pass
    if proc.exitcode and proc.exitcode != 0:
        return {'output': f'[Error] Worker playground berhenti dengan kode {proc.exitcode}.\n'}, 500
    return {'output': ''}, 200

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/run', methods=['POST'])
def run():
    data = request.get_json() or {}
    code = data.get('code', '')
    if len(code) > MAX_CODE_CHARS:
        return jsonify({'output': f'[Error] Kode terlalu panjang. Batas: {MAX_CODE_CHARS} karakter.'}), 400

    payload, status = _run_code_isolated(code, data.get('inputs'))
    payload['output'] = _trim_output(payload.get('output', ''))
    return jsonify(payload), status

@app.route('/transpile', methods=['POST'])
def transpile():
    data = request.get_json() or {}
    code = data.get('code', '')
    if len(code) > MAX_CODE_CHARS:
        return jsonify({'error': f'Kode terlalu panjang. Batas: {MAX_CODE_CHARS} karakter.'}), 400
    try:
        py = transpile_to_python(code)
        return jsonify({'py': py})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    print('Menjalankan server lokal pada http://127.0.0.1:5000')
    app.run(host='127.0.0.1', port=5000)
