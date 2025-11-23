from datetime import datetime
from unittest.mock import Mock

from via_node.application.use_case.add_domain_port_edge_use_case import AddDomainPortEdgeUseCase
from via_node.domain.model.dns_record import DnsRecord
from via_node.domain.model.network_topology_edge import NetworkTopologyEdge
from via_node.domain.model.port import Port


class TestAddDomainPortEdgeUseCase:
    def test_should_create_dns_record_when_it_does_not_exist(self) -> None:
        dns_record = DnsRecord(
            domain_name="example.com",
            record_type="A",
            ip_addresses=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        port = Port(
            port_number=443,
            protocol="TCP",
            service_name=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        edge = NetworkTopologyEdge(
            source_id="example.com",
            target_id="443_TCP",
            edge_type="domain_to_port",
            metadata={},
            created_at=datetime.now(),
        )

        repository = Mock()
        repository.get_dns_record.return_value = None
        repository.create_or_update_dns_record.return_value = dns_record
        repository.get_port.return_value = None
        repository.create_or_update_port.return_value = port
        repository.create_edge.return_value = edge

        use_case = AddDomainPortEdgeUseCase(repository)
        use_case.execute("example.com", 443, "TCP")

        repository.create_or_update_dns_record.assert_called_once()

    def test_should_create_port_when_it_does_not_exist(self) -> None:
        dns_record = DnsRecord(
            domain_name="example.com",
            record_type="A",
            ip_addresses=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        port = Port(
            port_number=443,
            protocol="TCP",
            service_name=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        edge = NetworkTopologyEdge(
            source_id="example.com",
            target_id="443_TCP",
            edge_type="domain_to_port",
            metadata={},
            created_at=datetime.now(),
        )

        repository = Mock()
        repository.get_dns_record.return_value = None
        repository.create_or_update_dns_record.return_value = dns_record
        repository.get_port.return_value = None
        repository.create_or_update_port.return_value = port
        repository.create_edge.return_value = edge

        use_case = AddDomainPortEdgeUseCase(repository)
        use_case.execute("example.com", 443, "TCP")

        repository.create_or_update_port.assert_called_once()

    def test_should_create_edge_between_dns_record_and_port(self) -> None:
        dns_record = DnsRecord(
            domain_name="example.com",
            record_type="A",
            ip_addresses=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        port = Port(
            port_number=443,
            protocol="TCP",
            service_name=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        edge = NetworkTopologyEdge(
            source_id="example.com",
            target_id="443_TCP",
            edge_type="domain_to_port",
            metadata={},
            created_at=datetime.now(),
        )

        repository = Mock()
        repository.get_dns_record.return_value = None
        repository.create_or_update_dns_record.return_value = dns_record
        repository.get_port.return_value = None
        repository.create_or_update_port.return_value = port
        repository.create_edge.return_value = edge

        use_case = AddDomainPortEdgeUseCase(repository)
        use_case.execute("example.com", 443, "TCP")

        repository.create_edge.assert_called_once()

    def test_should_update_existing_dns_record_when_it_exists(self) -> None:
        existing_dns_record = DnsRecord(
            domain_name="example.com",
            record_type="A",
            ip_addresses=[],
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1),
        )
        port = Port(
            port_number=443,
            protocol="TCP",
            service_name=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        edge = NetworkTopologyEdge(
            source_id="example.com",
            target_id="443_TCP",
            edge_type="domain_to_port",
            metadata={},
            created_at=datetime.now(),
        )

        repository = Mock()
        repository.get_dns_record.return_value = existing_dns_record
        repository.create_or_update_dns_record.return_value = existing_dns_record
        repository.get_port.return_value = None
        repository.create_or_update_port.return_value = port
        repository.create_edge.return_value = edge

        use_case = AddDomainPortEdgeUseCase(repository)
        use_case.execute("example.com", 443, "TCP")

        repository.create_or_update_dns_record.assert_called_once()

    def test_should_update_existing_port_when_it_exists(self) -> None:
        existing_port = Port(
            port_number=443,
            protocol="TCP",
            service_name="https",
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1),
        )
        dns_record = DnsRecord(
            domain_name="example.com",
            record_type="A",
            ip_addresses=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        edge = NetworkTopologyEdge(
            source_id="example.com",
            target_id="443_TCP",
            edge_type="domain_to_port",
            metadata={},
            created_at=datetime.now(),
        )

        repository = Mock()
        repository.get_dns_record.return_value = None
        repository.create_or_update_dns_record.return_value = dns_record
        repository.get_port.return_value = existing_port
        repository.create_or_update_port.return_value = existing_port
        repository.create_edge.return_value = edge

        use_case = AddDomainPortEdgeUseCase(repository)
        use_case.execute("example.com", 443, "TCP")

        repository.create_or_update_port.assert_called_once()

    def test_should_return_created_edge(self) -> None:
        dns_record = DnsRecord(
            domain_name="example.com",
            record_type="A",
            ip_addresses=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        port = Port(
            port_number=443,
            protocol="TCP",
            service_name=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        expected_edge = NetworkTopologyEdge(
            source_id="example.com",
            target_id="443",
            edge_type="domain_to_port",
            metadata={},
            created_at=datetime.now(),
        )

        repository = Mock()
        repository.get_dns_record.return_value = None
        repository.create_or_update_dns_record.return_value = dns_record
        repository.get_port.return_value = None
        repository.create_or_update_port.return_value = port
        repository.create_edge.return_value = expected_edge

        use_case = AddDomainPortEdgeUseCase(repository)
        result = use_case.execute("example.com", 443, "TCP")

        assert result == expected_edge

    def test_should_use_tcp_as_default_protocol(self) -> None:
        dns_record = DnsRecord(
            domain_name="example.com",
            record_type="A",
            ip_addresses=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        port = Port(
            port_number=443,
            protocol="TCP",
            service_name=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        edge = NetworkTopologyEdge(
            source_id="example.com",
            target_id="443_TCP",
            edge_type="domain_to_port",
            metadata={},
            created_at=datetime.now(),
        )

        repository = Mock()
        repository.get_dns_record.return_value = None
        repository.create_or_update_dns_record.return_value = dns_record
        repository.get_port.return_value = None
        repository.create_or_update_port.return_value = port
        repository.create_edge.return_value = edge

        use_case = AddDomainPortEdgeUseCase(repository)
        use_case.execute("example.com", 443)

        repository.create_or_update_port.assert_called_once()

    def test_should_pass_domain_name_to_dns_record_creation(self) -> None:
        dns_record = DnsRecord(
            domain_name="example.com",
            record_type="A",
            ip_addresses=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        port = Port(
            port_number=443,
            protocol="TCP",
            service_name=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        edge = NetworkTopologyEdge(
            source_id="example.com",
            target_id="443_TCP",
            edge_type="domain_to_port",
            metadata={},
            created_at=datetime.now(),
        )

        repository = Mock()
        repository.get_dns_record.return_value = None
        repository.create_or_update_dns_record.return_value = dns_record
        repository.get_port.return_value = None
        repository.create_or_update_port.return_value = port
        repository.create_edge.return_value = edge

        use_case = AddDomainPortEdgeUseCase(repository)
        use_case.execute("example.com", 443, "TCP")

        call_args = repository.create_or_update_dns_record.call_args[0][0]
        assert call_args.domain_name == "example.com"

    def test_should_pass_port_number_to_port_creation(self) -> None:
        dns_record = DnsRecord(
            domain_name="example.com",
            record_type="A",
            ip_addresses=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        port = Port(
            port_number=443,
            protocol="TCP",
            service_name=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        edge = NetworkTopologyEdge(
            source_id="example.com",
            target_id="443_TCP",
            edge_type="domain_to_port",
            metadata={},
            created_at=datetime.now(),
        )

        repository = Mock()
        repository.get_dns_record.return_value = None
        repository.create_or_update_dns_record.return_value = dns_record
        repository.get_port.return_value = None
        repository.create_or_update_port.return_value = port
        repository.create_edge.return_value = edge

        use_case = AddDomainPortEdgeUseCase(repository)
        use_case.execute("example.com", 443, "TCP")

        call_args = repository.create_or_update_port.call_args[0][0]
        assert call_args.port_number == 443
