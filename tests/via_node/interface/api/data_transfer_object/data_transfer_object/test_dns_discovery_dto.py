from datetime import datetime
from unittest.mock import MagicMock

from assertpy import assert_that

from via_node.domain.model.dns_record_discovery import DnsRecordType
from via_node.interface.api.data_transfer_object.dns_discovery_dto import (
    DnsDiscoveryApiRequestDataTransferObject,
    DnsDiscoveryApiResponseDataTransferObject,
    DnsDiscoveryResultApiResponseDataTransferObject,
)


class TestDnsDiscoveryApiRequestDataTransferObject:
    def test_creates_request_with_domain_name(self) -> None:
        dto = DnsDiscoveryApiRequestDataTransferObject(domain_name="example.com")

        assert_that(dto.domain_name).is_equal_to("example.com")

    def test_creates_request_with_record_types(self) -> None:
        dto = DnsDiscoveryApiRequestDataTransferObject(domain_name="example.com", record_types=["A", "AAAA"])

        assert_that(dto.record_types).is_equal_to(["A", "AAAA"])

    def test_creates_request_with_none_record_types_by_default(self) -> None:
        dto = DnsDiscoveryApiRequestDataTransferObject(domain_name="example.com")

        assert_that(dto.record_types).is_none()


class TestDnsDiscoveryResultApiResponseDataTransferObject:
    def test_from_domain_model_sets_correct_domain_name(self) -> None:
        domain_model = MagicMock()
        domain_model.domain_name = "example.com"
        domain_model.record_type = DnsRecordType.A
        domain_model.values = ["192.168.1.1"]
        domain_model.ttl = 300
        domain_model.discovered_at = datetime.now()

        result = DnsDiscoveryResultApiResponseDataTransferObject.from_domain_model(domain_model)

        assert_that(result.domain_name).is_equal_to("example.com")

    def test_from_domain_model_sets_correct_record_type(self) -> None:
        domain_model = MagicMock()
        domain_model.domain_name = "example.com"
        domain_model.record_type = DnsRecordType.MX
        domain_model.values = ["mail.example.com"]
        domain_model.ttl = 600
        domain_model.discovered_at = datetime.now()

        result = DnsDiscoveryResultApiResponseDataTransferObject.from_domain_model(domain_model)

        assert_that(result.record_type).is_equal_to("MX")

    def test_from_domain_model_sets_correct_values(self) -> None:
        domain_model = MagicMock()
        domain_model.domain_name = "example.com"
        domain_model.record_type = DnsRecordType.A
        domain_model.values = ["192.168.1.1", "192.168.1.2"]
        domain_model.ttl = 300
        domain_model.discovered_at = datetime.now()

        result = DnsDiscoveryResultApiResponseDataTransferObject.from_domain_model(domain_model)

        assert_that(result.values).is_equal_to(["192.168.1.1", "192.168.1.2"])

    def test_from_domain_model_sets_correct_ttl(self) -> None:
        domain_model = MagicMock()
        domain_model.domain_name = "example.com"
        domain_model.record_type = DnsRecordType.A
        domain_model.values = ["192.168.1.1"]
        domain_model.ttl = None
        domain_model.discovered_at = datetime.now()

        result = DnsDiscoveryResultApiResponseDataTransferObject.from_domain_model(domain_model)

        assert_that(result.ttl).is_none()


class TestDnsDiscoveryApiResponseDataTransferObject:
    def test_creates_response_with_discoveries(self) -> None:
        result = DnsDiscoveryResultApiResponseDataTransferObject(
            domain_name="example.com",
            record_type="A",
            values=["192.168.1.1"],
            ttl=300,
            discovered_at=datetime.now(),
        )

        response = DnsDiscoveryApiResponseDataTransferObject(discoveries=[result])

        assert_that(response.discoveries).is_length(1)

    def test_creates_response_with_empty_discoveries(self) -> None:
        response = DnsDiscoveryApiResponseDataTransferObject(discoveries=[])

        assert_that(response.discoveries).is_empty()
