# Modern Python Project Standards

## Purpose

This document outlines the principles and standards for modern Python projects targeting AWS and cloud-native environments. These guidelines ensure consistency, maintainability, and efficiency across repositories using current Python tooling and practices.

By adhering to these standards, we ensure that our development efforts are efficient, secure, and maintainable. Teams working on modern cloud-native applications are expected to follow these principles, with periodic reviews conducted to keep the guidelines current.

## Table of Contents

1. [Repository Setup](#1-repository-setup)
2. [Python Version Management](#2-python-version-management)
3. [Dependency Management](#3-dependency-management)
4. [Code Quality Standards](#4-code-quality-standards)
5. [AWS Lambda Best Practices](#5-aws-lambda-best-practices)
6. [Repository Documentation](#6-repository-documentation)
7. [Project Configuration](#7-project-configuration-pyprojecttoml)
8. [Repository Structure & Organization](#8-repository-structure--organization)
9. [Testing & Continuous Integration](#9-testing--continuous-integration)
10. [Git Workflow Standards](#10-git-workflow-standards)
11. [Logging & Error Handling](#11-logging--error-handling)
12. [Environment Variables](#12-environment-variables)

## 1. Repository Setup

### 1.1 Repository Topics

Assign appropriate GitHub topics to categorize repositories:
- `python-lib` - Python libraries/packages for distribution (requires 100% test coverage)
- `python-stack` - Python repositories with CDK stacks (not libraries)
- `python-app` - Python CDK applications
- `python-shared` - Python CDK apps shared across multiple customer deployments
- `composite-app` - CDK apps that deploy multiple stacks

### 1.2 README Badges

Include status badges from the workflow library:
```markdown
![badge](https://github.com/LiveData-Inc/livedata-badges/blob/main/{repo-name}/Repo-Integrity.svg)
![badge](https://github.com/LiveData-Inc/livedata-badges/blob/main/{repo-name}/Pip-Audit.svg)
![badge](https://github.com/LiveData-Inc/livedata-badges/blob/main/{repo-name}/Poetry-Export.svg)
![badge](https://github.com/LiveData-Inc/livedata-badges/blob/main/{repo-name}/Pytest.svg)
![badge](https://github.com/LiveData-Inc/livedata-badges/blob/main/{repo-name}/Ruff-Format.svg)
```

### 1.3 Permissions & Collaborators

- Add team `cloud-developers` with Write access
- Add team `devops` with Admin access for CI/CD configuration
- Individual collaborators as needed with appropriate permissions

### 1.4 Branch Protection Rules

Main branch protection must include:
- Require pull request reviews (minimum 1)
- Dismiss stale PR approvals when new commits are pushed
- Require status checks to pass before merging
- Require branches to be up to date before merging
- Include administrators in restrictions
- Restrict who can push to matching branches

### 1.5 GitHub Actions

Use the centralized workflow library:
```yaml
# .github/workflows/PythonManager.yml
name: Python-Manager

on: [push]

jobs:
  Precheck:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    outputs:
      pytestcov: "${{ steps.set_pytestcov.outputs.pytestcov }}"
    steps:
    - name: set pytestcov
      id: set_pytestcov
      run: |
        topicname=$(gh api repos/${{ github.repository }}/topics --jq '.names | join(",")')
        echo "topics: $topicname"
        if [[ "$topicname" == *python-lib* ]]; then
          pytestcov="100"
        else
          pytestcov="80"
        fi
        echo "pytestcov: $pytestcov"
        echo "pytestcov=$pytestcov" >> "$GITHUB_OUTPUT"
      env:
        GH_TOKEN: "${{ secrets.DEVOPS_LIVEDATA_PAT }}"
      shell: bash

  Python-Manager:
    needs: Precheck
    uses: LiveData-Inc/workflow-library/.github/workflows/PythonManager.yaml@main
    with:
      readmeexists: "true"
      srdexists: "true"
      descriptionexists: "true"
      branchprotection: "false"
      pyprojecttomlexists: "true"
      poetrylockexists: "true"
      pipaudit: "true"
      ruffcheck: "true"
      pytest: "true"
      pytestcov: "${{ needs.Precheck.outputs.pytestcov }}"
      poetryexport: "true"
    secrets:
      devops_PAT_token: "${{ secrets.DEVOPS_LIVEDATA_PAT }}"
      codeArtifact_ARN: "${{ secrets.CODEARTIFACT_ARN }}"
```

### 1.6 Ruff Auto-Formatting Workflow

```yaml
# .github/workflows/ApplyPythonRuffFormatting.yml
name: Apply-Python-Ruff-Formatting

on:
  workflow_dispatch:

jobs:
  ApplyPythonRuffFormatting:
    uses: LiveData-Inc/workflow-library/.github/workflows/ApplyPythonRuffFormatting.yaml@main
    secrets:
      devops_PAT_token: "${{ secrets.DEVOPS_LIVEDATA_PAT }}"
```

## 2. Python Version Management

### 2.1 Current Standard Version

- **Python 3.13** is the current standard (as of 2025)
- Specify in `pyproject.toml`:

```toml
requires-python = ">=3.13,<4.0.0"
```

### 2.2 Version Upgrade Process

1. Team lead announces version upgrade with 2-week notice
2. Create upgrade branch in all repositories
3. Update `pyproject.toml` and test thoroughly
4. Update `.sonarcloud.properties` to match
5. Coordinate merged across all repositories within 1 week window

### 2.3 Version Compatibility

- Use `>=3.13,<4.0.0` syntax for Python version requirements
- This allows minor version updates while preventing breaking changes

## 3. Dependency Management

### 3.1 Poetry Configuration

- **Current Version**: Poetry 2.1+
- Install via: `curl -sSL https://install.python-poetry.org | python3 -`
- Configure local virtual environments:

```bash
poetry config virtualenvs.in-project true
```

### 3.2 Poetry Plugins

Required plugins in `pyproject.toml`:
```toml
[tool.poetry.requires-plugins]
poetry-plugin-export = ">=1.8"
poetry-plugin-shell = "*"
ld-poetry-export-group-plugin = "*"
```

### 3.3 Dependency Organization

Use Poetry dependency groups for better organization:
```toml
[tool.poetry.dependencies]
python = ">=3.13,<4.0.0"
# Core runtime dependencies only

[tool.poetry.group.dev.dependencies]
pytest = "*"
pytest-asyncio = "*"
pytest-cov = "*"
moto = { version = "*", extras = ["all"] }
respx = "*"
uvicorn = "*"
```

### 3.4 Private Package Repository

Configure AWS CodeArtifact for internal packages:
```toml
[[tool.poetry.source]]
name = "ld"
url = "https://livedata-601616385421.d.codeartifact.us-east-1.amazonaws.com/pypi/ld/simple/"
priority = "primary"
```

### 3.5 Version Pinning Strategy

- Use wildcard (`*`) for development dependencies to get latest versions
- Use caret requirements for production dependencies when specific versions needed
- Document any pinned versions in comments

## 4. Code Quality Standards

### 4.1 Ruff - The Modern Python Linter

**Ruff replaces Flake8, isort, and Black** - providing faster, more consistent formatting and linting.

Configure in `pyproject.toml`:
```toml
[tool.ruff]
line-length = 120

[tool.ruff.format]
quote-style = "single"

[tool.ruff.lint]
extend-select = ["I"]  # Enable import sorting
```

Run Ruff:
```bash
# Format code
ruff format src tests

# Check linting
ruff check src tests

# Fix auto-fixable issues
ruff check --fix src tests
```

### 4.2 Type Checking with Pyright

Configure in `pyproject.toml`:
```toml
[tool.pyright]
extraPaths = ["src"]
include = ["src/**"]
exclude = ["**/__pycache__"]
# typeCheckingMode = "basic"  # Uncomment to enable
```

### 4.3 SonarCloud Configuration

Create `.sonarcloud.properties`:
```properties
sonar.python.version=3.13
sonar.cpd.exclusions=tests/unit,src/{package}/authorizers/authorizers.py
```

Configure additional settings in `pyproject.toml`:
```toml
[tool.sonar]
sonar.cpd.exclusions = "tests/unit,src/{package}/authorizers/authorizers.py"
```

## 5. AWS Lambda Best Practices

### 5.1 Lambda Project Structure

```text
lambda-function/
├── src/
│   ├── {package_name}/
│   │   ├── __init__.py
│   │   ├── authorizers/      # FastAPI dependencies
│   │   ├── config/           # Settings and configuration
│   │   ├── core/             # Core business logic
│   │   ├── endpoints/        # API endpoints
│   │   ├── mangum_handlers/  # Lambda handlers
│   │   ├── middleware/       # Request/response middleware
│   │   ├── protocols/        # Type protocols/interfaces
│   │   ├── schemas/          # Pydantic models
│   │   └── utils/            # Utilities
├── tests/
│   ├── unit/
│   └── integration/
├── docs/
├── pyproject.toml
├── poetry.lock
├── README.md
└── SRD.md
```

### 5.2 Mangum Handler Pattern

For FastAPI Lambda applications:
```python
from mangum import Mangum
from fastapi import FastAPI

app = FastAPI()

# Lambda handler
handler = Mangum(app)
```

### 5.3 Lambda Deployment Patterns

- Use Mangum for FastAPI/Starlette applications
- Implement proper cold start optimization
- Use Lambda Layers for shared dependencies
- Configure appropriate memory and timeout settings

## 6. Repository Documentation

### 6.1 Required Documentation Files

Every repository must include:
- `README.md` - Project overview, setup, and usage
- `SRD.md` - System Readiness Document

### 6.2 README.md Structure

```markdown
# Project Name

![status badges]

## Overview
Brief description formatted with `ruff`

```cmd
ruff format src tests
```

## Architecture
[Include architecture diagrams using PlantUML or Mermaid]

## Prerequisites
- Python 3.13+
- Poetry 2.1+
- AWS CLI configured

## Installation
```bash
poetry install
```

## Development
```bash
# Run tests
poetry run pytest

# Format code
poetry run ruff format src tests

# Lint code
poetry run ruff check src tests

# Type checking
poetry run pyright
```

## Deployment
[Deployment instructions]

## API Documentation
[Link to API docs or describe endpoints]
```

### 6.3 System Readiness Document (SRD.md)

Document system requirements, dependencies, environment variables, monitoring, and rollback procedures.


## 7. Project Configuration (pyproject.toml)

### 7.1 Modern Project Configuration

```toml
[project]
name = "project-name"
version = "0.1.0"
description = "Project description"
authors = [
    { name = "Author Name", email = "author@company.com" },
]
readme = "README.md"
keywords = ["python-lib"]  # or appropriate topic
requires-python = ">=3.13,<4.0.0"
dependencies = [
    # Core dependencies
]

[tool.poetry]
requires-poetry = ">=2.1"
packages = [{ include = "package_name", from = "src" }]

[tool.poetry.group.dev.dependencies]
pytest = "*"
pytest-asyncio = "*"
pytest-cov = "*"
moto = { version = "*", extras = ["all"] }
respx = "*"

[tool.poetry.requires-plugins]
poetry-plugin-export = ">=1.8"
poetry-plugin-shell = "*"
ld-poetry-export-group-plugin = "*"

[tool.pytest.ini_options]
addopts = [
    "--import-mode=importlib",
    "--cov-report=term-missing",
    "--cov=package_name",
]
pythonpath = ["tests/unit"]
testpaths = ["tests/unit"]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "module"
markers = [
    "current: mark a single test for debugging",
]
filterwarnings = [
    "error",
    "ignore::DeprecationWarning",
    "ignore::ResourceWarning",
]

[tool.coverage.report]
exclude_also = [
    "if TYPE_CHECKING:",
    "^\\s*\\.\\.\\.\\s*$",
    "^.*:\\s*\\.\\.\\.\\s*$",
]

[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.gha.pipaudit]
ignore-vulns = []

[tool.pyright]
extraPaths = ["src"]
include = ["src/**"]
exclude = ["**/__pycache__"]

[tool.ruff]
line-length = 120

[tool.ruff.format]
quote-style = "single"

[tool.ruff.lint]
extend-select = ["I"]

[[tool.poetry.source]]
name = "ld"
url = "https://livedata-601616385421.d.codeartifact.us-east-1.amazonaws.com/pypi/ld/simple/"
priority = "primary"

[tool.sonar]
sonar.cpd.exclusions = "tests/unit,src/package_name/authorizers/authorizers.py"
```

## 8. Repository Structure & Organization

### 8.1 Standard Project Layout

```text
project-root/
├── .github/
│   └── workflows/
│       ├── PythonManager.yml
│       ├── ApplyPythonRuffFormatting.yml
│       └── generate-plantuml.yml
├── docs/
│   ├── diagrams/          # PlantUML diagrams
│   ├── api/               # API documentation
│   └── architecture.md
├── src/
│   └── {package_name}/    # Main package
│       ├── __init__.py
│       ├── config/        # Configuration
│       ├── core/          # Core business logic
│       ├── endpoints/     # API endpoints
│       ├── middleware/    # Middleware
│       ├── protocols/     # Type protocols
│       ├── schemas/       # Pydantic models
│       └── utils/         # Utilities
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── examples/              # Usage examples
├── .gitignore
├── .sonarcloud.properties
├── poetry.lock
├── pyproject.toml
├── README.md
└── SRD.md
```

### 8.2 Naming Conventions

- **Files**: Use `snake_case.py` for Python files
- **Directories**: Use `snake_case` for package directories
- **Classes**: Use `PascalCase`
- **Functions/Variables**: Use `snake_case`
- **Constants**: Use `UPPER_SNAKE_CASE`
- **Test files**: Prefix with `test_` or suffix with `_test.py`

### 8.3 Import Organization

Ruff automatically handles import sorting with the `I` rule enabled.

## 9. Testing & Continuous Integration

### 9.1 Test Coverage Requirements

- **python-lib repositories**: 100% test coverage required
- **Other repositories**: Minimum 80% test coverage
- Coverage automatically determined by repository topic

### 9.2 Testing Configuration

Configure pytest in `pyproject.toml`:
```toml
[tool.pytest.ini_options]
addopts = [
    "--import-mode=importlib",
    "--cov-report=term-missing",
    "--cov=package_name",
]
pythonpath = ["tests/unit"]
testpaths = ["tests/unit"]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "module"
asyncio_default_test_loop_scope = "module"
markers = [
    "current: mark a single test for debugging",
]
```

### 9.3 Test Structure

```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def sample_fixture():
    """Provide sample data for tests."""
    return {"key": "value"}

def test_function_success(sample_fixture):
    """Test successful execution."""
    result = function_under_test(sample_fixture)
    assert result["status"] == "success"

@pytest.mark.current
def test_debugging_focus():
    """Test marked for solo debugging."""
    # Use pytest -m current to run only this test
    pass
```

### 9.4 Continuous Integration Pipeline

The centralized PythonManager workflow includes:
1. **Repository Integrity**: Check required files exist
2. **Pip Audit**: Security vulnerability scanning
3. **Ruff Check**: Linting and formatting validation
4. **Pytest**: Unit tests with coverage
5. **Poetry Export**: Dependency export validation
6. **SonarCloud**: Code quality analysis

## 10. Git Workflow Standards

### 10.1 Branch Naming Convention

- `feature/JIRA-123-description` - New features
- `bugfix/JIRA-456-description` - Bug fixes
- `hotfix/JIRA-789-description` - Production hotfixes
- `chore/description` - Maintenance tasks
- `docs/description` - Documentation updates

### 10.2 Commit Message Format

Follow Conventional Commits:

```text
<type>(<scope>): <subject>

<body>

<footer>
```

Types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Maintenance tasks

### 10.3 Pull Request Process

1. Create feature branch from `main`
2. Make changes following coding standards
3. Run `ruff format` and `ruff check`
4. Ensure tests pass with required coverage
5. Create pull request with descriptive title
6. Address review feedback
7. Merge after approval

## 11. Logging & Error Handling

### 11.1 Structured Logging

Use Python's logging module with structured output:
```python
import logging
import json

logger = logging.getLogger(__name__)

# Configure JSON logging
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
        }
        if hasattr(record, 'extra'):
            log_obj.update(record.extra)
        return json.dumps(log_obj)

# Use structured logging
logger.info("Processing request", extra={
    "request_id": "123",
    "user_id": "456",
    "action": "create_order"
})
```

### 11.2 Error Handling Patterns

```python
from typing import Optional
from pydantic import BaseModel

class Result(BaseModel):
    """Result wrapper for error handling."""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    error_code: Optional[str] = None

def process_data(input_data: dict) -> Result:
    """Process data with proper error handling."""
    try:
        # Process data
        result = perform_processing(input_data)
        return Result(success=True, data=result)

    except ValueError as e:
        logger.error("Value error during processing", exc_info=True)
        return Result(
            success=False,
            error=str(e),
            error_code="VALUE_ERROR"
        )
    except Exception as e:
        logger.exception("Unexpected error during processing")
        return Result(
            success=False,
            error="Internal processing error",
            error_code="INTERNAL_ERROR"
        )
```

## 12. Environment Variables

### 12.1 Configuration Management

Use pydantic-settings for environment variable validation:
```python
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Required settings
    environment: str = Field(..., alias="ENVIRONMENT")
    aws_region: str = Field("us-east-1", alias="AWS_REGION")

    # Optional settings with defaults
    log_level: str = Field("INFO", alias="LOG_LEVEL")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }

# Usage
settings = Settings()
```

### 12.2 Secret Management

- Never commit secrets to version control
- Use AWS Secrets Manager or Parameter Store
- Access secrets at runtime with proper caching


## Appendix A - AI-Assisted Development (Optional)

### A.1 Overview

AI-assisted development is optional and indicated by the presence of a `.ai/` folder and/or `CLAUDE.md` file in the repository.

### A.2 Installing AI Development Tracking

To enable AI development tracking in a project:

1. Download the template from https://github.com/LiveData-Inc/dot-ai-template
2. Extract the ZIP file contents to your project root
3. The `.ai/` folder structure will be created with all necessary files
4. Follow the instructions in `.ai/README.md` for initial setup

### A.3 AI Development Tracking Structure

Once installed, the AI tracking system provides:

```text
.ai/
├── README.md              # AI tracking instructions
├── AI_CHANGELOG.md        # High-level AI work summary
└── tasks/                 # Individual task logs
    └── YYYYMMDD-HHMM-description.md
```

### A.4 CLAUDE.md File

Include AI-specific instructions when using AI assistance:

```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## AI Task Tracking Protocol
[Reference to .ai/ folder if using AI tracking]

## Project Context
[Project-specific context and patterns]

## Key Commands
[Common development commands]

## Architecture Overview
[High-level architecture description]
```

### A.5 AI Interaction Standards

When using AI assistance:

- Use Critical Review Mode by default
- Create task files only when explicitly requested
- Document all changes in task files
- Include AI task references in commit messages

### A.6 Repository Structure with AI Support

When AI support is enabled, the repository structure includes:

```text
project-root/
├── .ai/                    # AI development tracking
│   ├── README.md
│   ├── AI_CHANGELOG.md
│   └── tasks/
├── CLAUDE.md              # AI assistant instructions
└── [standard project files]
```

## Appendix B - Quick Reference

### B.1 Essential Commands

```bash
# Development setup
poetry install
poetry shell

# Code quality
ruff format src tests
ruff check src tests
poetry run pyright

# Testing
poetry run pytest
poetry run pytest -m current  # Run marked test
poetry run pytest --cov=package_name

# Dependency management
poetry add package-name
poetry add --group dev package-name
poetry update
poetry export -f requirements.txt --output requirements.txt

# Build
poetry build
```

### B.2 VS Code Settings

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.testing.pytestEnabled": true,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    }
  },
  "ruff.enable": true,
  "ruff.format.args": ["--line-length=120"],
  "python.analysis.typeCheckingMode": "basic"
}
```

---

## Document Version

- **Version**: 3.0.0
- **Last Updated**: 2025-01-15
- **Next Review**: 2025-04-15

## Change Log

- v3.0.0 (2025-01-15): Major update based on bff-auth implementation
  - Migrated from Flake8/Black to Ruff
  - Updated to Python 3.13
  - Updated to Poetry 2.1+
  - Added AI-assisted development section
  - Simplified configuration with centralized workflows
  - Updated to use modern Python packaging standards
- v2.0.0 (2024-12-29): Complete rewrite with specific versions
- v1.0.0 (2024-08-25): Initial version from PDF conversion
