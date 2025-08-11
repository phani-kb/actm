#!/bin/bash

set -e

echo "Running Ruff checks..."
python -m ruff check .

echo "Applying Ruff fixes where possible..."
python -m ruff check --fix .

# echo ""
# echo "Running tests with coverage..."
# COVERAGE_FILE="coverage.json"
# python -m pytest --cov-report=html --cov-report=term --cov-report=json:$COVERAGE_FILE --cov=src/actm tests/
# echo "Coverage report saved to htmlcov/index.html"
