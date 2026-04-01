from fastapi.testclient import TestClient

from hingc.api.main import app


client = TestClient(app)


def test_health_endpoint():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["version"]


def test_examples_endpoint_contains_defaults():
    resp = client.get("/api/examples")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert any(item["name"] == "Hello Duniya" for item in data)


def test_snippet_save_and_get():
    save = client.post("/api/snippets/save", json={"title": "t1", "code": "shuru\nkhatam\n"})
    assert save.status_code == 200
    saved = save.json()
    assert saved["snippet_id"] > 0

    fetch = client.get(f"/api/snippets/{saved['snippet_id']}")
    assert fetch.status_code == 200
    fetched = fetch.json()
    assert fetched["title"] == "t1"
    assert fetched["code"] == "shuru\nkhatam\n"


def test_compile_endpoint_returns_compilation_payload():
    payload = {
        "source_code": 'shuru\nlikho("Hi\\n")\nkhatam\n',
        "get_llm_advice": False,
        "stdin_input": "",
    }
    resp = client.post("/api/compile", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["success"] is True
    assert isinstance(data["tokens"], list)
    assert data["ast_json"] is not None
    assert data["generated_c_code"] is not None
    assert data["phase_failed"] is None


def test_websocket_compile_streams_phases_and_done():
    with client.websocket_connect("/ws/compile") as ws:
        ws.send_json({"source_code": "shuru\nlikho(\"x\\n\")\nkhatam\n", "get_llm_advice": False, "stdin_input": ""})
        first = ws.receive_json()
        assert first["event"] == "phase"
        assert "lexing" in first["message"]

        done = None
        for _ in range(8):
            msg = ws.receive_json()
            if msg.get("event") == "done":
                done = msg
                break

        assert done is not None
        assert "result" in done
        assert "success" in done["result"]
