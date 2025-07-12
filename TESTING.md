# Testing Guide

This project uses **pytest** for all automated testing and has GitHub Actions CI/CD setup.

## Continuous Integration

The project uses GitHub Actions for automated testing and linting:

- **CI Workflow** (`.github/workflows/ci.yml`): Runs tests on Python 3.8, 3.9, and 3.10
- **Lint Workflow** (`.github/workflows/lint.yml`): Runs code quality checks

These workflows run automatically on:
- Every push to `main` and `develop` branches
- Every pull request to `main` branch

## Running Tests

To run all tests:

```bash
make test
```

Or directly with pytest:

```bash
pytest
```

## Code Coverage

To check code coverage:

```bash
make coverage
```

Or directly:

```bash
pytest --cov=agents --cov=core
```

## Linting and Code Quality

To run all linting checks:

```bash
make lint
```

To format code:

```bash
make format
```

Individual linting commands:
- `black --check .` - Check code formatting
- `isort --check-only .` - Check import sorting
- `flake8 .` - Check code style
- `mypy agents/ core/` - Check type hints

## Adding New Tests
- Place new test files in the project root or relevant subdirectory.
- Name test files as `test_*.py`.
- Use standard `unittest` or `pytest` style.

## Test Structure
- `test_error_handling.py`: Tests error handling and logging.
- `test_type_hints.py`: Tests type hints and type safety.
- `test_config_management.py`: Tests configuration management system.

## Best Practices
- Write tests for new features and bug fixes.
- Use fixtures for setup/teardown if needed.
- Keep tests isolated and idempotent.

## Troubleshooting
- If tests fail, check for missing dependencies or configuration files.
- Use `pytest -v` for verbose output.

---

For more information, see the [pytest documentation](https://docs.pytest.org/en/stable/). 