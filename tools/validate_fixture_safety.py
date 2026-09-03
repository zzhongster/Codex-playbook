#!/usr/bin/env python3
"""Key-path-aware safety checks for published synthetic JSON fixtures."""

import ipaddress
import re
from urllib.parse import urlsplit


_SECRET_KEY = re.compile(
    r"(?i)^(?:authorization|password|passwd|secret|token|"
    r"(?:access|refresh|id)[_-]?token|api[_-]?key|apikey)$"
)
_CREDENTIAL_VALUE = re.compile(
    r"(?i)(?:\b(?:password|passwd|secret|(?:access[ _-]?)?token|api[ _-]?key)\b"
    r"\s*[:=]\s*[\"']?[A-Za-z0-9._~+/-]{6,}|"
    r"\b(?:authorization\s*[:=]\s*)?bearer\s+[A-Za-z0-9._~+/-]{8,}|"
    r"\b(?:authorization\s*[:=]\s*)?basic\s+[A-Za-z0-9+/]{8,}={0,2})"
)
_JWT = re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b")
_AWS_ACCESS_KEY = re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")
_TOKEN_PREFIX = re.compile(
    r"\b(?:sk-(?:proj-)?[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,})\b"
)
_USER_PATH = re.compile(
    r"(?:/Users/[^/\s]+(?:/[^\s]*)?|/home/[^/\s]+(?:/[^\s]*)?|"
    r"/root/[^\s]*|"
    r"[A-Za-z]:[\\/](?:Users|Documents and Settings)[\\/]"
    r"[^\\/\s]+(?:[\\/][^\s]*)?)"
)
_LABELED_BUSINESS_RECORD = re.compile(
    r"(?i)\b(?:customer|client|business|company|tenant|contact)"
    r"[_-]?(?:record|name|id)?\s*[:=]\s*"
    r"(?!sample\b|synthetic\b|example\b|test\b)[^\s,;]+"
)
_URL = re.compile(r"\b[a-z][a-z0-9+.-]*://[^\s\"'<>]+", re.IGNORECASE)
_DOMAIN = re.compile(r"(?i)\b(?:[a-z0-9-]+\.)+[a-z]{2,63}\b")
_IPV4 = re.compile(r"(?<![0-9])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?![0-9])")
_IPV6 = re.compile(
    r"(?<![0-9A-Fa-f:])(?:[0-9A-Fa-f]{0,4}:){2,7}"
    r"[0-9A-Fa-f]{0,4}(?![0-9A-Fa-f:])"
)
_STABLE_ID = re.compile(
    r"(?:[a-z][a-z0-9-]*:[A-F0-9]{8,64}|"
    r"[a-z][a-z0-9-]*:[a-z][a-z0-9-]*(?:\.[a-z0-9-]+)+)"
)
_SAFE_FIXTURE_FILENAME = re.compile(
    r"(?i)(?:template|sample|synthetic|example|fixture|test|demo)"
    r"(?:[-_][a-z0-9-]+)*\.(?:csv|html|json|log|md|txt|xml|yaml|yml)"
)
_SAFE_SYNTHETIC_LOGICAL_KEY = re.compile(
    r"(?i)(?:[a-z][a-z0-9-]*:)?"
    r"(?:demo|example|fictional|fixture|sample|synthetic|template|test)"
    r"(?:\.[a-z0-9-]+)+"
)
_FICTIONAL_MARKER = re.compile(
    r"(?i)(?:^|[^a-z0-9])(?:demo|example|fictional|fixture|replace|sample|"
    r"synthetic|template|test)(?:[^a-z0-9]|$)"
)
_IDENTITY_FIELD = re.compile(
    r"(?i)^(?:username|user_name|login_user|owner|reviewer|approver|"
    r"approved_by|captured_by|executor|executed_by)$"
)
_PROJECT_IDENTITY_FIELD = re.compile(
    r"(?i)^project(?:[_-]?(?:id|key|name|owner|slug))?$"
)
_BUSINESS_SUBJECT_FIELD = re.compile(
    r"(?i)(?:^|[_-])(?:business(?:es)?|clients?|companies|company|"
    r"customers?|tenants?)(?=$|[_-]|record|name|id)"
)

_RESERVED_SUFFIXES = (".invalid", ".example", ".test", ".localhost")
_RESERVED_IPV4 = tuple(
    ipaddress.ip_network(network)
    for network in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24")
)
_RESERVED_IPV6 = ipaddress.ip_network("2001:db8::/32")


def _reserved_host(host):
    if not isinstance(host, str):
        return False
    normalized = host.rstrip(".").lower()
    if normalized in {"invalid", "example", "test", "localhost"}:
        return True
    if normalized.endswith(_RESERVED_SUFFIXES):
        return True
    try:
        address = ipaddress.ip_address(normalized)
    except ValueError:
        return False
    if isinstance(address, ipaddress.IPv4Address):
        return any(address in network for network in _RESERVED_IPV4)
    return address in _RESERVED_IPV6


def _stable_id_field(path_keys):
    if not path_keys:
        return False
    leaf = path_keys[-1].lower()
    parent = path_keys[-2].lower() if len(path_keys) > 1 else ""
    return (
        leaf == "id"
        or leaf.endswith("_id")
        or leaf.endswith("_reference")
        or leaf.endswith("_references")
        or parent.endswith("_references")
        or leaf in {"chosen", "source_id", "target_id"}
    )


def _requires_fictional_metadata(path_keys):
    if not path_keys:
        return False
    leaf = path_keys[-1]
    if _IDENTITY_FIELD.fullmatch(leaf) or _PROJECT_IDENTITY_FIELD.fullmatch(leaf):
        return True
    return any(_BUSINESS_SUBJECT_FIELD.search(key) for key in path_keys)


def _string_safety_errors(value, path, path_keys):
    errors = []
    if (
        _CREDENTIAL_VALUE.search(value)
        or _JWT.search(value)
        or _AWS_ACCESS_KEY.search(value)
        or _TOKEN_PREFIX.search(value)
    ):
        errors.append(f"{path}: credential-like value")
    if _USER_PATH.search(value):
        errors.append(f"{path}: absolute user path")
    if _LABELED_BUSINESS_RECORD.search(value):
        errors.append(f"{path}: customer or business record-like value")
    if _requires_fictional_metadata(path_keys) and not _FICTIONAL_MARKER.search(
        value
    ):
        errors.append(
            f"{path}: identity or business metadata is not explicitly fictional"
        )

    url_hosts = set()
    for match in _URL.finditer(value):
        try:
            parsed_url = urlsplit(match.group(0))
            host = parsed_url.hostname
        except ValueError:
            errors.append(f"{path}: malformed URL authority")
            continue
        if parsed_url.username is not None or parsed_url.password is not None:
            errors.append(f"{path}: URL userinfo credential")
        if isinstance(host, str):
            url_hosts.add(host.lower())
            if not _reserved_host(host):
                errors.append(f"{path}: non-reserved URL host {host}")

    non_url_text = _URL.sub("", value)
    normalized_non_url_text = non_url_text.strip(" \t\r\n[](){}<>,;\"'")
    is_typed_stable_id = bool(
        _stable_id_field(path_keys) and _STABLE_ID.fullmatch(normalized_non_url_text)
    )
    is_explicitly_safe_filename = bool(
        _SAFE_FIXTURE_FILENAME.fullmatch(normalized_non_url_text)
    )
    is_explicitly_synthetic_logical_key = bool(
        _SAFE_SYNTHETIC_LOGICAL_KEY.fullmatch(normalized_non_url_text)
    )
    for domain_match in _DOMAIN.finditer(non_url_text):
        domain = domain_match.group(0).lower()
        explicitly_labeled = bool(
            re.search(
                rf"(?i)\b(?:host|hostname|domain|server)\s*[:=]\s*{re.escape(domain)}\b",
                non_url_text,
            )
        )
        if (
            domain in url_hosts
            or is_typed_stable_id
            or is_explicitly_safe_filename
            or is_explicitly_synthetic_logical_key
            or _reserved_host(domain)
        ):
            continue
        location = (
            "non-reserved domain"
            if normalized_non_url_text.lower() == domain or explicitly_labeled
            else "embedded non-reserved domain"
        )
        errors.append(f"{path}: {location} {domain}")

    for address_match in _IPV4.finditer(value):
        address_text = address_match.group(0)
        try:
            address = ipaddress.ip_address(address_text)
        except ValueError:
            continue
        if not _reserved_host(address_text):
            errors.append(f"{path}: non-reserved IP address {address}")

    for address_match in _IPV6.finditer(value):
        address_text = address_match.group(0)
        try:
            address = ipaddress.ip_address(address_text)
        except ValueError:
            continue
        else:
            if not _reserved_host(str(address)):
                errors.append(f"{path}: non-reserved IP address {address}")
    return errors


def fixture_safety_errors(value):
    """Return path-qualified errors for unsafe fixture keys or values."""

    errors = []

    def visit(child, path, path_keys):
        if isinstance(child, dict):
            for key, nested in child.items():
                key_text = str(key)
                child_path = f"{path}.{key_text}"
                if _SECRET_KEY.fullmatch(key_text):
                    errors.append(f"{child_path}: secret-shaped key")
                visit(nested, child_path, (*path_keys, key_text))
        elif isinstance(child, list):
            for position, nested in enumerate(child):
                visit(nested, f"{path}[{position}]", path_keys)
        elif isinstance(child, str):
            errors.extend(_string_safety_errors(child, path, path_keys))

    visit(value, "$", ())
    return sorted(set(errors))
