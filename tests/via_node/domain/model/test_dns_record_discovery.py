from datetime import datetime

import pytest
from assertpy import assert_that

from via_node.domain.model.dns_record_discovery import DnsRecordDiscovery, DnsRecordType


class TestDnsRecordDiscoveryCreation:
    def test_create_dns_record_discovery_with_valid_data(self) -> None:
        discovery = DnsRecordDiscovery(
            domain_name="example.com",
            record_type=DnsRecordType.A,
            values=["192.168.1.1"],
            ttl=3600,
            discovered_at=datetime.now(),
        )

        assert_that(discovery.domain_name).is_equal_to("example.com")

    def test_create_dns_record_discovery_with_ipv6_address(self) -> None:
        discovery = DnsRecordDiscovery(
            domain_name="example.com",
            record_type=DnsRecordType.AAAA,
            values=["2001:db8::1"],
            ttl=3600,
            discovered_at=datetime.now(),
        )

        assert_that(discovery.record_type).is_equal_to(DnsRecordType.AAAA)

    def test_create_dns_record_discovery_with_cname(self) -> None:
        discovery = DnsRecordDiscovery(
            domain_name="www.example.com",
            record_type=DnsRecordType.CNAME,
            values=["example.com"],
            ttl=3600,
            discovered_at=datetime.now(),
        )

        assert_that(discovery.values).is_equal_to(["example.com"])

    def test_create_dns_record_discovery_with_mx_record(self) -> None:
        discovery = DnsRecordDiscovery(
            domain_name="example.com",
            record_type=DnsRecordType.MX,
            values=["mail.example.com"],
            ttl=3600,
            discovered_at=datetime.now(),
        )

        assert_that(discovery.record_type).is_equal_to(DnsRecordType.MX)

    def test_create_dns_record_discovery_with_multiple_values(self) -> None:
        discovery = DnsRecordDiscovery(
            domain_name="example.com",
            record_type=DnsRecordType.A,
            values=["192.168.1.1", "192.168.1.2", "192.168.1.3"],
            ttl=3600,
            discovered_at=datetime.now(),
        )

        assert_that(discovery.values).is_length(3)

    def test_create_dns_record_discovery_with_none_ttl(self) -> None:
        discovery = DnsRecordDiscovery(
            domain_name="example.com",
            record_type=DnsRecordType.A,
            values=["192.168.1.1"],
            ttl=None,
            discovered_at=datetime.now(),
        )

        assert_that(discovery.ttl).is_none()


class TestDnsRecordDiscoveryDomainValidation:
    def test_domain_name_cannot_be_empty(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            DnsRecordDiscovery(
                domain_name="",
                record_type=DnsRecordType.A,
                values=["192.168.1.1"],
                discovered_at=datetime.now(),
            )

        assert_that(str(exc_info.value)).contains("Domain name cannot be empty")

    def test_domain_name_cannot_be_whitespace_only(self) -> None:
        with pytest.raises(ValueError):
            DnsRecordDiscovery(
                domain_name="   ",
                record_type=DnsRecordType.A,
                values=["192.168.1.1"],
                discovered_at=datetime.now(),
            )

    def test_domain_name_is_lowercased(self) -> None:
        discovery = DnsRecordDiscovery(
            domain_name="EXAMPLE.COM",
            record_type=DnsRecordType.A,
            values=["192.168.1.1"],
            discovered_at=datetime.now(),
        )

        assert_that(discovery.domain_name).is_equal_to("example.com")

    def test_domain_name_whitespace_is_stripped(self) -> None:
        discovery = DnsRecordDiscovery(
            domain_name="  example.com  ",
            record_type=DnsRecordType.A,
            values=["192.168.1.1"],
            discovered_at=datetime.now(),
        )

        assert_that(discovery.domain_name).is_equal_to("example.com")


class TestDnsRecordDiscoveryValuesValidation:
    def test_values_cannot_be_empty_list(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            DnsRecordDiscovery(
                domain_name="example.com",
                record_type=DnsRecordType.A,
                values=[],
                discovered_at=datetime.now(),
            )

        assert_that(str(exc_info.value)).contains("Values list cannot be empty")

    def test_values_whitespace_is_stripped(self) -> None:
        discovery = DnsRecordDiscovery(
            domain_name="example.com",
            record_type=DnsRecordType.A,
            values=["  192.168.1.1  ", "192.168.1.2"],
            discovered_at=datetime.now(),
        )

        assert_that(discovery.values[0]).is_equal_to("192.168.1.1")

    def test_empty_string_values_are_filtered(self) -> None:
        discovery = DnsRecordDiscovery(
            domain_name="example.com",
            record_type=DnsRecordType.A,
            values=["192.168.1.1", "  ", "192.168.1.2"],
            discovered_at=datetime.now(),
        )

        assert_that(discovery.values).is_length(2)


class TestDnsRecordDiscoveryTtlValidation:
    def test_ttl_cannot_be_negative(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            DnsRecordDiscovery(
                domain_name="example.com",
                record_type=DnsRecordType.A,
                values=["192.168.1.1"],
                ttl=-1,
                discovered_at=datetime.now(),
            )

        assert_that(str(exc_info.value)).contains("TTL cannot be negative")

    def test_ttl_zero_is_valid(self) -> None:
        discovery = DnsRecordDiscovery(
            domain_name="example.com",
            record_type=DnsRecordType.A,
            values=["192.168.1.1"],
            ttl=0,
            discovered_at=datetime.now(),
        )

        assert_that(discovery.ttl).is_equal_to(0)

    def test_ttl_large_value_is_valid(self) -> None:
        discovery = DnsRecordDiscovery(
            domain_name="example.com",
            record_type=DnsRecordType.A,
            values=["192.168.1.1"],
            ttl=86400,
            discovered_at=datetime.now(),
        )

        assert_that(discovery.ttl).is_equal_to(86400)


class TestDnsRecordTypeEnum:
    def test_dns_record_type_a(self) -> None:
        assert_that(DnsRecordType.A.value).is_equal_to("A")

    def test_dns_record_type_aaaa(self) -> None:
        assert_that(DnsRecordType.AAAA.value).is_equal_to("AAAA")

    def test_dns_record_type_cname(self) -> None:
        assert_that(DnsRecordType.CNAME.value).is_equal_to("CNAME")

    def test_dns_record_type_mx(self) -> None:
        assert_that(DnsRecordType.MX.value).is_equal_to("MX")

    def test_dns_record_type_ns(self) -> None:
        assert_that(DnsRecordType.NS.value).is_equal_to("NS")

    def test_dns_record_type_soa(self) -> None:
        assert_that(DnsRecordType.SOA.value).is_equal_to("SOA")

    def test_dns_record_type_txt(self) -> None:
        assert_that(DnsRecordType.TXT.value).is_equal_to("TXT")
