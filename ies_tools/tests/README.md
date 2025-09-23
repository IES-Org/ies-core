# GitHub CLI Workflow Test Suite

This test suite provides comprehensive testing for the Click application that manages GitHub workflows and issues.

## Overview

The test suite includes:

1. **Unit Tests** - Tests for individual functions in the application
2. **Command Tests** - Tests for CLI commands
3. **GitHub API Mocking** - Specialized tests for GitHub API interactions

## Getting Started

### Installation

```bash
# Install the required dependencies
pip install pytest pytest-mock

# Clone the repository
git clone https://github.com/your-org/your-repo.git
cd your-repo

# Run the tests
pytest
```

### Directory Structure

```
tests/
├── conftest.py              # Common pytest fixtures
├── test_suite.py            # Main test suite
└── test_github_api.py       # GitHub API mocking tests
```

## Key Features

- **Mocked Subprocess Calls**: All subprocess calls are mocked to prevent actual GitHub API interactions.
- **Comprehensive Coverage**: Tests cover utility functions, commands, and error conditions.
- **Safety Checks**: The `conftest.py` file ensures no actual commands are run during tests.

## Running Specific Tests

```bash
# Run all tests
pytest

# Run with detailed output
pytest -v

# Run specific test file
pytest tests/test_suite.py

# Run specific test
pytest tests/test_suite.py::TestCreateIssue::test_create_issue_dev
```

## Mocking Strategy

The test suite uses several strategies to mock external interactions:

1. **Subprocess Mocking**: All `subprocess.run()`, `subprocess.check_output()`, etc. calls are mocked to return pre-defined outputs.
2. **GitHub CLI Mocking**: Specialized fixtures simulate GitHub CLI responses.
3. **Environment Mocking**: Prevents accidental use of real GitHub tokens or configs.

## Maintainer Guidelines

When adding new tests:

1. Use the existing fixtures to avoid duplicating mock setup code.
2. Test both success and failure paths for each function/command.
3. Use appropriate assertions to verify the expected behavior.
4. For GitHub API interactions, prefer using the `test_github_api.py` file.

## Test Isolation

These tests are designed to run in isolation without touching:

- Real GitHub repositories
- Actual git commands
- Local filesystem (beyond test artifacts)
- Network connections

Any test that attempts to use these resources will fail automatically.
