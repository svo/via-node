from datetime import datetime
from unittest.mock import MagicMock

import pytest
from assertpy import assert_that
from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient
from lagom import Container

from via_node.application.use_case.discover_dns_records_use_case import DiscoverDnsRecordsUseCase
from via_node.application.use_case.discover_subdomains_use_case import DiscoverSubdomainsUseCase
from via_node.domain.model.dns_record_discovery import DnsRecordDiscovery, DnsRecordType
from via_node.interface.api.controller.discovery_controller import (
    DiscoveryController,
    create_discovery_controller,
)


@pytest.fixture
def mock_discover_dns_records_use_case() -> MagicMock:
    return MagicMock(spec=DiscoverDnsRecordsUseCase)


@pytest.fixture
def mock_discover_subdomains_use_case() -> MagicMock:
    return MagicMock(spec=DiscoverSubdomainsUseCase)


@pytest.fixture
def discovery_controller(
    mock_discover_dns_records_use_case: MagicMock,
    mock_discover_subdomains_use_case: MagicMock,
) -> DiscoveryController:
    return DiscoveryController(
        discover_dns_records_use_case=mock_discover_dns_records_use_case,
        discover_subdomains_use_case=mock_discover_subdomains_use_case,
        authentication_dependency=None,
    )


@pytest.fixture
def test_client(discovery_controller: DiscoveryController) -> TestClient:
    app = FastAPI()
    app.include_router(discovery_controller.router)
    return TestClient(app)


class TestDiscoverDns:
    def test_discover_dns_returns_200_with_discoveries(
        self,
        test_client: TestClient,
        mock_discover_dns_records_use_case: MagicMock,
    ) -> None:
        sample_discovery = DnsRecordDiscovery(
            domain_name="example.com",
            record_type=DnsRecordType.A,
            values=["192.168.1.1"],
            ttl=300,
            discovered_at=datetime.now(),
        )
        mock_discover_dns_records_use_case.execute.return_value = [sample_discovery]

        response = test_client.post(
            "/api/v1/discover/dns",
            json={"domain_name": "example.com"},
        )

        assert_that(response.status_code).is_equal_to(status.HTTP_200_OK)

    def test_discover_dns_returns_correct_domain_name(
        self,
        test_client: TestClient,
        mock_discover_dns_records_use_case: MagicMock,
    ) -> None:
        sample_discovery = DnsRecordDiscovery(
            domain_name="example.com",
            record_type=DnsRecordType.A,
            values=["192.168.1.1"],
            ttl=300,
            discovered_at=datetime.now(),
        )
        mock_discover_dns_records_use_case.execute.return_value = [sample_discovery]

        response = test_client.post(
            "/api/v1/discover/dns",
            json={"domain_name": "example.com"},
        )

        data = response.json()
        assert_that(data["discoveries"][0]["domain_name"]).is_equal_to("example.com")

    def test_discover_dns_returns_correct_record_type(
        self,
        test_client: TestClient,
        mock_discover_dns_records_use_case: MagicMock,
    ) -> None:
        sample_discovery = DnsRecordDiscovery(
            domain_name="example.com",
            record_type=DnsRecordType.A,
            values=["192.168.1.1"],
            ttl=300,
            discovered_at=datetime.now(),
        )
        mock_discover_dns_records_use_case.execute.return_value = [sample_discovery]

        response = test_client.post(
            "/api/v1/discover/dns",
            json={"domain_name": "example.com"},
        )

        data = response.json()
        assert_that(data["discoveries"][0]["record_type"]).is_equal_to("A")

    def test_discover_dns_calls_use_case_with_correct_domain_name(
        self,
        test_client: TestClient,
        mock_discover_dns_records_use_case: MagicMock,
    ) -> None:
        mock_discover_dns_records_use_case.execute.return_value = []

        test_client.post(
            "/api/v1/discover/dns",
            json={"domain_name": "example.com"},
        )

        mock_discover_dns_records_use_case.execute.assert_called_once_with(
            domain_name="example.com",
            record_types=None,
        )

    def test_discover_dns_calls_use_case_with_record_types(
        self,
        test_client: TestClient,
        mock_discover_dns_records_use_case: MagicMock,
    ) -> None:
        mock_discover_dns_records_use_case.execute.return_value = []

        test_client.post(
            "/api/v1/discover/dns",
            json={"domain_name": "example.com", "record_types": ["A", "AAAA"]},
        )

        mock_discover_dns_records_use_case.execute.assert_called_once_with(
            domain_name="example.com",
            record_types=[DnsRecordType.A, DnsRecordType.AAAA],
        )

    def test_discover_dns_returns_400_on_validation_error(
        self,
        test_client: TestClient,
        mock_discover_dns_records_use_case: MagicMock,
    ) -> None:
        mock_discover_dns_records_use_case.execute.side_effect = ValueError("Domain name cannot be empty")

        response = test_client.post(
            "/api/v1/discover/dns",
            json={"domain_name": ""},
        )

        assert_that(response.status_code).is_equal_to(status.HTTP_400_BAD_REQUEST)
        assert_that(response.json()["detail"]).contains("Domain name cannot be empty")

    def test_discover_dns_returns_400_on_invalid_record_type(
        self,
        test_client: TestClient,
        mock_discover_dns_records_use_case: MagicMock,
    ) -> None:
        response = test_client.post(
            "/api/v1/discover/dns",
            json={"domain_name": "example.com", "record_types": ["INVALID"]},
        )

        assert_that(response.status_code).is_equal_to(status.HTTP_400_BAD_REQUEST)
        assert_that(response.json()["detail"]).contains("Invalid DNS record type")

    def test_discover_dns_returns_500_on_unexpected_error(
        self,
        test_client: TestClient,
        mock_discover_dns_records_use_case: MagicMock,
    ) -> None:
        mock_discover_dns_records_use_case.execute.side_effect = Exception("Network error")

        response = test_client.post(
            "/api/v1/discover/dns",
            json={"domain_name": "example.com"},
        )

        assert_that(response.status_code).is_equal_to(status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_discover_dns_returns_empty_list_when_no_records_found(
        self,
        test_client: TestClient,
        mock_discover_dns_records_use_case: MagicMock,
    ) -> None:
        mock_discover_dns_records_use_case.execute.return_value = []

        response = test_client.post(
            "/api/v1/discover/dns",
            json={"domain_name": "example.com"},
        )

        assert_that(response.status_code).is_equal_to(status.HTTP_200_OK)
        assert_that(response.json()["discoveries"]).is_empty()

    def test_discover_dns_returns_multiple_discoveries(
        self,
        test_client: TestClient,
        mock_discover_dns_records_use_case: MagicMock,
    ) -> None:
        discoveries = [
            DnsRecordDiscovery(
                domain_name="example.com",
                record_type=DnsRecordType.A,
                values=["192.168.1.1"],
                ttl=300,
                discovered_at=datetime.now(),
            ),
            DnsRecordDiscovery(
                domain_name="example.com",
                record_type=DnsRecordType.MX,
                values=["mail.example.com"],
                ttl=600,
                discovered_at=datetime.now(),
            ),
        ]
        mock_discover_dns_records_use_case.execute.return_value = discoveries

        response = test_client.post(
            "/api/v1/discover/dns",
            json={"domain_name": "example.com"},
        )

        assert_that(response.json()["discoveries"]).is_length(2)


class TestDiscoverSubdomains:
    def test_discover_subdomains_returns_200_with_results(
        self,
        test_client: TestClient,
        mock_discover_subdomains_use_case: MagicMock,
    ) -> None:
        sample_discovery = DnsRecordDiscovery(
            domain_name="www.example.com",
            record_type=DnsRecordType.A,
            values=["192.168.1.1"],
            ttl=300,
            discovered_at=datetime.now(),
        )
        mock_discover_subdomains_use_case.execute.return_value = [sample_discovery]

        response = test_client.post(
            "/api/v1/discover/subdomains",
            json={"domain_name": "example.com"},
        )

        assert_that(response.status_code).is_equal_to(status.HTTP_200_OK)

    def test_discover_subdomains_returns_correct_subdomain_name(
        self,
        test_client: TestClient,
        mock_discover_subdomains_use_case: MagicMock,
    ) -> None:
        sample_discovery = DnsRecordDiscovery(
            domain_name="www.example.com",
            record_type=DnsRecordType.A,
            values=["192.168.1.1"],
            ttl=300,
            discovered_at=datetime.now(),
        )
        mock_discover_subdomains_use_case.execute.return_value = [sample_discovery]

        response = test_client.post(
            "/api/v1/discover/subdomains",
            json={"domain_name": "example.com"},
        )

        data = response.json()
        assert_that(data["subdomains"][0]["domain_name"]).is_equal_to("www.example.com")

    def test_discover_subdomains_calls_use_case_with_correct_domain(
        self,
        test_client: TestClient,
        mock_discover_subdomains_use_case: MagicMock,
    ) -> None:
        mock_discover_subdomains_use_case.execute.return_value = []

        test_client.post(
            "/api/v1/discover/subdomains",
            json={"domain_name": "example.com"},
        )

        mock_discover_subdomains_use_case.execute.assert_called_once_with(
            domain_name="example.com",
        )

    def test_discover_subdomains_returns_400_on_validation_error(
        self,
        test_client: TestClient,
        mock_discover_subdomains_use_case: MagicMock,
    ) -> None:
        mock_discover_subdomains_use_case.execute.side_effect = ValueError("Domain name cannot be empty")

        response = test_client.post(
            "/api/v1/discover/subdomains",
            json={"domain_name": ""},
        )

        assert_that(response.status_code).is_equal_to(status.HTTP_400_BAD_REQUEST)
        assert_that(response.json()["detail"]).contains("Domain name cannot be empty")

    def test_discover_subdomains_returns_500_on_unexpected_error(
        self,
        test_client: TestClient,
        mock_discover_subdomains_use_case: MagicMock,
    ) -> None:
        mock_discover_subdomains_use_case.execute.side_effect = Exception("Network error")

        response = test_client.post(
            "/api/v1/discover/subdomains",
            json={"domain_name": "example.com"},
        )

        assert_that(response.status_code).is_equal_to(status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_discover_subdomains_returns_empty_list_when_no_subdomains_found(
        self,
        test_client: TestClient,
        mock_discover_subdomains_use_case: MagicMock,
    ) -> None:
        mock_discover_subdomains_use_case.execute.return_value = []

        response = test_client.post(
            "/api/v1/discover/subdomains",
            json={"domain_name": "example.com"},
        )

        assert_that(response.status_code).is_equal_to(status.HTTP_200_OK)
        assert_that(response.json()["subdomains"]).is_empty()


class TestDiscoverDnsHttpExceptionPassthrough:
    def test_discover_dns_passes_through_http_exception(
        self,
        test_client: TestClient,
        mock_discover_dns_records_use_case: MagicMock,
    ) -> None:
        mock_discover_dns_records_use_case.execute.side_effect = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

        response = test_client.post(
            "/api/v1/discover/dns",
            json={"domain_name": "example.com"},
        )

        assert_that(response.status_code).is_equal_to(status.HTTP_403_FORBIDDEN)


class TestDiscoverSubdomainsHttpExceptionPassthrough:
    def test_discover_subdomains_passes_through_http_exception(
        self,
        test_client: TestClient,
        mock_discover_subdomains_use_case: MagicMock,
    ) -> None:
        mock_discover_subdomains_use_case.execute.side_effect = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

        response = test_client.post(
            "/api/v1/discover/subdomains",
            json={"domain_name": "example.com"},
        )

        assert_that(response.status_code).is_equal_to(status.HTTP_403_FORBIDDEN)


class TestCreateDiscoveryController:
    def test_create_discovery_controller_returns_controller_instance(self) -> None:
        container = Container()
        mock_discover_dns = MagicMock(spec=DiscoverDnsRecordsUseCase)
        mock_discover_subdomains = MagicMock(spec=DiscoverSubdomainsUseCase)

        container[DiscoverDnsRecordsUseCase] = lambda: mock_discover_dns
        container[DiscoverSubdomainsUseCase] = lambda: mock_discover_subdomains

        controller = create_discovery_controller(container)

        assert_that(controller).is_instance_of(DiscoveryController)

    def test_create_discovery_controller_sets_correct_dns_use_case(self) -> None:
        container = Container()
        mock_discover_dns = MagicMock(spec=DiscoverDnsRecordsUseCase)
        mock_discover_subdomains = MagicMock(spec=DiscoverSubdomainsUseCase)

        container[DiscoverDnsRecordsUseCase] = lambda: mock_discover_dns
        container[DiscoverSubdomainsUseCase] = lambda: mock_discover_subdomains

        controller = create_discovery_controller(container)

        assert_that(controller.discover_dns_records_use_case).is_equal_to(mock_discover_dns)

    def test_create_discovery_controller_sets_correct_subdomains_use_case(self) -> None:
        container = Container()
        mock_discover_dns = MagicMock(spec=DiscoverDnsRecordsUseCase)
        mock_discover_subdomains = MagicMock(spec=DiscoverSubdomainsUseCase)

        container[DiscoverDnsRecordsUseCase] = lambda: mock_discover_dns
        container[DiscoverSubdomainsUseCase] = lambda: mock_discover_subdomains

        controller = create_discovery_controller(container)

        assert_that(controller.discover_subdomains_use_case).is_equal_to(mock_discover_subdomains)
