# Python Project Standards

A comprehensive framework for Python project standards and automated compliance checking tools.

## Overview

This repository provides:
- **Python Project Standards Documentation** - Modern best practices for Python projects
- **Automated Compliance Checker** - Tool to validate repositories against these standards
- **CI/CD Integration** - Workflows and scripts for continuous compliance monitoring

## Quick Start

### Check a Repository

```bash
# Check local repository
python src/compliance_checker/check_python_project_standards.py /path/to/repo

# Check GitHub repository by name
python src/compliance_checker/check_python_project_standards.py owner/repo

# Check GitHub repository by url
python src/compliance_checker/check_python_project_standards.py <full-github-url>
```

### Install Dependencies

```bash
pip install toml  # Required for compliance checker
```

## Documentation

- [📋 Python Project Standards](docs/python-project-standards.md) - Complete standards documentation
- [🔍 Compliance Checker Guide](docs/compliance-checker/README.md) - How to use the compliance checker
- [🤖 Unattended Setup](docs/compliance-checker/UNATTENDED_SETUP.md) - Automated checking setup
- [📊 System Readiness Document](SRD.md) - Project readiness and deployment information

## Features

### Python Standards (v3.0.0)
- Python 3.13+ with Poetry 2.1+
- Ruff for linting and formatting
- Pyright for type checking
- pytest for testing with coverage requirements
- Comprehensive CI/CD workflows
- AI-assisted development support (optional)

### Compliance Checker
- ✅ Supports both local and GitHub repositories
- 🔐 Multiple authentication methods
- 📊 JSON, Markdown, and console output formats
- 🚀 CI/CD ready with exit codes
- 📈 Scoring system with detailed feedback

## Project Structure

```
python-project-standards/
├── src/
│   └── compliance_checker/
│       ├── check_python_project_standards.py  # Main compliance checker
│       └── batch_checker.sh                   # Batch checking script
├── docs/
│   ├── python-project-standards.md            # Standards documentation
│   ├── cloud-team-python-project-standards.md # Team-specific standards
│   └── compliance-checker/
│       ├── README.md                          # Checker documentation
│       └── UNATTENDED_SETUP.md               # Automation guide
├── .github/
│   └── workflows/                             # CI/CD workflows
├── pyproject.toml                             # Python project configuration
└── README.md                                  # This file
```

## Usage Examples

### Command Line

```bash
# Verbose output with all checks
python src/compliance_checker/check_python_project_standards.py . --verbose

# Generate JSON report
python src/compliance_checker/check_python_project_standards.py owner/repo --json

# Save markdown report
python src/compliance_checker/check_python_project_standards.py . --output report.md
```

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Check Python Standards Compliance
  run: |
    pip install toml
    python src/compliance_checker/check_python_project_standards.py .
```

### Batch Checking

```bash
# Check multiple repositories
./src/compliance_checker/batch_checker.sh
```

## Compliance Scoring

- 🏆 **EXCELLENT (90-100%)** - Fully compliant with modern standards
- ✅ **GOOD (75-89%)** - Mostly compliant, minor improvements needed
- ⚠️ **FAIR (60-74%)** - Several updates required
- ❌ **NEEDS WORK (<60%)** - Significant updates needed

## Requirements

- Python 3.11+ (3.13+ recommended)
- `toml` package for parsing configuration
- GitHub CLI (`gh`) for GitHub repository checking (optional)
- GitHub personal access token or `gh` authentication for private repos

## Development

This project follows its own Python Project Standards and uses AI-assisted development tracking.

### AI Development Tracking

This project uses AI-assisted development with comprehensive tracking. See `.ai/README.md` for details.

### Contributing

1. Follow the Python Project Standards documented in this repository
2. Ensure all changes pass the compliance checker
3. Update documentation as needed
4. Include task tracking for AI-assisted changes

## License

This project is part of the LiveData Inc. Python ecosystem.

## Support

For issues or questions about:
- **Standards**: Review the [Python Project Standards](docs/python-project-standards.md)
- **Compliance Checker**: See the [Compliance Checker Guide](docs/compliance-checker/README.md)
- **Automation**: Check the [Unattended Setup Guide](docs/compliance-checker/UNATTENDED_SETUP.md)