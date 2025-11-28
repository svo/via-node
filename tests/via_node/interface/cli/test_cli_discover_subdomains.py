from datetime import datetime
from unittest.mock import MagicMock, patch
import tempfile
import os

from click.testing import CliRunner
from assertpy import assert_that

from via_node.interface.cli.main import cli, _load_subdomains_from_file
from via_node.domain.model.dns_record_discovery import DnsRecordDiscovery, DnsRecordType


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

            expected_discovery = DnsRecordDiscovery(
                domain_name="www.example.com",
                record_type=DnsRecordType.A,
                values=["192.168.1.1"],
                ttl=3600,
                discovered_at=datetime.now(),
            )
            mock_use_case.execute.return_value = [expected_discovery]
            mock_container.__getitem__.return_value = mock_use_case
            mock_container_factory.return_value = mock_container

            result = runner.invoke(cli, ["discover-subdomains", "--domain", "example.com"])

            assert_that(result.exit_code).is_equal_to(0)

    def test_discover_subdomains_displays_results(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
            mock_container = MagicMock()
            mock_use_case = MagicMock()

            expected_discovery = DnsRecordDiscovery(
                domain_name="www.example.com",
                record_type=DnsRecordType.A,
                values=["192.168.1.1"],
                ttl=3600,
                discovered_at=datetime.now(),
            )
            mock_use_case.execute.return_value = [expected_discovery]
            mock_container.__getitem__.return_value = mock_use_case
            mock_container_factory.return_value = mock_container

            result = runner.invoke(cli, ["discover-subdomains", "--domain", "example.com"])

            assert_that(result.output).contains("✓ Discovered 1 subdomain(s)")
            assert_that(result.output).contains("www.example.com")
            assert_that(result.output).contains("192.168.1.1")

    def test_discover_subdomains_with_custom_dictionary_file(self) -> None:
        runner = CliRunner()

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("custom1\n")
            f.write("custom2\n")
            f.write("custom3\n")
            temp_file = f.name

        try:
            with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
                mock_container = MagicMock()
                mock_repository = MagicMock()

                expected_discovery = DnsRecordDiscovery(
                    domain_name="custom1.example.com",
                    record_type=DnsRecordType.A,
                    values=["192.168.1.1"],
                    ttl=3600,
                    discovered_at=datetime.now(),
                )

                def container_getitem(key):
                    from via_node.domain.repository.network_topology_repository import (
                        NetworkTopologyRepository,
                    )

                    if key is NetworkTopologyRepository:
                        return mock_repository
                    raise KeyError(f"Unknown key: {key}")

                mock_container.__getitem__.side_effect = container_getitem
                mock_container_factory.return_value = mock_container

                with patch("via_node.interface.cli.main.DiscoverSubdomainsUseCase") as mock_use_case_class:
                    mock_use_case = MagicMock()
                    mock_use_case.execute.return_value = [expected_discovery]
                    mock_use_case_class.return_value = mock_use_case

                    result = runner.invoke(
                        cli,
                        [
                            "discover-subdomains",
                            "--domain",
                            "example.com",
                            "--dictionary-file",
                            temp_file,
                        ],
                    )

                    assert_that(result.exit_code).is_equal_to(0)
                    assert_that(result.output).contains("✓ Discovered")
        finally:
            os.unlink(temp_file)

    def test_discover_subdomains_rejects_nonexistent_dictionary_file(self) -> None:
        runner = CliRunner()

        result = runner.invoke(
            cli,
            ["discover-subdomains", "--domain", "example.com", "--dictionary-file", "/nonexistent/file.txt"],
        )

        assert_that(result.exit_code).is_not_equal_to(0)

    def test_discover_subdomains_rejects_empty_dictionary_file(self) -> None:
        runner = CliRunner()

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            temp_file = f.name

        try:
            with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
                mock_container = MagicMock()
                mock_container_factory.return_value = mock_container

                result = runner.invoke(
                    cli,
                    ["discover-subdomains", "--domain", "example.com", "--dictionary-file", temp_file],
                )

                assert_that(result.exit_code).is_not_equal_to(0)
                assert_that(result.output).contains("Dictionary file is empty")
        finally:
            os.unlink(temp_file)

    def test_discover_subdomains_handles_validation_error(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
            mock_container = MagicMock()
            mock_use_case = MagicMock()
            mock_use_case.execute.side_effect = ValueError("No subdomains found")
            mock_container.__getitem__.return_value = mock_use_case
            mock_container_factory.return_value = mock_container

            result = runner.invoke(cli, ["discover-subdomains", "--domain", "example.com"])

            assert_that(result.exit_code).is_not_equal_to(0)
            assert_that(result.output).contains("✗ Validation error")

    def test_discover_subdomains_handles_general_error(self) -> None:
        runner = CliRunner()

        with patch("via_node.interface.cli.main.create_container") as mock_container_factory:
            mock_container = MagicMock()
            mock_use_case = MagicMock()
            mock_use_case.execute.side_effect = Exception("Unexpected error")
            mock_container.__getitem__.return_value = mock_use_case
            mock_container_factory.return_value = mock_container

            result = runner.invoke(cli, ["discover-subdomains", "--domain", "example.com"])

            assert_that(result.exit_code).is_not_equal_to(0)
            assert_that(result.output).contains("✗ Error")


class TestLoadSubdomainsFromFile:
    def test_load_subdomains_from_file_reads_single_line(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("subdomain1\n")
            temp_file = f.name

        try:
            subdomains = _load_subdomains_from_file(temp_file)
            assert_that(subdomains).is_equal_to(["subdomain1"])
        finally:
            os.unlink(temp_file)

    def test_load_subdomains_from_file_reads_multiple_lines(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("subdomain1\n")
            f.write("subdomain2\n")
            f.write("subdomain3\n")
            temp_file = f.name

        try:
            subdomains = _load_subdomains_from_file(temp_file)
            assert_that(subdomains).is_equal_to(["subdomain1", "subdomain2", "subdomain3"])
        finally:
            os.unlink(temp_file)

    def test_load_subdomains_from_file_ignores_empty_lines(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("subdomain1\n")
            f.write("\n")
            f.write("subdomain2\n")
            f.write("   \n")
            f.write("subdomain3\n")
            temp_file = f.name

        try:
            subdomains = _load_subdomains_from_file(temp_file)
            assert_that(subdomains).is_equal_to(["subdomain1", "subdomain2", "subdomain3"])
        finally:
            os.unlink(temp_file)

    def test_load_subdomains_from_file_ignores_comments(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("# This is a comment\n")
            f.write("subdomain1\n")
            f.write("# Another comment\n")
            f.write("subdomain2\n")
            temp_file = f.name

        try:
            subdomains = _load_subdomains_from_file(temp_file)
            assert_that(subdomains).is_equal_to(["subdomain1", "subdomain2"])
        finally:
            os.unlink(temp_file)

    def test_load_subdomains_from_file_strips_whitespace(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("  subdomain1  \n")
            f.write("\tsubdomain2\t\n")
            f.write("subdomain3\n")
            temp_file = f.name

        try:
            subdomains = _load_subdomains_from_file(temp_file)
            assert_that(subdomains).is_equal_to(["subdomain1", "subdomain2", "subdomain3"])
        finally:
            os.unlink(temp_file)

    def test_load_subdomains_from_file_returns_empty_list_for_empty_file(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            temp_file = f.name

        try:
            subdomains = _load_subdomains_from_file(temp_file)
            assert_that(subdomains).is_equal_to([])
        finally:
            os.unlink(temp_file)

    def test_load_subdomains_from_file_raises_error_on_read_failure(self) -> None:
        with patch("builtins.open", side_effect=IOError("Permission denied")):
            try:
                _load_subdomains_from_file("/some/file.txt")
                assert_that(False).is_true()
            except ValueError as e:
                assert_that(str(e)).contains("Failed to read dictionary file")
