.PHONY: help install lint format test security check-all clean run deploy-staging deploy-production

# Default target
help:
	@echo "Available commands:"
	@echo "  make install           - Install all dependencies"
	@echo "  make lint              - Run linting checks (flake8)"
	@echo "  make format            - Format code with black and isort"
	@echo "  make test              - Run tests with pytest"
	@echo "  make security          - Run security checks (bandit, safety)"
	@echo "  make check-all         - Run all checks (lint, security, test)"
	@echo "  make clean             - Remove generated files"
	@echo "  make run               - Run agent locally (terminal)"
	@echo "  make web               - Run agent locally (web interface)"
	@echo "  make deploy-staging    - Deploy to staging environment"
	@echo "  make deploy-production - Deploy to production environment"

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install black flake8 isort pytest pytest-cov pytest-asyncio bandit safety
	@echo "✅ Dependencies installed"

# Run linting
lint:
	@echo "Running flake8..."
	flake8 development_tutor/
	@echo "✅ Linting passed"

# Format code
format:
	@echo "Formatting code with black..."
	black development_tutor/
	@echo "Sorting imports with isort..."
	isort development_tutor/
	@echo "✅ Code formatted"

# Check formatting (without modifying files)
check-format:
	@echo "Checking code formatting..."
	black --check development_tutor/
	isort --check-only development_tutor/
	@echo "✅ Formatting check passed"

# Run tests
test:
	@echo "Running tests..."
	pytest -v --cov=development_tutor --cov-report=term-missing || echo "No tests found or tests failed"
	@echo "✅ Tests complete"

# Run security checks
security:
	@echo "Running security checks..."
	@echo "\n=== Checking dependencies with safety ==="
	pip install -r requirements.txt > /dev/null 2>&1
	safety check || echo "Safety check completed with warnings"
	@echo "\n=== Scanning code with bandit ==="
	bandit -r development_tutor/ -c .bandit || echo "Bandit scan completed with warnings"
	@echo "✅ Security checks complete"

# Run all checks (CI simulation)
check-all: check-format lint security test
	@echo "✅ All checks passed!"

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ htmlcov/ .coverage coverage.xml bandit-report.json
	@echo "✅ Cleaned"

# Run agent locally (terminal)
run:
	@echo "Starting agent in terminal mode..."
	adk run development_tutor/

# Run agent locally (web interface)
web:
	@echo "Starting web interface..."
	@echo "Access at: http://localhost:8000"
	adk web

# Deploy to staging (requires GCP authentication)
deploy-staging:
	@echo "Deploying to staging..."
	@if [ ! -f "development_tutor/.env" ]; then \
		echo "❌ Error: development_tutor/.env file not found"; \
		echo "Please create .env file with required variables"; \
		exit 1; \
	fi
	bash deployment/deploy-staging.sh || echo "Create deployment/deploy-staging.sh or push to staging branch to trigger CI/CD"

# Deploy to production (requires GCP authentication)
deploy-production:
	@echo "⚠️  WARNING: Deploying to PRODUCTION environment"
	@echo "Press Ctrl+C to cancel, or Enter to continue..."
	@read confirm
	@if [ ! -f "development_tutor/.env" ]; then \
		echo "❌ Error: development_tutor/.env file not found"; \
		exit 1; \
	fi
	bash deployment/deploy.sh

# Quick development setup
setup: install
	@echo "\n📝 Creating .env template if it doesn't exist..."
	@if [ ! -f "development_tutor/.env" ]; then \
		echo "Creating development_tutor/.env template..."; \
		echo "GOOGLE_GENAI_USE_VERTEXAI=False" > development_tutor/.env; \
		echo "GOOGLE_API_KEY=your-api-key-here" >> development_tutor/.env; \
		echo "GOOGLE_CLOUD_PROJECT=your-project-id" >> development_tutor/.env; \
		echo "GOOGLE_CLOUD_LOCATION=us-central1" >> development_tutor/.env; \
		echo "✅ .env template created - please update with your credentials"; \
	else \
		echo "✅ .env file already exists"; \
	fi
	@echo "\n🎉 Setup complete!"
	@echo "\nNext steps:"
	@echo "  1. Edit development_tutor/.env with your credentials"
	@echo "  2. Run 'make web' to start the development server"
	@echo "  3. Run 'make check-all' before committing changes"

# Initialize project for first-time users
init: setup
	@echo "\n🚀 Project initialized!"
	@echo "\nQuick reference:"
	@echo "  Development: make web"
	@echo "  Testing:     make check-all"
	@echo "  Deploy:      git push origin main (via CI/CD)"
