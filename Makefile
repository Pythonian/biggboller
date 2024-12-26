.DEFAULT_GOAL=help

.PHONY: help venv install check clean

VENV_DIR = venv
PYTHON = python3
PIP = $(VENV_DIR)/bin/pip
PRE_COMMIT = $(VENV_DIR)/bin/pre-commit

# Check if virtual environment is activated
define check_venv
	@ if [ "$$($(PYTHON) -c 'import sys; print(sys.prefix)')" != "$(CURDIR)/$(VENV_DIR)" ]; then \
		echo "Error: Virtual environment not activated. Please activate or create one."; \
		exit 1; \
	fi
endef

help: ## Display this help message with available make commands.
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

venv: ## Create a virtual environment.
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Virtual environment created."
	@echo "Activate with the command 'source $(VENV_DIR)/bin/activate'"

install: ## Install project dependencies.
	$(call check_venv)
	$(PIP) install -U pre-commit
	$(PIP) install -r requirements.txt
	$(PRE_COMMIT) install
	@echo "Project dependencies installed."

check: ## Run code quality checks with Pre-commit
	$(call check_venv)
	$(PRE_COMMIT) run --all-files
	@echo "All checks passed"

clean: ## Clean up all generated files and directories.
	@echo "Cleaning up the project..."
	@rm -rf $(VENV_DIR)
	@rm -rf .cache
	@rm -rf htmlcov coverage.xml .coverage
	@rm -rf .tox
	@rm -rf .mypy_cache
	@rm -rf .ruff_cache
	@rm -rf *.egg-info
	@rm -rf dist
	@find . -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name "build" -exec rm -rf {} +
	@echo "Cleanup completed."
