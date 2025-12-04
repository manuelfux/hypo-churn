.PHONY: help build up down restart logs shell test clean health

# Docker Compose command (supports both v1 and v2)
DOCKER_COMPOSE := $(shell command -v docker-compose 2> /dev/null)
ifndef DOCKER_COMPOSE
	DOCKER_COMPOSE := docker compose
endif

# Default target
help:
	@echo "Verfügbare Befehle:"
	@echo "  make build      - Docker Image bauen"
	@echo "  make up         - API starten (Vordergrund)"
	@echo "  make up-bg      - API starten (Hintergrund)"
	@echo "  make down       - API stoppen"
	@echo "  make restart    - API neu starten"
	@echo "  make logs       - Logs anzeigen"
	@echo "  make shell      - In den Container einsteigen"
	@echo "  make health     - Health Check ausführen"
	@echo "  make test       - Tests im Container ausführen"
	@echo "  make clean      - Container und Images entfernen"
	@echo "  make rebuild    - Alles neu bauen (no-cache)"

# Build Docker image
build:
	$(DOCKER_COMPOSE) build

# Build without cache
rebuild:
	$(DOCKER_COMPOSE) build --no-cache

# Start API in foreground
up:
	$(DOCKER_COMPOSE) up

# Start API in background
up-bg:
	$(DOCKER_COMPOSE) up -d
	@echo "API läuft im Hintergrund auf http://localhost:8000"
	@echo "Docs: http://localhost:8000/docs"

# Stop API
down:
	$(DOCKER_COMPOSE) down

# Restart API
restart:
	$(DOCKER_COMPOSE) restart

# Show logs
logs:
	$(DOCKER_COMPOSE) logs -f api

# Enter container shell
shell:
	$(DOCKER_COMPOSE) exec api bash

# Health check
health:
	@echo "Checking API health..."
	@curl -s http://localhost:8000/health | python -m json.tool || echo "API nicht erreichbar"

# Run tests inside container
test:
	$(DOCKER_COMPOSE) exec api pytest

# Clean up
clean:
	$(DOCKER_COMPOSE) down -v --rmi local
	@echo "Cleanup abgeschlossen"

# Show container status
status:
	$(DOCKER_COMPOSE) ps

# Show API info
info:
	@curl -s http://localhost:8000/model/info | python -m json.tool || echo "API nicht erreichbar"
