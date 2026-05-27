# ─────────────────────────────────────────────
# Weather ETL Pipeline — Makefile
# ─────────────────────────────────────────────

.PHONY: help up down restart logs status test clean init

help:
	@echo "Available commands:"
	@echo "  make up       - Start all containers"
	@echo "  make down     - Stop all containers"
	@echo "  make restart  - Restart all containers"
	@echo "  make logs     - Show logs from all containers"
	@echo "  make status   - Show container status"
	@echo "  make test     - Run unit tests"
	@echo "  make init     - Initialize Airflow (first time only)"
	@echo "  make clean    - Stop containers and remove volumes"

up:
	docker-compose up airflow-webserver airflow-scheduler postgres -d
	@echo "Pipeline started. Airflow UI at http://localhost:8080"
	@echo "Login: admin / admin"

down:
	docker-compose down

restart:
	docker-compose down
	docker-compose up airflow-webserver airflow-scheduler postgres -d

logs:
	docker-compose logs -f

status:
	docker-compose ps

test:
	pytest tests/ -v

init:
	docker-compose up airflow-init
	@echo "Airflow initialized. Run make up to start the pipeline."

clean:
	docker-compose down -v
	@echo "All containers and volumes removed"