################################################################################################################

# Makefile for automated environment setup & configuration

################################################################################################################

PROJECT_NAME = gdpr-obfuscator
REGION = eu-west-2
PYTHON_INTERPRETER = python3
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
	python3 -m venv venv

requirements: create-environment
	$(call execute_in_env, pip3 install -r requirements.txt)

dev-setup:
	$(call execute_in_env, pip3 install bandit black pytest-cov flake8 pip-audit)

## Run security test
security-test:
	$(call execute_in_env, bandit -lll ./src/*.py ./tests/*.py)

## Run the black code check
run-black:
	$(call execute_in_env, black ./src ./tests)

## Run the unit tests
unit-test:
	$(call execute_in_env, pytest -vv)

## Run the coverage check
check-coverage:
	$(call execute_in_env, pytest --cov=src tests/)

## Run lint
lint:
	$(call execute_in_env, flake8 . --max-line-length=150 --exclude=.git,__pycache__,./venv,./layer,./dependencies_db --ignore=E203,W503,E402)

## Run audit
audit:
	$(call execute_in_env, pip-audit)

## Run all checks
run-checks: security-test run-black lint unit-test check-coverage audit