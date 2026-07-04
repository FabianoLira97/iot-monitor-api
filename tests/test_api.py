from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ["DATABASE_URL"] = tempfile.NamedTemporaryFile(suffix=".db", delete=False).name

from fastapi.testclient import TestClient  # noqa: E402

from app.database import init_db  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app)


def setup_function():
    init_db()


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_sensor_and_reading():
    sensor_response = client.post(
        "/sensores",
        json={
            "nome": "Sensor Teste",
            "localizacao": "Bancada 01",
            "descricao": "Sensor usado em teste automatizado",
        },
    )
    assert sensor_response.status_code == 201
    sensor_id = sensor_response.json()["id"]

    leitura_response = client.post(
        "/leituras",
        json={"sensor_id": sensor_id, "temperatura": 25.5, "umidade": 60.0},
    )
    assert leitura_response.status_code == 201
    assert leitura_response.json()["status"] == "NORMAL"


def test_temperature_alert():
    sensor_response = client.post(
        "/sensores",
        json={"nome": "Sensor Alerta", "localizacao": "Sala de Máquinas"},
    )
    sensor_id = sensor_response.json()["id"]

    leitura_response = client.post(
        "/leituras",
        json={"sensor_id": sensor_id, "temperatura": 35.0, "umidade": 50.0},
    )
    assert leitura_response.status_code == 201
    assert leitura_response.json()["status"] == "ALERTA_TEMPERATURA"
