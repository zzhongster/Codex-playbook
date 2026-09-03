#!/usr/bin/env python3
"""Value-aware safety checks for published synthetic JSON fixtures."""

import ipaddress
import re
from urllib.parse import urlsplit


_SECRET_KEY = re.compile(
    r"(?i)^(?:password|passwd|secret|access[_-]?token|api[_-]?key)$"
)
_CREDENTIAL_VALUE = re.compile(
    r"(?i)(?:\b(?:password|passwd|secret|access[ _-]?token|api[ _-]?key)\b"
    r"\s*[:=]\s*\S+|\bbearer\s+[A-Za-z0-9._~+/-]{8,})"
)
_JWT = re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b")
_AWS_ACCESS_KEY = re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")
_TOKEN_PREFIX = re.compile(
    r"\b(?:sk-(?:proj-)?[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,})\b"
)
_USER_PATH = re.compile(
    r"(?:^|\s)(?:/Users/[^\s]+|/home/[^\s]+|[A-Za-z]:[\\/]Users[\\/][^\s]+)"
)
_LABELED_BUSINESS_RECORD = re.compile(
    r"(?i)\b(?:customer|business|company|contact)[_-]?(?:name|id)?\s*[:=]\s*"
    r"(?!sample\b|synthetic\b|example\b|test\b)[^\s,;]+"
)
_URL = re.compile(r"\b[a-z][a-z0-9+.-]*://[^\s\"'<>]+", re.IGNORECASE)
_DOMAIN = re.compile(r"(?i)\b(?:[a-z0-9-]+\.)+[a-z]{2,63}\b")
_IPV4 = re.compile(r"(?<![0-9])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?![0-9])")

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


def _string_safety_errors(value, path):
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

    url_hosts = set()
    for match in _URL.finditer(value):
        host = urlsplit(match.group(0)).hostname
        if isinstance(host, str):
            url_hosts.add(host.lower())
            if not _reserved_host(host):
                errors.append(f"{path}: non-reserved URL host {host}")

    non_url_text = _URL.sub("", value)
    normalized_non_url_text = non_url_text.strip(" \t\r\n[](){}<>,;\"'")
    for domain_match in _DOMAIN.finditer(non_url_text):
        domain = domain_match.group(0).lower()
        explicitly_labeled = bool(
            re.search(
                rf"(?i)\b(?:host|hostname|domain|server)\s*[:=]\s*{re.escape(domain)}\b",
                non_url_text,
            )
        )
        if (
            domain not in url_hosts
            and (normalized_non_url_text.lower() == domain or explicitly_labeled)
            and not _reserved_host(domain)
        ):
            errors.append(f"{path}: non-reserved domain {domain}")

    for address_match in _IPV4.finditer(value):
        address_text = address_match.group(0)
        try:
            address = ipaddress.ip_address(address_text)
        except ValueError:
            continue
        if not _reserved_host(address_text):
            errors.append(f"{path}: non-reserved IP address {address}")

    stripped = value.strip(" [](){}<>,;")
    if ":" in stripped and not "://" in stripped:
        try:
            address = ipaddress.ip_address(stripped)
        except ValueError:
            pass
        else:
            if not _reserved_host(str(address)):
                errors.append(f"{path}: non-reserved IP address {address}")
    return errors


def fixture_safety_errors(value):
    """Return path-qualified errors for unsafe fixture keys or values."""

    errors = []

    def visit(child, path):
        if isinstance(child, dict):
            for key, nested in child.items():
                key_text = str(key)
                child_path = f"{path}.{key_text}"
                if _SECRET_KEY.fullmatch(key_text):
                    errors.append(f"{child_path}: secret-shaped key")
                visit(nested, child_path)
        elif isinstance(child, list):
            for position, nested in enumerate(child):
                visit(nested, f"{path}[{position}]")
        elif isinstance(child, str):
            errors.extend(_string_safety_errors(child, path))

    visit(value, "$")
    return sorted(set(errors))
