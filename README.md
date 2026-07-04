# IoT Monitor API

API REST para monitoramento de temperatura e umidade usando sensores IoT simulados.

Este projeto foi criado para portfólio no GitHub e demonstra conceitos de **Python**, **API REST**, **SQLite**, **IoT**, **automação industrial**, validação de dados e organização básica de backend.

## Funcionalidades

- Cadastro e listagem de sensores.
- Ativação e desativação de sensores.
- Registro de leituras de temperatura e umidade.
- Classificação automática de leituras como normal ou alerta.
- Consulta de histórico de leituras.
- Consulta específica de alertas.
- Resumo para dashboard.
- Simulador de sensor enviando dados automaticamente para a API.
- Testes automatizados básicos.
- Execução local ou via Docker.

## Tecnologias utilizadas

- Python
- FastAPI
- SQLite
- Uvicorn
- Pydantic
- Requests
- Pytest
- Docker

## Estrutura do projeto

```text
.
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   ├── repository.py
│   └── schemas.py
├── scripts/
│   └── simulador_sensor.py
├── tests/
│   └── test_api.py
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── LICENSE
├── Makefile
├── README.md
└── requirements.txt
```

## Como executar localmente

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/iot-monitor-api.git
cd iot-monitor-api
```

### 2. Crie o ambiente virtual

No Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

No Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Execute a API

```bash
uvicorn app.main:app --reload
```

A API ficará disponível em:

```text
http://127.0.0.1:8000
```

A documentação interativa ficará em:

```text
http://127.0.0.1:8000/docs
```

## Como executar com Docker

```bash
docker compose up --build
```

Depois acesse:

```text
http://127.0.0.1:8000/docs
```

## Variáveis de ambiente

Crie um arquivo `.env` baseado no `.env.example`, se quiser personalizar os limites de alerta:

```env
DATABASE_URL=sqlite:///iot_monitor.db
TEMP_MAX=30
UMIDADE_MAX=70
```

Por padrão:

- Leituras com temperatura maior que `30°C` geram alerta.
- Leituras com umidade maior que `70%` geram alerta.

## Endpoints principais

### Status da API

```http
GET /health
```

Resposta:

```json
{
  "status": "ok"
}
```

### Cadastrar sensor

```http
POST /sensores
```

Body:

```json
{
  "nome": "Sensor Linha 01",
  "localizacao": "Setor de Produção",
  "descricao": "Sensor de temperatura e umidade da linha 01"
}
```

### Listar sensores

```http
GET /sensores
```

### Buscar sensor por ID

```http
GET /sensores/1
```

### Ativar ou desativar sensor

```http
PATCH /sensores/1/status
```

Body:

```json
{
  "ativo": true
}
```

### Registrar leitura

```http
POST /leituras
```

Body:

```json
{
  "sensor_id": 1,
  "temperatura": 28.5,
  "umidade": 62.0
}
```

### Listar leituras

```http
GET /leituras
```

Com filtros:

```http
GET /leituras?sensor_id=1&limit=10&apenas_alertas=false
```

### Listar alertas

```http
GET /leituras/alertas
```

### Resumo do dashboard

```http
GET /dashboard/resumo
```

Exemplo de resposta:

```json
{
  "total_sensores": 1,
  "sensores_ativos": 1,
  "total_leituras": 20,
  "total_alertas": 5,
  "media_temperatura": 27.86,
  "media_umidade": 61.42,
  "ultima_leitura": {
    "id": 20,
    "sensor_id": 1,
    "temperatura": 31.2,
    "umidade": 66.5,
    "status": "ALERTA_TEMPERATURA",
    "criado_em": "2026-07-04 12:00:00"
  }
}
```

## Usando o simulador de sensor

Com a API rodando, execute:

```bash
python scripts/simulador_sensor.py
```

O simulador cria um sensor automaticamente, caso não seja informado um ID, e envia leituras aleatórias para a API.

Exemplo com parâmetros:

```bash
python scripts/simulador_sensor.py --quantidade 30 --intervalo 1 --temp-min 22 --temp-max 38 --umidade-min 40 --umidade-max 90
```

Exemplo usando um sensor já cadastrado:

```bash
python scripts/simulador_sensor.py --sensor-id 1 --quantidade 10
```

## Rodando os testes

```bash
pytest -q
```

## Regras de alerta

A API define o status de cada leitura assim:

| Condição | Status |
|---|---|
| Temperatura dentro do limite e umidade dentro do limite | `NORMAL` |
| Temperatura acima do limite | `ALERTA_TEMPERATURA` |
| Umidade acima do limite | `ALERTA_UMIDADE` |
| Temperatura e umidade acima do limite | `ALERTA_TEMPERATURA_UMIDADE` |

## Ideias de melhorias futuras

- Criar frontend com dashboard visual.
- Adicionar autenticação com JWT.
- Usar PostgreSQL em vez de SQLite.
- Integrar com MQTT.
- Enviar alertas por e-mail ou Telegram.
- Criar gráficos com histórico por sensor.
- Adicionar deploy em Render, Railway ou Fly.io.

## Objetivo do projeto

Este projeto simula um cenário comum em ambientes industriais: sensores enviando dados de temperatura e umidade para uma aplicação central, que armazena as leituras e identifica situações de alerta automaticamente.

Ele pode ser usado como projeto inicial de portfólio para demonstrar conhecimentos em backend, banco de dados, APIs REST, automação e IoT.

## Licença

Este projeto está sob a licença MIT.
