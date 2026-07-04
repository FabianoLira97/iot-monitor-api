from __future__ import annotations

from pydantic import BaseModel, Field


class SensorCreate(BaseModel):
    nome: str = Field(..., min_length=3, max_length=80, examples=["Sensor Linha 01"])
    localizacao: str = Field(..., min_length=2, max_length=120, examples=["Setor de Produção"])
    descricao: str | None = Field(default=None, max_length=255, examples=["Sensor simulado de temperatura e umidade"])


class SensorUpdateStatus(BaseModel):
    ativo: bool = Field(..., examples=[True])


class SensorResponse(BaseModel):
    id: int
    nome: str
    localizacao: str
    descricao: str | None
    ativo: bool
    criado_em: str


class ReadingCreate(BaseModel):
    sensor_id: int = Field(..., ge=1, examples=[1])
    temperatura: float = Field(..., ge=-50, le=120, examples=[26.5])
    umidade: float = Field(..., ge=0, le=100, examples=[61.0])


class ReadingResponse(BaseModel):
    id: int
    sensor_id: int
    temperatura: float
    umidade: float
    status: str
    criado_em: str


class DashboardResumo(BaseModel):
    total_sensores: int
    sensores_ativos: int
    total_leituras: int
    total_alertas: int
    media_temperatura: float | None
    media_umidade: float | None
    ultima_leitura: ReadingResponse | None
