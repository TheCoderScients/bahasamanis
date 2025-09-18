# server.py - Flask server for BahasaManis playground
from flask import Flask, request, jsonify
import io, sys, traceback
from bahasamanis import Interpreter, transpile_to_python

app = Flask(__name__, static_folder='static')
# Disable static caching so UI updates are reflected without stale cache
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
interp = Interpreter()
interp.globals['user'] = 'Fatal'  # default interpolated user
interp_input_queue = []

# Wire interpreter input to pull from a queue provided per request
def _web_input_provider():
    return interp_input_queue.pop(0) if interp_input_queue else ""
interp.input_func = _web_input_provider

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/run', methods=['POST'])
def run():
    data = request.get_json() or {}
    code = data.get('code', '')
    # Prepare input queue from client (array of strings)
    global interp_input_queue
    inp = data.get('inputs')
    if isinstance(inp, list):
        # Normalize to strings
        interp_input_queue = [str(x) for x in inp]
    else:
        interp_input_queue = []
    old_stdout = sys.stdout
    buf = io.StringIO()
    sys.stdout = buf
    try:
        interp.run(code)
    except Exception as e:
        print(f"[Error] {e}")
    finally:
        sys.stdout = old_stdout
    return jsonify({'output': buf.getvalue()})

@app.route('/transpile', methods=['POST'])
def transpile():
    data = request.get_json() or {}
    code = data.get('code', '')
    try:
        py = transpile_to_python(code)
        return jsonify({'py': py})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    print('Menjalankan server lokal pada http://127.0.0.1:5000')
    app.run(host='127.0.0.1', port=5000)
