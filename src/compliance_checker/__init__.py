"""
Python Standards Compliance Checker

A comprehensive tool for checking Python repositories against Python Project Standards.
"""

__version__ = '1.0.0'
__all__ = ['check_python_project_standards']

from .check_python_project_standards import (
    ComplianceCheck,
    ComplianceReport,
    LocalChecker,
    GitHubChecker,
    determine_repository_type,
)
