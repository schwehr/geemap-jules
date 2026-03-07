# geemap AGENTS.md

This file provides context, guidelines, and instructions for automated agents contributing to the `geemap` project.

## Overview
- The project is a Python package named `geemap` used for interactive mapping and Earth Engine integration.
- The supported Python versions for the project are 3.13 and 3.14, with 3.13 being the minimum required version.

## Setup and Environment
- The repository heavily utilizes `uv` for dependency management, virtual environment setup, and running commands, especially within GitHub Actions CI/CD workflows (e.g., `uv sync`, `uv run python -m unittest ...`, `uv pip install`).
- To install the project for development along with all test dependencies, prefer using `uv sync` to create the environment and resolve all dependencies, or `uv pip install -e '.[all,tests]'` if already inside an active virtual environment.
- System requirements include `libpq-dev`, which can be installed via `sudo apt-get install -y libpq-dev`.
- The project may require `numpy<2` to avoid build or testing compatibility issues with newer NumPy releases.
- The project requires `python-box` instead of `box`. If testing or importing fails with an `AttributeError` on `box.Box`, resolve the dependency conflict by running `pip uninstall -y box python-box && pip install python-box`. If uninstalling fails, `pip install --ignore-installed python-box==7.4.1` can resolve the issue.

## Coding Standards
- The project enforces that f-strings must contain interpolated variables. Do not use the `f` prefix on strings without variables (`f-string-without-interpolation` rule is enabled in pylint).

## Testing Guidelines
- Tests in the repository are written using the standard `unittest` framework.
- To run the test suite, use `uv run python -m unittest tests/test_*.py`. Individual test files can be run with `uv run python -m unittest tests/test_<name>.py`.
- When writing tests for modules that rely on optional dependencies (e.g., `scikit-learn` in `geemap.ml`), use a `try...except ImportError` block to check for the package's presence, and use `@unittest.skipIf(not HAS_PACKAGE, ...)` to gracefully skip the tests if the dependency is missing.
- When testing the `foliumap` module, ensure you set `os.environ["USE_FOLIUM"] = "1"` before importing `geemap` or `geemap.foliumap` to enforce loading the folium backend instead of the default `ipyleaflet` backend.
- When writing tests that generate plots or figures, ensure you mock `matplotlib.pyplot.show` to prevent UI windows from popping up and blocking the automated test suite.

## Mocking Guidelines
- External API calls and dependencies (like `osmnx` or Earth Engine) should be mocked using `unittest.mock` to keep tests fast and avoid network requests.
- When writing unit tests involving Earth Engine (`ee`) operations, use the `tests.fake_ee` module to mock objects like `FeatureCollection`, `Geometry`, `Image`, and `ImageCollection` to avoid requiring an active, authenticated Earth Engine session.
- To test `geemap.Map` initialization without triggering actual Earth Engine network requests, pass `ee_initialize=False` during initialization or use `@patch('geemap.coreutils.ee_initialize')`.
- When mocking dependencies, always prefer `@mock.patch.object` over `@mock.patch`. For optional dependencies imported within a `try...except ImportError` block (e.g., `osmnx` as `ox` in `geemap.osm`), use `create=True` with `mock.patch.object` (e.g., `@mock.patch.object(osm, 'ox', create=True)`) to prevent `AttributeError`s in environments where the dependency is missing (such as CI).
- When writing tests, ensure you do not use `@patch` to mock the specific method you are trying to test (e.g., mocking `Map.add` while testing `Map.add`), as it creates tautological tests and provides no real test coverage of the actual logic.
