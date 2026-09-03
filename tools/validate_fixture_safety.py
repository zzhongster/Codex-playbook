#!/usr/bin/env python3
"""Key-path-aware safety checks for published synthetic JSON fixtures."""

import base64
import binascii
import ipaddress
import re
from urllib.parse import unquote, urlsplit


_SECRET_KEY = re.compile(
    r"(?i)^(?:password|passwd|password[_-]?hash|pwd|secret|"
    r"client[_-]?secret|token|(?:access|refresh|id)[_-]?token|"
    r"api[_-]?key|apikey|credential|credentials|private[_-]?key|"
    r"connection[_-]?string)$"
)
_CREDENTIAL_VALUE = re.compile(
    r"(?i)(?:\b(?:password|passwd|secret|(?:access[ _-]?)?token|api[ _-]?key)\b"
    r"\s*[:=]\s*[\"']?[A-Za-z0-9._~+/-]{6,})"
)
_AUTHORIZATION_HEADER = re.compile(
    r"(?i)\bauthorization\s*[:=]\s*[a-z][a-z0-9._~-]{0,31}\s+\S+"
)
_BASIC_CREDENTIAL = re.compile(r"(?i)\bbasic\s+([A-Za-z0-9+/]{8,}={0,2})")
_BEARER_CREDENTIAL = re.compile(
    r"(?i)\bbearer\s+[A-Za-z0-9._~+/-]{8,}"
)
_NEGOTIATE_CREDENTIAL = re.compile(
    r"(?i)\bnegotiate\s+([A-Za-z0-9+/]{8,}={0,2})"
)
_DIGEST_CREDENTIAL = re.compile(
    r"(?i)\bdigest\s+[^\r\n]{0,1024}\b"
    r"(?:username|nonce|response|signature)\s*="
)
_JWT = re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b")
_AWS_ACCESS_KEY = re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")
_TOKEN_PREFIX = re.compile(
    r"\b(?:sk-(?:proj-)?[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,})\b"
)
_CONNECTION_STRING_CREDENTIAL = re.compile(
    r"(?i)(?:^|;)\s*(?:user\s+id|uid|pwd|password|client\s+secret)"
    r"\s*=\s*[^;\s][^;]*"
)
_PEM_PRIVATE_KEY = re.compile(
    r"-----BEGIN (?:EC |ENCRYPTED |OPENSSH |RSA )?PRIVATE KEY-----"
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
_DOMAIN = re.compile(
    r"(?<![A-Za-z0-9_-])"
    r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+"
    r"(?:[a-z]{2,63}|xn--[a-z0-9](?:[a-z0-9-]{0,57}[a-z0-9])?)"
    r"(?![A-Za-z0-9_-])",
    re.IGNORECASE,
)
_DNS_SINGLE_LABEL = re.compile(
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
)
_IPV4 = re.compile(r"(?<![0-9])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?![0-9])")
_IPV6 = re.compile(
    r"(?<![0-9A-Fa-f:])(?:[0-9A-Fa-f]{0,4}:){2,7}"
    r"[0-9A-Fa-f]{0,4}(?![0-9A-Fa-f:])"
)
_STABLE_ID = re.compile(
    r"(?:[a-z][a-z0-9-]*:[A-F0-9]{8,64}|"
    r"[a-z][a-z0-9-]*:[a-z][a-z0-9-]*(?:\.[a-z0-9-]+)+)"
)
_NETWORK_LABEL = re.compile(
    r"(?i)(?<![a-z0-9_-])"
    r"(?:address|domain|host|hostname|ip|ip-address|node|peer|server)"
    r"\s*[:=]\s*(?P<target>[^\s,;\"'<>]+)"
)
_NETWORK_FIELD = re.compile(
    r"(?i)(?:^|[_-])(?:host|hostname|node|peer|server)"
    r"(?:[_-](?:address|id|name))?$"
)
_NETWORK_AUTHORITY = re.compile(
    r"(?:\[[0-9A-Fa-f:.]+\]|"
    r"[A-Za-z0-9](?:[A-Za-z0-9.-]{0,251}[A-Za-z0-9])?)"
    r"(?::[0-9]+)?"
)
_AUTHORIZATION_FIELD = re.compile(r"(?i)^(?:authorization|proxy_authorization)$")
_AUTHORIZATION_PARAMETER_FIELD = re.compile(
    r"(?i)^(?:cnonce|credential|credentials|nonce|response|signature|username)$"
)
_SAFE_AUTHORIZATION_STATUSES = frozenset(
    {
        "allowed",
        "approved",
        "authorized",
        "denied",
        "disallowed",
        "fail",
        "not-applicable",
        "not-required",
        "pass",
        "pending",
        "required",
        "unauthorized",
    }
)
_DOCUMENTATION_DOMAINS = frozenset({"example.com", "example.net", "example.org"})
_TECHNICAL_FIELD = re.compile(
    r"(?i)(?:^|[_-])(?:type|class|symbol|package|namespace|assembly|module|unit)"
    r"(?:[_-](?:name|reference))?$"
)
_DOTTED_IDENTIFIER = re.compile(
    r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+"
)
_STANDARD_PLATFORM_SYMBOL = re.compile(
    r"(?:java|javax|jakarta|kotlin|scala)"
    r"(?:\.[A-Za-z_][A-Za-z0-9_]*)+"
)
_DOTNET_NAMESPACE = re.compile(
    r"[A-Z][A-Za-z0-9_]*(?:\.[A-Z][A-Za-z0-9_]*)+"
)
_REVERSE_DOMAIN_PACKAGE = re.compile(
    r"(?:com|org|net|io)(?:\.[a-z_][a-z0-9_]*)+"
)
_KNOWN_FIXTURE_FILE = re.compile(
    r"(?i)^[a-z0-9][a-z0-9_-]*\.(?:csv|html|json|log|md|txt|xml|yaml|yml)$"
)
_VERSION_FIELD = re.compile(
    r"(?i)^(?:version|assembly_version|file_version|product_version)$"
)
_FOUR_PART_VERSION = re.compile(r"[0-9]+(?:\.[0-9]+){3}")
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
    if normalized in _DOCUMENTATION_DOMAINS or any(
        normalized.endswith(f".{domain}") for domain in _DOCUMENTATION_DOMAINS
    ):
        return True
    try:
        address = ipaddress.ip_address(normalized)
    except ValueError:
        return False
    if isinstance(address, ipaddress.IPv4Address):
        return any(address in network for network in _RESERVED_IPV4)
    return address in _RESERVED_IPV6


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


def _network_identifier_errors(identifier, path, reject_single_label=False):
    normalized = identifier.strip("[]").rstrip(".")
    try:
        address = ipaddress.ip_address(normalized)
    except ValueError:
        if _DOMAIN.fullmatch(normalized) and not _reserved_host(normalized):
            return [f"{path}: non-reserved domain {normalized.lower()}"]
        if (
            reject_single_label
            and _DNS_SINGLE_LABEL.fullmatch(normalized)
            and not _reserved_host(normalized)
            and not _FICTIONAL_MARKER.search(normalized)
        ):
            return [f"{path}: non-synthetic single-label host {normalized}"]
        return []
    if not _reserved_host(str(address)):
        return [f"{path}: non-reserved IP address {address}"]
    return []


def _parse_network_authority(value):
    normalized = value.strip()
    if not normalized or any(character.isspace() for character in normalized):
        return None, "malformed authority"
    try:
        authority = urlsplit(f"//{normalized}")
    except ValueError:
        return None, "malformed authority"
    if authority.username is not None or authority.password is not None:
        return None, "credential/userinfo in network authority"
    if (
        authority.hostname is None
        or authority.path
        or authority.query
        or authority.fragment
        or not _NETWORK_AUTHORITY.fullmatch(normalized)
    ):
        return None, "malformed authority"
    try:
        port = authority.port
    except ValueError:
        return None, "malformed authority"
    if port is not None and not 1 <= port <= 65535:
        return None, "malformed authority"

    normalized_host = authority.hostname.rstrip(".")
    try:
        ipaddress.ip_address(normalized_host)
    except ValueError:
        if not (
            _DOMAIN.fullmatch(normalized_host)
            or _DNS_SINGLE_LABEL.fullmatch(normalized_host)
        ):
            return None, "malformed authority"
    return authority.hostname, None


def _valid_base64_token(token, require_colon=False):
    try:
        decoded = base64.b64decode(token, validate=True)
    except (binascii.Error, ValueError):
        return False
    return not require_colon or b":" in decoded


def _has_authorization_credential_syntax(value):
    if _AUTHORIZATION_HEADER.search(value) or _BEARER_CREDENTIAL.search(value):
        return True
    if _DIGEST_CREDENTIAL.search(value):
        return True
    for match in _BASIC_CREDENTIAL.finditer(value):
        if _valid_base64_token(match.group(1), require_colon=True):
            return True
    for match in _NEGOTIATE_CREDENTIAL.finditer(value):
        if _valid_base64_token(match.group(1)):
            return True
    return False


def _authorization_context(path_keys):
    return any(_AUTHORIZATION_FIELD.fullmatch(key) for key in path_keys[:-1])


def _technical_symbol_literal(value, path_keys):
    normalized = value.strip()
    if not _DOTTED_IDENTIFIER.fullmatch(normalized):
        return False
    if path_keys and _TECHNICAL_FIELD.search(path_keys[-1]):
        return True
    return bool(
        _STANDARD_PLATFORM_SYMBOL.fullmatch(normalized)
        or _DOTNET_NAMESPACE.fullmatch(normalized)
        or _REVERSE_DOMAIN_PACKAGE.fullmatch(normalized)
    )


def _four_part_version_literal(value, path_keys):
    return bool(
        path_keys
        and _VERSION_FIELD.fullmatch(path_keys[-1])
        and _FOUR_PART_VERSION.fullmatch(value.strip())
    )


def _string_safety_errors(value, path, path_keys):
    errors = []
    if (
        _CREDENTIAL_VALUE.search(value)
        or _has_authorization_credential_syntax(value)
        or _JWT.search(value)
        or _AWS_ACCESS_KEY.search(value)
        or _TOKEN_PREFIX.search(value)
        or _CONNECTION_STRING_CREDENTIAL.search(value)
        or _PEM_PRIVATE_KEY.search(value)
    ):
        errors.append(f"{path}: credential-like value")
    if path_keys and _AUTHORIZATION_FIELD.fullmatch(path_keys[-1]):
        if value.strip().lower() not in _SAFE_AUTHORIZATION_STATUSES:
            errors.append(f"{path}: authorization scalar is not a safe status")
    elif (
        path_keys
        and _authorization_context(path_keys)
        and _AUTHORIZATION_PARAMETER_FIELD.fullmatch(path_keys[-1])
    ):
        errors.append(f"{path}: authorization credential parameter")
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
        except ValueError:
            errors.append(f"{path}: malformed URL authority")
            continue
        authority_host, authority_error = _parse_network_authority(
            unquote(parsed_url.netloc)
        )
        if authority_error == "credential/userinfo in network authority":
            errors.append(f"{path}: URL userinfo credential")
        elif authority_error:
            errors.append(f"{path}: malformed URL authority")
        else:
            errors.extend(
                _network_identifier_errors(
                    authority_host, path, reject_single_label=True
                )
            )

    non_url_text = _URL.sub("", value)
    normalized_non_url_text = non_url_text.strip(" \t\r\n[](){}<>,;\"'")
    stable_id_literal = bool(_STABLE_ID.fullmatch(normalized_non_url_text))
    precise_non_network_literal = bool(
        _technical_symbol_literal(value, path_keys)
        or _KNOWN_FIXTURE_FILE.fullmatch(value.strip())
    )

    if not _four_part_version_literal(value, path_keys):
        for match in _IPV4.finditer(value):
            errors.extend(_network_identifier_errors(match.group(0), path))
    for match in _IPV6.finditer(value):
        errors.extend(_network_identifier_errors(match.group(0), path))

    if not stable_id_literal and not precise_non_network_literal:
        for match in _DOMAIN.finditer(non_url_text):
            errors.extend(_network_identifier_errors(match.group(0), path))

    if path_keys and _NETWORK_FIELD.search(path_keys[-1]):
        authority_host, authority_error = _parse_network_authority(
            non_url_text.strip()
        )
        if authority_error:
            errors.append(f"{path}: {authority_error}")
        else:
            errors.extend(
                _network_identifier_errors(
                    authority_host, path, reject_single_label=True
                )
            )

    for match in _NETWORK_LABEL.finditer(non_url_text):
        target = match.group("target")
        authority_host, authority_error = _parse_network_authority(target)
        if authority_error:
            errors.append(f"{path}: {authority_error}")
        else:
            errors.extend(
                _network_identifier_errors(
                    authority_host, path, reject_single_label=True
                )
            )
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
                if (
                    _AUTHORIZATION_FIELD.fullmatch(key_text)
                    and not isinstance(nested, (dict, list, str))
                ):
                    errors.append(
                        f"{child_path}: authorization scalar is not a safe status"
                    )
                visit(nested, child_path, (*path_keys, key_text))
        elif isinstance(child, list):
            for position, nested in enumerate(child):
                visit(nested, f"{path}[{position}]", path_keys)
        elif isinstance(child, str):
            errors.extend(_string_safety_errors(child, path, path_keys))

    visit(value, "$", ())
    return sorted(set(errors))
