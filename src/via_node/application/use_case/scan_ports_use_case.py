from datetime import datetime
from typing import Any, List

import nmap  # type: ignore[import-untyped]

from via_node.domain.model.port_scan_result import PortScanResult, PortState
from via_node.domain.repository.network_topology_repository import NetworkTopologyRepository


class ScanPortsUseCase:
    def __init__(self, repository: NetworkTopologyRepository) -> None:
        self._repository = repository

    def execute(
        self,
        target_ip: str,
        ports: str = "1-1000",
        scan_type: str = "sT",
    ) -> List[PortScanResult]:
        self._validate_target_ip(target_ip)

        scanner = nmap.PortScanner()
        try:
            scanner.scan(target_ip, ports, arguments=f"-{scan_type}")
        except nmap.PortScannerError as e:
            raise ValueError(f"Port scan failed: {str(e)}")

        results = self._extract_scan_results(scanner, target_ip)

        for result in results:
            self._repository.create_or_update_port_scan_result(result)

        return results

    def _validate_target_ip(self, target_ip: str) -> None:
        if not target_ip or len(target_ip.strip()) == 0:
            raise ValueError("Target IP cannot be empty")

    def _extract_scan_results(self, scanner: Any, target_ip: str) -> List[PortScanResult]:
        results: List[PortScanResult] = []

        if target_ip not in scanner.all_hosts():
            return results

        host = scanner[target_ip]

        for proto in host.all_protocols():
            ports = host[proto]

            for port in ports.keys():
                port_info = ports[port]
                result = self._create_port_scan_result(target_ip, proto, port, port_info)
                results.append(result)

        return results

    def _create_port_scan_result(self, target_ip: str, protocol: str, port: int, port_info: Any) -> PortScanResult:
        state = self._map_port_state(port_info["state"])
        service_name = port_info.get("name")
        service_version = port_info.get("version")

        return PortScanResult(
            target_ip=target_ip,
            port_number=int(port),
            protocol=protocol,
            state=state,
            service_name=service_name,
            service_version=service_version,
            scanned_at=datetime.now(),
        )

    def _map_port_state(self, state_string: str) -> PortState:
        state_map = {
            "open": PortState.OPEN,
            "closed": PortState.CLOSED,
            "filtered": PortState.FILTERED,
            "unfiltered": PortState.UNFILTERED,
        }
        return state_map.get(state_string, PortState.FILTERED)
