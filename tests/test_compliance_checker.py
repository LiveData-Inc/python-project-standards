#!/usr/bin/env python3
"""
Simplified unit tests for the Python Project Standards Compliance Checker.

These tests focus on the pure functions that don't require mocking.
"""

import sys
from pathlib import Path

# Add the compliance checker directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'compliance_checker'))

# Import from the main compliance checker script
from check_python_project_standards import (
    ComplianceCheck,
    ComplianceReport,
    check_python_version,
    check_poetry_configuration,
    check_testing_configuration,
    check_code_quality_tools,
    check_repository_keywords,
    determine_repository_type,
    CURRENT_PYTHON_VERSION,
    ACCEPTABLE_PYTHON_VERSION,
    SCORE_EXCELLENT,
    SCORE_GOOD,
)


def test_compliance_check():
    """Test ComplianceCheck creation."""
    check = ComplianceCheck(
        name='Test Check',
        category='Test Category',
        passed=True,
        message='Test passed',
        severity='info'
    )
    assert check.name == 'Test Check'
    assert check.category == 'Test Category'
    assert check.passed is True
    assert check.message == 'Test passed'
    assert check.severity == 'info'
    print('✅ ComplianceCheck test passed')


def test_compliance_report():
    """Test ComplianceReport functionality."""
    report = ComplianceReport('test/repo', 'repo', 'github')

    # Test adding checks
    report.add_check('Check1', 'Cat1', True, 'Passed')
    report.add_check('Check2', 'Cat2', False, 'Failed', 'warning')

    assert report.total_checks == 2
    assert report.passed_checks == 1
    assert report.failed_checks == 1
    assert len(report.checks) == 2

    # Test score calculation
    score = report.calculate_score()
    assert 0 <= score <= 100
    print('✅ ComplianceReport test passed')


def test_check_python_version():
    """Test Python version checking."""
    # Current version
    config = {'project': {'requires-python': f'>={CURRENT_PYTHON_VERSION}'}}
    check = check_python_version(config)
    assert check.passed is True
    assert check.severity == 'info'

    # Acceptable version
    config = {'project': {'requires-python': f'>={ACCEPTABLE_PYTHON_VERSION}'}}
    check = check_python_version(config)
    assert check.passed is False
    assert check.severity == 'warning'

    # Old version
    config = {'project': {'requires-python': '>=3.9'}}
    check = check_python_version(config)
    assert check.passed is False
    assert check.severity == 'error'

    print('✅ Python version check tests passed')


def test_check_poetry_configuration():
    """Test Poetry configuration checking."""
    # With Poetry configured
    config = {'tool': {'poetry': {'requires-poetry': '>=2.1'}}}
    checks = check_poetry_configuration(config)
    assert len(checks) > 0
    assert any(c.passed and 'Poetry' in c.name for c in checks)

    # Without Poetry
    config = {'tool': {}}
    checks = check_poetry_configuration(config)
    assert len(checks) > 0
    assert any(not c.passed for c in checks)

    print('✅ Poetry configuration check tests passed')


def test_check_code_quality_tools():
    """Test code quality tools checking."""
    # With Ruff and Pyright
    config = {
        'tool': {
            'ruff': {'target-version': 'py313', 'line-length': 120},
            'pyright': {'pythonVersion': '3.13'}
        }
    }
    checks = check_code_quality_tools(config)

    # Should have at least linter and type checker
    assert len(checks) >= 2
    linter_check = next((c for c in checks if 'Linter' in c.name), None)
    type_check = next((c for c in checks if 'Type Checker' in c.name), None)

    assert linter_check is not None
    assert type_check is not None
    assert linter_check.passed is True
    assert type_check.passed is True

    print('✅ Code quality tools check tests passed')


def test_check_testing_configuration():
    """Test testing configuration checking."""
    # With pytest and coverage
    config = {
        'tool': {
            'pytest': {'ini_options': {'addopts': '--cov'}},
            'coverage': {}
        }
    }
    checks = check_testing_configuration(config)

    assert len(checks) == 2  # Test Framework and Test Coverage
    assert all(c.passed for c in checks)

    # With pytest only
    config = {'tool': {'pytest': {}}}
    checks = check_testing_configuration(config)
    assert len(checks) == 2
    pytest_check = next(c for c in checks if 'Test Framework' in c.name)
    coverage_check = next(c for c in checks if 'Coverage' in c.name)
    assert pytest_check.passed is True
    assert coverage_check.passed is False

    print('✅ Testing configuration check tests passed')


def test_determine_repository_type():
    """Test repository type determination."""
    assert determine_repository_type('https://github.com/owner/repo') == 'github'
    assert determine_repository_type('http://github.com/owner/repo') == 'github'
    assert determine_repository_type('git@github.com:owner/repo.git') == 'github'
    assert determine_repository_type('owner/repo') == 'github'
    assert determine_repository_type('/path/to/repo') == 'local'
    assert determine_repository_type('./relative/path') == 'local'
    assert determine_repository_type('C:\\Windows\\Path') == 'local'

    print('✅ Repository type determination tests passed')


def test_constants():
    """Test that constants are properly defined."""
    assert CURRENT_PYTHON_VERSION == '3.13'
    assert ACCEPTABLE_PYTHON_VERSION == '3.12'
    assert SCORE_EXCELLENT == 90.0
    assert SCORE_GOOD == 75.0

    print('✅ Constants tests passed')


def main():
    """Run all tests."""
    print('\n' + '=' * 60)
    print('Running Simplified Compliance Checker Tests')
    print('=' * 60 + '\n')

    try:
        test_compliance_check()
        test_compliance_report()
        test_check_python_version()
        test_check_poetry_configuration()
        test_check_code_quality_tools()
        test_check_testing_configuration()
        test_determine_repository_type()
        test_constants()

        print('\n' + '=' * 60)
        print('✅ ALL TESTS PASSED')
        print('=' * 60 + '\n')
        return 0
    except Exception as e:
        print(f'\n❌ TEST FAILED: {e}')
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())