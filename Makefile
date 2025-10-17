# Makefile for automated environment setup & configuration

PROJECT_NAME = gdpr-obfuscator
REGION = eu-north-1
PYTHON_INTERPRETER = python3.13
WD=$(shell pwd)
PYTHONPATH=${WD}
SHELL := /bin/bash 
ACTIVATE_ENV := source venv/bin/activate

# Utility to run a command inside the virtual environment
define execute_in_env
	$(ACTIVATE_ENV) && $1
endef

# Create a virtual environment
create-environment:
	@echo ">>> Creating local virtual environment"
	$(PYTHON_INTERPRETER) -m venv venv

requirements: create-environment
	venv/bin/pip install -r requirements.txt

dev-setup:
	venv/bin/pip install bandit black pytest-cov flake8 pip-audit

## Run security test
security-test:
	venv/bin/bandit -lll ./src/*.py ./tests/*.py

## Run the black code check
run-black:
	venv/bin/black ./src ./tests

## Run the unit tests
unit-test:
	venv/bin/pytest -vv tests/

## Run the coverage check
check-coverage:
	venv/bin/pytest --cov=src tests/

## Run lint
lint:
	venv/bin/flake8 . --max-line-length=150 --exclude=.git,__pycache__,./venv,./dependencies-layer --ignore=E203,W503,E402

## Run audit
audit:
	venv/bin/pip-audit -r requirements.txt

## Run all checks
run-checks: security-test run-black lint unit-test check-coverage audit

## Build the zip files necessary to use the module in AWS Lambda

run-build:
	@echo "Zipping dependencies from dependencies-layer"
	cd dependencies-layer && zip -r ../dependencies-layer.zip .
	@echo "Zip file dependencies-layer.zip created 🎉"

	@echo "Zipping deployment-package"
	rm -rf deployment-package
	mkdir deployment-package
	cp -r src/* deployment-package/
	cd deployment-package && zip -r ../deployment-package.zip .
	@echo "Zip file deployment-package.zip created 🎉"

	@echo "Build complete ✅"