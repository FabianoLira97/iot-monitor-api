install:
	python -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

run:
	uvicorn app.main:app --reload

simulator:
	python scripts/simulador_sensor.py --quantidade 20 --intervalo 2

test:
	pytest -q

docker-build:
	docker compose build

docker-run:
	docker compose up
