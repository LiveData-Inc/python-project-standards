#!/usr/bin/env python3
"""
Python Project Standards Compliance Checker (Unified Version)

A comprehensive script that checks Python repositories for compliance with modern Python standards.
Combines full functionality with testable architecture and single-file deployment capability.

Usage:
    # Local repository
    python check_python_standards.py /path/to/repo

    # GitHub repository
    python check_python_standards.py https://github.com/owner/repo
    python check_python_standards.py owner/repo

    # Run embedded tests
    python check_python_standards.py --test

    # With explicit authentication
    python check_python_standards.py owner/repo --auth=token
    python check_python_standards.py owner/repo --auth=gh

Authentication:
    1. Token: Set GITHUB_TOKEN or GH_TOKEN environment variable
    2. GitHub CLI: Run 'gh auth login' once
    3. Automatic: Checks for token first, then gh CLI

Requirements:
    - Python 3.9+
    - toml package (pip install toml)
    - For GitHub repos: gh CLI or GITHUB_TOKEN
"""

import argparse
import base64
import json
import os
import re
import subprocess
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Protocol
from urllib.parse import urlparse

try:
    import toml
except ImportError:
    print("Error: 'toml' package is required")
    print('Install with: pip install toml')
    sys.exit(1)


# ============================================================================
# CONSTANTS
# ============================================================================

CURRENT_PYTHON_VERSION = '3.13'
ACCEPTABLE_PYTHON_VERSION = '3.12'
MIN_PYTHON_VERSION = '3.9'

SCORE_EXCELLENT = 90.0
SCORE_GOOD = 75.0

# Repository type keywords
REQUIRED_KEYWORDS = ['python-lib', 'python-stack', 'python-app', 'python-shared', 'composite-app']

# Emojis with Windows fallback
EMOJI_SUCCESS = '✅'
EMOJI_ERROR = '❌'
EMOJI_WARNING = '⚠️'

if sys.platform == 'win32':
    try:
        '✅'.encode(sys.stdout.encoding if hasattr(sys.stdout, 'encoding') else 'utf-8')
    except (UnicodeEncodeError, AttributeError):
        EMOJI_SUCCESS = '[OK]'
        EMOJI_ERROR = '[X]'
        EMOJI_WARNING = '[!]'


# ============================================================================
# DATA CLASSES
# ============================================================================


@dataclass
class ComplianceCheck:
    """Represents a single compliance check."""

    name: str
    category: str
    passed: bool
    message: str
    severity: str = 'error'  # error, warning, info


@dataclass
class ComplianceReport:
    """Complete compliance report for a repository."""

    repo_identifier: str
    repo_name: str
    repo_type: str  # 'local' or 'github'
    checks: List[ComplianceCheck] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    @property
    def total_checks(self) -> int:
        return len(self.checks)

    @property
    def passed_checks(self) -> int:
        return sum(1 for check in self.checks if check.passed)

    @property
    def failed_checks(self) -> int:
        return sum(1 for check in self.checks if not check.passed)

    def calculate_score(self) -> float:
        """Calculate compliance score as a percentage."""
        if self.total_checks == 0:
            return 0.0
        return (self.passed_checks / self.total_checks) * 100

    def add_check(self, name: str, category: str, passed: bool, message: str, severity: str = 'error'):
        """Add a compliance check result."""
        self.checks.append(ComplianceCheck(name, category, passed, message, severity))

    def get_summary(self) -> str:
        """Get a summary of the compliance status."""
        score = self.metadata.get('score', self.calculate_score())

        if score >= SCORE_EXCELLENT:
            return f'{EMOJI_SUCCESS} EXCELLENT: Repository meets all standards.'
        elif score >= SCORE_GOOD:
            return f'{EMOJI_SUCCESS} GOOD: Repository follows most standards with minor improvements needed.'
        else:
            return f'{EMOJI_ERROR} NEEDS WORK: Repository requires significant updates to meet standards.'

    def print_report(self, verbose: bool = False):
        """Print formatted compliance report."""
        score = self.calculate_score()

        print('\n' + '=' * 80)
        print('MODERN PYTHON PROJECT STANDARDS COMPLIANCE REPORT')
        print('=' * 80)
        print(f'Repository: {self.repo_name}')
        print(f'Type: {self.repo_type.upper()}')
        if self.repo_type == 'github':
            print(f'Location: {self.repo_identifier}')
        print(f'Compliance Score: {score:.1f}%')
        print(f'Checks Passed: {self.passed_checks}/{self.total_checks}')
        print('-' * 80)

        # Group checks by category
        categories = {}
        for check in self.checks:
            if check.category not in categories:
                categories[check.category] = []
            categories[check.category].append(check)

        # Print by category
        for category in sorted(categories.keys()):
            print(f'\n{category}:')
            for check in categories[category]:
                # Always show all checks to match original behavior
                icon = (
                    EMOJI_SUCCESS
                    if check.passed
                    else (EMOJI_WARNING if check.severity == 'warning' else EMOJI_ERROR)
                )
                # Original behavior: show short messages for passed, detailed for failed
                if check.passed and not verbose:
                    print(f'  {icon} {check.name}: No problems noted')
                else:
                    print(f'  {icon} {check.name}: {check.message}')

        print('\n' + '=' * 80)
        print(self.get_summary())
        print('=' * 80 + '\n')

    def to_dict(self) -> dict:
        """Convert report to dictionary for JSON output."""
        return {
            'repository': self.repo_identifier,
            'repo_type': self.repo_type,
            'total_checks': self.total_checks,
            'passed_checks': self.passed_checks,
            'failed_checks': self.failed_checks,
            'score': self.calculate_score(),
            'summary': self.get_summary(),
            'checks': [
                {
                    'name': check.name,
                    'category': check.category,
                    'passed': check.passed,
                    'message': check.message,
                    'severity': check.severity,
                }
                for check in self.checks
            ],
        }


# ============================================================================
# CHECK FUNCTIONS - Pure functions for testing
# ============================================================================


def check_python_version(config: dict) -> ComplianceCheck:
    """Check Python version requirement."""
    if not config:
        return ComplianceCheck('Python Version', 'Configuration', False, 'pyproject.toml not found or invalid', 'error')

    # Check in [project] section first (PEP 621)
    if 'project' in config and 'requires-python' in config['project']:
        version = config['project']['requires-python']
    # Check in [tool.poetry.dependencies] for Poetry projects
    elif 'tool' in config and 'poetry' in config['tool'] and 'dependencies' in config['tool']['poetry']:
        deps = config['tool']['poetry']['dependencies']
        version = deps.get('python', '')
    else:
        return ComplianceCheck(
            'Python Version', 'Configuration', False, 'Python version not specified in pyproject.toml', 'error'
        )

    # Check version
    if CURRENT_PYTHON_VERSION in version:
        return ComplianceCheck(
            'Python Version', 'Configuration', True, f'Uses Python {version} (current standard)', 'info'
        )
    elif ACCEPTABLE_PYTHON_VERSION in version:
        return ComplianceCheck(
            'Python Version',
            'Configuration',
            False,
            f'Uses Python {version} (acceptable but should upgrade to >={CURRENT_PYTHON_VERSION})',
            'warning',
        )
    else:
        return ComplianceCheck(
            'Python Version',
            'Configuration',
            False,
            f'Uses Python {version} (should be >={CURRENT_PYTHON_VERSION})',
            'error',
        )


def check_poetry_configuration(config: dict) -> List[ComplianceCheck]:
    """Check Poetry configuration and version."""
    checks = []

    if not config:
        checks.append(ComplianceCheck('Poetry Version', 'Configuration', False, 'No pyproject.toml found', 'error'))
        return checks

    # Check if Poetry is used
    if 'tool' not in config or 'poetry' not in config['tool']:
        checks.append(ComplianceCheck('Poetry Version', 'Configuration', False, 'Not using Poetry', 'warning'))
        return checks

    # Check for Poetry plugins if using Poetry
    poetry_config = config['tool']['poetry']
    if 'requires-plugins' in poetry_config:
        plugins = poetry_config['requires-plugins']
        required_plugins = ['poetry-plugin-export', 'poetry-plugin-shell', 'ld-poetry-export-group-plugin']
        for plugin in required_plugins:
            if plugin in plugins:
                checks.append(ComplianceCheck(
                    f'Poetry Plugin: {plugin}', 'Configuration', True, 'Required plugin configured', 'info'
                ))
            else:
                checks.append(ComplianceCheck(
                    f'Poetry Plugin: {plugin}', 'Configuration', False, 'Missing required plugin', 'warning'
                ))

    # Check for Poetry version requirement
    poetry_found = False

    # Check in tool.poetry
    if 'requires-poetry' in poetry_config:
        version = poetry_config['requires-poetry']
        if '>=2.1' in version or '>=2.0' in version or '^2' in version:
            checks.append(ComplianceCheck('Poetry Version', 'Configuration', True, f'Poetry {version} specified', 'info'))
            poetry_found = True
        else:
            checks.append(ComplianceCheck(
                'Poetry Version', 'Configuration', False, 'Should specify Poetry >=2.1', 'warning'
            ))
            poetry_found = True

    # Check in build-system if not found
    if not poetry_found and 'build-system' in config:
        requires = config['build-system'].get('requires', [])
        for req in requires:
            if 'poetry' in req.lower():
                if '>=2.1' in req or '>=2.0' in req or '^2' in req:
                    checks.append(ComplianceCheck('Poetry Version', 'Configuration', True, 'Poetry >=2.1 specified', 'info'))
                    poetry_found = True
                else:
                    checks.append(ComplianceCheck(
                        'Poetry Version', 'Configuration', False, 'Should specify Poetry >=2.1', 'warning'
                    ))
                    poetry_found = True
                break

    if not poetry_found:
        checks.append(ComplianceCheck('Poetry Version', 'Configuration', False, 'Should specify Poetry >=2.1', 'warning'))

    return checks


def check_code_quality_tools(config: dict) -> List[ComplianceCheck]:
    """Check for code quality tools (linter/formatter and type checker)."""
    checks = []

    if not config:
        checks.append(ComplianceCheck('Linter/Formatter', 'Code Quality', False, 'No configuration found', 'error'))
        checks.append(ComplianceCheck('Type Checker', 'Code Quality', False, 'No configuration found', 'error'))
        return checks

    tool = config.get('tool', {})

    # Check linter/formatter
    if 'ruff' in tool:
        ruff_config = tool['ruff']
        target = ruff_config.get('target-version', '')
        if 'py313' in target or 'py312' in target:
            checks.append(ComplianceCheck(
                'Linter/Formatter', 'Code Quality', True, f'Ruff configured with target {target}', 'info'
            ))
        else:
            checks.append(ComplianceCheck(
                'Linter/Formatter', 'Code Quality', False, 'Ruff configured but with outdated target version', 'warning'
            ))

        # Check line length
        if 'line-length' in ruff_config and ruff_config['line-length'] == 120:
            checks.append(ComplianceCheck('Line Length', 'Code Quality', True, 'Line length set to 120', 'info'))

        # Check quote style
        if 'format' in ruff_config and 'quote-style' in ruff_config['format']:
            checks.append(ComplianceCheck('Quote Style', 'Code Quality', True, 'Quote style configured', 'info'))
    elif 'black' in tool:
        checks.append(ComplianceCheck(
            'Linter/Formatter', 'Code Quality', False, 'Uses Black (should migrate to Ruff)', 'warning'
        ))
    else:
        checks.append(ComplianceCheck(
            'Linter/Formatter', 'Code Quality', False, 'No linter/formatter configured', 'error'
        ))

    # Check type checker
    if 'pyright' in tool or 'basedpyright' in tool:
        pyright_tool = tool.get('pyright', tool.get('basedpyright', {}))
        py_version = pyright_tool.get('pythonVersion', '')
        type_tool = 'basedpyright' if 'basedpyright' in tool else 'pyright'

        if CURRENT_PYTHON_VERSION in py_version:
            checks.append(ComplianceCheck(
                'Type Checker', 'Code Quality', True, f'Pyright configured for Python {py_version}', 'info'
            ))
        else:
            checks.append(ComplianceCheck(
                'Type Checker',
                'Code Quality',
                False,
                f'Pyright not configured for Python {CURRENT_PYTHON_VERSION}',
                'warning',
            ))
    elif 'mypy' in tool:
        checks.append(ComplianceCheck('Type Checker', 'Code Quality', False, 'Uses mypy (consider pyright)', 'warning'))
    else:
        checks.append(ComplianceCheck('Type Checker', 'Code Quality', False, 'Pyright not configured', 'warning'))

    return checks


def check_testing_configuration(config: dict) -> List[ComplianceCheck]:
    """Check testing configuration."""
    checks = []

    if not config:
        checks.append(ComplianceCheck('Test Framework', 'Testing', False, 'No configuration found', 'error'))
        return checks

    tool = config.get('tool', {})
    has_pytest = 'pytest' in tool

    if has_pytest:
        checks.append(ComplianceCheck('Test Framework', 'Testing', True, 'Pytest configured', 'info'))

        # Check for coverage separately
        pytest_config = tool.get('pytest', {})
        addopts = ''
        if 'ini_options' in pytest_config:
            addopts = str(pytest_config.get('ini_options', {}).get('addopts', ''))

        if 'coverage' in tool or '--cov' in addopts:
            checks.append(ComplianceCheck('Test Coverage', 'Testing', True, 'Coverage reporting configured', 'info'))
        else:
            checks.append(ComplianceCheck('Test Coverage', 'Testing', False, 'Coverage reporting not configured', 'warning'))
    else:
        checks.append(ComplianceCheck('Test Framework', 'Testing', False, 'Pytest not configured', 'error'))

    return checks


def check_repository_keywords(config: dict) -> ComplianceCheck:
    """Check repository keywords in pyproject.toml."""
    if not config:
        return ComplianceCheck('Repository Keywords', 'Configuration', False, 'No pyproject.toml found', 'error')

    keywords = []

    # Check in [project] section (PEP 621)
    if 'project' in config:
        keywords = config['project'].get('keywords', [])
    # Check in [tool.poetry] for Poetry projects
    elif 'tool' in config and 'poetry' in config['tool']:
        keywords = config['tool']['poetry'].get('keywords', [])

    # Check if any required keyword is present
    has_required = any(kw in REQUIRED_KEYWORDS for kw in keywords)

    if has_required:
        return ComplianceCheck('Repository Keywords', 'Configuration', True, f'Has required keyword(s)', 'info')
    else:
        return ComplianceCheck(
            'Repository Keywords',
            'Configuration',
            False,
            f'Missing required keyword. Should have one of: {", ".join(REQUIRED_KEYWORDS)}',
            'error',
        )


# ============================================================================
# BASE CHECKER CLASS
# ============================================================================


class BaseChecker(ABC):
    """Abstract base class for compliance checkers."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.report = None

    @abstractmethod
    def check_repository(self, identifier: str) -> ComplianceReport:
        """Check repository compliance."""
        pass

    def run_standard_checks(self, config: dict):
        """Run standard compliance checks."""
        # Python version
        check = check_python_version(config)
        self.report.add_check(check.name, check.category, check.passed, check.message, check.severity)

        # Poetry configuration
        for check in check_poetry_configuration(config):
            self.report.add_check(check.name, check.category, check.passed, check.message, check.severity)

        # Code quality tools
        for check in check_code_quality_tools(config):
            self.report.add_check(check.name, check.category, check.passed, check.message, check.severity)

        # Testing
        for check in check_testing_configuration(config):
            self.report.add_check(check.name, check.category, check.passed, check.message, check.severity)

        # Repository keywords
        check = check_repository_keywords(config)
        self.report.add_check(check.name, check.category, check.passed, check.message, check.severity)


# ============================================================================
# LOCAL CHECKER
# ============================================================================


class LocalChecker(BaseChecker):
    """Checker for local repositories."""

    def check_repository(self, path_str: str) -> ComplianceReport:
        """Check a local repository."""
        path = Path(path_str).resolve()
        repo_name = path.name

        # Create report
        self.report = ComplianceReport(repo_identifier=str(path), repo_name=repo_name, repo_type='local')

        # Check if path exists and is a directory
        if not path.exists() or not path.is_dir():
            self.report.add_check(
                'Repository Access',
                'Infrastructure',
                False,
                f'Path does not exist or is not a directory: {path}',
                'error',
            )
            return self.report

        # Load pyproject.toml
        config = self.load_config(path)

        # Run standard checks
        self.run_standard_checks(config)

        # Check for additional files
        self.check_additional_files(path, config)

        return self.report

    def load_config(self, path: Path) -> dict:
        """Load pyproject.toml configuration."""
        pyproject_path = path / 'pyproject.toml'

        if not pyproject_path.exists():
            return {}

        try:
            return toml.loads(pyproject_path.read_text())
        except Exception as e:
            if self.verbose:
                print(f'Error reading pyproject.toml: {e}')
            return {}

    def check_additional_files(self, path: Path, config: dict):
        """Check for additional configuration files."""
        # Check for README.md
        if (path / 'README.md').exists():
            self.report.add_check('README.md', 'Documentation', True, 'README.md present', 'info')
        else:
            self.report.add_check('README.md', 'Documentation', False, 'README.md missing', 'error')

        # Check for SRD.md
        if (path / 'SRD.md').exists():
            self.report.add_check('SRD.md', 'Documentation', True, 'System Readiness Document present', 'info')
        else:
            self.report.add_check('SRD.md', 'Documentation', False, 'System Readiness Document missing', 'error')

        # Check for poetry.lock if using Poetry
        if config.get('tool', {}).get('poetry'):
            if (path / 'poetry.lock').exists():
                self.report.add_check('Poetry Lock File', 'Configuration', True, 'poetry.lock present', 'info')
            else:
                self.report.add_check('Poetry Lock File', 'Configuration', False, 'poetry.lock missing', 'error')

        # Check for GitHub workflows
        workflows_path = path / '.github' / 'workflows'
        if workflows_path.exists():
            workflow_files = list(workflows_path.glob('*.yml')) + list(workflows_path.glob('*.yaml'))

            # Check for PythonManager.yml
            if (workflows_path / 'PythonManager.yml').exists():
                self.report.add_check(
                    'Python Manager Workflow', 'CI/CD', True, 'PythonManager.yml workflow present', 'info'
                )
            else:
                self.report.add_check(
                    'Python Manager Workflow', 'CI/CD', False, 'Missing PythonManager.yml workflow', 'error'
                )

            # Check for Ruff formatting workflow
            has_ruff_workflow = any('ruff' in f.name.lower() or 'format' in f.name.lower() for f in workflow_files)
            if has_ruff_workflow:
                self.report.add_check(
                    'Ruff Formatting Workflow', 'CI/CD', True, 'Ruff auto-formatting workflow present', 'info'
                )
            else:
                self.report.add_check(
                    'Ruff Formatting Workflow', 'CI/CD', False, 'Missing Ruff auto-formatting workflow', 'warning'
                )
        else:
            self.report.add_check('Python Manager Workflow', 'CI/CD', False, 'No .github/workflows directory', 'error')
            self.report.add_check(
                'Ruff Formatting Workflow', 'CI/CD', False, 'No .github/workflows directory', 'warning'
            )

        # Check for CLAUDE.md (optional)
        if (path / 'CLAUDE.md').exists():
            self.report.add_check(
                'CLAUDE.md', 'Documentation', True, 'AI assistant instructions present (optional)', 'info'
            )

        # Check for AI tracking (optional)
        if (path / '.ai' / 'README.md').exists():
            self.report.add_check(
                'AI Tracking', 'Documentation', True, 'AI development tracking configured (optional)', 'info'
            )

        # Check for SonarCloud configuration
        sonar_files = [path / 'sonar-project.properties', path / '.sonarcloud.properties']

        has_sonar = any(f.exists() for f in sonar_files)

        # Also check in GitHub workflows
        if workflows_path.exists():
            workflow_files = list(workflows_path.glob('*.yml')) + list(workflows_path.glob('*.yaml'))
            for wf in workflow_files:
                content = wf.read_text().lower()
                if 'sonarcloud' in content or 'sonar' in content:
                    has_sonar = True
                    break

        if has_sonar:
            # Check if configured for current Python version
            if config:
                py_version = None
                if 'project' in config and 'requires-python' in config['project']:
                    py_version = config['project']['requires-python']
                elif 'tool' in config and 'poetry' in config['tool']:
                    deps = config['tool']['poetry'].get('dependencies', {})
                    py_version = deps.get('python', '')

                if py_version and CURRENT_PYTHON_VERSION in py_version:
                    self.report.add_check(
                        'SonarCloud',
                        'Code Quality',
                        True,
                        f'SonarCloud configured for Python {CURRENT_PYTHON_VERSION}',
                        'info',
                    )
                else:
                    self.report.add_check(
                        'SonarCloud',
                        'Code Quality',
                        False,
                        f'SonarCloud configured but not for Python {CURRENT_PYTHON_VERSION}',
                        'warning',
                    )
            else:
                self.report.add_check('SonarCloud', 'Code Quality', True, 'SonarCloud configuration found', 'info')
        else:
            self.report.add_check('SonarCloud', 'Code Quality', False, 'SonarCloud not configured', 'warning')


# ============================================================================
# GITHUB CHECKER
# ============================================================================


class GitHubChecker(BaseChecker):
    """Checker for GitHub repositories."""

    def __init__(self, verbose: bool = False, auth_method: str = 'auto'):
        super().__init__(verbose)
        self.auth_method = auth_method
        self.token = None
        self.use_token = False
        self._setup_authentication()

    def _setup_authentication(self):
        """Set up authentication method."""
        if self.auth_method == 'token':
            self.use_token = True
            self.token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
            if not self.token:
                raise ValueError('Token authentication requested but GITHUB_TOKEN/GH_TOKEN not found')
        elif self.auth_method == 'gh':
            self.use_token = False
            self.token = None
            if not self._command_exists('gh'):
                raise ValueError('gh CLI authentication requested but gh command not found')
        else:  # auto
            self.token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
            self.use_token = bool(self.token)

            if not self.use_token and not self._command_exists('gh'):
                raise ValueError('No authentication available. Set GITHUB_TOKEN or install gh CLI')

    def _command_exists(self, command: str) -> bool:
        """Check if a command exists."""
        try:
            subprocess.run(['which', command], capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def _run_gh_command(self, args: List[str]) -> Optional[str]:
        """Run a gh CLI command."""
        env = os.environ.copy()
        if self.use_token and self.token:
            env['GH_TOKEN'] = self.token

        try:
            result = subprocess.run(['gh'] + args, capture_output=True, text=True, check=True, env=env, timeout=10)
            return result.stdout
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return None

    def _get_file_content(self, repo: str, path: str) -> Optional[str]:
        """Fetch file content from GitHub."""
        # Try using gh api with raw content
        content = self._run_gh_command(
            [
                'api',
                f'/repos/{repo}/contents/{path}',
                '-q',
                '.content',
                '--header',
                'Accept: application/vnd.github.raw',
            ]
        )

        if content and content.strip() and content.strip() != 'null':
            # If we got base64 content, decode it
            if not content.startswith('{'):  # Not JSON, likely base64
                try:
                    # Remove any whitespace/newlines
                    content = content.strip().replace('\n', '').replace(' ', '')
                    return base64.b64decode(content).decode('utf-8')
                except Exception:
                    pass
            return content

        # Alternative: try direct raw content
        content = self._run_gh_command(
            ['api', f'/repos/{repo}/contents/{path}', '--header', 'Accept: application/vnd.github.raw']
        )

        if content and content.strip():
            return content

        return None

    def _file_exists(self, repo: str, path: str) -> bool:
        """Check if a file exists in the repository."""
        result = self._run_gh_command(['api', f'/repos/{repo}/contents/{path}', '--jq', '.name'])
        return result is not None and result.strip() not in ['null', '']

    def _get_repo_info(self, repo: str) -> Optional[dict]:
        """Get repository information from GitHub API."""
        result = self._run_gh_command(['api', f'/repos/{repo}', '--jq', '.'])

        if result:
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                pass
        return None

    def check_repository(self, repo_spec: str) -> ComplianceReport:
        """Check a GitHub repository."""
        # Parse repository specification
        repo = self._parse_repo_spec(repo_spec)
        repo_url = f'https://github.com/{repo}'
        repo_name = repo.split('/')[-1]

        # Create report
        self.report = ComplianceReport(repo_identifier=repo_url, repo_name=repo, repo_type='github')

        # Get pyproject.toml
        config = self.load_config(repo)

        # Run standard checks
        self.run_standard_checks(config)

        # Check for additional files
        self.check_additional_files(repo, config)

        # Check GitHub-specific items
        self.check_repository_topics(repo)

        return self.report

    def _parse_repo_spec(self, repo_spec: str) -> str:
        """Parse repository specification to owner/repo format."""
        # Remove common prefixes
        repo_spec = repo_spec.replace('https://', '').replace('http://', '')
        repo_spec = repo_spec.replace('github.com/', '')
        repo_spec = repo_spec.replace('git@github.com:', '')
        repo_spec = repo_spec.replace('.git', '')

        # Clean up
        repo_spec = repo_spec.strip('/')

        # Validate format
        if '/' not in repo_spec or len(repo_spec.split('/')) < 2:
            raise ValueError(f'Invalid repository format: {repo_spec}')

        parts = repo_spec.split('/')
        return f'{parts[0]}/{parts[1]}'

    def load_config(self, repo: str) -> dict:
        """Load pyproject.toml from GitHub."""
        content = self._get_file_content(repo, 'pyproject.toml')

        if content:
            try:
                return toml.loads(content)
            except Exception as e:
                if self.verbose:
                    print(f'Error parsing pyproject.toml: {e}')

        return {}

    def check_additional_files(self, repo: str, config: dict):
        """Check for additional files in GitHub repository."""
        # Check for README.md
        if self._file_exists(repo, 'README.md'):
            self.report.add_check('README.md', 'Documentation', True, 'README.md present', 'info')
        else:
            self.report.add_check('README.md', 'Documentation', False, 'README.md missing', 'error')

        # Check for SRD.md
        if self._file_exists(repo, 'SRD.md'):
            self.report.add_check('SRD.md', 'Documentation', True, 'System Readiness Document present', 'info')
        else:
            self.report.add_check('SRD.md', 'Documentation', False, 'System Readiness Document missing', 'error')

        # Check for poetry.lock if using Poetry
        if config.get('tool', {}).get('poetry'):
            if self._file_exists(repo, 'poetry.lock'):
                self.report.add_check('Poetry Lock File', 'Configuration', True, 'poetry.lock present', 'info')
            else:
                self.report.add_check('Poetry Lock File', 'Configuration', False, 'poetry.lock missing', 'error')
        else:
            self.report.add_check('Poetry Lock File', 'Configuration', True, 'No problems noted', 'info')

        # Check for GitHub workflows
        if self._file_exists(repo, '.github/workflows/PythonManager.yml'):
            self.report.add_check(
                'Python Manager Workflow', 'CI/CD', True, 'PythonManager.yml workflow present', 'info'
            )
        else:
            self.report.add_check(
                'Python Manager Workflow', 'CI/CD', False, 'Missing PythonManager.yml workflow', 'error'
            )

        # Check for Ruff formatting workflow
        workflows = self._run_gh_command(['api', f'/repos/{repo}/contents/.github/workflows', '--jq', '.[].name'])

        has_ruff_workflow = False
        if workflows:
            for workflow in workflows.strip().split('\n'):
                if 'ruff' in workflow.lower() or 'format' in workflow.lower():
                    has_ruff_workflow = True
                    break

        if has_ruff_workflow:
            self.report.add_check(
                'Ruff Formatting Workflow', 'CI/CD', True, 'Ruff auto-formatting workflow present', 'info'
            )
        else:
            self.report.add_check(
                'Ruff Formatting Workflow', 'CI/CD', False, 'Missing Ruff auto-formatting workflow', 'warning'
            )

        # Check for SonarCloud
        has_sonar = False

        # Check for sonar config files
        if self._file_exists(repo, 'sonar-project.properties') or self._file_exists(repo, '.sonarcloud.properties'):
            has_sonar = True

        # Check workflows for SonarCloud
        if workflows:
            for workflow_name in workflows.strip().split('\n'):
                if workflow_name and workflow_name != 'null':
                    workflow_content = self._get_file_content(repo, f'.github/workflows/{workflow_name}')
                    if workflow_content and (
                        'sonarcloud' in workflow_content.lower() or 'sonar' in workflow_content.lower()
                    ):
                        has_sonar = True
                        break

        if has_sonar:
            # Check if configured for current Python version
            if config:
                py_version = None
                if 'project' in config and 'requires-python' in config['project']:
                    py_version = config['project']['requires-python']
                elif 'tool' in config and 'poetry' in config['tool']:
                    deps = config['tool']['poetry'].get('dependencies', {})
                    py_version = deps.get('python', '')

                if py_version and CURRENT_PYTHON_VERSION in py_version:
                    self.report.add_check(
                        'SonarCloud',
                        'Code Quality',
                        True,
                        f'SonarCloud configured for Python {CURRENT_PYTHON_VERSION}',
                        'info',
                    )
                else:
                    self.report.add_check(
                        'SonarCloud',
                        'Code Quality',
                        False,
                        f'SonarCloud configured but not for Python {CURRENT_PYTHON_VERSION}',
                        'warning',
                    )
            else:
                self.report.add_check('SonarCloud', 'Code Quality', True, 'SonarCloud configuration found', 'info')
        else:
            self.report.add_check('SonarCloud', 'Code Quality', False, 'SonarCloud not configured', 'warning')

    def check_repository_topics(self, repo: str):
        """Check GitHub repository topics."""
        repo_info = self._get_repo_info(repo)

        if not repo_info:
            self.report.add_check(
                'Repository Topics', 'Configuration', False, 'Could not fetch repository information', 'error'
            )
            return

        topics = repo_info.get('topics', [])

        # Check if any required topic is present
        has_required = any(topic in REQUIRED_KEYWORDS for topic in topics)

        if has_required:
            self.report.add_check('Repository Topics', 'Configuration', True, f'Has required GitHub topic(s)', 'info')
        else:
            self.report.add_check(
                'Repository Topics',
                'Configuration',
                False,
                f'Missing required GitHub topic. Should have one of: {", ".join(REQUIRED_KEYWORDS)}',
                'error',
            )


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def determine_repository_type(path_or_url: str) -> str:
    """Determine if input is a local path or GitHub repository."""
    # Check for GitHub patterns
    github_patterns = [
        r'^https?://github\.com/[\w-]+/[\w-]+',
        r'^git@github\.com:[\w-]+/[\w-]+',
        r'^github\.com/[\w-]+/[\w-]+',
        r'^[\w-]+/[\w-]+$',  # Simple owner/repo format
    ]

    for pattern in github_patterns:
        if re.match(pattern, path_or_url):
            return 'github'

    return 'local'


# ============================================================================
# EMBEDDED TESTS
# ============================================================================


def run_embedded_tests():
    """Run embedded unit tests."""
    print('Running embedded tests...')
    print('-' * 60)

    # Test ComplianceCheck
    check = ComplianceCheck('Test', 'Category', True, 'Message')
    assert check.name == 'Test'
    assert check.passed == True
    print(f'{EMOJI_SUCCESS} ComplianceCheck creation')

    # Test ComplianceReport
    report = ComplianceReport('test-repo', 'test', 'local')
    report.add_check('Test1', 'Cat', True, 'Pass')
    report.add_check('Test2', 'Cat', False, 'Fail')
    assert report.total_checks == 2
    assert report.passed_checks == 1
    assert report.calculate_score() == 50.0
    print(f'{EMOJI_SUCCESS} ComplianceReport score calculation')

    # Test check functions
    config_good = {'project': {'requires-python': '>=3.13'}}
    check = check_python_version(config_good)
    assert check.passed == True
    print(f'{EMOJI_SUCCESS} check_python_version (good)')

    # Test repository type detection
    assert determine_repository_type('https://github.com/owner/repo') == 'github'
    assert determine_repository_type('/local/path') == 'local'
    print(f'{EMOJI_SUCCESS} determine_repository_type')

    print('-' * 60)
    print(f'{EMOJI_SUCCESS} All embedded tests passed!')
    return True


# ============================================================================
# MAIN EXECUTION
# ============================================================================


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Check Python repository compliance with modern standards',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument('--test', action='store_true', help='Run embedded unit tests')

    parser.add_argument('repository', nargs='?', help='Local path or GitHub repository')

    parser.add_argument(
        '--auth',
        choices=['auto', 'token', 'gh'],
        default='auto',
        help='Authentication method for GitHub repos (default: auto)',
    )

    parser.add_argument('--verbose', action='store_true', help='Show all checks (not just failures)')

    parser.add_argument('--json', action='store_true', help='Output in JSON format')

    parser.add_argument('--output', help='Save report to file')

    args = parser.parse_args()

    # Handle test mode
    if args.test:
        success = run_embedded_tests()
        sys.exit(0 if success else 1)

    # Require repository
    if not args.repository:
        parser.error('repository argument is required (unless using --test)')

    # Determine repository type
    repo_type = determine_repository_type(args.repository)

    # Create appropriate checker
    if repo_type == 'local':
        checker = LocalChecker(verbose=args.verbose)
        identifier = args.repository
    else:
        checker = GitHubChecker(verbose=args.verbose, auth_method=args.auth)
        identifier = args.repository

    # Run compliance check
    try:
        report = checker.check_repository(identifier)

        # Calculate score
        score = report.calculate_score()
        report.metadata['score'] = score

        # Output results
        if args.json:
            output = json.dumps(report.to_dict(), indent=2)
            print(output)
            if args.output:
                Path(args.output).write_text(output)
        else:
            report.print_report(verbose=args.verbose)

            if args.output:
                # Save text report
                with open(args.output, 'w') as f:
                    f.write(f'Compliance Report for {report.repo_identifier}\n')
                    f.write(f'Score: {score:.1f}%\n')
                    f.write(f'Status: {report.get_summary()}\n\n')
                    for check in report.checks:
                        status = 'PASS' if check.passed else 'FAIL'
                        f.write(f'[{status}] {check.name}: {check.message}\n')

        # Exit with appropriate code
        sys.exit(0 if score >= SCORE_GOOD else 1)

    except Exception as e:
        print(f'{EMOJI_ERROR} Error checking repository: {e}', file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(2)


if __name__ == '__main__':
    main()
