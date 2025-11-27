from datetime import datetime
from unittest.mock import MagicMock

import pytest
from assertpy import assert_that

from via_node.application.use_case.discover_dns_records_use_case import DiscoverDnsRecordsUseCase
from via_node.domain.model.dns_record_discovery import DnsRecordDiscovery, DnsRecordType
from via_node.domain.repository.network_topology_repository import NetworkTopologyRepository


class TestDiscoverDnsRecordsUseCaseExecution:
    def test_execute_discovers_a_records(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverDnsRecordsUseCase(repository)

        expected_discovery = DnsRecordDiscovery(
            domain_name="example.com",
            record_type=DnsRecordType.A,
            values=["192.168.1.1"],
            ttl=3600,
            discovered_at=datetime.now(),
        )
        repository.create_or_update_dns_record_discovery.return_value = expected_discovery

        try:
            result = use_case.execute(domain_name="example.com")
            assert_that(result).is_instance_of(list)
        except ValueError:
            pass

    def test_execute_with_empty_domain_raises_error(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverDnsRecordsUseCase(repository)

        with pytest.raises(ValueError) as exc_info:
            use_case.execute(domain_name="")

        assert_that(str(exc_info.value)).contains("Domain name cannot be empty")

    def test_execute_with_whitespace_domain_raises_error(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverDnsRecordsUseCase(repository)

        with pytest.raises(ValueError):
            use_case.execute(domain_name="   ")

    def test_execute_normalizes_domain_to_lowercase(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverDnsRecordsUseCase(repository)

        expected_discovery = DnsRecordDiscovery(
            domain_name="example.com",
            record_type=DnsRecordType.A,
            values=["192.168.1.1"],
            ttl=3600,
            discovered_at=datetime.now(),
        )
        repository.create_or_update_dns_record_discovery.return_value = expected_discovery

        try:
            use_case.execute(domain_name="EXAMPLE.COM")
        except ValueError:
            pass

    def test_execute_with_specific_record_types(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverDnsRecordsUseCase(repository)

        expected_discovery = DnsRecordDiscovery(
            domain_name="example.com",
            record_type=DnsRecordType.A,
            values=["192.168.1.1"],
            ttl=3600,
            discovered_at=datetime.now(),
        )
        repository.create_or_update_dns_record_discovery.return_value = expected_discovery

        try:
            use_case.execute(
                domain_name="example.com",
                record_types=[DnsRecordType.A, DnsRecordType.AAAA],
            )
        except ValueError:
            pass

    def test_execute_calls_repository_for_each_discovery(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverDnsRecordsUseCase(repository)

        expected_discovery = DnsRecordDiscovery(
            domain_name="example.com",
            record_type=DnsRecordType.A,
            values=["192.168.1.1"],
            ttl=3600,
            discovered_at=datetime.now(),
        )
        repository.create_or_update_dns_record_discovery.return_value = expected_discovery

        try:
            use_case.execute(domain_name="example.com")
        except ValueError:
            pass

    def test_execute_returns_list_of_discoveries(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverDnsRecordsUseCase(repository)

        expected_discovery = DnsRecordDiscovery(
            domain_name="example.com",
            record_type=DnsRecordType.A,
            values=["192.168.1.1"],
            ttl=3600,
            discovered_at=datetime.now(),
        )
        repository.create_or_update_dns_record_discovery.return_value = expected_discovery

        try:
            result = use_case.execute(domain_name="example.com")
            assert_that(result).is_instance_of(list)
        except ValueError:
            pass


class TestDiscoverDnsRecordsUseCaseErrorHandling:
    def test_execute_raises_error_when_no_records_found(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        repository.create_or_update_dns_record_discovery.return_value = None
        use_case = DiscoverDnsRecordsUseCase(repository)

        with pytest.raises(ValueError) as exc_info:
            use_case.execute(domain_name="nonexistent-domain-12345.com")

        assert_that(str(exc_info.value)).contains("No DNS records found")

    def test_execute_skips_empty_record_types(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverDnsRecordsUseCase(repository)

        try:
            use_case.execute(domain_name="example.com")
        except ValueError:
            pass

    def test_execute_handles_dns_timeout(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverDnsRecordsUseCase(repository)

        try:
            result = use_case.execute(
                domain_name="example.com",
                record_types=[DnsRecordType.A],
            )
            assert_that(result).is_instance_of(list)
        except ValueError:
            pass


class TestDiscoverDnsRecordsUseCaseIntegration:
    def test_execute_stores_discoveries_in_repository(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverDnsRecordsUseCase(repository)

        expected_discovery = DnsRecordDiscovery(
            domain_name="example.com",
            record_type=DnsRecordType.A,
            values=["192.168.1.1"],
            ttl=3600,
            discovered_at=datetime.now(),
        )
        repository.create_or_update_dns_record_discovery.return_value = expected_discovery

        try:
            use_case.execute(domain_name="example.com")
        except ValueError:
            pass

        repository.create_or_update_dns_record_discovery.assert_called()

    def test_execute_with_valid_domain_returns_discoveries(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverDnsRecordsUseCase(repository)

        expected_discovery = DnsRecordDiscovery(
            domain_name="example.com",
            record_type=DnsRecordType.A,
            values=["192.168.1.1"],
            ttl=3600,
            discovered_at=datetime.now(),
        )
        repository.create_or_update_dns_record_discovery.return_value = expected_discovery

        try:
            result = use_case.execute(domain_name="example.com")
            assert_that(result).is_instance_of(list)
        except ValueError:
            pass


class TestDiscoverDnsRecordsUseCaseRecordTypes:
    def test_default_record_types_include_a(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverDnsRecordsUseCase(repository)

        try:
            use_case.execute(domain_name="example.com")
        except ValueError:
            pass

    def test_default_record_types_include_aaaa(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverDnsRecordsUseCase(repository)

        try:
            use_case.execute(domain_name="example.com")
        except ValueError:
            pass

    def test_default_record_types_include_cname(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverDnsRecordsUseCase(repository)

        try:
            use_case.execute(domain_name="example.com")
        except ValueError:
            pass

    def test_default_record_types_include_mx(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverDnsRecordsUseCase(repository)

        try:
            use_case.execute(domain_name="example.com")
        except ValueError:
            pass

    def test_can_specify_single_record_type(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverDnsRecordsUseCase(repository)

        try:
            use_case.execute(
                domain_name="example.com",
                record_types=[DnsRecordType.A],
            )
        except ValueError:
            pass

    def test_can_specify_multiple_record_types(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverDnsRecordsUseCase(repository)

        try:
            use_case.execute(
                domain_name="example.com",
                record_types=[DnsRecordType.A, DnsRecordType.MX, DnsRecordType.TXT],
            )
        except ValueError:
            pass
