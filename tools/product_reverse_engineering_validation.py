#!/usr/bin/env python3
"""Offline JSON Schema and semantic validation for reverse-engineering records."""

import json
from datetime import datetime
from pathlib import Path

from jsonschema import (
    Draft202012Validator,
    FormatChecker,
    ValidationError,
    validators,
)
from referencing import Registry, Resource
from referencing.exceptions import NoSuchResource


SCHEMA_ROOT = (
    Path(__file__).resolve().parents[1]
    / "guides"
    / "product-reverse-engineering"
    / "toolkit"
    / "schemas"
)
SCHEMA_NAMES = (
    "definitions",
    "asset",
    "evidence",
    "claim",
    "trace-link",
    "experiment",
    "decision",
    "coverage-summary",
)
RECORD_SCHEMA_NAMES = tuple(name for name in SCHEMA_NAMES if name != "definitions")


def load_schemas(schema_root=SCHEMA_ROOT):
    """Load the complete local schema bundle without any network access."""

    root = Path(schema_root)
    return {
        name: json.loads((root / f"{name}.schema.json").read_text(encoding="utf-8"))
        for name in SCHEMA_NAMES
    }


def create_schema_registry(schemas):
    """Build a registry that resolves only the supplied local schema resources."""

    def reject_remote_retrieval(uri):
        raise NoSuchResource(ref=uri)

    resources = [
        (schema["$id"], Resource.from_contents(schema)) for schema in schemas.values()
    ]
    return Registry(retrieve=reject_remote_retrieval).with_resources(resources)


def coverage_buckets_fit_denominator(validator, enabled, instance, schema):
    bucket_names = (
        "numerator",
        "unknown_count",
        "conflicting_count",
        "excluded_count",
    )
    if not enabled or not isinstance(instance, dict):
        return
    denominator = instance.get("denominator")
    buckets = [instance.get(bucket) for bucket in bucket_names]
    if type(denominator) is not int or not all(
        type(bucket) is int for bucket in buckets
    ):
        return
    if sum(buckets) != denominator:
        yield ValidationError(
            "numerator + unknown_count + conflicting_count + "
            "excluded_count must equal denominator"
        )


def experiment_artifacts_are_bound(validator, enabled, instance, schema):
    if not enabled or not isinstance(instance, dict):
        return

    def parse_timestamp(value):
        if not isinstance(value, str):
            return None
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, OverflowError):
            return None
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            return None
        return parsed

    protocol = instance.get("protocol")
    if not isinstance(protocol, dict):
        return
    protocol_created_value = protocol.get("created_at")
    protocol_frozen_value = protocol.get("protocol_frozen_at")
    protocol_created_at = parse_timestamp(protocol_created_value)
    protocol_frozen_at = parse_timestamp(protocol_frozen_value)
    if isinstance(protocol_created_value, str) and protocol_created_at is None:
        yield ValidationError("protocol.created_at must be a timezone-aware timestamp")
    if isinstance(protocol_frozen_value, str) and protocol_frozen_at is None:
        yield ValidationError(
            "protocol.protocol_frozen_at must be a timezone-aware timestamp"
        )
    if (
        protocol_created_at is not None
        and protocol_frozen_at is not None
        and protocol_created_at > protocol_frozen_at
    ):
        yield ValidationError(
            "protocol.created_at must not follow protocol.protocol_frozen_at"
        )
    expected_reference = {
        "protocol_id": protocol.get("artifact_id"),
        "protocol_content_hash": protocol.get("content_hash"),
    }
    artifacts = [
        instance.get(artifact_name)
        for artifact_name in ("protocol", "result", "effects")
    ]
    complete_artifacts = [
        artifact for artifact in artifacts if isinstance(artifact, dict)
    ]
    artifact_ids = [
        artifact.get("artifact_id")
        for artifact in complete_artifacts
        if isinstance(artifact.get("artifact_id"), str)
    ]
    artifact_hashes = [
        artifact.get("content_hash")
        for artifact in complete_artifacts
        if isinstance(artifact.get("content_hash"), str)
    ]
    if len(artifact_ids) != len(set(artifact_ids)):
        yield ValidationError("experiment artifact IDs must be unique")
    if len(artifact_hashes) != len(set(artifact_hashes)):
        yield ValidationError("experiment artifact hashes must be unique")
    if protocol.get("record_id") != protocol.get("artifact_id"):
        yield ValidationError("protocol record_id must equal its artifact_id")
    claim_references = protocol.get("claim_references")
    target_claim_references = protocol.get("target_claim_references")
    if (
        isinstance(claim_references, list)
        and isinstance(target_claim_references, list)
        and all(
            isinstance(reference, str)
            for reference in (*claim_references, *target_claim_references)
        )
    ):
        if not set(target_claim_references).issubset(set(claim_references)):
            yield ValidationError("target claims must be declared by the protocol")
    for artifact_name in ("result", "effects"):
        artifact = instance.get(artifact_name)
        if not isinstance(artifact, dict):
            continue
        if artifact.get("protocol_reference") != expected_reference:
            yield ValidationError(
                f"{artifact_name} must reference the exact frozen protocol"
            )
        for context_key in ("product_version", "scope_or_module"):
            if artifact.get(context_key) != protocol.get(context_key):
                yield ValidationError(
                    f"{artifact_name}.{context_key} must equal protocol.{context_key}"
                )

    def inner_evidence_references(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in {
                    "evidence_references",
                    "disposition_proof_references",
                } and isinstance(child, list):
                    yield from child
                elif key == "evidence_id" and isinstance(child, str):
                    yield child
                else:
                    yield from inner_evidence_references(child)
        elif isinstance(value, list):
            for child in value:
                yield from inner_evidence_references(child)

    for artifact_name in ("protocol", "result", "effects"):
        artifact = instance.get(artifact_name)
        if not isinstance(artifact, dict):
            continue
        evidence_references = artifact.get("evidence_references")
        method_definitions = artifact.get("method_definitions")
        evidence_method_entries = artifact.get("evidence_method_entries")
        if (
            isinstance(evidence_references, list)
            and isinstance(method_definitions, list)
            and isinstance(evidence_method_entries, list)
        ):
            method_ids = [
                method.get("method_id")
                for method in method_definitions
                if isinstance(method, dict) and isinstance(method.get("method_id"), str)
            ]
            mapped_evidence_ids = [
                entry.get("evidence_id")
                for entry in evidence_method_entries
                if isinstance(entry, dict) and isinstance(entry.get("evidence_id"), str)
            ]
            mapped_method_ids = {
                entry.get("method_id")
                for entry in evidence_method_entries
                if isinstance(entry, dict) and isinstance(entry.get("method_id"), str)
            }
            if len(method_ids) != len(set(method_ids)):
                yield ValidationError(f"{artifact_name} method IDs must be unique")
            if all(
                isinstance(reference, str) for reference in evidence_references
            ) and (
                set(evidence_references) != set(mapped_evidence_ids)
                or len(mapped_evidence_ids) != len(set(mapped_evidence_ids))
            ):
                yield ValidationError(f"{artifact_name} evidence must map exactly once")
            if set(method_ids) != mapped_method_ids:
                yield ValidationError(
                    f"{artifact_name} mapped methods must equal declared methods"
                )
        declared = (
            set(evidence_references)
            if isinstance(evidence_references, list)
            and all(isinstance(reference, str) for reference in evidence_references)
            else None
        )
        nested_payload = {
            key: value
            for key, value in artifact.items()
            if key != "evidence_references"
        }
        nested_references = list(inner_evidence_references(nested_payload))
        undeclared = (
            set(nested_references) - declared
            if declared is not None
            and all(isinstance(reference, str) for reference in nested_references)
            else set()
        )
        if declared is not None and undeclared:
            yield ValidationError(
                f"{artifact_name} contains evidence references absent from its top-level index"
            )

    result = instance.get("result")
    if isinstance(result, dict):
        primary_runs = result.get("run_results")
        independent_runs = result.get("independent_reproduction_results")
        runs = []
        for list_name in (
            "run_results",
            "independent_reproduction_results",
        ):
            run_list = result.get(list_name)
            if isinstance(run_list, list):
                runs.extend(run for run in run_list if isinstance(run, dict))
        run_ids = [
            run.get("run_id") for run in runs if isinstance(run.get("run_id"), str)
        ]
        if len(run_ids) != len(set(run_ids)):
            yield ValidationError("experiment run IDs must be unique")
        if isinstance(primary_runs, list) and isinstance(independent_runs, list):
            primary_executors = {
                run.get("executor")
                for run in primary_runs
                if isinstance(run, dict) and isinstance(run.get("executor"), str)
            }
            independent_executors = {
                run.get("executor")
                for run in independent_runs
                if isinstance(run, dict) and isinstance(run.get("executor"), str)
            }
            if primary_executors & independent_executors:
                yield ValidationError(
                    "independent reproduction must use a different executor"
                )
        reproduction_criteria = protocol.get("reproduction_criteria")
        if isinstance(reproduction_criteria, dict):
            required_runs = reproduction_criteria.get("required_runs")
            if type(required_runs) is int and len(runs) < required_runs:
                yield ValidationError(
                    "declared runs must satisfy reproduction criteria"
                )
        failed_run_ids = []
        failed_run_count = 0
        parsed_failed_runs = []
        parsed_runs = []
        for sequence, run in enumerate(runs):
            started_at = run.get("started_at")
            ended_at = run.get("ended_at")
            start = parse_timestamp(started_at)
            end = parse_timestamp(ended_at)
            if isinstance(started_at, str) and start is None:
                yield ValidationError(
                    "run started_at must be a timezone-aware timestamp"
                )
            if isinstance(ended_at, str) and end is None:
                yield ValidationError("run ended_at must be a timezone-aware timestamp")
            if (
                protocol_frozen_at is not None
                and start is not None
                and start < protocol_frozen_at
            ):
                yield ValidationError(
                    "protocol.protocol_frozen_at must not follow any run.started_at"
                )
            if start is not None and end is not None:
                if end < start:
                    yield ValidationError("run ended_at must not precede started_at")
                run_id = run.get("run_id")
                if isinstance(run_id, str):
                    parsed_runs.append((sequence, run_id, start, end))
            run_result = run.get("result")
            if isinstance(run_result, str) and run_result in {
                "failed",
                "mixed",
            }:
                failed_run_count += 1
                run_id = run.get("run_id")
                if isinstance(run_id, str):
                    failed_run_ids.append(run_id)
                    if start is not None and end is not None:
                        parsed_failed_runs.append((sequence, run_id, start, end))
                observations = run.get("actual_observations")
                evidence = run.get("evidence_references")
                if not isinstance(observations, list) or not observations:
                    yield ValidationError(
                        "failed or mixed run requires actual observations"
                    )
                if not isinstance(evidence, list) or not evidence:
                    yield ValidationError(
                        "failed or mixed run requires evidence references"
                    )

        first_failure = result.get("first_failure")
        if isinstance(first_failure, dict):
            failure_run_id = first_failure.get("run_id")
            if first_failure.get("present") is True:
                if not isinstance(failure_run_id, str) or (
                    failure_run_id not in failed_run_ids
                ):
                    yield ValidationError(
                        "first_failure.run_id must resolve to a failed or mixed run"
                    )
                if first_failure.get("preserved_before_retry") is not True:
                    yield ValidationError(
                        "first failure must be preserved before retry"
                    )
                if failed_run_count > 0 and len(parsed_failed_runs) == failed_run_count:
                    earliest_failure = min(
                        parsed_failed_runs,
                        key=lambda item: (item[2], item[0]),
                    )
                    (
                        earliest_sequence,
                        earliest_run_id,
                        earliest_start,
                        earliest_end,
                    ) = earliest_failure
                    if failure_run_id != earliest_run_id:
                        yield ValidationError(
                            "first_failure.run_id must identify the earliest failed or mixed run"
                        )
                    captured_value = first_failure.get("captured_at")
                    captured_at = parse_timestamp(captured_value)
                    if isinstance(captured_value, str) and captured_at is None:
                        yield ValidationError(
                            "first_failure.captured_at must be a timezone-aware timestamp"
                        )
                    if captured_at is not None:
                        if not earliest_start <= captured_at <= earliest_end:
                            yield ValidationError(
                                "first_failure.captured_at must fall within the earliest failed run"
                            )
                        subsequent_starts = [
                            run_start
                            for (
                                sequence,
                                _run_id,
                                run_start,
                                _run_end,
                            ) in parsed_runs
                            if sequence > earliest_sequence
                            and run_start > earliest_start
                        ]
                        if any(
                            captured_at >= retry_start
                            for retry_start in subsequent_starts
                        ):
                            yield ValidationError(
                                "first failure must be captured before any subsequent retry starts"
                            )
            elif failed_run_ids:
                yield ValidationError(
                    "failed or mixed runs require first_failure.present true"
                )

    effects = instance.get("effects")
    if isinstance(effects, dict):
        effect_records = effects.get("side_effect_records")
        if isinstance(effect_records, list):
            for effect in effect_records:
                if not isinstance(effect, dict):
                    continue
                occurred = effect.get("occurred")
                disposition = effect.get("disposition")
                if (
                    occurred is True
                    and isinstance(disposition, str)
                    and (disposition == "not-created")
                ):
                    yield ValidationError(
                        "an occurred side effect cannot be not-created"
                    )
                if (
                    occurred is False
                    and isinstance(disposition, str)
                    and (disposition != "not-created")
                ):
                    yield ValidationError(
                        "a side effect that did not occur must be not-created"
                    )


def coverage_gates_are_consistent(validator, enabled, instance, schema):
    if not enabled or not isinstance(instance, dict):
        return
    gates = instance.get("gates")
    if not isinstance(gates, dict):
        return
    evidence_references = instance.get("evidence_references")
    method_definitions = instance.get("method_definitions")
    evidence_method_entries = instance.get("evidence_method_entries")
    if (
        isinstance(evidence_references, list)
        and all(isinstance(item, str) for item in evidence_references)
        and isinstance(method_definitions, list)
        and isinstance(evidence_method_entries, list)
    ):
        method_ids = [
            method.get("method_id")
            for method in method_definitions
            if isinstance(method, dict) and isinstance(method.get("method_id"), str)
        ]
        mapped_evidence_ids = [
            entry.get("evidence_id")
            for entry in evidence_method_entries
            if isinstance(entry, dict) and isinstance(entry.get("evidence_id"), str)
        ]
        mapped_method_ids = [
            entry.get("method_id")
            for entry in evidence_method_entries
            if isinstance(entry, dict) and isinstance(entry.get("method_id"), str)
        ]
        if len(method_ids) != len(set(method_ids)) or set(method_ids) != set(
            mapped_method_ids
        ):
            yield ValidationError("coverage methods must be unique and fully mapped")
        if len(mapped_evidence_ids) != len(set(mapped_evidence_ids)) or set(
            evidence_references
        ) != set(mapped_evidence_ids):
            yield ValidationError("coverage evidence must map exactly once")
    gate_record_ids = []
    for expected_gate_id, gate in gates.items():
        if not isinstance(gate, dict):
            continue
        if gate.get("gate_id") != expected_gate_id:
            yield ValidationError(
                f"{expected_gate_id}.gate_id must equal {expected_gate_id}"
            )
        reference = gate.get("gate_record_reference")
        if isinstance(reference, dict):
            record_id = reference.get("id")
            if isinstance(record_id, str):
                gate_record_ids.append(record_id)
        gate_evidence = gate.get("evidence_references")
        if (
            isinstance(evidence_references, list)
            and all(isinstance(item, str) for item in evidence_references)
            and isinstance(gate_evidence, list)
            and all(isinstance(item, str) for item in gate_evidence)
            and not set(gate_evidence).issubset(set(evidence_references))
        ):
            yield ValidationError(
                f"{expected_gate_id} evidence must resolve in the summary index"
            )
    if len(gate_record_ids) != len(set(gate_record_ids)):
        yield ValidationError("different gates must not reuse a gate record ID")
    dimensions = instance.get("dimensions")
    runtime = dimensions.get("runtime") if isinstance(dimensions, dict) else None
    g5 = gates.get("G5")
    if not isinstance(runtime, dict) or not isinstance(g5, dict):
        return
    unknown_count = runtime.get("unknown_count")
    conflicting_count = runtime.get("conflicting_count")
    static_coverage = g5.get("static_non_runtime_coverage")
    if (
        type(unknown_count) is not int
        or type(conflicting_count) is not int
        or not isinstance(static_coverage, dict)
    ):
        return
    unresolved_runtime = unknown_count + conflicting_count
    gap_count = static_coverage.get("gap_count")
    selected_branch = g5.get("selected_branch")
    verdict = g5.get("verdict")
    if (
        selected_branch == "approved-static"
        and type(gap_count) is int
        and gap_count != unresolved_runtime
    ):
        yield ValidationError(
            "approved-static G5 gap_count must equal runtime unknown_count "
            "+ conflicting_count"
        )
    if selected_branch == "runtime" and verdict == "pass" and unresolved_runtime != 0:
        yield ValidationError(
            "runtime G5 pass requires zero unknown and conflicting items"
        )


def chosen_alternative_is_declared(validator, enabled, instance, schema):
    if not enabled or not isinstance(instance, dict):
        return
    alternatives = instance.get("alternatives")
    if not isinstance(alternatives, list):
        return
    declared = {
        alternative.get("alternative_id")
        for alternative in alternatives
        if isinstance(alternative, dict)
        and isinstance(alternative.get("alternative_id"), str)
    }
    alternative_ids = [
        alternative.get("alternative_id")
        for alternative in alternatives
        if isinstance(alternative, dict)
        and isinstance(alternative.get("alternative_id"), str)
    ]
    if len(alternative_ids) != len(set(alternative_ids)):
        yield ValidationError("alternative_id values must be unique")
    chosen_outcome = instance.get("chosen_outcome")
    if isinstance(chosen_outcome, str) and chosen_outcome not in declared:
        yield ValidationError(
            "chosen_outcome must resolve to a declared alternative_id"
        )
    if instance.get("supersedes_decision_id") == instance.get("record_id"):
        yield ValidationError("a decision must not supersede itself")


CONTRACT_VALIDATOR = validators.extend(
    Draft202012Validator,
    {
        "x-coverage-buckets-fit-denominator": coverage_buckets_fit_denominator,
        "x-experiment-artifacts-are-bound": experiment_artifacts_are_bound,
        "x-coverage-gates-are-consistent": coverage_gates_are_consistent,
        "x-chosen-alternative-is-declared": chosen_alternative_is_declared,
    },
)


def create_schema_validator(name, schemas=None, schema_root=SCHEMA_ROOT):
    """Create a Draft 2020-12 validator with local-only reference resolution."""

    if schemas is None:
        schemas = load_schemas(schema_root)
    if name not in RECORD_SCHEMA_NAMES:
        raise ValueError(f"unknown schema: {name}")
    return CONTRACT_VALIDATOR(
        schemas[name],
        registry=create_schema_registry(schemas),
        format_checker=FormatChecker(),
    )


def infer_schema_name(record):
    """Infer a record schema from a stable record ID or experiment artifact shape."""

    if not isinstance(record, dict):
        raise ValueError("record must be a JSON object")
    record_id = record.get("record_id")
    if isinstance(record_id, str):
        prefix = record_id.split(":", 1)[0]
        mapping = {
            "asset": "asset",
            "evidence": "evidence",
            "claim": "claim",
            "trace": "trace-link",
            "experiment": "experiment",
            "decision": "decision",
            "coverage": "coverage-summary",
        }
        if prefix in mapping:
            return mapping[prefix]
    shape_markers = (
        ("asset_type", "asset"),
        ("claim_status", "claim"),
        ("dimensions", "coverage-summary"),
        ("chosen_outcome", "decision"),
        ("claim_relations", "evidence"),
        ("source_id", "trace-link"),
    )
    for marker, schema_name in shape_markers:
        if marker in record:
            return schema_name
    if all(key in record for key in ("protocol", "result", "effects")):
        return "experiment"
    artifact_type = record.get("artifact_type")
    if isinstance(artifact_type, str) and artifact_type.startswith("ART-P5-"):
        return "experiment"
    raise ValueError("unknown record type; provide --schema explicitly")


def validate_record(record, schema_name=None, schemas=None):
    """Return all standard and custom semantic validation errors."""

    schemas = schemas if schemas is not None else load_schemas()
    name = schema_name or infer_schema_name(record)
    validator = create_schema_validator(name, schemas=schemas)
    return sorted(
        validator.iter_errors(record),
        key=lambda error: (
            tuple(str(part) for part in error.absolute_path),
            error.message,
        ),
    )


def _record_index(records, kind, errors):
    index = {}
    if not isinstance(records, (list, tuple)):
        errors.append(f"{kind} records must be a list or tuple")
        return index
    for position, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"{kind}[{position}] must be an object")
            continue
        record_id = record.get("record_id")
        if not isinstance(record_id, str) or not record_id.strip():
            errors.append(f"{kind}[{position}].record_id must be a string")
            continue
        if record_id in index:
            errors.append(f"duplicate record ID: {record_id}")
            continue
        index[record_id] = record
    return index


def _relation_map(records, list_key, endpoint_key, label, errors):
    relations = {}
    for record_id, record in records.items():
        entries = record.get(list_key)
        if not isinstance(entries, list):
            continue
        for position, entry in enumerate(entries):
            if not isinstance(entry, dict):
                errors.append(f"{record_id}.{list_key}[{position}] must be an object")
                continue
            endpoint_id = entry.get(endpoint_key)
            relation = entry.get("relation")
            if not isinstance(endpoint_id, str) or not isinstance(relation, str):
                errors.append(
                    f"{record_id}.{list_key}[{position}] has malformed relation values"
                )
                continue
            pair = (
                (record_id, endpoint_id)
                if label == "claim"
                else (endpoint_id, record_id)
            )
            relations.setdefault(pair, set()).add(relation)
    return relations


def validate_claim_evidence_trace_bundle(
    claims, evidence_records, trace_links, known_record_ids=()
):
    """Return deterministic errors for a fully local record bundle.

    JSON Schema validation remains responsible for field types and formats. This
    validator closes references across independently valid records and never
    performs network retrieval.
    """

    errors = []
    claim_index = _record_index(claims, "claim", errors)
    evidence_index = _record_index(evidence_records, "evidence", errors)
    trace_index = _record_index(trace_links, "trace", errors)

    known = set()
    if isinstance(known_record_ids, (list, tuple, set, frozenset)):
        for position, record_id in enumerate(known_record_ids):
            if isinstance(record_id, str) and record_id.strip():
                known.add(record_id)
            else:
                errors.append(
                    f"known_record_ids[{position}] must be a non-empty string"
                )
    else:
        errors.append("known_record_ids must be a local collection")

    claim_relations = _relation_map(
        claim_index, "evidence_relations", "evidence_id", "claim", errors
    )
    evidence_relations = _relation_map(
        evidence_index, "claim_relations", "claim_id", "evidence", errors
    )

    for claim_id, evidence_id in sorted(set(claim_relations) | set(evidence_relations)):
        claim_side = claim_relations.get((claim_id, evidence_id), set())
        evidence_side = evidence_relations.get((claim_id, evidence_id), set())
        if claim_id not in claim_index:
            errors.append(f"dangling claim relation endpoint: {claim_id}")
        if evidence_id not in evidence_index:
            errors.append(f"dangling evidence relation endpoint: {evidence_id}")
        if not claim_side or not evidence_side:
            errors.append(
                f"one-sided claim/evidence relation: {claim_id} <-> {evidence_id}"
            )
        elif claim_side != evidence_side or len(claim_side) != 1:
            errors.append(f"relation conflict: {claim_id} <-> {evidence_id}")

    resolvable_ids = set(claim_index) | set(evidence_index) | set(trace_index) | known
    for trace_id, trace in trace_index.items():
        for endpoint_key in ("source_id", "target_id"):
            endpoint_id = trace.get(endpoint_key)
            if not isinstance(endpoint_id, str):
                errors.append(f"{trace_id}.{endpoint_key} must be a string")
            elif endpoint_id not in resolvable_ids:
                errors.append(
                    f"dangling trace endpoint: {trace_id}.{endpoint_key}={endpoint_id}"
                )
        evidence_references = trace.get("evidence_references")
        if isinstance(evidence_references, list):
            for position, evidence_id in enumerate(evidence_references):
                if not isinstance(evidence_id, str):
                    errors.append(
                        f"{trace_id}.evidence_references[{position}] must be a string"
                    )
                elif evidence_id not in evidence_index:
                    errors.append(
                        f"dangling trace evidence reference: {trace_id} -> {evidence_id}"
                    )

    return sorted(set(errors))
