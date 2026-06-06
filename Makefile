.PHONY: help start stop restart logs clean init-db download-model test

help: ## Show this help message
	@echo "CANMOS-NITI - Available Commands"
	@echo "================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

start: ## Start all Docker containers
	@echo "Starting CANMOS-NITI..."
	docker compose up -d
	@echo "Services started successfully!"
	@echo "Frontend:      http://localhost:3000"
	@echo "Backend API:   http://localhost:8000/docs"
	@echo "MinIO Console: http://localhost:9001"

start-ocr: ## Start with OCR service
	@echo "Starting CANMOS-NITI with OCR..."
	COMPOSE_PROFILES=ocr docker compose up -d
	@echo "Services started with OCR!"

start-prod: ## Start production stack (with nginx)
	@echo "Starting CANMOS-NITI production..."
	docker compose -f docker-compose.prod.yml up -d
	@echo "Production stack started on http://localhost:80"

stop: ## Stop all Docker containers
	@echo "Stopping CANMOS-NITI..."
	docker compose down

stop-prod: ## Stop production stack
	docker compose -f docker-compose.prod.yml down

restart: ## Restart all containers
	@echo "Restarting CANMOS-NITI..."
	docker compose restart

logs: ## Show logs from all containers
	docker compose logs -f

logs-backend: ## Show backend logs only
	docker compose logs -f backend

logs-frontend: ## Show frontend logs only
	docker compose logs -f frontend

clean: ## Stop containers and remove volumes
	@echo "Cleaning up..."
	docker compose down -v
	@echo "Done!"

init-db: ## Run database migrations
	@echo "Running database migrations..."
	cd backend && alembic upgrade head
	@echo "Migrations completed!"

db-migrate: ## Create new migration (autogenerate)
	@echo "Creating new migration..."
	@read -p "Migration name: " name; \
	cd backend && alembic revision --autogenerate -m "$$name"

db-upgrade: ## Apply all pending migrations
	@echo "Applying migrations..."
	cd backend && alembic upgrade head

db-downgrade: ## Rollback last migration
	@echo "Rolling back last migration..."
	cd backend && alembic downgrade -1

db-current: ## Show current migration revision
	cd backend && alembic current

db-history: ## Show migration history
	cd backend && alembic history

db-verify: ## Verify database schema
	@echo "Verifying database schema..."
	cd backend && python scripts/verify_schema.py

validate: ## Validate project structure and configs
	@echo "Validating project..."
	cd backend && python scripts/validate_project.py

download-model: ## Download Ollama AI model (legacy - now auto-pulls)
	@echo "Downloading Ollama model..."
	docker exec canmos-ollama ollama pull phi3:mini
	@echo "Model downloaded!"

test-backend: ## Run backend tests
	@echo "Running backend tests..."
	cd backend && pytest --cov=app --cov-report=html

test-frontend: ## Run frontend tests
	@echo "Running frontend tests..."
	cd frontend && npm test -- --coverage

test-all: ## Run all tests (backend + frontend)
	@echo "Running all tests..."
	$(MAKE) test-backend
	$(MAKE) test-frontend
	@echo "All tests completed!"

dev-backend: ## Run backend in development mode (without Docker)
	@echo "Starting backend in dev mode..."
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Run frontend in development mode (without Docker)
	@echo "Starting frontend in dev mode..."
	cd frontend && npm run dev

shell-backend: ## Open shell in backend container
	docker exec -it canmos-backend /bin/bash

shell-db: ## Open PostgreSQL shell (Supabase)
	@echo "Connect to Supabase PostgreSQL..."
	@echo "Use: psql $(DATABASE_URL)"

install: ## Install dependencies (backend + frontend)
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Dependencies installed!"

format: ## Format code (black + prettier)
	@echo "Formatting backend code..."
	cd backend && black app/
	@echo "Formatting frontend code..."
	cd frontend && npx prettier --write .

lint: ## Lint code (ruff + eslint)
	@echo "Linting backend..."
	cd backend && ruff check app/
	@echo "Linting frontend..."
	cd frontend && npm run lint
