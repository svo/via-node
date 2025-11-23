from datetime import datetime

from via_node.domain.model.dns_record import DnsRecord
from via_node.domain.model.network_topology_edge import NetworkTopologyEdge
from via_node.domain.model.port import Port
from via_node.domain.repository.network_topology_repository import NetworkTopologyRepository


class AddDomainPortEdgeUseCase:
    def __init__(self, repository: NetworkTopologyRepository) -> None:
        self._repository = repository

    def execute(self, domain_name: str, port_number: int, protocol: str = "TCP") -> NetworkTopologyEdge:
        current_time = datetime.now()

        dns_record = self._create_or_update_dns_record(domain_name, current_time)
        port = self._create_or_update_port(port_number, protocol, current_time)
        edge = self._create_edge(dns_record, port, current_time)

        return edge

    def _create_or_update_dns_record(self, domain_name: str, current_time: datetime) -> DnsRecord:
        existing_record = self._repository.get_dns_record(domain_name)

        if existing_record:
            existing_record.updated_at = current_time
            return self._repository.create_or_update_dns_record(existing_record)

        dns_record = DnsRecord(
            domain_name=domain_name,
            record_type="A",
            ip_addresses=[],
            created_at=current_time,
            updated_at=current_time,
        )

        return self._repository.create_or_update_dns_record(dns_record)

    def _create_or_update_port(self, port_number: int, protocol: str, current_time: datetime) -> Port:
        existing_port = self._repository.get_port(port_number, protocol)

        if existing_port:
            existing_port.updated_at = current_time
            return self._repository.create_or_update_port(existing_port)

        port = Port(
            port_number=port_number,
            protocol=protocol,
            service_name=None,
            created_at=current_time,
            updated_at=current_time,
        )

        return self._repository.create_or_update_port(port)

    def _create_edge(self, dns_record: DnsRecord, port: Port, current_time: datetime) -> NetworkTopologyEdge:
        edge = NetworkTopologyEdge(
            source_id=dns_record.domain_name,
            target_id=f"{port.port_number}_{port.protocol}",
            edge_type="domain_to_port",
            metadata={},
            created_at=current_time,
        )

        return self._repository.create_edge(edge)
