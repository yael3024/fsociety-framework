import ipaddress

import pytest

from fsociety.core.permissions import ScopeError, authorize_network
from fsociety.modules.network import scan_network
from fsociety.utils.validators import validate_ip


def test_private_scope_and_prefix_limit(tmp_path):
    scope = tmp_path / "scope.txt"
    scope.write_text("10.0.0.0/8\n", encoding="utf-8")
    assert authorize_network("10.1.2.0/24", scope) == ipaddress.ip_network("10.1.2.0/24")
    with pytest.raises(ScopeError):
        authorize_network("10.0.0.0/23", scope)
    with pytest.raises(ScopeError):
        authorize_network("8.8.8.0/24", scope)
    with pytest.raises(ScopeError):
        authorize_network("192.0.2.0/24", scope)


def test_scope_requires_registered_network(tmp_path):
    scope = tmp_path / "scope.txt"
    scope.write_text("192.168.4.0/24\n", encoding="utf-8")
    with pytest.raises(ScopeError):
        authorize_network("192.168.5.0/24", scope)


def test_validate_ip_ipv4_only():
    assert str(validate_ip("127.0.0.1")) == "127.0.0.1"
    with pytest.raises(ValueError):
        validate_ip("2001:db8::1")


def test_scanner_rejects_unregistered_before_network_io(tmp_path):
    with pytest.raises(ScopeError):
        scan_network("192.168.1.0/24", tmp_path / "missing.txt")
