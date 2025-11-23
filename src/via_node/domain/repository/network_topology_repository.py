from abc import ABC, abstractmethod
from typing import Optional

from via_node.domain.model.dns_record import DnsRecord
from via_node.domain.model.network_topology_edge import NetworkTopologyEdge
from via_node.domain.model.port import Port


class NetworkTopologyRepository(ABC):
    @abstractmethod
    def create_or_update_dns_record(self, dns_record: DnsRecord) -> DnsRecord:
        raise NotImplementedError()

    @abstractmethod
    def create_or_update_port(self, port: Port) -> Port:
        raise NotImplementedError()

    @abstractmethod
    def create_edge(self, edge: NetworkTopologyEdge) -> NetworkTopologyEdge:
        raise NotImplementedError()

    @abstractmethod
    def get_dns_record(self, domain_name: str) -> Optional[DnsRecord]:
        raise NotImplementedError()

    @abstractmethod
    def get_port(self, port_number: int, protocol: str) -> Optional[Port]:
        raise NotImplementedError()
