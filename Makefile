.PHONY: help install dev lint format type-check check run clean

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make dev          - Install dev dependencies"
	@echo "  make lint         - Run ruff linter"
	@echo "  make format       - Format code with ruff"
	@echo "  make type-check   - Run ty type checker"
	@echo "  make check        - Run all checks (lint + type-check)"
	@echo "  make fix          - Auto-fix linting issues and format code"
	@echo "  make run          - Run the FastAPI server"
	@echo "  make clean        - Remove cache files"

install:
	uv sync

dev:
	uv sync --dev

lint:
	ruff check .

format:
	ruff format .

ty:
	ty check .

check: lint ty
	@echo "✓ All checks passed"

fix:
	ruff check --fix .
	ruff format .

run-fe:
	cd medical-ai-ui && npm run dev

run:
	uvicorn main:app --reload

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
