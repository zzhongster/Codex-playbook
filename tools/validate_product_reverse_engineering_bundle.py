#!/usr/bin/env python3
"""Compatibility entry point for local claim/evidence/trace bundle validation."""

import importlib.util
import sys
from pathlib import Path


sys.dont_write_bytecode = True
_MODULE_PATH = (
    Path(__file__).resolve().with_name("product_reverse_engineering_validation.py")
)
_SPEC = importlib.util.spec_from_file_location(
    "_product_reverse_engineering_validation", _MODULE_PATH
)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"cannot load sibling validator: {_MODULE_PATH}")
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
validate_claim_evidence_trace_bundle = _MODULE.validate_claim_evidence_trace_bundle


__all__ = ("validate_claim_evidence_trace_bundle",)
