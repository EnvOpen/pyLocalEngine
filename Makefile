# Makefile for pyLocalEngine development

.PHONY: help install install-dev test test-cov lint format clean build upload docs

# Default target
help:
	@echo "Available targets:"
	@echo "  install      - Install package in current environment"
	@echo "  install-dev  - Install package with development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage report"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code with black and isort"
	@echo "  type-check   - Run type checking with mypy"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build distribution packages"
	@echo "  docs         - Generate documentation"
	@echo "  example      - Run basic usage example"
	@echo "  example-adv  - Run advanced usage example"
	@echo "  example-remote - Run remote loading example"
	@echo "  benchmark    - Run performance benchmarks"
	@echo "  migrate      - Show migration tool usage"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=localengine --cov-report=html --cov-report=term

# Code quality
lint:
	black --check localengine/ tests/ examples/ tools/
	isort --check-only localengine/ tests/ examples/ tools/

format:
	black localengine/ tests/ examples/ tools/
	isort localengine/ tests/ examples/ tools/

type-check:
	mypy localengine/

# Development
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

# Examples
example:
	cd examples && python basic_usage.py

example-adv:
	cd examples && python advanced_usage.py

example-remote:
	cd examples && python remote_loading.py

benchmark:
	cd examples && python benchmark.py

migrate:
	@echo "Migration tool usage:"
	@echo "  python tools/migrate.py <source> <output> --source-format <format>"
	@echo ""
	@echo "Example:"
	@echo "  python tools/migrate.py ./i18next_files ./locales --source-format i18next"

# Documentation
docs:
	@echo "Documentation files:"
	@echo "  README.md     - Project overview and quick start"
	@echo "  USER.md       - Complete user guide"
	@echo "  DOCS.md       - Comprehensive documentation"
	@echo "  architecture.md - LocalEngine specification"
	@echo ""
	@echo "To view HTML coverage report: open htmlcov/index.html"

# Development workflow
dev-setup: install-dev
	@echo "Development environment ready!"
	@echo "Run 'make test' to verify installation"

# Full check (run before committing)
check: format lint type-check test
	@echo "All checks passed!"

# Pre-commit setup
pre-commit-setup:
	pip install pre-commit
	pre-commit install
	@echo "Pre-commit hooks installed!"
