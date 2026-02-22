VENV ?= .venv312
PYTHON ?= $(VENV)/bin/python
PIP ?= $(VENV)/bin/pip

.PHONY: help venv install lint typecheck test simulate schema e2e-all e2e-claude e2e-claude-verbose check build smoke-import package-check release-readiness release-check release-check-claude version bump-patch bump-minor bump-major clean

help:
	@echo "Targets:"
	@echo "  make venv         - Create Python 3.12 virtualenv ($(VENV))"
	@echo "  make install      - Install project + dev dependencies"
	@echo "  make lint         - Run ruff"
	@echo "  make typecheck    - Run mypy"
	@echo "  make test         - Run pytest"
	@echo "  make simulate     - Run hook simulation examples"
	@echo "  make schema       - Generate JSON schemas for models/tools"
	@echo "  make e2e-all      - Validate all 15 hook events with runner E2E payloads"
	@echo "  make e2e-claude   - Run real Claude CLI hook E2E (if claude is available)"
	@echo "  make e2e-claude-verbose - Run Claude CLI E2E with full payload logging"
	@echo "  make check        - Run lint + typecheck + test"
	@echo "  make build        - Build sdist/wheel"
	@echo "  make smoke-import - Install built wheel in temp venv and import cc_hooks"
	@echo "  make package-check- Build package, twine check, and smoke import"
	@echo "  make release-readiness - Verify version/changelog consistency"
	@echo "  make release-check - Run check + package-check + e2e-all + release-readiness"
	@echo "  make release-check-claude - Run release-check plus real Claude E2E"
	@echo "  make version      - Print current package version"
	@echo "  make bump-patch   - Bump patch version via hatch"
	@echo "  make bump-minor   - Bump minor version via hatch"
	@echo "  make bump-major   - Bump major version via hatch"
	@echo "  make clean        - Remove build artifacts"

venv:
	python3.12 -m venv $(VENV)

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e '.[dev]'

lint:
	$(PYTHON) -m ruff check .

typecheck:
	$(PYTHON) -m mypy src

test:
	$(PYTHON) -m pytest -q

simulate:
	$(PYTHON) examples/simulate_claude_hooks.py

schema:
	$(PYTHON) scripts/generate_schemas.py

e2e-all:
	$(PYTHON) scripts/e2e_all_hooks_payloads.py

e2e-claude:
	$(PYTHON) scripts/e2e_claude_hooks.py

e2e-claude-verbose:
	E2E_CLAUDE_VERBOSE=1 $(PYTHON) scripts/e2e_claude_hooks.py

check: lint typecheck test

build:
	$(PYTHON) -m build

smoke-import:
	$(PYTHON) scripts/smoke_import_wheel.py

package-check: clean build
	$(PYTHON) -m twine check dist/*
	$(MAKE) smoke-import

release-readiness:
	$(PYTHON) scripts/check_release_readiness.py

release-check: check package-check e2e-all release-readiness

release-check-claude: release-check e2e-claude

version:
	$(PYTHON) -m hatch version

bump-patch:
	$(PYTHON) -m hatch version patch

bump-minor:
	$(PYTHON) -m hatch version minor

bump-major:
	$(PYTHON) -m hatch version major

clean:
	rm -rf build dist *.egg-info
