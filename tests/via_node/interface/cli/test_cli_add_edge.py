from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

from click.testing import CliRunner

from via_node.domain.model.network_topology_edge import NetworkTopologyEdge
from via_node.interface.cli.main import cli


class TestCliAddEdge:
    @patch("via_node.interface.cli.main.create_container")
    def test_should_execute_use_case_when_domain_and_port_are_provided(self, mock_create_container: Mock) -> None:
        mock_use_case = Mock()
        mock_edge = NetworkTopologyEdge(
            source_id="example.com",
            target_id="443_TCP",
            edge_type="domain_to_port",
            metadata={},
            created_at=datetime.now(),
        )
        mock_use_case.execute.return_value = mock_edge

        mock_container = MagicMock()
        mock_container.__getitem__.return_value = mock_use_case
        mock_create_container.return_value = mock_container

        runner = CliRunner()
        runner.invoke(cli, ["add-edge", "--domain", "example.com", "--port", "443"])

        mock_use_case.execute.assert_called_once()

    @patch("via_node.interface.cli.main.create_container")
    def test_should_display_success_message_when_edge_is_created(self, mock_create_container: Mock) -> None:
        mock_use_case = Mock()
        mock_edge = NetworkTopologyEdge(
            source_id="example.com",
            target_id="443_TCP",
            edge_type="domain_to_port",
            metadata={},
            created_at=datetime.now(),
        )
        mock_use_case.execute.return_value = mock_edge

        mock_container = MagicMock()
        mock_container.__getitem__.return_value = mock_use_case
        mock_create_container.return_value = mock_container

        runner = CliRunner()
        result = runner.invoke(cli, ["add-edge", "--domain", "example.com", "--port", "443"])

        assert "Edge created" in result.output

    @patch("via_node.interface.cli.main.create_container")
    def test_should_use_short_option_for_domain(self, mock_create_container: Mock) -> None:
        mock_use_case = Mock()
        mock_edge = NetworkTopologyEdge(
            source_id="example.com",
            target_id="443_TCP",
            edge_type="domain_to_port",
            metadata={},
            created_at=datetime.now(),
        )
        mock_use_case.execute.return_value = mock_edge

        mock_container = MagicMock()
        mock_container.__getitem__.return_value = mock_use_case
        mock_create_container.return_value = mock_container

        runner = CliRunner()
        result = runner.invoke(cli, ["add-edge", "-d", "example.com", "-p", "443"])

        assert result.exit_code == 0

    @patch("via_node.interface.cli.main.create_container")
    def test_should_use_tcp_as_default_protocol(self, mock_create_container: Mock) -> None:
        mock_use_case = Mock()
        mock_edge = NetworkTopologyEdge(
            source_id="example.com",
            target_id="443_TCP",
            edge_type="domain_to_port",
            metadata={},
            created_at=datetime.now(),
        )
        mock_use_case.execute.return_value = mock_edge

        mock_container = MagicMock()
        mock_container.__getitem__.return_value = mock_use_case
        mock_create_container.return_value = mock_container

        runner = CliRunner()
        runner.invoke(cli, ["add-edge", "-d", "example.com", "-p", "443"])

        call_kwargs = mock_use_case.execute.call_args[1]
        assert call_kwargs["protocol"] == "TCP"

    @patch("via_node.interface.cli.main.create_container")
    def test_should_accept_custom_protocol(self, mock_create_container: Mock) -> None:
        mock_use_case = Mock()
        mock_edge = NetworkTopologyEdge(
            source_id="example.com",
            target_id="53",
            edge_type="domain_to_port",
            metadata={},
            created_at=datetime.now(),
        )
        mock_use_case.execute.return_value = mock_edge

        mock_container = MagicMock()
        mock_container.__getitem__.return_value = mock_use_case
        mock_create_container.return_value = mock_container

        runner = CliRunner()
        runner.invoke(cli, ["add-edge", "-d", "example.com", "-p", "53", "--protocol", "UDP"])

        call_kwargs = mock_use_case.execute.call_args[1]
        assert call_kwargs["protocol"] == "UDP"

    @patch("via_node.interface.cli.main.create_container")
    def test_should_display_error_when_validation_fails(self, mock_create_container: Mock) -> None:
        mock_use_case = Mock()
        mock_use_case.execute.side_effect = ValueError("Invalid domain")

        mock_container = MagicMock()
        mock_container.__getitem__.return_value = mock_use_case
        mock_create_container.return_value = mock_container

        runner = CliRunner()
        result = runner.invoke(cli, ["add-edge", "-d", "", "-p", "443"])

        assert "Validation error" in result.output

    def test_should_fail_when_domain_is_not_provided(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["add-edge", "-p", "443"])

        assert result.exit_code != 0

    def test_should_fail_when_port_is_not_provided(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["add-edge", "-d", "example.com"])

        assert result.exit_code != 0

    @patch("via_node.interface.cli.main.create_container")
    def test_should_pass_domain_name_to_use_case(self, mock_create_container: Mock) -> None:
        mock_use_case = Mock()
        mock_edge = NetworkTopologyEdge(
            source_id="test.com",
            target_id="443_TCP",
            edge_type="domain_to_port",
            metadata={},
            created_at=datetime.now(),
        )
        mock_use_case.execute.return_value = mock_edge

        mock_container = MagicMock()
        mock_container.__getitem__.return_value = mock_use_case
        mock_create_container.return_value = mock_container

        runner = CliRunner()
        runner.invoke(cli, ["add-edge", "-d", "test.com", "-p", "443"])

        call_kwargs = mock_use_case.execute.call_args[1]
        assert call_kwargs["domain_name"] == "test.com"

    @patch("via_node.interface.cli.main.create_container")
    def test_should_pass_port_number_to_use_case(self, mock_create_container: Mock) -> None:
        mock_use_case = Mock()
        mock_edge = NetworkTopologyEdge(
            source_id="example.com",
            target_id="8080",
            edge_type="domain_to_port",
            metadata={},
            created_at=datetime.now(),
        )
        mock_use_case.execute.return_value = mock_edge

        mock_container = MagicMock()
        mock_container.__getitem__.return_value = mock_use_case
        mock_create_container.return_value = mock_container

        runner = CliRunner()
        runner.invoke(cli, ["add-edge", "-d", "example.com", "-p", "8080"])

        call_kwargs = mock_use_case.execute.call_args[1]
        assert call_kwargs["port_number"] == 8080

    @patch("via_node.interface.cli.main.create_container")
    def test_should_display_error_when_generic_exception_occurs(self, mock_create_container: Mock) -> None:
        mock_use_case = Mock()
        mock_use_case.execute.side_effect = RuntimeError("Database connection failed")

        mock_container = MagicMock()
        mock_container.__getitem__.return_value = mock_use_case
        mock_create_container.return_value = mock_container

        runner = CliRunner()
        result = runner.invoke(cli, ["add-edge", "-d", "example.com", "-p", "443"])

        assert "Error" in result.output
