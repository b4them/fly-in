PYTHON	 = python3
VENV	 = venv
VENV_BIN = $(VENV)/bin
V_PYTHON = $(VENV_BIN)/python
V_PIP	 = $(VENV_BIN)/pip
MAIN	 = main.py

# Mandatory mypy flags
MYPY_FLAGS	 = --warn-return-any --warn-unused-ignores --ignore-missing-imports \
                --disallow-untyped-defs --check-untyped-defs

# Default map if none is specified
MAP			?= 01_linear_path.txt

all: install

$(VENV):
	@echo "Initializing virtual environment..."
	@$(PYTHON) -m venv $(VENV)
	@$(V_PIP) install -q --upgrade pip

install: $(VENV)
	@echo "Installing project dependencies..."
	@if [ -f requirements.txt ]; then \
		$(V_PIP) install -q -r requirements.txt; \
	else \
		$(V_PIP) install -q flake8 mypy; \
	fi

run: install
	@echo "Running simulation with: $(MAP)"
	@$(V_PYTHON) $(MAIN) $(MAP)

debug: install
	@echo "Starting pdb debugger..."
	@$(V_PYTHON) -m pdb $(MAIN) $(MAP)

clean:
	@echo "Cleaning up environment and caches..."
	@rm -rf $(VENV)
	@rm -rf .mypy_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +

# Mandatory lint flags
lint: install
	@echo "Executing flake8..."
	@$(VENV_BIN)/flake8 .
	@echo "Executing mypy with mandatory flags..."
	@$(VENV_BIN)/mypy $(MYPY_FLAGS) .

lint-strict: install
	@echo "Executing strict mypy check..."
	@$(VENV_BIN)/mypy --strict .

.PHONY: all install run debug clean lint lint-strict
