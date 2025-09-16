# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a static code analysis wrapper project for the BFF-Auth library located at `repos/bff-auth/` (symlinked to `../../../LiveData-Inc/bff-auth`). The project was created on Mon Sep 15 09:08:42 EDT 2025 for analyzing and reviewing the BFF-Auth authentication library codebase.

## AI Task Tracking Protocol

This project uses AI-assisted development tracking. See `.ai/README.md` for the complete protocol.

**Important**: Only create task files when the user explicitly requests with "Task:" prefix. Task files are immutable historical records and should never be modified once created.

## Key Commands

Since this is primarily an analysis wrapper, most commands should be run within the `repos/bff-auth/` directory:

### Code Quality & Analysis
```bash
# Navigate to the actual project
cd repos/bff-auth/

# Format code with Ruff
poetry run ruff format src tests

# Run linting
poetry run ruff check src tests

# Type checking
poetry run pyright
```

### Testing
```bash
cd repos/bff-auth/

# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=bff_auth --cov-report=term-missing

# Run specific test
poetry run pytest tests/unit/test_specific.py

# Run marked test
poetry run pytest -m current
```

### Project Setup
```bash
cd repos/bff-auth/

# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Build distribution
poetry build
```

## Architecture Overview

The BFF-Auth library (`repos/bff-auth/`) is a Backend For Frontend Authentication library implementing:

- **OAuth 2.0/OIDC with PKCE**: Browser-based authentication flows
- **SRP (Secure Remote Password)**: Direct authentication protocol
- **Session Management**: DynamoDB-backed session storage
- **JWT Token Management**: Token validation, refresh, and claims processing

### Core Structure

```
repos/bff-auth/
├── src/bff_auth/
│   ├── authorizers/        # FastAPI authentication dependencies
│   ├── config/             # Settings and configuration
│   ├── core/               # Core services (Session, Token, OIDC, SRP)
│   ├── endpoints/          # API route handlers
│   ├── mangum_handlers/    # Lambda/SQS handlers
│   ├── middleware/         # Security and request processing
│   ├── protocols/          # Type interfaces
│   └── schemas/            # Pydantic models
├── tests/unit/             # Comprehensive test suite
└── docs/                   # Additional documentation
```

### Deployment Modes

The library operates in three modes:
1. **Full Mode**: Frontend + Backend with sessions
2. **Backend-Only Mode**: JWT validation only
3. **Microservice Mode**: No Cognito integration

## Code Analysis Guidelines

When analyzing this codebase:

1. **Security Focus**: Priority on authentication/authorization security patterns
2. **AWS Integration**: Review DynamoDB, Cognito, SNS, SQS, Lambda integrations
3. **FastAPI Patterns**: Middleware stack, dependency injection, routing
4. **Testing Coverage**: Ensure comprehensive test coverage with pytest
5. **Type Safety**: Validate Pydantic models and type hints

## Important Patterns

- **Service Provider Pattern**: Central dependency injection in `core/service_provider.py`
- **Lazy Loading**: Performance optimization in main `__init__.py`
- **Protocol Classes**: Type interfaces in `protocols/`
- **Middleware Composition**: Layered security architecture
- **NO RETRIES Philosophy**: Immediate error responses in SQS handlers

## Critical Rules

1. **Import Organization**: ALL imports must be at the top of files, not inside functions
2. **Test Verification**: ALWAYS run tests after changes and before claiming completion
3. **Documentation**: Follow the `.ai/` tracking protocol for all modifications
4. **Security**: Never expose secrets, keys, or sensitive configuration