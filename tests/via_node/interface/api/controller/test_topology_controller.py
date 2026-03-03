from datetime import datetime
from unittest.mock import MagicMock

import pytest
from assertpy import assert_that
from fastapi import status
from fastapi.testclient import TestClient
from lagom import Container

from via_node.application.use_case.add_dns_resolves_to_host_edge_use_case import (
    AddDnsResolvesToHostEdgeUseCase,
)
from via_node.application.use_case.add_domain_port_edge_use_case import AddDomainPortEdgeUseCase
from via_node.application.use_case.add_host_use_case import AddHostUseCase
from via_node.domain.model.dns_record import DnsRecord
from via_node.domain.model.host import Host
from via_node.domain.model.network_topology_edge import NetworkTopologyEdge
from via_node.domain.model.port import Port
from via_node.domain.repository.network_topology_repository import NetworkTopologyRepository
from via_node.interface.api.controller.topology_controller import (
    TopologyController,
    create_topology_controller,
)


@pytest.fixture
def mock_add_host_use_case() -> MagicMock:
    return MagicMock(spec=AddHostUseCase)


@pytest.fixture
def mock_add_domain_port_edge_use_case() -> MagicMock:
    return MagicMock(spec=AddDomainPortEdgeUseCase)


@pytest.fixture
def mock_add_dns_resolves_to_host_edge_use_case() -> MagicMock:
    return MagicMock(spec=AddDnsResolvesToHostEdgeUseCase)


@pytest.fixture
def mock_network_topology_repository() -> MagicMock:
    return MagicMock(spec=NetworkTopologyRepository)


@pytest.fixture
def topology_controller(
    mock_add_host_use_case: MagicMock,
    mock_add_domain_port_edge_use_case: MagicMock,
    mock_add_dns_resolves_to_host_edge_use_case: MagicMock,
    mock_network_topology_repository: MagicMock,
) -> TopologyController:
    return TopologyController(
        add_host_use_case=mock_add_host_use_case,
        add_domain_port_edge_use_case=mock_add_domain_port_edge_use_case,
        add_dns_resolves_to_host_edge_use_case=mock_add_dns_resolves_to_host_edge_use_case,
        network_topology_repository=mock_network_topology_repository,
        authentication_dependency=None,
    )


@pytest.fixture
def test_client(topology_controller: TopologyController) -> TestClient:
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(topology_controller.router)
    return TestClient(app)


class TestCreateHost:
    def test_create_host_returns_201_with_location_header(
        self,
        test_client: TestClient,
        mock_add_host_use_case: MagicMock,
    ) -> None:
        sample_host = Host(
            ip_address="192.168.1.1",
            hostname="test.example.com",
            os_type="Linux",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_add_host_use_case.execute.return_value = sample_host

        response = test_client.post(
            "/api/v1/hosts",
            json={
                "ip_address": "192.168.1.1",
                "hostname": "test.example.com",
                "os_type": "Linux",
            },
        )

        assert_that(response.status_code).is_equal_to(status.HTTP_201_CREATED)
        assert_that(response.headers.get("Location")).is_equal_to("/api/v1/hosts/192.168.1.1")

    def test_create_host_calls_use_case_with_correct_parameters(
        self,
        test_client: TestClient,
        mock_add_host_use_case: MagicMock,
    ) -> None:
        sample_host = Host(
            ip_address="192.168.1.1",
            hostname="test.example.com",
            os_type="Linux",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_add_host_use_case.execute.return_value = sample_host

        test_client.post(
            "/api/v1/hosts",
            json={
                "ip_address": "192.168.1.1",
                "hostname": "test.example.com",
                "os_type": "Linux",
                "metadata": {"key": "value"},
            },
        )

        mock_add_host_use_case.execute.assert_called_once_with(
            ip_address="192.168.1.1",
            hostname="test.example.com",
            os_type="Linux",
            metadata={"key": "value"},
        )

    def test_create_host_returns_400_on_validation_error(
        self,
        test_client: TestClient,
        mock_add_host_use_case: MagicMock,
    ) -> None:
        mock_add_host_use_case.execute.side_effect = ValueError("Invalid IP address")

        response = test_client.post(
            "/api/v1/hosts",
            json={
                "ip_address": "invalid-ip",
                "hostname": "test.example.com",
                "os_type": "Linux",
            },
        )

        assert_that(response.status_code).is_equal_to(status.HTTP_400_BAD_REQUEST)
        assert_that(response.json()["detail"]).contains("Invalid IP address")

    def test_create_host_returns_500_on_unexpected_error(
        self,
        test_client: TestClient,
        mock_add_host_use_case: MagicMock,
    ) -> None:
        mock_add_host_use_case.execute.side_effect = Exception("Database error")

        response = test_client.post(
            "/api/v1/hosts",
            json={
                "ip_address": "192.168.1.1",
                "hostname": "test.example.com",
                "os_type": "Linux",
            },
        )

        assert_that(response.status_code).is_equal_to(status.HTTP_500_INTERNAL_SERVER_ERROR)


class TestGetHost:
    def test_get_host_returns_host_when_found(
        self,
        test_client: TestClient,
        mock_network_topology_repository: MagicMock,
    ) -> None:
        sample_host = Host(
            ip_address="192.168.1.1",
            hostname="test.example.com",
            os_type="Linux",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_network_topology_repository.get_host.return_value = sample_host

        response = test_client.get("/api/v1/hosts/192.168.1.1")

        assert_that(response.status_code).is_equal_to(status.HTTP_200_OK)
        data = response.json()
        assert_that(data["ip_address"]).is_equal_to("192.168.1.1")
        assert_that(data["hostname"]).is_equal_to("test.example.com")
        assert_that(data["os_type"]).is_equal_to("Linux")

    def test_get_host_calls_repository_with_correct_ip(
        self,
        test_client: TestClient,
        mock_network_topology_repository: MagicMock,
    ) -> None:
        sample_host = Host(
            ip_address="192.168.1.1",
            hostname="test.example.com",
            os_type="Linux",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_network_topology_repository.get_host.return_value = sample_host

        test_client.get("/api/v1/hosts/192.168.1.1")

        mock_network_topology_repository.get_host.assert_called_once_with("192.168.1.1")

    def test_get_host_returns_404_when_host_not_found(
        self,
        test_client: TestClient,
        mock_network_topology_repository: MagicMock,
    ) -> None:
        mock_network_topology_repository.get_host.return_value = None

        response = test_client.get("/api/v1/hosts/192.168.1.1")

        assert_that(response.status_code).is_equal_to(status.HTTP_404_NOT_FOUND)
        assert_that(response.json()["detail"]).contains("not found")

    def test_get_host_returns_500_on_unexpected_error(
        self,
        test_client: TestClient,
        mock_network_topology_repository: MagicMock,
    ) -> None:
        mock_network_topology_repository.get_host.side_effect = Exception("Database error")

        response = test_client.get("/api/v1/hosts/192.168.1.1")

        assert_that(response.status_code).is_equal_to(status.HTTP_500_INTERNAL_SERVER_ERROR)


class TestCreateDomainPortEdge:
    def test_create_domain_port_edge_returns_201(
        self,
        test_client: TestClient,
        mock_add_domain_port_edge_use_case: MagicMock,
    ) -> None:
        sample_edge = NetworkTopologyEdge(
            source_id="example.com",
            target_id="443/TCP",
            edge_type="domain_to_port",
            metadata={},
            created_at=datetime.now(),
        )
        mock_add_domain_port_edge_use_case.execute.return_value = sample_edge

        response = test_client.post(
            "/api/v1/edges/domain-port",
            json={"domain_name": "example.com", "port_number": 443, "protocol": "TCP"},
        )

        assert_that(response.status_code).is_equal_to(status.HTTP_201_CREATED)
        assert_that(response.headers.get("Location")).contains("example.com")

    def test_create_domain_port_edge_calls_use_case_with_correct_parameters(
        self,
        test_client: TestClient,
        mock_add_domain_port_edge_use_case: MagicMock,
    ) -> None:
        sample_edge = NetworkTopologyEdge(
            source_id="example.com",
            target_id="443/TCP",
            edge_type="domain_to_port",
            metadata={},
            created_at=datetime.now(),
        )
        mock_add_domain_port_edge_use_case.execute.return_value = sample_edge

        test_client.post(
            "/api/v1/edges/domain-port",
            json={"domain_name": "example.com", "port_number": 443, "protocol": "TCP"},
        )

        mock_add_domain_port_edge_use_case.execute.assert_called_once_with(
            domain_name="example.com",
            port_number=443,
            protocol="TCP",
        )

    def test_create_domain_port_edge_returns_400_on_validation_error(
        self,
        test_client: TestClient,
        mock_add_domain_port_edge_use_case: MagicMock,
    ) -> None:
        mock_add_domain_port_edge_use_case.execute.side_effect = ValueError("Invalid port")

        response = test_client.post(
            "/api/v1/edges/domain-port",
            json={"domain_name": "example.com", "port_number": 443, "protocol": "TCP"},
        )

        assert_that(response.status_code).is_equal_to(status.HTTP_400_BAD_REQUEST)


class TestCreateDnsResolvesToHostEdge:
    def test_create_dns_resolves_to_host_edge_returns_201(
        self,
        test_client: TestClient,
        mock_add_dns_resolves_to_host_edge_use_case: MagicMock,
    ) -> None:
        sample_edge = NetworkTopologyEdge(
            source_id="example.com",
            target_id="192.168.1.1",
            edge_type="dns_resolves_to_host",
            metadata={},
            created_at=datetime.now(),
        )
        mock_add_dns_resolves_to_host_edge_use_case.execute.return_value = sample_edge

        response = test_client.post(
            "/api/v1/edges/dns-resolves-to-host",
            json={"domain_name": "example.com", "ip_address": "192.168.1.1"},
        )

        assert_that(response.status_code).is_equal_to(status.HTTP_201_CREATED)
        assert_that(response.headers.get("Location")).contains("example.com")

    def test_create_dns_resolves_to_host_edge_calls_use_case_with_correct_parameters(
        self,
        test_client: TestClient,
        mock_add_dns_resolves_to_host_edge_use_case: MagicMock,
    ) -> None:
        sample_edge = NetworkTopologyEdge(
            source_id="example.com",
            target_id="192.168.1.1",
            edge_type="dns_resolves_to_host",
            metadata={},
            created_at=datetime.now(),
        )
        mock_add_dns_resolves_to_host_edge_use_case.execute.return_value = sample_edge

        test_client.post(
            "/api/v1/edges/dns-resolves-to-host",
            json={"domain_name": "example.com", "ip_address": "192.168.1.1"},
        )

        mock_add_dns_resolves_to_host_edge_use_case.execute.assert_called_once_with(
            domain_name="example.com",
            ip_address="192.168.1.1",
        )

    def test_create_dns_resolves_to_host_edge_returns_400_on_validation_error(
        self,
        test_client: TestClient,
        mock_add_dns_resolves_to_host_edge_use_case: MagicMock,
    ) -> None:
        mock_add_dns_resolves_to_host_edge_use_case.execute.side_effect = ValueError("DNS record not found")

        response = test_client.post(
            "/api/v1/edges/dns-resolves-to-host",
            json={"domain_name": "nonexistent.com", "ip_address": "192.168.1.1"},
        )

        assert_that(response.status_code).is_equal_to(status.HTTP_400_BAD_REQUEST)


class TestGetPort:
    def test_get_port_returns_port_when_found(
        self,
        test_client: TestClient,
        mock_network_topology_repository: MagicMock,
    ) -> None:
        sample_port = Port(
            port_number=443,
            protocol="TCP",
            service_name="HTTPS",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_network_topology_repository.get_port.return_value = sample_port

        response = test_client.get("/api/v1/ports/443/TCP")

        assert_that(response.status_code).is_equal_to(status.HTTP_200_OK)
        data = response.json()
        assert_that(data["port_number"]).is_equal_to(443)
        assert_that(data["protocol"]).is_equal_to("TCP")
        assert_that(data["service_name"]).is_equal_to("HTTPS")

    def test_get_port_calls_repository_with_correct_parameters(
        self,
        test_client: TestClient,
        mock_network_topology_repository: MagicMock,
    ) -> None:
        sample_port = Port(
            port_number=443,
            protocol="TCP",
            service_name="HTTPS",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_network_topology_repository.get_port.return_value = sample_port

        test_client.get("/api/v1/ports/443/TCP")

        mock_network_topology_repository.get_port.assert_called_once_with(443, "TCP")

    def test_get_port_returns_404_when_port_not_found(
        self,
        test_client: TestClient,
        mock_network_topology_repository: MagicMock,
    ) -> None:
        mock_network_topology_repository.get_port.return_value = None

        response = test_client.get("/api/v1/ports/443/TCP")

        assert_that(response.status_code).is_equal_to(status.HTTP_404_NOT_FOUND)
        assert_that(response.json()["detail"]).contains("not found")


class TestGetDnsRecord:
    def test_get_dns_record_returns_dns_record_when_found(
        self,
        test_client: TestClient,
        mock_network_topology_repository: MagicMock,
    ) -> None:
        sample_dns_record = DnsRecord(
            domain_name="example.com",
            record_type="A",
            ip_addresses=["192.168.1.1", "192.168.1.2"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_network_topology_repository.get_dns_record.return_value = sample_dns_record

        response = test_client.get("/api/v1/dns-records/example.com")

        assert_that(response.status_code).is_equal_to(status.HTTP_200_OK)
        data = response.json()
        assert_that(data["domain_name"]).is_equal_to("example.com")
        assert_that(data["record_type"]).is_equal_to("A")
        assert_that(data["ip_addresses"]).is_length(2)

    def test_get_dns_record_calls_repository_with_correct_domain(
        self,
        test_client: TestClient,
        mock_network_topology_repository: MagicMock,
    ) -> None:
        sample_dns_record = DnsRecord(
            domain_name="example.com",
            record_type="A",
            ip_addresses=["192.168.1.1"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_network_topology_repository.get_dns_record.return_value = sample_dns_record

        test_client.get("/api/v1/dns-records/example.com")

        mock_network_topology_repository.get_dns_record.assert_called_once_with("example.com")

    def test_get_dns_record_returns_404_when_not_found(
        self,
        test_client: TestClient,
        mock_network_topology_repository: MagicMock,
    ) -> None:
        mock_network_topology_repository.get_dns_record.return_value = None

        response = test_client.get("/api/v1/dns-records/example.com")

        assert_that(response.status_code).is_equal_to(status.HTTP_404_NOT_FOUND)
        assert_that(response.json()["detail"]).contains("not found")

    def test_get_dns_record_returns_500_on_unexpected_error(
        self,
        test_client: TestClient,
        mock_network_topology_repository: MagicMock,
    ) -> None:
        mock_network_topology_repository.get_dns_record.side_effect = Exception("Database error")

        response = test_client.get("/api/v1/dns-records/example.com")

        assert_that(response.status_code).is_equal_to(status.HTTP_500_INTERNAL_SERVER_ERROR)


class TestCreateDomainPortEdgeErrorHandling:
    def test_create_domain_port_edge_returns_500_on_unexpected_error(
        self,
        test_client: TestClient,
        mock_add_domain_port_edge_use_case: MagicMock,
    ) -> None:
        mock_add_domain_port_edge_use_case.execute.side_effect = Exception("Database error")

        response = test_client.post(
            "/api/v1/edges/domain-port",
            json={"domain_name": "example.com", "port_number": 443, "protocol": "TCP"},
        )

        assert_that(response.status_code).is_equal_to(status.HTTP_500_INTERNAL_SERVER_ERROR)


class TestCreateDnsResolvesToHostEdgeErrorHandling:
    def test_create_dns_resolves_to_host_edge_returns_500_on_unexpected_error(
        self,
        test_client: TestClient,
        mock_add_dns_resolves_to_host_edge_use_case: MagicMock,
    ) -> None:
        mock_add_dns_resolves_to_host_edge_use_case.execute.side_effect = Exception("Database error")

        response = test_client.post(
            "/api/v1/edges/dns-resolves-to-host",
            json={"domain_name": "example.com", "ip_address": "192.168.1.1"},
        )

        assert_that(response.status_code).is_equal_to(status.HTTP_500_INTERNAL_SERVER_ERROR)


class TestGetPortErrorHandling:
    def test_get_port_returns_500_on_unexpected_error(
        self,
        test_client: TestClient,
        mock_network_topology_repository: MagicMock,
    ) -> None:
        mock_network_topology_repository.get_port.side_effect = Exception("Database error")

        response = test_client.get("/api/v1/ports/443/TCP")

        assert_that(response.status_code).is_equal_to(status.HTTP_500_INTERNAL_SERVER_ERROR)


class TestCreateTopologyController:
    def test_create_topology_controller_returns_controller_instance(self) -> None:
        container = Container()
        mock_add_host_use_case = MagicMock(spec=AddHostUseCase)
        mock_add_domain_port_edge_use_case = MagicMock(spec=AddDomainPortEdgeUseCase)
        mock_add_dns_resolves_to_host_edge_use_case = MagicMock(spec=AddDnsResolvesToHostEdgeUseCase)
        mock_repository = MagicMock(spec=NetworkTopologyRepository)

        container[AddHostUseCase] = lambda: mock_add_host_use_case
        container[AddDomainPortEdgeUseCase] = lambda: mock_add_domain_port_edge_use_case
        container[AddDnsResolvesToHostEdgeUseCase] = lambda: mock_add_dns_resolves_to_host_edge_use_case
        container[NetworkTopologyRepository] = lambda: mock_repository  # type: ignore[type-abstract]

        controller = create_topology_controller(container)

        assert_that(controller).is_instance_of(TopologyController)
        assert_that(controller.add_host_use_case).is_equal_to(mock_add_host_use_case)
        assert_that(controller.add_domain_port_edge_use_case).is_equal_to(mock_add_domain_port_edge_use_case)
        assert_that(controller.add_dns_resolves_to_host_edge_use_case).is_equal_to(
            mock_add_dns_resolves_to_host_edge_use_case
        )
        assert_that(controller.network_topology_repository).is_equal_to(mock_repository)
