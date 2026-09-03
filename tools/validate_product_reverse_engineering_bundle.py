#!/usr/bin/env python3
"""Compatibility entry point for local claim/evidence/trace bundle validation."""

try:
    from tools.product_reverse_engineering_validation import (
        validate_claim_evidence_trace_bundle,
    )
except ModuleNotFoundError:
    from product_reverse_engineering_validation import (
        validate_claim_evidence_trace_bundle,
    )


__all__ = ("validate_claim_evidence_trace_bundle",)
