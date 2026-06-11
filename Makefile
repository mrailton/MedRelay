.PHONY: help install dev clean test test-verbose test-file test-coverage test-k \
       lint lint-fix format format-check typecheck lint-imports \
       assets assets-watch

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Setup ────────────────────────────────────────────────────────────────────

install: ## Install all dependencies (Python + Node)
	uv sync
	npm ci

clean: ## Remove cache and temporary files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage import_linter_cache .mypy_cache .ruff_cache

# ── Testing ──────────────────────────────────────────────────────────────────

test: ## Run test suite (with coverage gate)
	uv run pytest

test-verbose: ## Run test suite with verbose output
	uv run pytest -v

test-file: ## Run a single test file (FILE=tests/path/to/test.py)
	uv run pytest $(FILE)

test-coverage: ## Run tests with coverage report
	uv run pytest --cov=app --cov-report=term-missing --cov-report=html --no-cov-on-fail
	@echo ""
	@echo "HTML coverage report generated in htmlcov/"

test-k: ## Run tests matching keyword (K="test_something")
	uv run pytest -k "$(K)"

# ── Linting ──────────────────────────────────────────────────────────────────

lint: ## Run all quality checks (ruff + format + import boundaries)
	uv run ruff check app/ tests/
	uv run ruff format --check app/ tests/
	uv run lint-imports

lint-fix: ## Auto-fix all lint and formatting issues
	uv run ruff check --fix app/ tests/
	uv run ruff format app/ tests/
	uv run lint-imports

format: ## Format code with ruff
	uv run ruff format app/ tests/

format-check: ## Check code formatting without modifying
	uv run ruff format --check app/ tests/

typecheck: ## Run mypy type checking
	uv run mypy app/

lint-imports: ## Check module boundary contracts
	uv run lint-imports

# ── Assets ───────────────────────────────────────────────────────────────────

assets: ## Build production assets with Vite
	npm run build

assets-watch: ## Watch and rebuild assets on change
	npm run dev

