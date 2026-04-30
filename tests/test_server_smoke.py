import server

def post_run(client, code, inputs=None):
    return client.post("/run", json={"code": code, "inputs": inputs or []})

def test_playground_runs_basic_code():
    client = server.app.test_client()
    response = post_run(client, 'cetak "Halo playground"')
    assert response.status_code == 200
    assert "Halo playground" in response.get_json()["output"]

def test_playground_safe_mode_blocks_import_and_file_access():
    client = server.app.test_client()

    response = post_run(client, 'paket "os" sebagai os')
    assert response.status_code == 200
    assert "mode aman" in response.get_json()["output"]

    response = post_run(client, 'tulis_berkas("/tmp/bm-playground.txt", "isi")')
    assert response.status_code == 200
    assert "mode aman" in response.get_json()["output"]

def test_playground_limits_output(monkeypatch):
    monkeypatch.setattr(server, "MAX_OUTPUT_CHARS", 12)
    client = server.app.test_client()
    response = post_run(client, 'cetak "12345678901234567890"')
    output = response.get_json()["output"]
    assert "123456789012" in output
    assert "Output dipotong" in output

def test_playground_times_out_infinite_loop(monkeypatch):
    monkeypatch.setattr(server, "RUN_TIMEOUT_SECONDS", 0.25)
    client = server.app.test_client()
    response = post_run(client, "selama benar lakukan\n    lewati\nakhir")
    assert response.status_code == 408
    assert "melewati batas waktu" in response.get_json()["output"]
