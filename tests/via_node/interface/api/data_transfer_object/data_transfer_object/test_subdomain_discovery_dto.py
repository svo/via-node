from datetime import datetime
from unittest.mock import MagicMock

from assertpy import assert_that

from via_node.domain.model.dns_record_discovery import DnsRecordType
from via_node.interface.api.data_transfer_object.subdomain_discovery_dto import (
    SubdomainDiscoveryApiRequestDataTransferObject,
    SubdomainDiscoveryApiResponseDataTransferObject,
    SubdomainDiscoveryResultApiResponseDataTransferObject,
)


class TestSubdomainDiscoveryApiRequestDataTransferObject:
    def test_creates_request_with_domain_name(self) -> None:
        dto = SubdomainDiscoveryApiRequestDataTransferObject(domain_name="example.com")

        assert_that(dto.domain_name).is_equal_to("example.com")

    def test_creates_request_with_none_dictionary_by_default(self) -> None:
        dto = SubdomainDiscoveryApiRequestDataTransferObject(domain_name="example.com")

        assert_that(dto.dictionary).is_none()

    def test_creates_request_with_dictionary(self) -> None:
        dto = SubdomainDiscoveryApiRequestDataTransferObject(
            domain_name="example.com", dictionary=["www", "mail", "ftp"]
        )

        assert_that(dto.dictionary).is_equal_to(["www", "mail", "ftp"])


class TestSubdomainDiscoveryResultApiResponseDataTransferObject:
    def test_from_domain_model_sets_correct_domain_name(self) -> None:
        domain_model = MagicMock()
        domain_model.domain_name = "www.example.com"
        domain_model.record_type = DnsRecordType.A
        domain_model.values = ["192.168.1.1"]
        domain_model.ttl = 300
        domain_model.discovered_at = datetime.now()

        result = SubdomainDiscoveryResultApiResponseDataTransferObject.from_domain_model(domain_model)

        assert_that(result.domain_name).is_equal_to("www.example.com")

    def test_from_domain_model_sets_correct_record_type(self) -> None:
        domain_model = MagicMock()
        domain_model.domain_name = "www.example.com"
        domain_model.record_type = DnsRecordType.A
        domain_model.values = ["192.168.1.1"]
        domain_model.ttl = 300
        domain_model.discovered_at = datetime.now()

        result = SubdomainDiscoveryResultApiResponseDataTransferObject.from_domain_model(domain_model)

        assert_that(result.record_type).is_equal_to("A")

    def test_from_domain_model_sets_correct_values(self) -> None:
        domain_model = MagicMock()
        domain_model.domain_name = "www.example.com"
        domain_model.record_type = DnsRecordType.A
        domain_model.values = ["192.168.1.1", "192.168.1.2"]
        domain_model.ttl = 300
        domain_model.discovered_at = datetime.now()

        result = SubdomainDiscoveryResultApiResponseDataTransferObject.from_domain_model(domain_model)

        assert_that(result.values).is_equal_to(["192.168.1.1", "192.168.1.2"])


class TestSubdomainDiscoveryApiResponseDataTransferObject:
    def test_creates_response_with_subdomains(self) -> None:
        result = SubdomainDiscoveryResultApiResponseDataTransferObject(
            domain_name="www.example.com",
            record_type="A",
            values=["192.168.1.1"],
            ttl=300,
            discovered_at=datetime.now(),
        )

        response = SubdomainDiscoveryApiResponseDataTransferObject(subdomains=[result])

        assert_that(response.subdomains).is_length(1)

    def test_creates_response_with_empty_subdomains(self) -> None:
        response = SubdomainDiscoveryApiResponseDataTransferObject(subdomains=[])

        assert_that(response.subdomains).is_empty()
