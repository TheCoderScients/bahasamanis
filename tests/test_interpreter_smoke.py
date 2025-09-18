import re
from bahasamanis import Interpreter, transpile_to_python

def test_print_smoke(capsys):
    src = 'cetak "Halo"'
    it = Interpreter()
    it.run(src)
    captured = capsys.readouterr()
    assert "Halo" in captured.out

def test_transpile_smoke():
    src = 'cetak "Halo, {1+2}"'
    py = transpile_to_python(src)
    assert "def __bm_main():" in py
    # pastikan interpolasi menjadi f-string
    assert 'print(f"Halo, {1+2}")' in py
