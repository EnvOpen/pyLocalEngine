#!/bin/bash
# Local CI/CD test script for pyLocalEngine (without PyPI push)
# This script emulates the GitHub Actions workflow locally

set -e  # Exit on any error

echo "🚀 Starting CI/CD Test for pyLocalEngine"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${YELLOW}📝 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in a virtual environment, if not create one
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_step "Setting up virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    print_success "Virtual environment activated"
else
    print_success "Already in virtual environment: $VIRTUAL_ENV"
fi

# Install dependencies
print_step "Installing dependencies..."
pip install -e ".[dev]"
print_success "Dependencies installed"

# Run linting checks
print_step "Running flake8 linting..."
flake8 localengine tests examples --max-line-length=100 --extend-ignore=E203,W503
print_success "Flake8 linting passed"

# Run code formatting check
print_step "Checking code formatting with black..."
black --check localengine tests examples
print_success "Black formatting check passed"

# Run import sorting check
print_step "Checking import sorting with isort..."
isort --check-only localengine tests examples
print_success "Import sorting check passed"

# Run type checking with mypy (only if Python >= 3.10)
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [[ $(echo "$PYTHON_VERSION >= 3.10" | bc -l) -eq 1 ]]; then
    print_step "Running type checking with mypy..."
    mypy localengine
    print_success "Type checking passed"
else
    print_step "Skipping mypy (Python $PYTHON_VERSION < 3.10)"
fi

# Run tests with coverage
print_step "Running tests with pytest..."
pytest tests/ -v --cov=localengine --cov-report=xml --cov-report=term
print_success "All tests passed"

# Test examples
print_step "Testing examples..."
PYTHONPATH=. python examples/basic_usage.py > /dev/null
PYTHONPATH=. python examples/advanced_usage.py > /dev/null
print_success "Examples executed successfully"

# Final summary
echo ""
echo "🎉 All CI/CD checks passed!"
echo "========================================"
echo "✅ Linting (flake8)"
echo "✅ Code formatting (black)"
echo "✅ Import sorting (isort)"
if [[ $(echo "$PYTHON_VERSION >= 3.10" | bc -l) -eq 1 ]]; then
    echo "✅ Type checking (mypy)"
else
    echo "⏭️  Type checking (skipped - Python $PYTHON_VERSION)"
fi
echo "✅ Unit tests"
echo "✅ Example scripts"
echo ""
echo "🚢 Ready for deployment!"
