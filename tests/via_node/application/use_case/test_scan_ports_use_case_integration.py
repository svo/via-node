from datetime import datetime
from unittest.mock import MagicMock, patch

from assertpy import assert_that

from via_node.application.use_case.scan_ports_use_case import ScanPortsUseCase
from via_node.domain.model.port_scan_result import PortScanResult, PortState
from via_node.domain.repository.network_topology_repository import NetworkTopologyRepository


class TestScanPortsUseCaseIntegration:
    def test_execute_scans_ports_and_stores_results(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = ScanPortsUseCase(repository)

        expected_result = PortScanResult(
            target_ip="192.168.1.1",
            port_number=80,
            protocol="tcp",
            state=PortState.OPEN,
            service_name="http",
            scanned_at=datetime.now(),
        )
        repository.create_or_update_port_scan_result.return_value = expected_result

        with patch("via_node.application.use_case.scan_ports_use_case.nmap.PortScanner") as mock_scanner_class:
            mock_scanner = MagicMock()
            mock_scanner_class.return_value = mock_scanner

            mock_scanner.all_hosts.return_value = ["192.168.1.1"]
            mock_scanner.__getitem__.return_value.all_protocols.return_value = ["tcp"]
            mock_scanner.__getitem__.return_value.__getitem__.return_value.keys.return_value = [80]
            mock_scanner.__getitem__.return_value.__getitem__.return_value.__getitem__.return_value = {
                "state": "open",
                "name": "http",
                "version": None,
            }

            result = use_case.execute(target_ip="192.168.1.1")

            assert_that(result).is_instance_of(list)
            assert_that(result).is_length(1)

    def test_execute_handles_multiple_ports(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = ScanPortsUseCase(repository)

        def mock_port_scan_result(port_num: int) -> PortScanResult:
            return PortScanResult(
                target_ip="192.168.1.1",
                port_number=port_num,
                protocol="tcp",
                state=PortState.OPEN,
                service_name="http" if port_num == 80 else "https",
                scanned_at=datetime.now(),
            )

        repository.create_or_update_port_scan_result.side_effect = lambda x: x

        with patch("via_node.application.use_case.scan_ports_use_case.nmap.PortScanner") as mock_scanner_class:
            mock_scanner = MagicMock()
            mock_scanner_class.return_value = mock_scanner

            mock_scanner.all_hosts.return_value = ["192.168.1.1"]
            mock_scanner.__getitem__.return_value.all_protocols.return_value = ["tcp"]
            mock_scanner.__getitem__.return_value.__getitem__.return_value.keys.return_value = [80, 443]

            port_info = {
                80: {"state": "open", "name": "http", "version": None},
                443: {"state": "open", "name": "https", "version": None},
            }
            mock_scanner.__getitem__.return_value.__getitem__.return_value.__getitem__.side_effect = (
                lambda port: port_info[port]
            )

            result = use_case.execute(target_ip="192.168.1.1")

            assert_that(result).is_instance_of(list)
            assert_that(result).is_length(2)

    def test_execute_handles_mixed_port_states(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = ScanPortsUseCase(repository)

        repository.create_or_update_port_scan_result.side_effect = lambda x: x

        with patch("via_node.application.use_case.scan_ports_use_case.nmap.PortScanner") as mock_scanner_class:
            mock_scanner = MagicMock()
            mock_scanner_class.return_value = mock_scanner

            mock_scanner.all_hosts.return_value = ["192.168.1.1"]
            mock_scanner.__getitem__.return_value.all_protocols.return_value = ["tcp"]
            mock_scanner.__getitem__.return_value.__getitem__.return_value.keys.return_value = [22, 80, 443]

            port_info = {
                22: {"state": "open", "name": "ssh", "version": None},
                80: {"state": "open", "name": "http", "version": None},
                443: {"state": "closed", "name": "https", "version": None},
            }
            mock_scanner.__getitem__.return_value.__getitem__.return_value.__getitem__.side_effect = (
                lambda port: port_info[port]
            )

            result = use_case.execute(target_ip="192.168.1.1")

            assert_that(result).is_instance_of(list)
            assert_that(result).is_length(3)
            assert_that([r.state for r in result]).contains(PortState.OPEN, PortState.CLOSED)

    def test_execute_calls_repository_for_each_port(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = ScanPortsUseCase(repository)

        repository.create_or_update_port_scan_result.side_effect = lambda x: x

        with patch("via_node.application.use_case.scan_ports_use_case.nmap.PortScanner") as mock_scanner_class:
            mock_scanner = MagicMock()
            mock_scanner_class.return_value = mock_scanner

            mock_scanner.all_hosts.return_value = ["192.168.1.1"]
            mock_scanner.__getitem__.return_value.all_protocols.return_value = ["tcp"]
            mock_scanner.__getitem__.return_value.__getitem__.return_value.keys.return_value = [80, 443]

            port_info = {
                80: {"state": "open", "name": "http", "version": None},
                443: {"state": "open", "name": "https", "version": None},
            }
            mock_scanner.__getitem__.return_value.__getitem__.return_value.__getitem__.side_effect = (
                lambda port: port_info[port]
            )

            use_case.execute(target_ip="192.168.1.1")

            assert_that(repository.create_or_update_port_scan_result.call_count).is_equal_to(2)

    def test_execute_handles_udp_protocol(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = ScanPortsUseCase(repository)

        repository.create_or_update_port_scan_result.side_effect = lambda x: x

        with patch("via_node.application.use_case.scan_ports_use_case.nmap.PortScanner") as mock_scanner_class:
            mock_scanner = MagicMock()
            mock_scanner_class.return_value = mock_scanner

            mock_scanner.all_hosts.return_value = ["192.168.1.1"]
            mock_scanner.__getitem__.return_value.all_protocols.return_value = ["udp"]
            mock_scanner.__getitem__.return_value.__getitem__.return_value.keys.return_value = [53]

            port_info = {53: {"state": "open", "name": "dns", "version": None}}
            mock_scanner.__getitem__.return_value.__getitem__.return_value.__getitem__.side_effect = (
                lambda port: port_info[port]
            )

            result = use_case.execute(target_ip="192.168.1.1")

            assert_that(result).is_instance_of(list)
            assert_that(result[0].protocol).is_equal_to("udp")

    def test_execute_with_service_version(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = ScanPortsUseCase(repository)

        repository.create_or_update_port_scan_result.side_effect = lambda x: x

        with patch("via_node.application.use_case.scan_ports_use_case.nmap.PortScanner") as mock_scanner_class:
            mock_scanner = MagicMock()
            mock_scanner_class.return_value = mock_scanner

            mock_scanner.all_hosts.return_value = ["192.168.1.1"]
            mock_scanner.__getitem__.return_value.all_protocols.return_value = ["tcp"]
            mock_scanner.__getitem__.return_value.__getitem__.return_value.keys.return_value = [80]

            port_info = {80: {"state": "open", "name": "http", "version": "Apache/2.4.41"}}
            mock_scanner.__getitem__.return_value.__getitem__.return_value.__getitem__.side_effect = (
                lambda port: port_info[port]
            )

            result = use_case.execute(target_ip="192.168.1.1")

            assert_that(result[0].service_version).is_equal_to("Apache/2.4.41")

    def test_execute_with_filtered_port(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = ScanPortsUseCase(repository)

        repository.create_or_update_port_scan_result.side_effect = lambda x: x

        with patch("via_node.application.use_case.scan_ports_use_case.nmap.PortScanner") as mock_scanner_class:
            mock_scanner = MagicMock()
            mock_scanner_class.return_value = mock_scanner

            mock_scanner.all_hosts.return_value = ["192.168.1.1"]
            mock_scanner.__getitem__.return_value.all_protocols.return_value = ["tcp"]
            mock_scanner.__getitem__.return_value.__getitem__.return_value.keys.return_value = [22]

            port_info = {22: {"state": "filtered", "name": "ssh", "version": None}}
            mock_scanner.__getitem__.return_value.__getitem__.return_value.__getitem__.side_effect = (
                lambda port: port_info[port]
            )

            result = use_case.execute(target_ip="192.168.1.1")

            assert_that(result[0].state).is_equal_to(PortState.FILTERED)

    def test_execute_with_custom_port_range(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = ScanPortsUseCase(repository)

        repository.create_or_update_port_scan_result.side_effect = lambda x: x

        with patch("via_node.application.use_case.scan_ports_use_case.nmap.PortScanner") as mock_scanner_class:
            mock_scanner = MagicMock()
            mock_scanner_class.return_value = mock_scanner

            mock_scanner.all_hosts.return_value = ["192.168.1.1"]
            mock_scanner.__getitem__.return_value.all_protocols.return_value = ["tcp"]
            mock_scanner.__getitem__.return_value.__getitem__.return_value.keys.return_value = [22, 80, 443]

            port_info = {
                22: {"state": "open", "name": "ssh", "version": None},
                80: {"state": "open", "name": "http", "version": None},
                443: {"state": "open", "name": "https", "version": None},
            }
            mock_scanner.__getitem__.return_value.__getitem__.return_value.__getitem__.side_effect = (
                lambda port: port_info[port]
            )

            use_case.execute(target_ip="192.168.1.1", ports="22,80,443")

            mock_scanner.scan.assert_called_once()

    def test_create_port_scan_result_with_all_fields(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = ScanPortsUseCase(repository)

        repository.create_or_update_port_scan_result.side_effect = lambda x: x

        with patch("via_node.application.use_case.scan_ports_use_case.nmap.PortScanner") as mock_scanner_class:
            mock_scanner = MagicMock()
            mock_scanner_class.return_value = mock_scanner

            mock_scanner.all_hosts.return_value = ["192.168.1.1"]
            mock_scanner.__getitem__.return_value.all_protocols.return_value = ["tcp"]
            mock_scanner.__getitem__.return_value.__getitem__.return_value.keys.return_value = [443]

            port_info = {443: {"state": "open", "name": "https", "version": "Nginx/1.18.0"}}
            mock_scanner.__getitem__.return_value.__getitem__.return_value.__getitem__.side_effect = (
                lambda port: port_info[port]
            )

            result = use_case.execute(target_ip="192.168.1.1")

            assert_that(result[0].target_ip).is_equal_to("192.168.1.1")
            assert_that(result[0].port_number).is_equal_to(443)
            assert_that(result[0].protocol).is_equal_to("tcp")
            assert_that(result[0].state).is_equal_to(PortState.OPEN)
            assert_that(result[0].service_name).is_equal_to("https")
            assert_that(result[0].service_version).is_equal_to("Nginx/1.18.0")

    def test_execute_handles_nmap_port_scanner_error(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = ScanPortsUseCase(repository)

        with patch("via_node.application.use_case.scan_ports_use_case.nmap.PortScanner") as mock_scanner_class:
            import nmap

            mock_scanner = MagicMock()
            mock_scanner_class.return_value = mock_scanner
            mock_scanner.scan.side_effect = nmap.PortScannerError("Scan error")

            try:
                use_case.execute(target_ip="192.168.1.1")
            except ValueError as e:
                assert_that(str(e)).contains("Port scan failed")

    def test_execute_with_no_hosts_found_in_scan(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = ScanPortsUseCase(repository)

        with patch("via_node.application.use_case.scan_ports_use_case.nmap.PortScanner") as mock_scanner_class:
            mock_scanner = MagicMock()
            mock_scanner_class.return_value = mock_scanner
            mock_scanner.all_hosts.return_value = []

            try:
                use_case.execute(target_ip="192.168.1.1")
            except ValueError as e:
                assert_that(str(e)).contains("No open ports found")
