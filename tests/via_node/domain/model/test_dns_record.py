from datetime import datetime

import pytest

from via_node.domain.model.dns_record import DnsRecord


class TestDnsRecord:
    def test_should_create_dns_record_when_all_fields_are_valid(self) -> None:
        dns_record = DnsRecord(
            domain_name="example.com",
            record_type="A",
            ip_addresses=["192.168.1.1"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert dns_record.domain_name == "example.com"

    def test_should_normalize_domain_name_to_lowercase(self) -> None:
        dns_record = DnsRecord(
            domain_name="EXAMPLE.COM",
            record_type="A",
            ip_addresses=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert dns_record.domain_name == "example.com"

    def test_should_strip_whitespace_from_domain_name(self) -> None:
        dns_record = DnsRecord(
            domain_name="  example.com  ",
            record_type="A",
            ip_addresses=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert dns_record.domain_name == "example.com"

    def test_should_raise_error_when_domain_name_is_empty(self) -> None:
        with pytest.raises(ValueError, match="Domain name cannot be empty"):
            DnsRecord(
                domain_name="",
                record_type="A",
                ip_addresses=[],
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

    def test_should_raise_error_when_domain_name_exceeds_253_characters(self) -> None:
        with pytest.raises(ValueError, match="Domain name cannot exceed 253 characters"):
            DnsRecord(
                domain_name="a" * 254,
                record_type="A",
                ip_addresses=[],
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

    def test_should_normalize_record_type_to_uppercase(self) -> None:
        dns_record = DnsRecord(
            domain_name="example.com",
            record_type="a",
            ip_addresses=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert dns_record.record_type == "A"

    def test_should_accept_valid_record_type_aaaa(self) -> None:
        dns_record = DnsRecord(
            domain_name="example.com",
            record_type="AAAA",
            ip_addresses=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert dns_record.record_type == "AAAA"

    def test_should_accept_valid_record_type_cname(self) -> None:
        dns_record = DnsRecord(
            domain_name="example.com",
            record_type="CNAME",
            ip_addresses=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert dns_record.record_type == "CNAME"

    def test_should_raise_error_when_record_type_is_invalid(self) -> None:
        with pytest.raises(ValueError, match="Record type must be one of"):
            DnsRecord(
                domain_name="example.com",
                record_type="INVALID",
                ip_addresses=[],
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

    def test_should_strip_whitespace_from_ip_addresses(self) -> None:
        dns_record = DnsRecord(
            domain_name="example.com",
            record_type="A",
            ip_addresses=["  192.168.1.1  ", "  10.0.0.1  "],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert dns_record.ip_addresses == ["192.168.1.1", "10.0.0.1"]
