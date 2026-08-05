import json

import pytest

import flask_website as site


@pytest.fixture
def client(tmp_path, monkeypatch):
    banco_teste = tmp_path / "banco_dados.json"
    banco_teste.write_text(json.dumps({"usuarios_salvos": []}), encoding="utf-8")
    monkeypatch.setattr(site, "arquivo_banco", str(banco_teste))
    site.app.config["TESTING"] = True
    with site.app.test_client() as client:
        yield client


def test_duplicated_user_returns_conflict_page(client):
    client.post(
        "/api/dados",
        data={
            "nome_usuario": "ana",
            "idade": "20",
            "email": "ana@example.com",
            "senha": "123456",
        },
    )

    response = client.post(
        "/api/dados",
        data={
            "nome_usuario": "ANA",
            "idade": "21",
            "email": "outra@example.com",
            "senha": "654321",
        },
    )

    assert response.status_code == 409
    assert b"ERROR 409" in response.data
    assert b"Este nome de usu\u00e1rio j\u00e1 est\u00e1 sendo utilizado" in response.data
