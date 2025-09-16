# Python Standards Compliance Checker

A unified tool for checking Python repositories against Python Project Standards. Supports both local repositories and GitHub repositories with flexible authentication options.

## Features

- **Dual Mode Support**: Works with both local directories and GitHub repositories
- **Smart Detection**: Automatically determines if input is a local path or GitHub URL
- **Flexible Authentication**: Supports multiple auth methods for different use cases
- **Comprehensive Checks**: Validates all aspects of modern Python standards
- **Multiple Output Formats**: Console, JSON, and Markdown reports
- **CI/CD Ready**: Exit codes and formats suitable for automation

## Installation

```bash
# Install required dependency
pip install toml

# For GitHub repositories, also need gh CLI
brew install gh  # macOS
# or
sudo apt install gh  # Ubuntu/Debian
```

## Usage

### Local Repositories

```bash
# Check current directory
python src/compliance_checker/check_python_project_standards.py .

# Check specific directory
python src/compliance_checker/check_python_project_standards.py /path/to/repo
python src/compliance_checker/check_python_project_standards.py ../my-project
```

### GitHub Repositories

```bash
# Various input formats supported
python src/compliance_checker/check_python_project_standards.py owner/repo
python src/compliance_checker/check_python_project_standards.py https://github.com/owner/repo
python src/compliance_checker/check_python_project_standards.py github.com/owner/repo

# With explicit authentication
python src/compliance_checker/check_python_project_standards.py owner/repo --auth=token
python src/compliance_checker/check_python_project_standards.py owner/repo --auth=gh
```

### Command Line Options

```bash
# Verbose output (shows all checks, not just failures)
python src/compliance_checker/check_python_project_standards.py repo --verbose

# Save report to file
python src/compliance_checker/check_python_project_standards.py repo --output report.md

# JSON output for programmatic use
python src/compliance_checker/check_python_project_standards.py repo --json

# Combine options
python src/compliance_checker/check_python_project_standards.py repo --verbose --output report.md
```

## Authentication

### For Local Repositories
No authentication needed - the script reads files directly from disk.

### For GitHub Repositories

#### Option 1: Personal Access Token (Recommended for CI/CD)

1. Create a GitHub Personal Access Token:
   - Go to Settings → Developer settings → Personal access tokens
   - Generate token with `repo` scope

2. Set environment variable:
   ```bash
   export GITHUB_TOKEN=ghp_your_token_here
   # or
   export GH_TOKEN=ghp_your_token_here
   ```

3. Run the script:
   ```bash
   python src/compliance_checker/check_python_project_standards.py owner/repo
   # or force token auth
   python src/compliance_checker/check_python_project_standards.py owner/repo --auth=token
   ```

#### Option 2: GitHub CLI (Recommended for Local Development)

1. Install and authenticate gh CLI:
   ```bash
   gh auth login
   ```

2. Run the script:
   ```bash
   python src/compliance_checker/check_python_project_standards.py owner/repo
   # or force gh auth
   python src/compliance_checker/check_python_project_standards.py owner/repo --auth=gh
   ```

#### Option 3: Automatic (Default)

The script automatically tries:
1. GITHUB_TOKEN/GH_TOKEN environment variable
2. gh CLI authentication
3. Falls back to local mode if path exists

## What It Checks

### Configuration
- **Python Version**: Requires 3.13+
- **Poetry Setup**: Version 2.1+ with required plugins
- **Poetry Lock**: Presence of poetry.lock file
- **Repository Keywords**: Appropriate categorization

### Code Quality
- **Linter/Formatter**: Ruff (preferred) or Flake8
- **Type Checking**: Pyright configuration
- **Line Length**: Set to 120 characters
- **Quote Style**: Configured formatting
- **SonarCloud**: Code analysis configuration

### Testing
- **Test Framework**: pytest configuration
- **Coverage**: Coverage reporting setup
- **Coverage Requirements**: Based on repository type

### CI/CD
- **Python Manager Workflow**: Standard CI/CD pipeline
- **Ruff Formatting Workflow**: Auto-formatting setup

### Documentation
- **README.md**: Project documentation
- **SRD.md**: System Readiness Document
- **CLAUDE.md**: AI assistant instructions (optional)
- **AI Tracking**: Development tracking (optional)

### GitHub-Specific
- **Repository Topics**: GitHub categorization tags

## Output Formats

### Console Output (Default)

Shows a summary with categorized results:
- ✅ Passed checks
- ⚠️ Warnings (non-critical issues)
- ❌ Failed checks (must fix)

### JSON Output (--json)

Structured data for programmatic processing:
```json
{
  "repository": "owner/repo",
  "type": "github",
  "score": 95.5,
  "passed": 20,
  "total": 21,
  "checks": [...]
}
```

### Markdown Report (--output)

Formatted report suitable for documentation or issues.

## Exit Codes

- `0`: Success (compliance score ≥ 75%)
- `1`: Failure (score < 75% or error)

## CI/CD Integration

### GitHub Actions

```yaml
name: Compliance Check

on: [push, pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install toml

      - name: Check compliance
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python src/compliance_checker/check_python_project_standards.py ${{ github.repository }}
```

### Jenkins

```groovy
pipeline {
    agent any

    environment {
        GITHUB_TOKEN = credentials('github-token')
    }

    stages {
        stage('Compliance Check') {
            steps {
                sh 'pip install toml'
                sh 'python src/compliance_checker/check_python_project_standards.py .'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: '*.md', allowEmptyArchive: true
        }
    }
}
```

### Bash Script for Batch Checking

Use with `check_compliance_batch.sh` for checking multiple repositories:

```bash
#!/bin/bash
for repo in $(cat repos.txt); do
    echo "Checking $repo..."
    python src/compliance_checker/check_python_project_standards.py "$repo" --output "reports/${repo//\//_}.md"
done
```

## Compliance Levels

- **🏆 EXCELLENT (90-100%)**: Highly compliant with modern standards
- **✅ GOOD (75-89%)**: Follows most standards, minor improvements needed
- **⚠️ FAIR (60-74%)**: Needs several updates
- **❌ NEEDS WORK (<60%)**: Requires significant updates

## Troubleshooting

### "No authentication available"
- Set GITHUB_TOKEN environment variable, or
- Run `gh auth login` to authenticate GitHub CLI

### "Cannot access repository"
- Check repository name/URL is correct
- Verify you have access to private repositories
- Check your authentication is valid

### "toml package is required"
- Install with: `pip install toml`

### Rate Limiting
- Use authentication to increase limits (60/hour → 5000/hour)
- Consider caching results for repeated checks

## Examples

### Check Multiple Repositories

```python
#!/usr/bin/env python3
import subprocess
import json

repos = [
    "owner/repo1",
    "owner/repo2",
    "./local-repo"
]

results = []
for repo in repos:
    result = subprocess.run(
        ["python", "src/compliance_checker/check_python_project_standards.py", repo, "--json"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        data = json.loads(result.stdout)
        results.append({
            "repo": repo,
            "score": data["score"]
        })

# Print summary
for r in sorted(results, key=lambda x: x["score"], reverse=True):
    print(f"{r['repo']}: {r['score']:.1f}%")
```

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
python src/compliance_checker/check_python_project_standards.py . --verbose
if [ $? -ne 0 ]; then
    echo "Compliance check failed. Please fix issues before committing."
    exit 1
fi
```

## License

This tool is provided as part of the Modern Python Project Standards initiative.