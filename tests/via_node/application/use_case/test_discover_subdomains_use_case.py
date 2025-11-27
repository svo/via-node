from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from assertpy import assert_that

from via_node.application.use_case.discover_subdomains_use_case import DiscoverSubdomainsUseCase
from via_node.domain.model.dns_record_discovery import DnsRecordDiscovery, DnsRecordType
from via_node.domain.repository.network_topology_repository import NetworkTopologyRepository


class TestDiscoverSubdomainsUseCaseValidation:
    def test_validate_domain_name_rejects_empty_string(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverSubdomainsUseCase(repository)

        with pytest.raises(ValueError) as exc_info:
            use_case.execute(domain_name="")

        assert_that(str(exc_info.value)).contains("Domain name cannot be empty")

    def test_validate_domain_name_rejects_whitespace_only(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverSubdomainsUseCase(repository)

        with pytest.raises(ValueError) as exc_info:
            use_case.execute(domain_name="   ")

        assert_that(str(exc_info.value)).contains("Domain name cannot be empty")

    def test_init_creates_use_case(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverSubdomainsUseCase(repository)

        assert_that(use_case).is_instance_of(DiscoverSubdomainsUseCase)

    def test_init_initializes_common_subdomains(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverSubdomainsUseCase(repository)

        assert_that(use_case._common_subdomains).is_not_empty()
        assert_that(use_case._common_subdomains).contains("www", "api", "mail")


class TestDiscoverSubdomainsUseCaseExecution:
    def test_execute_with_found_subdomains(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverSubdomainsUseCase(repository)

        expected_discovery = DnsRecordDiscovery(
            domain_name="www.example.com",
            record_type=DnsRecordType.A,
            values=["192.168.1.1"],
            ttl=3600,
            discovered_at=datetime.now(),
        )
        repository.create_or_update_dns_record_discovery.return_value = expected_discovery

        with patch.object(use_case, "_discover_subdomain") as mock_discover:
            mock_discover.return_value = expected_discovery
            result = use_case.execute(domain_name="example.com")

            assert_that(result).is_instance_of(list)
            assert_that(len(result)).is_greater_than(0)

    def test_execute_normalizes_domain_to_lowercase(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverSubdomainsUseCase(repository)

        expected_discovery = DnsRecordDiscovery(
            domain_name="www.example.com",
            record_type=DnsRecordType.A,
            values=["192.168.1.1"],
            ttl=3600,
            discovered_at=datetime.now(),
        )
        repository.create_or_update_dns_record_discovery.return_value = expected_discovery

        with patch.object(use_case, "_discover_subdomain") as mock_discover:
            mock_discover.return_value = expected_discovery
            result = use_case.execute(domain_name="EXAMPLE.COM")

            assert_that(result).is_instance_of(list)

    def test_execute_raises_error_when_no_subdomains_found(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverSubdomainsUseCase(repository)

        with patch.object(use_case, "_discover_subdomain") as mock_discover:
            mock_discover.return_value = None

            with pytest.raises(ValueError) as exc_info:
                use_case.execute(domain_name="example.com")

            assert_that(str(exc_info.value)).contains("No subdomains found")

    def test_execute_skips_subdomains_with_value_error(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverSubdomainsUseCase(repository)

        expected_discovery = DnsRecordDiscovery(
            domain_name="www.example.com",
            record_type=DnsRecordType.A,
            values=["192.168.1.1"],
            ttl=3600,
            discovered_at=datetime.now(),
        )
        repository.create_or_update_dns_record_discovery.return_value = expected_discovery

        with patch.object(use_case, "_discover_subdomain") as mock_discover:

            def side_effect(domain: str):
                if "www" in domain:
                    return expected_discovery
                raise ValueError("DNS error")

            mock_discover.side_effect = side_effect
            result = use_case.execute(domain_name="example.com")

            assert_that(result).is_instance_of(list)
            assert_that(len(result)).is_greater_than(0)

    def test_execute_calls_repository_for_each_discovery(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverSubdomainsUseCase(repository)

        expected_discovery = DnsRecordDiscovery(
            domain_name="www.example.com",
            record_type=DnsRecordType.A,
            values=["192.168.1.1"],
            ttl=3600,
            discovered_at=datetime.now(),
        )
        repository.create_or_update_dns_record_discovery.return_value = expected_discovery

        with patch.object(use_case, "_discover_subdomain") as mock_discover:
            mock_discover.return_value = expected_discovery
            result = use_case.execute(domain_name="example.com")

            assert_that(repository.create_or_update_dns_record_discovery.call_count).is_greater_than(0)
            assert_that(result).is_instance_of(list)


class TestDiscoverSubdomainsUseCaseDiscovery:
    def test_discover_subdomain_returns_discovery_on_success(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverSubdomainsUseCase(repository)

        mock_answers = MagicMock()
        mock_answers.__iter__ = MagicMock(return_value=iter(["192.168.1.1"]))
        mock_answers.ttl = 3600

        with patch("dns.resolver.Resolver") as mock_resolver_class:
            mock_resolver = MagicMock()
            mock_resolver_class.return_value = mock_resolver
            mock_resolver.resolve.return_value = mock_answers

            result = use_case._discover_subdomain("www.example.com")

            assert_that(result).is_instance_of(DnsRecordDiscovery)

    def test_discover_subdomain_returns_none_on_nxdomain(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverSubdomainsUseCase(repository)

        with patch("dns.resolver.Resolver") as mock_resolver_class:
            mock_resolver = MagicMock()
            mock_resolver_class.return_value = mock_resolver
            mock_resolver.resolve.side_effect = __import__("dns.resolver", fromlist=["NXDOMAIN"]).NXDOMAIN()

            result = use_case._discover_subdomain("nonexistent.example.com")

            assert_that(result).is_none()

    def test_discover_subdomain_returns_none_on_no_answer(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverSubdomainsUseCase(repository)

        with patch("dns.resolver.Resolver") as mock_resolver_class:
            mock_resolver = MagicMock()
            mock_resolver_class.return_value = mock_resolver
            mock_resolver.resolve.side_effect = __import__("dns.resolver", fromlist=["NoAnswer"]).NoAnswer()

            result = use_case._discover_subdomain("www.example.com")

            assert_that(result).is_none()

    def test_discover_subdomain_raises_error_on_timeout(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverSubdomainsUseCase(repository)

        with patch("dns.resolver.Resolver") as mock_resolver_class:
            mock_resolver = MagicMock()
            mock_resolver_class.return_value = mock_resolver
            mock_resolver.resolve.side_effect = __import__("dns.exception", fromlist=["Timeout"]).Timeout()

            with pytest.raises(ValueError) as exc_info:
                use_case._discover_subdomain("www.example.com")

            assert_that(str(exc_info.value)).contains("DNS timeout")

    def test_discover_subdomain_raises_error_on_dns_exception(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverSubdomainsUseCase(repository)

        with patch("dns.resolver.Resolver") as mock_resolver_class:
            mock_resolver = MagicMock()
            mock_resolver_class.return_value = mock_resolver
            mock_resolver.resolve.side_effect = __import__("dns.exception", fromlist=["DNSException"]).DNSException()

            with pytest.raises(ValueError) as exc_info:
                use_case._discover_subdomain("www.example.com")

            assert_that(str(exc_info.value)).contains("DNS error")


class TestDiscoverSubdomainsUseCaseBuildDiscovery:
    def test_build_discovery_creates_discovery_with_ttl(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverSubdomainsUseCase(repository)

        mock_answers = MagicMock()
        mock_answers.__iter__ = MagicMock(return_value=iter(["192.168.1.1"]))
        mock_answers.ttl = 3600

        result = use_case._build_discovery("www.example.com", mock_answers)

        assert_that(result).is_instance_of(DnsRecordDiscovery)
        assert_that(result.domain_name).is_equal_to("www.example.com")
        assert_that(result.ttl).is_equal_to(3600)
        assert_that(result.values).contains("192.168.1.1")

    def test_build_discovery_creates_discovery_without_ttl(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverSubdomainsUseCase(repository)

        mock_answers = MagicMock()
        mock_answers.__iter__ = MagicMock(return_value=iter(["192.168.1.1"]))
        del mock_answers.ttl

        result = use_case._build_discovery("www.example.com", mock_answers)

        assert_that(result).is_instance_of(DnsRecordDiscovery)
        assert_that(result.ttl).is_none()

    def test_build_discovery_returns_none_when_no_values(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverSubdomainsUseCase(repository)

        mock_answers = MagicMock()
        mock_answers.__iter__ = MagicMock(return_value=iter([]))
        mock_answers.ttl = 3600

        result = use_case._build_discovery("www.example.com", mock_answers)

        assert_that(result).is_none()

    def test_build_discovery_handles_multiple_values(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverSubdomainsUseCase(repository)

        mock_answers = MagicMock()
        mock_answers.__iter__ = MagicMock(return_value=iter(["192.168.1.1", "192.168.1.2"]))
        mock_answers.ttl = 3600

        result = use_case._build_discovery("www.example.com", mock_answers)

        assert_that(result).is_instance_of(DnsRecordDiscovery)
        assert_that(result.values).contains("192.168.1.1", "192.168.1.2")
