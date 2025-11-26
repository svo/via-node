from datetime import datetime

import pytest
from assertpy import assert_that

from via_node.domain.model.host import Host


class TestHost:
    def test_valid_host_creation_with_ip(self) -> None:
        now = datetime.now()
        host = Host(
            ip_address="192.168.1.1",
            hostname="example.com",
            os_type="Linux",
            metadata={"version": "1.0"},
            created_at=now,
            updated_at=now,
        )

        assert_that(host.ip_address).is_equal_to("192.168.1.1")

    def test_valid_host_creation_with_hostname(self) -> None:
        now = datetime.now()
        host = Host(
            ip_address="192.168.1.1",
            hostname="example.com",
            os_type="Linux",
            metadata={"version": "1.0"},
            created_at=now,
            updated_at=now,
        )

        assert_that(host.hostname).is_equal_to("example.com")

    def test_valid_host_creation_with_os_type(self) -> None:
        now = datetime.now()
        host = Host(
            ip_address="192.168.1.1",
            hostname="example.com",
            os_type="Linux",
            metadata={"version": "1.0"},
            created_at=now,
            updated_at=now,
        )

        assert_that(host.os_type).is_equal_to("Linux")

    def test_valid_host_creation_with_metadata(self) -> None:
        now = datetime.now()
        host = Host(
            ip_address="192.168.1.1",
            hostname="example.com",
            os_type="Linux",
            metadata={"version": "1.0"},
            created_at=now,
            updated_at=now,
        )

        assert_that(host.metadata).is_equal_to({"version": "1.0"})

    def test_host_without_metadata(self) -> None:
        now = datetime.now()
        host = Host(
            ip_address="192.168.1.1",
            hostname="example.com",
            os_type="Linux",
            created_at=now,
            updated_at=now,
        )

        assert_that(host.metadata).is_none()

    def test_valid_ipv4_addresses(self) -> None:
        now = datetime.now()
        valid_ips = [
            "0.0.0.0",
            "127.0.0.1",
            "192.168.1.1",
            "255.255.255.255",
            "10.0.0.1",
        ]

        for ip in valid_ips:
            host = Host(
                ip_address=ip,
                hostname="example.com",
                os_type="Linux",
                created_at=now,
                updated_at=now,
            )
            assert_that(host.ip_address).is_equal_to(ip)

    def test_invalid_ipv4_addresses(self) -> None:
        now = datetime.now()
        invalid_ips = [
            "256.0.0.1",  # octet > 255
            "192.168.1",  # too few octets
            "192.168.1.1.1",  # too many octets
            "192.168.a.1",  # non-numeric
            "",  # empty
        ]

        for ip in invalid_ips:
            with pytest.raises(ValueError):
                Host(
                    ip_address=ip,
                    hostname="example.com",
                    os_type="Linux",
                    created_at=now,
                    updated_at=now,
                )

    def test_valid_ipv6_addresses(self) -> None:
        now = datetime.now()
        valid_ips = [
            "::1",
            "2001:db8::1",
            "fe80::1",
        ]

        for ip in valid_ips:
            host = Host(
                ip_address=ip,
                hostname="example.com",
                os_type="Linux",
                created_at=now,
                updated_at=now,
            )
            assert_that(host.ip_address).is_equal_to(ip)

    def test_invalid_ipv6_addresses(self) -> None:
        from pydantic_core import ValidationError

        now = datetime.now()
        invalid_ips = [
            "gggg::1",  # invalid hex characters
        ]

        for ip in invalid_ips:
            with pytest.raises(ValidationError):
                Host(
                    ip_address=ip,
                    hostname="example.com",
                    os_type="Linux",
                    created_at=now,
                    updated_at=now,
                )

    def test_hostname_normalization(self) -> None:
        now = datetime.now()
        host = Host(
            ip_address="192.168.1.1",
            hostname="  EXAMPLE.COM  ",
            os_type="Linux",
            created_at=now,
            updated_at=now,
        )

        assert_that(host.hostname).is_equal_to("example.com")

    def test_empty_hostname_raises_error(self) -> None:
        now = datetime.now()
        with pytest.raises(ValueError):
            Host(
                ip_address="192.168.1.1",
                hostname="",
                os_type="Linux",
                created_at=now,
                updated_at=now,
            )

    def test_whitespace_only_hostname_raises_error(self) -> None:
        now = datetime.now()
        with pytest.raises(ValueError):
            Host(
                ip_address="192.168.1.1",
                hostname="   ",
                os_type="Linux",
                created_at=now,
                updated_at=now,
            )

    def test_hostname_exceeding_max_length_raises_error(self) -> None:
        now = datetime.now()
        long_hostname = "a" * 254
        with pytest.raises(ValueError):
            Host(
                ip_address="192.168.1.1",
                hostname=long_hostname,
                os_type="Linux",
                created_at=now,
                updated_at=now,
            )

    def test_empty_os_type_raises_error(self) -> None:
        now = datetime.now()
        with pytest.raises(ValueError):
            Host(
                ip_address="192.168.1.1",
                hostname="example.com",
                os_type="",
                created_at=now,
                updated_at=now,
            )

    def test_whitespace_only_os_type_raises_error(self) -> None:
        now = datetime.now()
        with pytest.raises(ValueError):
            Host(
                ip_address="192.168.1.1",
                hostname="example.com",
                os_type="   ",
                created_at=now,
                updated_at=now,
            )

    def test_various_os_types(self) -> None:
        now = datetime.now()
        os_types = ["Linux", "Windows", "macOS", "FreeBSD", "Unknown"]

        for os_type in os_types:
            host = Host(
                ip_address="192.168.1.1",
                hostname="example.com",
                os_type=os_type,
                created_at=now,
                updated_at=now,
            )
            assert host.os_type == os_type

    def test_invalid_metadata_raises_error(self) -> None:
        now = datetime.now()
        with pytest.raises(ValueError):
            Host(
                ip_address="192.168.1.1",
                hostname="example.com",
                os_type="Linux",
                metadata="invalid",
                created_at=now,
                updated_at=now,
            )
