"""Run tests via pytest, capturing all output for CI debugging."""
import sys
import pytest

if __name__ == "__main__":
    # pytest.main() raises SystemExit; we intercept to see the error
    try:
        rc = pytest.main(["tests/", "-v", "--tb=long", "--no-header"])
    except SystemExit as e:
        rc = e.code if e.code is not None else 1
    sys.exit(rc)
