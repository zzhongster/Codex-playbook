#!/usr/bin/env python3
import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
REPO_ROOT = Path(__file__).resolve().parents[1]
TEST_FILE = REPO_ROOT / "tests" / "test_product_reverse_engineering_guide.py"


def load_test_suite(test_file=TEST_FILE):
    test_file = Path(test_file).resolve()
    if not test_file.is_file():
        raise RuntimeError(f"test file does not exist: {test_file}")

    spec = importlib.util.spec_from_file_location(
        "_product_reverse_engineering_guide_tests", test_file
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load test file: {test_file}")

    test_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(test_module)
    suite = unittest.defaultTestLoader.loadTestsFromModule(test_module)
    if suite.countTestCases() == 0:
        raise RuntimeError(f"zero tests loaded from: {test_file}")
    return suite


def main():
    try:
        suite = load_test_suite()
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
