#!/usr/bin/env python3
"""Offline semantic validation for claim, evidence, and trace record bundles."""


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
                errors.append(
                    f"{record_id}.{list_key}[{position}] must be an object"
                )
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

    for claim_id, evidence_id in sorted(
        set(claim_relations) | set(evidence_relations)
    ):
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
            errors.append(
                f"relation conflict: {claim_id} <-> {evidence_id}"
            )

    resolvable_ids = (
        set(claim_index) | set(evidence_index) | set(trace_index) | known
    )
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
