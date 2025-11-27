from abc import ABC, abstractmethod
from typing import List, Optional

from via_node.domain.model.dns_record import DnsRecord
from via_node.domain.model.dns_record_discovery import DnsRecordDiscovery
from via_node.domain.model.host import Host
from via_node.domain.model.network_topology_edge import NetworkTopologyEdge
from via_node.domain.model.port import Port
from via_node.domain.model.port_scan_result import PortScanResult


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

    @abstractmethod
    def create_or_update_host(self, host: Host) -> Host:
        raise NotImplementedError()

    @abstractmethod
    def get_host(self, ip_address: str) -> Optional[Host]:
        raise NotImplementedError()

    @abstractmethod
    def create_or_update_dns_record_discovery(self, dns_record_discovery: DnsRecordDiscovery) -> DnsRecordDiscovery:
        raise NotImplementedError()

    @abstractmethod
    def get_dns_record_discoveries(self, domain_name: str) -> List[DnsRecordDiscovery]:
        raise NotImplementedError()

    @abstractmethod
    def create_or_update_port_scan_result(self, port_scan_result: PortScanResult) -> PortScanResult:
        raise NotImplementedError()

    @abstractmethod
    def get_port_scan_results(self, target_ip: str) -> List[PortScanResult]:
        raise NotImplementedError()
