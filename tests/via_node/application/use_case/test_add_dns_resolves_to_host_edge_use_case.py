from datetime import datetime
from unittest.mock import MagicMock

import pytest
from assertpy import assert_that

from via_node.application.use_case.add_dns_resolves_to_host_edge_use_case import (
    AddDnsResolvesToHostEdgeUseCase,
)
from via_node.domain.model.dns_record import DnsRecord
from via_node.domain.model.host import Host
from via_node.domain.model.network_topology_edge import NetworkTopologyEdge


class TestAddDnsResolvesToHostEdgeUseCase:
    def test_execute_creates_edge_with_correct_source(self) -> None:
        repository = MagicMock()
        use_case = AddDnsResolvesToHostEdgeUseCase(repository)

        now = datetime.now()
        dns_record = DnsRecord(
            domain_name="example.com",
            record_type="A",
            ip_addresses=["192.168.1.1"],
            created_at=now,
            updated_at=now,
        )
        host = Host(
            ip_address="192.168.1.1",
            hostname="example.com",
            os_type="Linux",
            created_at=now,
            updated_at=now,
        )
        edge = NetworkTopologyEdge(
            source_id="example.com",
            target_id="192.168.1.1",
            edge_type="dns_resolves_to_host",
            metadata={},
            created_at=now,
        )

        repository.get_dns_record.return_value = dns_record
        repository.get_host.return_value = host
        repository.create_edge.return_value = edge

        result = use_case.execute(domain_name="example.com", ip_address="192.168.1.1")

        assert_that(result.source_id).is_equal_to("example.com")

    def test_execute_creates_edge_with_correct_target(self) -> None:
        repository = MagicMock()
        use_case = AddDnsResolvesToHostEdgeUseCase(repository)

        now = datetime.now()
        dns_record = DnsRecord(
            domain_name="example.com",
            record_type="A",
            ip_addresses=["192.168.1.1"],
            created_at=now,
            updated_at=now,
        )
        host = Host(
            ip_address="192.168.1.1",
            hostname="example.com",
            os_type="Linux",
            created_at=now,
            updated_at=now,
        )
        edge = NetworkTopologyEdge(
            source_id="example.com",
            target_id="192.168.1.1",
            edge_type="dns_resolves_to_host",
            metadata={},
            created_at=now,
        )

        repository.get_dns_record.return_value = dns_record
        repository.get_host.return_value = host
        repository.create_edge.return_value = edge

        result = use_case.execute(domain_name="example.com", ip_address="192.168.1.1")

        assert_that(result.target_id).is_equal_to("192.168.1.1")

    def test_execute_validates_dns_record(self) -> None:
        repository = MagicMock()
        use_case = AddDnsResolvesToHostEdgeUseCase(repository)

        now = datetime.now()
        dns_record = DnsRecord(
            domain_name="example.com",
            record_type="A",
            ip_addresses=["192.168.1.1"],
            created_at=now,
            updated_at=now,
        )
        host = Host(
            ip_address="192.168.1.1",
            hostname="example.com",
            os_type="Linux",
            created_at=now,
            updated_at=now,
        )
        edge = NetworkTopologyEdge(
            source_id="example.com",
            target_id="192.168.1.1",
            edge_type="dns_resolves_to_host",
            metadata={},
            created_at=now,
        )

        repository.get_dns_record.return_value = dns_record
        repository.get_host.return_value = host
        repository.create_edge.return_value = edge

        use_case.execute(domain_name="example.com", ip_address="192.168.1.1")

        repository.get_dns_record.assert_called_once_with("example.com")

    def test_execute_validates_host(self) -> None:
        repository = MagicMock()
        use_case = AddDnsResolvesToHostEdgeUseCase(repository)

        now = datetime.now()
        dns_record = DnsRecord(
            domain_name="example.com",
            record_type="A",
            ip_addresses=["192.168.1.1"],
            created_at=now,
            updated_at=now,
        )
        host = Host(
            ip_address="192.168.1.1",
            hostname="example.com",
            os_type="Linux",
            created_at=now,
            updated_at=now,
        )
        edge = NetworkTopologyEdge(
            source_id="example.com",
            target_id="192.168.1.1",
            edge_type="dns_resolves_to_host",
            metadata={},
            created_at=now,
        )

        repository.get_dns_record.return_value = dns_record
        repository.get_host.return_value = host
        repository.create_edge.return_value = edge

        use_case.execute(domain_name="example.com", ip_address="192.168.1.1")

        repository.get_host.assert_called_once_with("192.168.1.1")

    def test_execute_fails_if_dns_record_not_found(self) -> None:
        repository = MagicMock()
        use_case = AddDnsResolvesToHostEdgeUseCase(repository)

        repository.get_dns_record.return_value = None

        with pytest.raises(ValueError) as exc_info:
            use_case.execute(domain_name="nonexistent.com", ip_address="192.168.1.1")

        assert "DNS record" in str(exc_info.value)
        assert "not found" in str(exc_info.value)

    def test_execute_fails_if_host_not_found(self) -> None:
        repository = MagicMock()
        use_case = AddDnsResolvesToHostEdgeUseCase(repository)

        now = datetime.now()
        dns_record = DnsRecord(
            domain_name="example.com",
            record_type="A",
            ip_addresses=["192.168.1.1"],
            created_at=now,
            updated_at=now,
        )
        repository.get_dns_record.return_value = dns_record
        repository.get_host.return_value = None

        with pytest.raises(ValueError) as exc_info:
            use_case.execute(domain_name="example.com", ip_address="192.168.1.1")

        assert "Host" in str(exc_info.value)
        assert "not found" in str(exc_info.value)

    def test_execute_creates_edge_with_correct_type(self) -> None:
        repository = MagicMock()
        use_case = AddDnsResolvesToHostEdgeUseCase(repository)

        now = datetime.now()
        dns_record = DnsRecord(
            domain_name="example.com",
            record_type="A",
            ip_addresses=["192.168.1.1"],
            created_at=now,
            updated_at=now,
        )
        host = Host(
            ip_address="192.168.1.1",
            hostname="example.com",
            os_type="Linux",
            created_at=now,
            updated_at=now,
        )

        repository.get_dns_record.return_value = dns_record
        repository.get_host.return_value = host

        use_case.execute(domain_name="example.com", ip_address="192.168.1.1")

        call_args = repository.create_edge.call_args
        edge = call_args[0][0]
        assert_that(edge.edge_type).is_equal_to("dns_resolves_to_host")
