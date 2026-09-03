#!/usr/bin/env python3
"""Key-path-aware safety checks for published synthetic JSON fixtures."""

import ipaddress
import re
from urllib.parse import urlsplit


_SECRET_KEY = re.compile(
    r"(?i)^(?:password|passwd|secret|token|"
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
    r"[_-]?(?:record|identity|name|id|address|contact|email|phone)?"
    r"\s*[:=]\s*"
    r"(?!sample\b|synthetic\b|example\b|test\b)[^\s,;]+"
)
_BUSINESS_RECORD_FILENAME = re.compile(
    r"(?i)(?<![a-z0-9_-])(?:business|client|company|customer|tenant)"
    r"(?:[-_](?:data|record|records))?\.(?:csv|json|md|txt|xml|yaml|yml)"
    r"(?![a-z0-9])"
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
_NETWORK_FIELD = re.compile(
    r"(?i)(?:^|[_-])(?:address|domain|endpoint|host|hostname|ip|ip-address|"
    r"ip_address|ipv4|ipv6|origin|server|uri|url)$"
)
_NETWORK_LABEL = re.compile(
    r"(?i)\b(?:address|domain|host|hostname|ip|ip-address|server)"
    r"\s*[:=]\s*(?P<target>\[[0-9a-f:]+\]|"
    r"(?:[0-9a-f]{0,4}:){2,7}[0-9a-f]{0,4}|[a-z0-9.-]+)"
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
_BUSINESS_CONTAINER_FIELD = re.compile(
    r"(?i)^(?:business(?:es)?|clients?|companies|company|customers?|tenants?)$"
)
_BUSINESS_IDENTITY_FIELD = re.compile(
    r"(?i)^(?:business(?:es)?|clients?|companies|company|customers?|tenants?)"
    r"(?:[_-]?(?:address|contact|email|id|identity|name|phone|record))?$"
)
_SUBJECT_IDENTITY_FIELD = re.compile(
    r"(?i)^(?:address|contact|email|id|identity|name|phone|record|user_name|"
    r"username)$"
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


def _network_field(path_keys):
    if not path_keys:
        return False
    return bool(_NETWORK_FIELD.search(path_keys[-1]))


def _requires_fictional_metadata(path_keys):
    if not path_keys:
        return False
    leaf = path_keys[-1]
    if _IDENTITY_FIELD.fullmatch(leaf) or _PROJECT_IDENTITY_FIELD.fullmatch(leaf):
        return True
    if _BUSINESS_IDENTITY_FIELD.fullmatch(leaf):
        return True
    for position, key in enumerate(path_keys[:-1]):
        if not _BUSINESS_CONTAINER_FIELD.fullmatch(key):
            continue
        if any(
            _SUBJECT_IDENTITY_FIELD.fullmatch(descendant)
            for descendant in path_keys[position + 1 :]
        ):
            return True
    return False


def _network_identifier_errors(identifier, path):
    normalized = identifier.strip("[]").rstrip(".")
    try:
        address = ipaddress.ip_address(normalized)
    except ValueError:
        if _DOMAIN.fullmatch(normalized) and not _reserved_host(normalized):
            return [f"{path}: non-reserved domain {normalized.lower()}"]
        return []
    if not _reserved_host(str(address)):
        return [f"{path}: non-reserved IP address {address}"]
    return []


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
    if _BUSINESS_RECORD_FILENAME.search(value):
        errors.append(f"{path}: customer or business record-like filename")
    if _requires_fictional_metadata(path_keys) and not _FICTIONAL_MARKER.search(
        value
    ):
        errors.append(
            f"{path}: identity or business metadata is not explicitly fictional"
        )

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
            errors.extend(_network_identifier_errors(host, path))

    non_url_text = _URL.sub("", value)
    normalized_non_url_text = non_url_text.strip(" \t\r\n[](){}<>,;\"'")
    if _network_field(path_keys) and not _STABLE_ID.fullmatch(
        normalized_non_url_text
    ):
        for pattern in (_DOMAIN, _IPV4, _IPV6):
            for match in pattern.finditer(non_url_text):
                errors.extend(_network_identifier_errors(match.group(0), path))

    for match in _NETWORK_LABEL.finditer(non_url_text):
        errors.extend(_network_identifier_errors(match.group("target"), path))
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
