from datetime import datetime
from unittest.mock import MagicMock, patch

from click.testing import CliRunner
from assertpy import assert_that

from via_node.interface.cli.main import cli
from via_node.domain.model.dns_record_discovery import DnsRecordDiscovery, DnsRecordType


class TestDiscoverDnsCommand:
    def test_discover_dns_requires_domain_option(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["discover-dns"])

        assert_that(result.exit_code).is_not_equal_to(0)
        assert_that(result.output).contains("Missing option")

    def test_discover_dns_with_valid_domain(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
            mock_container = MagicMock()
            mock_use_case = MagicMock()

            expected_discovery = DnsRecordDiscovery(
                domain_name="example.com",
                record_type=DnsRecordType.A,
                values=["192.168.1.1"],
                ttl=3600,
                discovered_at=datetime.now(),
            )
            mock_use_case.execute.return_value = [expected_discovery]
            mock_container.__getitem__.return_value = mock_use_case
            mock_container_factory.return_value = mock_container

            result = runner.invoke(cli, ["discover-dns", "--domain", "example.com"])

            assert_that(result.exit_code).is_equal_to(0)

    def test_discover_dns_displays_results(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
            mock_container = MagicMock()
            mock_use_case = MagicMock()

            expected_discovery = DnsRecordDiscovery(
                domain_name="example.com",
                record_type=DnsRecordType.A,
                values=["192.168.1.1"],
                ttl=3600,
                discovered_at=datetime.now(),
            )
            mock_use_case.execute.return_value = [expected_discovery]
            mock_container.__getitem__.return_value = mock_use_case
            mock_container_factory.return_value = mock_container

            result = runner.invoke(cli, ["discover-dns", "--domain", "example.com"])

            assert_that(result.output).contains("Discovered")

    def test_discover_dns_displays_record_type(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
            mock_container = MagicMock()
            mock_use_case = MagicMock()

            expected_discovery = DnsRecordDiscovery(
                domain_name="example.com",
                record_type=DnsRecordType.A,
                values=["192.168.1.1"],
                ttl=3600,
                discovered_at=datetime.now(),
            )
            mock_use_case.execute.return_value = [expected_discovery]
            mock_container.__getitem__.return_value = mock_use_case
            mock_container_factory.return_value = mock_container

            result = runner.invoke(cli, ["discover-dns", "--domain", "example.com"])

            assert_that(result.output).contains("A:")

    def test_discover_dns_displays_values(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
            mock_container = MagicMock()
            mock_use_case = MagicMock()

            expected_discovery = DnsRecordDiscovery(
                domain_name="example.com",
                record_type=DnsRecordType.A,
                values=["192.168.1.1"],
                ttl=3600,
                discovered_at=datetime.now(),
            )
            mock_use_case.execute.return_value = [expected_discovery]
            mock_container.__getitem__.return_value = mock_use_case
            mock_container_factory.return_value = mock_container

            result = runner.invoke(cli, ["discover-dns", "--domain", "example.com"])

            assert_that(result.output).contains("192.168.1.1")

    def test_discover_dns_displays_ttl(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
            mock_container = MagicMock()
            mock_use_case = MagicMock()

            expected_discovery = DnsRecordDiscovery(
                domain_name="example.com",
                record_type=DnsRecordType.A,
                values=["192.168.1.1"],
                ttl=3600,
                discovered_at=datetime.now(),
            )
            mock_use_case.execute.return_value = [expected_discovery]
            mock_container.__getitem__.return_value = mock_use_case
            mock_container_factory.return_value = mock_container

            result = runner.invoke(cli, ["discover-dns", "--domain", "example.com"])

            assert_that(result.output).contains("TTL")

    def test_discover_dns_handles_validation_error(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
            mock_container = MagicMock()
            mock_use_case = MagicMock()
            mock_use_case.execute.side_effect = ValueError("Invalid domain")
            mock_container.__getitem__.return_value = mock_use_case
            mock_container_factory.return_value = mock_container

            result = runner.invoke(cli, ["discover-dns", "--domain", "example.com"])

            assert_that(result.exit_code).is_not_equal_to(0)
            assert_that(result.output).contains("Validation error")

    def test_discover_dns_handles_generic_error(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
            mock_container = MagicMock()
            mock_use_case = MagicMock()
            mock_use_case.execute.side_effect = Exception("Database error")
            mock_container.__getitem__.return_value = mock_use_case
            mock_container_factory.return_value = mock_container

            result = runner.invoke(cli, ["discover-dns", "--domain", "example.com"])

            assert_that(result.exit_code).is_not_equal_to(0)
            assert_that(result.output).contains("Error")

    def test_discover_dns_with_short_option(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
            mock_container = MagicMock()
            mock_use_case = MagicMock()

            expected_discovery = DnsRecordDiscovery(
                domain_name="example.com",
                record_type=DnsRecordType.A,
                values=["192.168.1.1"],
                ttl=3600,
                discovered_at=datetime.now(),
            )
            mock_use_case.execute.return_value = [expected_discovery]
            mock_container.__getitem__.return_value = mock_use_case
            mock_container_factory.return_value = mock_container

            result = runner.invoke(cli, ["discover-dns", "-d", "example.com"])

            assert_that(result.exit_code).is_equal_to(0)

    def test_discover_dns_with_record_type_option(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
            mock_container = MagicMock()
            mock_use_case = MagicMock()

            expected_discovery = DnsRecordDiscovery(
                domain_name="example.com",
                record_type=DnsRecordType.A,
                values=["192.168.1.1"],
                ttl=3600,
                discovered_at=datetime.now(),
            )
            mock_use_case.execute.return_value = [expected_discovery]
            mock_container.__getitem__.return_value = mock_use_case
            mock_container_factory.return_value = mock_container

            result = runner.invoke(cli, ["discover-dns", "--domain", "example.com", "--type", "A"])

            assert_that(result.exit_code).is_equal_to(0)

    def test_discover_dns_with_multiple_record_types(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
            mock_container = MagicMock()
            mock_use_case = MagicMock()

            expected_discovery = DnsRecordDiscovery(
                domain_name="example.com",
                record_type=DnsRecordType.A,
                values=["192.168.1.1"],
                ttl=3600,
                discovered_at=datetime.now(),
            )
            mock_use_case.execute.return_value = [expected_discovery]
            mock_container.__getitem__.return_value = mock_use_case
            mock_container_factory.return_value = mock_container

            result = runner.invoke(
                cli,
                [
                    "discover-dns",
                    "--domain",
                    "example.com",
                    "--type",
                    "A",
                    "--type",
                    "MX",
                ],
            )

            assert_that(result.exit_code).is_equal_to(0)

    def test_discover_dns_displays_multiple_discoveries(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
            mock_container = MagicMock()
            mock_use_case = MagicMock()

            discoveries = [
                DnsRecordDiscovery(
                    domain_name="example.com",
                    record_type=DnsRecordType.A,
                    values=["192.168.1.1"],
                    ttl=3600,
                    discovered_at=datetime.now(),
                ),
                DnsRecordDiscovery(
                    domain_name="example.com",
                    record_type=DnsRecordType.MX,
                    values=["mail.example.com"],
                    ttl=3600,
                    discovered_at=datetime.now(),
                ),
            ]
            mock_use_case.execute.return_value = discoveries
            mock_container.__getitem__.return_value = mock_use_case
            mock_container_factory.return_value = mock_container

            result = runner.invoke(cli, ["discover-dns", "--domain", "example.com"])

            assert_that(result.exit_code).is_equal_to(0)
            assert_that(result.output).contains("2")


class TestScanPortsCommand:
    def test_scan_ports_requires_target_option(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["scan-ports"])

        assert_that(result.exit_code).is_not_equal_to(0)
        assert_that(result.output).contains("Missing option")

    def test_scan_ports_with_valid_target(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
            mock_container = MagicMock()
            mock_use_case = MagicMock()

            expected_result = MagicMock()
            expected_result.target_ip = "192.168.1.1"
            expected_result.port_number = 80
            expected_result.protocol = "tcp"
            expected_result.state.value = "open"
            expected_result.service_name = "http"

            mock_use_case.execute.return_value = [expected_result]
            mock_container.__getitem__.return_value = mock_use_case
            mock_container_factory.return_value = mock_container

            result = runner.invoke(cli, ["scan-ports", "--target", "192.168.1.1"])

            assert_that(result.exit_code).is_equal_to(0)

    def test_scan_ports_displays_results(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
            mock_container = MagicMock()
            mock_use_case = MagicMock()

            expected_result = MagicMock()
            expected_result.target_ip = "192.168.1.1"
            expected_result.port_number = 80
            expected_result.protocol = "tcp"
            expected_result.state.value = "open"
            expected_result.service_name = "http"

            mock_use_case.execute.return_value = [expected_result]
            mock_container.__getitem__.return_value = mock_use_case
            mock_container_factory.return_value = mock_container

            result = runner.invoke(cli, ["scan-ports", "--target", "192.168.1.1"])

            assert_that(result.output).contains("Scanned")

    def test_scan_ports_displays_port_number(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
            mock_container = MagicMock()
            mock_use_case = MagicMock()

            expected_result = MagicMock()
            expected_result.target_ip = "192.168.1.1"
            expected_result.port_number = 443
            expected_result.protocol = "tcp"
            expected_result.state.value = "open"
            expected_result.service_name = "https"

            mock_use_case.execute.return_value = [expected_result]
            mock_container.__getitem__.return_value = mock_use_case
            mock_container_factory.return_value = mock_container

            result = runner.invoke(cli, ["scan-ports", "--target", "192.168.1.1"])

            assert_that(result.output).contains("TCP/443")

    def test_scan_ports_with_short_option(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
            mock_container = MagicMock()
            mock_use_case = MagicMock()

            expected_result = MagicMock()
            expected_result.target_ip = "192.168.1.1"
            expected_result.port_number = 80
            expected_result.protocol = "tcp"
            expected_result.state.value = "open"
            expected_result.service_name = "http"

            mock_use_case.execute.return_value = [expected_result]
            mock_container.__getitem__.return_value = mock_use_case
            mock_container_factory.return_value = mock_container

            result = runner.invoke(cli, ["scan-ports", "-t", "192.168.1.1"])

            assert_that(result.exit_code).is_equal_to(0)

    def test_scan_ports_with_ports_option(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
            mock_container = MagicMock()
            mock_use_case = MagicMock()

            expected_result = MagicMock()
            expected_result.target_ip = "192.168.1.1"
            expected_result.port_number = 80
            expected_result.protocol = "tcp"
            expected_result.state.value = "open"
            expected_result.service_name = "http"

            mock_use_case.execute.return_value = [expected_result]
            mock_container.__getitem__.return_value = mock_use_case
            mock_container_factory.return_value = mock_container

            result = runner.invoke(cli, ["scan-ports", "--target", "192.168.1.1", "--ports", "22,80,443"])

            assert_that(result.exit_code).is_equal_to(0)

    def test_scan_ports_handles_validation_error(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
            mock_container = MagicMock()
            mock_use_case = MagicMock()
            mock_use_case.execute.side_effect = ValueError("Invalid target")
            mock_container.__getitem__.return_value = mock_use_case
            mock_container_factory.return_value = mock_container

            result = runner.invoke(cli, ["scan-ports", "--target", "invalid"])

            assert_that(result.exit_code).is_not_equal_to(0)
            assert_that(result.output).contains("Validation error")

    def test_scan_ports_handles_generic_error(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
            mock_container = MagicMock()
            mock_use_case = MagicMock()
            mock_use_case.execute.side_effect = Exception("Scan error")
            mock_container.__getitem__.return_value = mock_use_case
            mock_container_factory.return_value = mock_container

            result = runner.invoke(cli, ["scan-ports", "--target", "192.168.1.1"])

            assert_that(result.exit_code).is_not_equal_to(0)
            assert_that(result.output).contains("Error")

    def test_scan_ports_displays_multiple_results(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
            mock_container = MagicMock()
            mock_use_case = MagicMock()

            results = []
            for port in [22, 80, 443]:
                result = MagicMock()
                result.target_ip = "192.168.1.1"
                result.port_number = port
                result.protocol = "tcp"
                result.state.value = "open"
                result.service_name = f"service_{port}"
                results.append(result)

            mock_use_case.execute.return_value = results
            mock_container.__getitem__.return_value = mock_use_case
            mock_container_factory.return_value = mock_container

            result = runner.invoke(cli, ["scan-ports", "--target", "192.168.1.1"])

            assert_that(result.exit_code).is_equal_to(0)
            assert_that(result.output).contains("3")

    def test_scan_ports_displays_no_open_ports_when_empty(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
            mock_container = MagicMock()
            mock_use_case = MagicMock()

            mock_use_case.execute.return_value = []
            mock_container.__getitem__.return_value = mock_use_case
            mock_container_factory.return_value = mock_container

            result = runner.invoke(cli, ["scan-ports", "--target", "192.168.1.1"])

            assert_that(result.exit_code).is_equal_to(0)
            assert_that(result.output).contains("No open ports found")


class TestDiscoverSubdomainsCommand:
    def test_discover_subdomains_requires_domain_option(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["discover-subdomains"])

        assert_that(result.exit_code).is_not_equal_to(0)
        assert_that(result.output).contains("Missing option")

    def test_discover_subdomains_with_valid_domain(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
            mock_container = MagicMock()
            mock_use_case = MagicMock()

            expected_result = MagicMock()
            expected_result.domain_name = "www.example.com"
            expected_result.values = ["192.168.1.1"]

            mock_use_case.execute.return_value = [expected_result]
            mock_container.__getitem__.return_value = mock_use_case
            mock_container_factory.return_value = mock_container

            result = runner.invoke(cli, ["discover-subdomains", "--domain", "example.com"])

            assert_that(result.exit_code).is_equal_to(0)

    def test_discover_subdomains_displays_results(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
            mock_container = MagicMock()
            mock_use_case = MagicMock()

            expected_result = MagicMock()
            expected_result.domain_name = "www.example.com"
            expected_result.values = ["192.168.1.1"]

            mock_use_case.execute.return_value = [expected_result]
            mock_container.__getitem__.return_value = mock_use_case
            mock_container_factory.return_value = mock_container

            result = runner.invoke(cli, ["discover-subdomains", "--domain", "example.com"])

            assert_that(result.output).contains("Discovered")

    def test_discover_subdomains_displays_subdomain_name(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
            mock_container = MagicMock()
            mock_use_case = MagicMock()

            expected_result = MagicMock()
            expected_result.domain_name = "api.example.com"
            expected_result.values = ["10.0.0.1"]

            mock_use_case.execute.return_value = [expected_result]
            mock_container.__getitem__.return_value = mock_use_case
            mock_container_factory.return_value = mock_container

            result = runner.invoke(cli, ["discover-subdomains", "--domain", "example.com"])

            assert_that(result.output).contains("api.example.com")

    def test_discover_subdomains_with_short_option(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
            mock_container = MagicMock()
            mock_use_case = MagicMock()

            expected_result = MagicMock()
            expected_result.domain_name = "www.example.com"
            expected_result.values = ["192.168.1.1"]

            mock_use_case.execute.return_value = [expected_result]
            mock_container.__getitem__.return_value = mock_use_case
            mock_container_factory.return_value = mock_container

            result = runner.invoke(cli, ["discover-subdomains", "-d", "example.com"])

            assert_that(result.exit_code).is_equal_to(0)

    def test_discover_subdomains_handles_validation_error(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
            mock_container = MagicMock()
            mock_use_case = MagicMock()
            mock_use_case.execute.side_effect = ValueError("Invalid domain")
            mock_container.__getitem__.return_value = mock_use_case
            mock_container_factory.return_value = mock_container

            result = runner.invoke(cli, ["discover-subdomains", "--domain", ""])

            assert_that(result.exit_code).is_not_equal_to(0)
            assert_that(result.output).contains("Validation error")

    def test_discover_subdomains_handles_generic_error(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
            mock_container = MagicMock()
            mock_use_case = MagicMock()
            mock_use_case.execute.side_effect = Exception("Discovery error")
            mock_container.__getitem__.return_value = mock_use_case
            mock_container_factory.return_value = mock_container

            result = runner.invoke(cli, ["discover-subdomains", "--domain", "example.com"])

            assert_that(result.exit_code).is_not_equal_to(0)
            assert_that(result.output).contains("Error")

    def test_discover_subdomains_displays_multiple_results(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
            mock_container = MagicMock()
            mock_use_case = MagicMock()

            results = []
            for subdomain in ["www", "api", "mail"]:
                result = MagicMock()
                result.domain_name = f"{subdomain}.example.com"
                result.values = ["192.168.1.1"]
                results.append(result)

            mock_use_case.execute.return_value = results
            mock_container.__getitem__.return_value = mock_use_case
            mock_container_factory.return_value = mock_container

            result = runner.invoke(cli, ["discover-subdomains", "--domain", "example.com"])

            assert_that(result.exit_code).is_equal_to(0)
            assert_that(result.output).contains("3")
