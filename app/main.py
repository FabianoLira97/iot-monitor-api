from __future__ import annotations

import os
import sqlite3
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, status

from app.database import init_db
from app.repository import (
    create_reading,
    create_sensor,
    get_dashboard_summary,
    get_sensor,
    list_readings,
    list_sensors,
    update_sensor_status,
)
from app.schemas import (
    DashboardResumo,
    ReadingCreate,
    ReadingResponse,
    SensorCreate,
    SensorResponse,
    SensorUpdateStatus,
)

TEMP_MAX = float(os.getenv("TEMP_MAX", "30"))
UMIDADE_MAX = float(os.getenv("UMIDADE_MAX", "70"))


def calculate_status(temperatura: float, umidade: float) -> str:
    """Return reading status according to configured alert thresholds."""
    temp_alert = temperatura > TEMP_MAX
    humidity_alert = umidade > UMIDADE_MAX

    if temp_alert and humidity_alert:
        return "ALERTA_TEMPERATURA_UMIDADE"
    if temp_alert:
        return "ALERTA_TEMPERATURA"
    if humidity_alert:
        return "ALERTA_UMIDADE"
    return "NORMAL"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="IoT Monitor API",
    description="API REST para monitoramento IoT de temperatura e umidade com sensores simulados.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", tags=["Status"])
def root() -> dict[str, str]:
    return {
        "mensagem": "IoT Monitor API está online",
        "documentacao": "/docs",
    }


@app.get("/health", tags=["Status"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/sensores", response_model=SensorResponse, status_code=status.HTTP_201_CREATED, tags=["Sensores"])
def cadastrar_sensor(sensor: SensorCreate):
    try:
        return create_sensor(sensor.nome, sensor.localizacao, sensor.descricao)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um sensor cadastrado com esse nome.",
        ) from exc


@app.get("/sensores", response_model=list[SensorResponse], tags=["Sensores"])
def listar_sensores(ativos: bool = Query(default=False, description="Filtrar apenas sensores ativos")):
    return list_sensors(only_active=ativos)


@app.get("/sensores/{sensor_id}", response_model=SensorResponse, tags=["Sensores"])
def buscar_sensor(sensor_id: int):
    sensor = get_sensor(sensor_id)
    if sensor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sensor não encontrado.")
    return sensor


@app.patch("/sensores/{sensor_id}/status", response_model=SensorResponse, tags=["Sensores"])
def alterar_status_sensor(sensor_id: int, payload: SensorUpdateStatus):
    sensor = update_sensor_status(sensor_id, payload.ativo)
    if sensor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sensor não encontrado.")
    return sensor


@app.post("/leituras", response_model=ReadingResponse, status_code=status.HTTP_201_CREATED, tags=["Leituras"])
def registrar_leitura(leitura: ReadingCreate):
    sensor = get_sensor(leitura.sensor_id)
    if sensor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sensor não encontrado.")
    if not sensor["ativo"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sensor inativo. Ative o sensor antes de registrar leituras.")

    status_leitura = calculate_status(leitura.temperatura, leitura.umidade)
    return create_reading(
        sensor_id=leitura.sensor_id,
        temperatura=leitura.temperatura,
        umidade=leitura.umidade,
        status=status_leitura,
    )


@app.get("/leituras", response_model=list[ReadingResponse], tags=["Leituras"])
def listar_leituras(
    sensor_id: int | None = Query(default=None, ge=1),
    limit: Annotated[int, Query(ge=1, le=500)] = 50,
    apenas_alertas: bool = Query(default=False),
):
    if sensor_id is not None and get_sensor(sensor_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sensor não encontrado.")
    return list_readings(sensor_id=sensor_id, limit=limit, apenas_alertas=apenas_alertas)


@app.get("/leituras/alertas", response_model=list[ReadingResponse], tags=["Leituras"])
def listar_alertas(limit: Annotated[int, Query(ge=1, le=500)] = 50):
    return list_readings(limit=limit, apenas_alertas=True)


@app.get("/dashboard/resumo", response_model=DashboardResumo, tags=["Dashboard"])
def dashboard_resumo():
    return get_dashboard_summary()
