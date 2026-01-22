.PHONY: help install test lint format clean docker-build docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make install     - Install dependencies"
	@echo "  make test        - Run tests"
	@echo "  make lint        - Run linter"
	@echo "  make format      - Format code"
	@echo "  make clean       - Clean temporary files"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-up   - Start infrastructure (Kafka, PostgreSQL)"
	@echo "  make docker-down - Stop infrastructure"

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt 2>/dev/null || true

test:
	pytest tests/ -v

lint:
	flake8 src/ tests/ --max-line-length=120 --exclude=__pycache__

format:
	black src/ tests/
	isort src/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov dist build *.egg-info

docker-build:
	docker build -t zoomcar-etl .

docker-up:
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 15
	@echo "Services started!"

docker-down:
	docker-compose down -v
