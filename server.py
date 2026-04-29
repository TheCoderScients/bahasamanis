# server.py - Flask server for BahasaManis playground
from flask import Flask, request, jsonify
import io, os, sys
from bahasamanis import Interpreter, transpile_to_python

app = Flask(__name__, static_folder='static')
# Disable static caching so UI updates are reflected without stale cache
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

PLAYGROUND_UNSAFE = os.environ.get("BM_PLAYGROUND_UNSAFE") == "1"
MAX_CODE_CHARS = int(os.environ.get("BM_PLAYGROUND_MAX_CODE_CHARS", "20000"))
MAX_OUTPUT_CHARS = int(os.environ.get("BM_PLAYGROUND_MAX_OUTPUT_CHARS", "20000"))

def _trim_output(text: str) -> str:
    if len(text) <= MAX_OUTPUT_CHARS:
        return text
    return text[:MAX_OUTPUT_CHARS] + "\n[Output dipotong agar playground tetap stabil]\n"

def _make_request_interpreter(inputs):
    input_queue = [str(x) for x in inputs] if isinstance(inputs, list) else []
    interp = Interpreter(aman=not PLAYGROUND_UNSAFE)
    interp.globals['user'] = 'Fatal'

    def _web_input_provider():
        return input_queue.pop(0) if input_queue else ""

    interp.input_func = _web_input_provider
    return interp

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/run', methods=['POST'])
def run():
    data = request.get_json() or {}
    code = data.get('code', '')
    if len(code) > MAX_CODE_CHARS:
        return jsonify({'output': f'[Error] Kode terlalu panjang. Batas: {MAX_CODE_CHARS} karakter.'}), 400

    interp = _make_request_interpreter(data.get('inputs'))
    old_stdout = sys.stdout
    buf = io.StringIO()
    sys.stdout = buf
    try:
        interp.run(code)
    except Exception as e:
        print(f"[Error] {e}")
    finally:
        sys.stdout = old_stdout
    return jsonify({'output': _trim_output(buf.getvalue())})

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
