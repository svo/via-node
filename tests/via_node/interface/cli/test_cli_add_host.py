from datetime import datetime
from unittest.mock import MagicMock, patch

from click.testing import CliRunner
from assertpy import assert_that

from via_node.domain.model.host import Host
from via_node.interface.cli.main import cli


class TestCliAddHost:
    def test_add_host_command_success(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_create_container:
            mock_container = MagicMock()
            mock_create_container.return_value = mock_container

            now = datetime.now()
            mock_use_case = MagicMock()
            mock_host = Host(
                ip_address="192.168.1.1",
                hostname="example.com",
                os_type="Linux",
                created_at=now,
                updated_at=now,
            )
            mock_use_case.execute.return_value = mock_host

            mock_container.__getitem__.return_value = mock_use_case

            result = runner.invoke(
                cli,
                [
                    "add-host",
                    "--ip",
                    "192.168.1.1",
                    "--hostname",
                    "example.com",
                    "--os-type",
                    "Linux",
                ],
            )

            assert_that(result.exit_code).is_equal_to(0)
            assert_that(result.output).contains("192.168.1.1")
            assert_that(result.output).contains("example.com")
            mock_use_case.execute.assert_called_once()

    def test_add_host_command_with_missing_required_option(self) -> None:
        runner = CliRunner()

        result = runner.invoke(
            cli,
            [
                "add-host",
                "--hostname",
                "example.com",
                "--os-type",
                "Linux",
            ],
        )

        assert_that(result.exit_code).is_not_equal_to(0)

    def test_add_host_command_validation_error(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_create_container:
            mock_container = MagicMock()
            mock_create_container.return_value = mock_container

            mock_use_case = MagicMock()
            mock_use_case.execute.side_effect = ValueError("Invalid IP address")

            mock_container.__getitem__.return_value = mock_use_case

            result = runner.invoke(
                cli,
                [
                    "add-host",
                    "--ip",
                    "invalid-ip",
                    "--hostname",
                    "example.com",
                    "--os-type",
                    "Linux",
                ],
            )

            assert_that(result.exit_code).is_not_equal_to(0)
            assert_that(result.output).contains("Validation error") or "Invalid IP address" in result.output

    def test_add_host_command_generic_error(self) -> None:
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
                    "add-host",
                    "--ip",
                    "192.168.1.1",
                    "--hostname",
                    "example.com",
                    "--os-type",
                    "Linux",
                ],
            )

            assert_that(result.exit_code).is_not_equal_to(0)
            assert_that(result.output).contains("Error")
