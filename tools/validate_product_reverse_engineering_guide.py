#!/usr/bin/env python3
import argparse
import importlib.util
import json
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
REPO_ROOT = Path(__file__).resolve().parents[1]
TEST_FILE = REPO_ROOT / "tests" / "test_product_reverse_engineering_guide.py"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.product_reverse_engineering_validation import (  # noqa: E402
    RECORD_SCHEMA_NAMES,
    infer_schema_name,
    validate_record,
)


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


def run_guide_tests():
    try:
        suite = load_test_suite()
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


def _display_path(error):
    if not error.absolute_path:
        return "$"
    return "$" + "".join(
        f"[{part}]" if isinstance(part, int) else f".{part}"
        for part in error.absolute_path
    )


def validate_record_file(record_path, schema_name=None):
    path = Path(record_path)
    if not path.is_file():
        print(f"ERROR: record file does not exist: {path}", file=sys.stderr)
        return 2
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        print(f"ERROR: cannot read JSON record {path}: {error}", file=sys.stderr)
        return 2

    try:
        selected_schema = schema_name or infer_schema_name(record)
        errors = validate_record(record, schema_name=selected_schema)
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    except Exception as error:
        print(
            f"ERROR: validation could not be completed: "
            f"{type(error).__name__}: {error}",
            file=sys.stderr,
        )
        return 2

    if errors:
        for error in errors:
            print(
                f"validation error [{selected_schema}] "
                f"{_display_path(error)}: {error.message}",
                file=sys.stderr,
            )
        return 1

    print(f"VALID [{selected_schema}] {path}")
    return 0


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description=(
            "Validate one reverse-engineering JSON record. With no arguments, "
            "run the complete guide test suite."
        )
    )
    parser.add_argument("record", help="path to one JSON record")
    parser.add_argument(
        "--schema",
        choices=RECORD_SCHEMA_NAMES,
        help="explicit schema name; otherwise infer from record_id/artifact shape",
    )
    return parser.parse_args(argv)


def main(argv=None):
    arguments = list(sys.argv[1:] if argv is None else argv)
    if not arguments:
        return run_guide_tests()
    args = parse_args(arguments)
    return validate_record_file(args.record, schema_name=args.schema)


if __name__ == "__main__":
    raise SystemExit(main())
