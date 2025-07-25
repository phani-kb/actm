#!/bin/bash

# Script to run code checks and tests with coverage
# Usage: ./run_checks.sh

set -e  # Exit immediately if a command exits with a non-zero status

echo "Running Ruff checks..."
python -m ruff check .

echo ""
echo "Applying Ruff fixes where possible..."
python -m ruff check --fix .

# echo ""
# echo "Running tests with coverage..."
# COVERAGE_FILE="coverage.json"
# python -m pytest --cov-report=html --cov-report=term --cov-report=json:$COVERAGE_FILE --cov=src/actm tests/

echo ""
echo "All checks completed!"
# echo "Coverage report saved to htmlcov/index.html"
