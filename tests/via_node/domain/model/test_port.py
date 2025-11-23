from datetime import datetime

import pytest

from via_node.domain.model.port import Port


class TestPort:
    def test_should_create_port_when_all_fields_are_valid(self) -> None:
        port = Port(
            port_number=443,
            protocol="TCP",
            service_name="https",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert port.port_number == 443

    def test_should_accept_minimum_valid_port_number(self) -> None:
        port = Port(
            port_number=1,
            protocol="TCP",
            service_name=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert port.port_number == 1

    def test_should_accept_maximum_valid_port_number(self) -> None:
        port = Port(
            port_number=65535,
            protocol="TCP",
            service_name=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert port.port_number == 65535

    def test_should_raise_error_when_port_number_is_zero(self) -> None:
        with pytest.raises(ValueError, match="Port number must be between 1 and 65535"):
            Port(
                port_number=0,
                protocol="TCP",
                service_name=None,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

    def test_should_raise_error_when_port_number_exceeds_maximum(self) -> None:
        with pytest.raises(ValueError, match="Port number must be between 1 and 65535"):
            Port(
                port_number=65536,
                protocol="TCP",
                service_name=None,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

    def test_should_normalize_protocol_to_uppercase(self) -> None:
        port = Port(
            port_number=443,
            protocol="tcp",
            service_name=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert port.protocol == "TCP"

    def test_should_accept_udp_protocol(self) -> None:
        port = Port(
            port_number=53,
            protocol="UDP",
            service_name="dns",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert port.protocol == "UDP"

    def test_should_raise_error_when_protocol_is_invalid(self) -> None:
        with pytest.raises(ValueError, match="Protocol must be one of"):
            Port(
                port_number=443,
                protocol="INVALID",
                service_name=None,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

    def test_should_allow_none_for_optional_service_name(self) -> None:
        port = Port(
            port_number=443,
            protocol="TCP",
            service_name=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert port.service_name is None
