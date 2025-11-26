from datetime import datetime

from via_node.domain.model.network_topology_edge import NetworkTopologyEdge
from via_node.domain.repository.network_topology_repository import NetworkTopologyRepository


class AddDnsResolvesToHostEdgeUseCase:
    def __init__(self, repository: NetworkTopologyRepository) -> None:
        self._repository = repository

    def execute(self, domain_name: str, ip_address: str) -> NetworkTopologyEdge:
        dns_record = self._repository.get_dns_record(domain_name)
        if not dns_record:
            raise ValueError(f"DNS record '{domain_name}' not found")

        host = self._repository.get_host(ip_address)
        if not host:
            raise ValueError(f"Host with IP '{ip_address}' not found")

        edge = NetworkTopologyEdge(
            source_id=domain_name,
            target_id=ip_address,
            edge_type="dns_resolves_to_host",
            metadata={},
            created_at=datetime.now(),
        )

        return self._repository.create_edge(edge)
