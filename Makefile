# LunVex Code Makefile
.PHONY: help install dev test lint format clean build publish docker

# Default target
help:
	@echo "LunVex Code Development Commands:"
	@echo ""
	@echo "  make install     Install dependencies"
	@echo "  make dev         Install development dependencies"
	@echo "  make test        Run tests"
	@echo "  make test-cov    Run tests with coverage"
	@echo "  make lint        Run linting checks"
	@echo "  make format      Format code"
	@echo "  make type-check  Check type hints"
	@echo "  make security    Run security checks"
	@echo "  make clean       Clean build artifacts"
	@echo "  make build       Build package"
	@echo "  make publish     Publish to PyPI (dry-run)"
	@echo "  make docker      Build Docker image"
	@echo "  make docker-run  Run in Docker container"
	@echo ""

# Installation
install:
	pip install -e .

dev:
	pip install -e ".[dev]"
	./scripts/setup_pre_commit.sh

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=lunvex_code --cov-report=term-missing --cov-report=html

# Code quality
lint:
	ruff check lunvex_code/ tests/
	ruff format --check lunvex_code/ tests/

format:
	ruff format lunvex_code/ tests/
	ruff check --fix lunvex_code/ tests/

type-check:
	python scripts/check_typing.py

# Security
security:
	python scripts/check_security.py

# Build
clean:
	rm -rf build/ dist/ *.egg-info .coverage htmlcov/ .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

publish: build
	twine upload --repository testpypi dist/*

# Docker
docker:
	docker build -t lunvex-code:latest .

docker-run:
	docker run -it --rm \
		-e DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY} \
		-v $(PWD):/workspace \
		-v lunvex-code-data:/home/lunvex/.lunvex-code \
		lunvex-code:latest

# Development shortcuts
all: dev lint type-check test security
	@echo "✅ All checks passed!"

pre-commit: format lint type-check
	@echo "✅ Ready to commit!"

ci: lint type-check test security
	@echo "✅ CI checks passed!"
