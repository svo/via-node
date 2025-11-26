from datetime import datetime
from unittest.mock import MagicMock, patch

from click.testing import CliRunner
from assertpy import assert_that

from via_node.domain.model.network_topology_edge import NetworkTopologyEdge
from via_node.interface.cli.main import cli


class TestCliAddDnsResolvesToHostEdge:
    def test_add_dns_resolves_to_host_edge_command_success(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_create_container:
            mock_container = MagicMock()
            mock_create_container.return_value = mock_container

            now = datetime.now()
            mock_use_case = MagicMock()
            mock_edge = NetworkTopologyEdge(
                source_id="example.com",
                target_id="192.168.1.1",
                edge_type="dns_resolves_to_host",
                metadata={},
                created_at=now,
            )
            mock_use_case.execute.return_value = mock_edge

            mock_container.__getitem__.return_value = mock_use_case

            result = runner.invoke(
                cli,
                [
                    "add-dns-resolves-to-host",
                    "--domain",
                    "example.com",
                    "--ip",
                    "192.168.1.1",
                ],
            )

            assert_that(result.exit_code).is_equal_to(0)
            assert_that(result.output).contains("example.com")
            assert_that(result.output).contains("192.168.1.1")
            mock_use_case.execute.assert_called_once_with(domain_name="example.com", ip_address="192.168.1.1")

    def test_add_dns_resolves_to_host_edge_command_missing_domain(self) -> None:
        runner = CliRunner()

        result = runner.invoke(
            cli,
            [
                "add-dns-resolves-to-host",
                "--ip",
                "192.168.1.1",
            ],
        )

        assert_that(result.exit_code).is_not_equal_to(0)

    def test_add_dns_resolves_to_host_edge_command_missing_ip(self) -> None:
        runner = CliRunner()

        result = runner.invoke(
            cli,
            [
                "add-dns-resolves-to-host",
                "--domain",
                "example.com",
            ],
        )

        assert_that(result.exit_code).is_not_equal_to(0)

    def test_add_dns_resolves_to_host_edge_command_dns_not_found(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_create_container:
            mock_container = MagicMock()
            mock_create_container.return_value = mock_container

            mock_use_case = MagicMock()
            mock_use_case.execute.side_effect = ValueError("DNS record 'notfound.com' not found")

            mock_container.__getitem__.return_value = mock_use_case

            result = runner.invoke(
                cli,
                [
                    "add-dns-resolves-to-host",
                    "--domain",
                    "notfound.com",
                    "--ip",
                    "192.168.1.1",
                ],
            )

            assert_that(result.exit_code).is_not_equal_to(0)
            assert_that(result.output).contains("Validation error") or "not found" in result.output

    def test_add_dns_resolves_to_host_edge_command_host_not_found(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_create_container:
            mock_container = MagicMock()
            mock_create_container.return_value = mock_container

            mock_use_case = MagicMock()
            mock_use_case.execute.side_effect = ValueError("Host with IP '192.168.1.1' not found")

            mock_container.__getitem__.return_value = mock_use_case

            result = runner.invoke(
                cli,
                [
                    "add-dns-resolves-to-host",
                    "--domain",
                    "example.com",
                    "--ip",
                    "192.168.1.1",
                ],
            )

            assert_that(result.exit_code).is_not_equal_to(0)
            assert_that(result.output).contains("Validation error") or "not found" in result.output

    def test_add_dns_resolves_to_host_edge_command_generic_error(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_create_container:
            mock_container = MagicMock()
            mock_create_container.return_value = mock_container

            mock_use_case = MagicMock()
            mock_use_case.execute.side_effect = RuntimeError("Database connection failed")

            mock_container.__getitem__.return_value = mock_use_case

            result = runner.invoke(
                cli,
                [
                    "add-dns-resolves-to-host",
                    "--domain",
                    "example.com",
                    "--ip",
                    "192.168.1.1",
                ],
            )

            assert_that(result.exit_code).is_not_equal_to(0)
            assert_that(result.output).contains("Error")
