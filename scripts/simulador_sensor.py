from __future__ import annotations

import argparse
import random
import time
from typing import Any

import requests


def criar_sensor(base_url: str, nome: str, localizacao: str) -> int:
    payload = {
        "nome": nome,
        "localizacao": localizacao,
        "descricao": "Sensor criado automaticamente pelo simulador.",
    }
    response = requests.post(f"{base_url}/sensores", json=payload, timeout=10)

    if response.status_code == 409:
        sensores = requests.get(f"{base_url}/sensores", timeout=10).json()
        for sensor in sensores:
            if sensor["nome"] == nome:
                return int(sensor["id"])
        raise RuntimeError("Sensor já existe, mas não foi encontrado na listagem.")

    response.raise_for_status()
    return int(response.json()["id"])


def enviar_leitura(base_url: str, sensor_id: int, temperatura: float, umidade: float) -> dict[str, Any]:
    payload = {
        "sensor_id": sensor_id,
        "temperatura": round(temperatura, 2),
        "umidade": round(umidade, 2),
    }
    response = requests.post(f"{base_url}/leituras", json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulador de sensor IoT de temperatura e umidade")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="URL base da API")
    parser.add_argument("--sensor-id", type=int, help="ID de um sensor já cadastrado")
    parser.add_argument("--nome", default="Sensor Simulado 01", help="Nome usado se o simulador precisar criar um sensor")
    parser.add_argument("--localizacao", default="Laboratório IoT", help="Localização usada ao criar sensor")
    parser.add_argument("--intervalo", type=float, default=2.0, help="Intervalo entre envios em segundos")
    parser.add_argument("--quantidade", type=int, default=20, help="Quantidade de leituras geradas")
    parser.add_argument("--temp-min", type=float, default=20.0, help="Temperatura mínima simulada")
    parser.add_argument("--temp-max", type=float, default=36.0, help="Temperatura máxima simulada")
    parser.add_argument("--umidade-min", type=float, default=45.0, help="Umidade mínima simulada")
    parser.add_argument("--umidade-max", type=float, default=85.0, help="Umidade máxima simulada")
    args = parser.parse_args()

    sensor_id = args.sensor_id or criar_sensor(args.base_url, args.nome, args.localizacao)
    print(f"Enviando leituras para o sensor ID {sensor_id}...")

    for indice in range(1, args.quantidade + 1):
        temperatura = random.uniform(args.temp_min, args.temp_max)
        umidade = random.uniform(args.umidade_min, args.umidade_max)
        leitura = enviar_leitura(args.base_url, sensor_id, temperatura, umidade)
        print(
            f"{indice:02d}/{args.quantidade} | "
            f"temperatura={leitura['temperatura']}°C | "
            f"umidade={leitura['umidade']}% | "
            f"status={leitura['status']}"
        )
        time.sleep(args.intervalo)


if __name__ == "__main__":
    main()
