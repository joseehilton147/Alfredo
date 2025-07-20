.PHONY: help install test format clean docker-build docker-run setup quality-check quality-report

# Default target
help:
	@echo "🤖 Alfredo AI - Makefile"
	@echo ""
	@echo "📋 Available commands:"
	@echo ""
	@echo "🚀 Setup & Installation:"
	@echo "  setup           - Complete setup (recommended)"
	@echo "  install         - Install dependencies only"
	@echo "  install-dev     - Install development dependencies"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  test            - Run all tests with coverage"
	@echo "  test-unit       - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-bdd        - Run BDD tests only"
	@echo "  test-watch      - Run tests in watch mode"
	@echo ""
	@echo "🔍 Quality Assurance:"
	@echo "  quality-check   - Run all quality checks (recommended)"
	@echo "  quality-report  - Generate comprehensive quality report"
	@echo "  lint            - Run linting tools"
	@echo "  format          - Format code (black, isort)"
	@echo "  format-check    - Check code formatting"
	@echo "  complexity      - Check code complexity"
	@echo "  duplication     - Check code duplication"
	@echo "  security        - Run security analysis"
	@echo "  type-check      - Run type checking"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  docker-build    - Build Docker image"
	@echo "  docker-run      - Run in Docker"
	@echo "  docker-up       - Start services with docker-compose"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  clean           - Clean build artifacts"
	@echo "  clean-all       - Deep clean (including caches)"

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

# ============================================================================
# QUALITY ASSURANCE PIPELINE
# ============================================================================

# Main quality check command - runs all quality verifications
quality-check: format-check lint type-check complexity duplication security test-coverage
	@echo ""
	@echo "🎉 All quality checks completed!"
	@echo "📊 Run 'make quality-report' for detailed report"

# Generate comprehensive quality report
quality-report:
	@echo "📊 Generating comprehensive quality report..."
	@mkdir -p data/output/reports
	@echo "$(shell date)" > data/output/reports/quality_report_$(shell date +%Y%m%d_%H%M%S).txt
	@echo "=" >> data/output/reports/quality_report_$(shell date +%Y%m%d_%H%M%S).txt
	@echo "ALFREDO AI - QUALITY REPORT" >> data/output/reports/quality_report_$(shell date +%Y%m%d_%H%M%S).txt
	@echo "=" >> data/output/reports/quality_report_$(shell date +%Y%m%d_%H%M%S).txt
	@$(MAKE) --no-print-directory quality-check-parallel 2>&1 | tee -a data/output/reports/quality_report_$(shell date +%Y%m%d_%H%M%S).txt
	@echo "📄 Quality report saved to data/output/reports/"

# Parallel quality checks for faster execution
quality-check-parallel:
	@echo "🚀 Running quality checks in parallel..."
	@$(MAKE) --no-print-directory -j4 format-check-silent lint-silent type-check-silent complexity-silent
	@$(MAKE) --no-print-directory duplication-silent security-silent
	@$(MAKE) --no-print-directory test-coverage-silent
	@echo "✅ All parallel checks completed"

# Silent versions for parallel execution
format-check-silent:
	@echo "🎨 Checking code formatting..."
	@black --check --quiet src/ tests/ || (echo "❌ Code formatting issues found" && exit 1)
	@isort --check-only --quiet src/ tests/ || (echo "❌ Import sorting issues found" && exit 1)
	@echo "✅ Code formatting OK"

lint-silent:
	@echo "🔍 Running linting..."
	@flake8 src/ tests/ --quiet || (echo "❌ Linting issues found" && exit 1)
	@pylint src/ --score=no --reports=no || (echo "❌ Pylint issues found" && exit 1)
	@echo "✅ Linting OK"

type-check-silent:
	@echo "🔤 Checking types..."
	@mypy src/ --no-error-summary || (echo "❌ Type checking issues found" && exit 1)
	@echo "✅ Type checking OK"

complexity-silent:
	@echo "📊 Checking complexity..."
	@python scripts/quality_check.py --json > /dev/null || (echo "❌ Complexity issues found" && exit 1)
	@echo "✅ Complexity OK"

duplication-silent:
	@echo "🔄 Checking duplication..."
	@python scripts/duplication_check.py --json > /dev/null || (echo "❌ Duplication issues found" && exit 1)
	@echo "✅ Duplication OK"

security-silent:
	@echo "🔒 Running security analysis..."
	@bandit -r src/ -f json -o /dev/null --quiet || (echo "❌ Security issues found" && exit 1)
	@safety check --json > /dev/null || (echo "❌ Dependency vulnerabilities found" && exit 1)
	@echo "✅ Security OK"

test-coverage-silent:
	@echo "🧪 Checking test coverage..."
	@python scripts/coverage_analysis.py --min-coverage 80 --output /dev/null --no-run > /dev/null || (echo "❌ Test coverage below 80%" && exit 1)
	@echo "✅ Test coverage OK"

# Individual quality checks (verbose versions)
complexity:
	@echo "📊 Running complexity analysis..."
	@python scripts/quality_check.py
	@echo "✅ Complexity check completed"

duplication:
	@echo "🔄 Running duplication analysis..."
	@python scripts/duplication_check.py
	@echo "✅ Duplication check completed"

extension-time:
	@echo "⏱️ Validating extension time..."
	@python scripts/validate_extension_time.py
	@echo "✅ Extension time validation completed"

# Enhanced linting with multiple tools
lint-full:
	@echo "🔍 Running comprehensive linting..."
	@flake8 src/ tests/
	@pylint src/
	@vulture src/ --min-confidence 80
	@echo "✅ Comprehensive linting completed"

# Code quality metrics
metrics:
	@echo "📈 Generating code metrics..."
	@mkdir -p data/output/metrics
	@radon cc src/ --json > data/output/metrics/complexity.json
	@radon mi src/ --json > data/output/metrics/maintainability.json
	@radon raw src/ --json > data/output/metrics/raw_metrics.json
	@echo "📊 Metrics saved to data/output/metrics/"

# Test coverage with detailed report
test-coverage:
	@echo "🧪 Running tests with coverage analysis..."
	@pytest tests/ --cov=src --cov-report=html:data/output/coverage --cov-report=xml:data/output/coverage.xml --cov-report=term-missing --cov-fail-under=80
	@echo "📊 Coverage report saved to data/output/coverage/"

# Automated coverage analysis with detailed reporting
coverage-analysis:
	@echo "📊 Running automated coverage analysis..."
	@python scripts/coverage_analysis.py --output data/output/reports/coverage_detailed.txt
	@echo "✅ Detailed coverage analysis completed"

# Coverage analysis without running tests (use existing coverage.json)
coverage-analysis-quick:
	@echo "⚡ Quick coverage analysis (using existing data)..."
	@python scripts/coverage_analysis.py --no-run --output data/output/reports/coverage_quick.txt
	@echo "✅ Quick coverage analysis completed"

# Coverage regression check
coverage-regression:
	@echo "🔍 Checking coverage regression..."
	@python scripts/coverage_analysis.py --baseline data/output/reports/coverage_baseline.json
	@echo "✅ Coverage regression check completed"

# BDD tests specifically
test-bdd:
	@echo "🥒 Running BDD tests..."
	@pytest tests/bdd/ -v --tb=short
	@echo "✅ BDD tests completed"

# Performance and benchmark tests
test-performance:
	@echo "⚡ Running performance tests..."
	@pytest tests/performance/ -v --tb=short
	@echo "✅ Performance tests completed"

# Security analysis with detailed report
security-full:
	@echo "🔒 Running comprehensive security analysis..."
	@mkdir -p data/output/security
	@bandit -r src/ -f json -o data/output/security/bandit_report.json
	@safety check --json --output data/output/security/safety_report.json
	@echo "🔒 Security reports saved to data/output/security/"

# Clean quality artifacts
clean-quality:
	@echo "🧹 Cleaning quality artifacts..."
	@rm -rf data/output/reports/
	@rm -rf data/output/metrics/
	@rm -rf data/output/security/
	@rm -rf data/output/coverage/
	@echo "✅ Quality artifacts cleaned"

# SOLID compliance verification
solid-check:
	@echo "🏗️ Verificando conformidade SOLID..."
	@python scripts/solid_compliance_check.py --output data/output/reports/solid_compliance.txt --json data/output/reports/solid_compliance.json
	@echo "✅ Verificação SOLID concluída"

# Quality dashboard generation
quality-dashboard:
	@echo "📊 Gerando dashboard de qualidade..."
	@python scripts/quality_dashboard.py
	@echo "✅ Dashboard de qualidade gerado"

# Open quality dashboard in browser
quality-dashboard-open: quality-dashboard
	@echo "🌐 Abrindo dashboard no navegador..."
	@python -m http.server 8080 --directory data/output/dashboard &
	@echo "📊 Dashboard disponível em: http://localhost:8080/quality_dashboard.html"

# Enhanced clean with all caches
clean-all: clean clean-quality
	@echo "🧹 Deep cleaning..."
	@rm -rf .mypy_cache/
	@rm -rf .pytest_cache/
	@rm -rf __pycache__/
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name ".coverage" -delete
	@echo "✅ Deep clean completed"

# Pre-commit hooks for quality
pre-commit-quality:
	@echo "🔧 Running pre-commit quality checks..."
	@pre-commit run --all-files
	@echo "✅ Pre-commit checks completed"

# CI/CD quality pipeline
ci-quality: install-dev quality-check-parallel test-coverage
	@echo "🚀 CI/CD quality pipeline completed"
	@echo "📊 All quality gates passed"

# Quality dashboard (opens coverage and reports)
quality-dashboard:
	@echo "📊 Opening quality dashboard..."
	@python -m http.server 8080 --directory data/output/coverage &
	@echo "🌐 Coverage report available at: http://localhost:8080"
	@echo "📄 Quality reports available in: data/output/reports/"

# Continuous quality monitoring
quality-watch:
	@echo "👀 Starting continuous quality monitoring..."
	@while true; do \
		$(MAKE) --no-print-directory quality-check-parallel; \
		echo "⏰ Next check in 60 seconds..."; \
		sleep 60; \
	done

# Quality gate for CI/CD (strict mode)
quality-gate:
	@echo "🚪 Running quality gate (strict mode)..."
	@$(MAKE) --no-print-directory quality-check-parallel
	@$(MAKE) --no-print-directory test-coverage
	@$(MAKE) --no-print-directory security-full
	@echo "✅ Quality gate passed - ready for deployment"
