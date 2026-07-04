from __future__ import annotations

from typing import Any

from app.database import get_connection, row_to_dict


def normalize_sensor(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    row["ativo"] = bool(row["ativo"])
    return row


def create_sensor(nome: str, localizacao: str, descricao: str | None) -> dict[str, Any]:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO sensors (nome, localizacao, descricao)
            VALUES (?, ?, ?)
            """,
            (nome, localizacao, descricao),
        )
        sensor_id = cursor.lastrowid
        row = connection.execute("SELECT * FROM sensors WHERE id = ?", (sensor_id,)).fetchone()
        return normalize_sensor(row_to_dict(row))  # type: ignore[return-value]


def list_sensors(only_active: bool = False) -> list[dict[str, Any]]:
    query = "SELECT * FROM sensors"
    params: tuple[Any, ...] = ()
    if only_active:
        query += " WHERE ativo = 1"
    query += " ORDER BY id ASC"

    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()
        return [normalize_sensor(row_to_dict(row)) for row in rows if row is not None]  # type: ignore[list-item]


def get_sensor(sensor_id: int) -> dict[str, Any] | None:
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM sensors WHERE id = ?", (sensor_id,)).fetchone()
        return normalize_sensor(row_to_dict(row))


def update_sensor_status(sensor_id: int, ativo: bool) -> dict[str, Any] | None:
    with get_connection() as connection:
        connection.execute("UPDATE sensors SET ativo = ? WHERE id = ?", (int(ativo), sensor_id))
        row = connection.execute("SELECT * FROM sensors WHERE id = ?", (sensor_id,)).fetchone()
        return normalize_sensor(row_to_dict(row))


def create_reading(sensor_id: int, temperatura: float, umidade: float, status: str) -> dict[str, Any]:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO readings (sensor_id, temperatura, umidade, status)
            VALUES (?, ?, ?, ?)
            """,
            (sensor_id, temperatura, umidade, status),
        )
        reading_id = cursor.lastrowid
        row = connection.execute("SELECT * FROM readings WHERE id = ?", (reading_id,)).fetchone()
        return row_to_dict(row)  # type: ignore[return-value]


def list_readings(
    sensor_id: int | None = None,
    limit: int = 50,
    apenas_alertas: bool = False,
) -> list[dict[str, Any]]:
    query = "SELECT * FROM readings WHERE 1=1"
    params: list[Any] = []

    if sensor_id is not None:
        query += " AND sensor_id = ?"
        params.append(sensor_id)

    if apenas_alertas:
        query += " AND status != 'NORMAL'"

    query += " ORDER BY criado_em DESC, id DESC LIMIT ?"
    params.append(limit)

    with get_connection() as connection:
        rows = connection.execute(query, tuple(params)).fetchall()
        return [row_to_dict(row) for row in rows if row is not None]  # type: ignore[list-item]


def get_dashboard_summary() -> dict[str, Any]:
    with get_connection() as connection:
        total_sensores = connection.execute("SELECT COUNT(*) FROM sensors").fetchone()[0]
        sensores_ativos = connection.execute("SELECT COUNT(*) FROM sensors WHERE ativo = 1").fetchone()[0]
        total_leituras = connection.execute("SELECT COUNT(*) FROM readings").fetchone()[0]
        total_alertas = connection.execute("SELECT COUNT(*) FROM readings WHERE status != 'NORMAL'").fetchone()[0]
        medias = connection.execute(
            "SELECT AVG(temperatura) AS media_temperatura, AVG(umidade) AS media_umidade FROM readings"
        ).fetchone()
        ultima = connection.execute("SELECT * FROM readings ORDER BY criado_em DESC, id DESC LIMIT 1").fetchone()

    return {
        "total_sensores": total_sensores,
        "sensores_ativos": sensores_ativos,
        "total_leituras": total_leituras,
        "total_alertas": total_alertas,
        "media_temperatura": round(medias["media_temperatura"], 2) if medias["media_temperatura"] is not None else None,
        "media_umidade": round(medias["media_umidade"], 2) if medias["media_umidade"] is not None else None,
        "ultima_leitura": row_to_dict(ultima),
    }
