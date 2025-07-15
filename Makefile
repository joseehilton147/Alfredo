.PHONY: help install test format clean docker-build docker-run setup

# Default target
help:
	@echo "🤖 Alfredo AI - Makefile"
	@echo ""
	@echo "📋 Available commands:"
	@echo "  setup        - Complete setup (recommended)"
	@echo "  install      - Install dependencies only"
	@echo "  test         - Run tests with coverage"
	@echo "  format       - Format code (black, isort)"
	@echo "  clean        - Clean build artifacts"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run in Docker"

# Complete setup
setup:
	@echo "🚀 Setting up Alfredo AI..."
	python -m venv venv || true
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -e .
	mkdir -p data/{input/{local,youtube},output,logs,temp}
	cp .env.example .env 2>/dev/null || true
	@echo "✅ Setup complete! Run: source venv/bin/activate && python -m src.main --help"

# Install dependencies
install:
	pip install -r requirements.txt
	pip install -e .

# Run tests
test:
	pytest tests/ -v --cov=src --cov-report=term-missing

# Format code
format:
	black src/ tests/
	isort src/ tests/

# Clean build artifacts
clean:
	rm -rf build/ dist/ *.egg-info/
	rm -rf .pytest_cache/ .mypy_cache/ .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Docker commands
docker-build:
	docker build -t alfredo-ai:latest .

docker-run:
	docker run -it --rm -v $(pwd)/data:/app/data alfredo-ai:latest

# Development install
install-dev: install
	pip install -r requirements-dev.txt
	pre-commit install

# Testing
test:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

test-watch:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term -f

test-integration:
	pytest tests/integration/ -v --cov=src --cov-report=html --cov-report=term

test-unit:
	pytest tests/unit/ -v --cov=src --cov-report=html --cov-report=term

# Linting
lint:
	flake8 src/ tests/
	mypy src/
	bandit -r src/

lint-fix:
	black src/ tests/
	isort src/ tests/

# Formatting
format:
	black src/ tests/
	isort src/ tests/

format-check:
	black --check src/ tests/
	isort --check-only src/ tests/

# Cleaning
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Building
build:
	python -m build

build-wheel:
	python setup.py bdist_wheel

build-sdist:
	python setup.py sdist

# Docker
docker-build:
	docker build -t alfredo-ai:latest .

docker-run:
	docker run --rm -it alfredo-ai:latest

docker-run-dev:
	docker run --rm -it -v $(PWD):/app -v $(PWD)/data:/app/data alfredo-ai:latest

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-shell:
	docker-compose exec alfredo-dev /bin/bash

# Pre-commit
pre-commit:
	pre-commit run --all-files

pre-commit-install:
	pre-commit install

# Development setup
setup-dev:
	python -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && make install-dev

# Environment
env-example:
	cp .env.example .env

# Documentation
docs:
	sphinx-build -b html docs/ docs/_build/html

docs-serve:
	cd docs/_build/html && python -m http.server 8000

# Security
security:
	bandit -r src/
	safety check

# Release
release-check:
	python -m build
	twine check dist/*

release-test:
	python -m build
	twine upload --repository testpypi dist/*

release:
	python -m build
	twine upload dist/*

# CI/CD
ci-test:
	pytest tests/ -v --cov=src --cov-report=xml --cov-report=term
	flake8 src/ tests/
	mypy src/
	bandit -r src/

# Utilities
update-deps:
	pip-compile requirements.in
	pip-compile requirements-dev.in

check-deps:
	pip-audit
	safety check

# Development server
dev-server:
	python -m alfredo_ai.server

# Database
db-init:
	python -m alfredo_ai.database init

db-migrate:
	python -m alfredo_ai.database migrate

db-reset:
	python -m alfredo_ai.database reset

# Monitoring
monitor:
	python -m alfredo_ai.monitor

# Backup
backup:
	tar -czf backup-$(shell date +%Y%m%d-%H%M%S).tar.gz data/ src/ tests/ requirements*.txt

restore:
	tar -xzf backup-*.tar.gz

# Performance
profile:
	python -m cProfile -o profile.stats -m alfredo_ai.cli process https://www.youtube.com/watch?v=example
	python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(20)"

# Benchmark
benchmark:
	python -m pytest tests/benchmark/ -v --benchmark-only

# All-in-one development setup
dev-setup: clean setup-dev pre-commit-install
	@echo "Development environment ready!"
	@echo "Run 'make test' to run tests"
	@echo "Run 'make lint' to run linting"
	@echo "Run 'make format' to format code"
