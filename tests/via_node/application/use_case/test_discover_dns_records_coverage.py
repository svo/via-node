from datetime import datetime
from unittest.mock import MagicMock, patch

from assertpy import assert_that

from via_node.application.use_case.discover_dns_records_use_case import (
    DiscoverDnsRecordsUseCase,
    RecordValueExtractor,
)
from via_node.domain.model.dns_record_discovery import DnsRecordDiscovery, DnsRecordType
from via_node.domain.repository.network_topology_repository import NetworkTopologyRepository


class TestDiscoverDnsRecordsCoverageGaps:
    def test_discover_record_type_handles_generic_dns_exception(self) -> None:
        """Test line 83-84: except DNSException as e"""
        from dns.exception import DNSException

        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverDnsRecordsUseCase(repository)
        repository.create_or_update_dns_record_discovery.return_value = None

        with patch(
            "via_node.application.use_case.discover_dns_records_use_case.dns.resolver.Resolver"
        ) as mock_resolver_class:
            mock_resolver = MagicMock()
            mock_resolver_class.return_value = mock_resolver

            mock_resolver.resolve.side_effect = DNSException("Generic DNS error")

            try:
                use_case.execute(domain_name="example.com")
            except ValueError as e:
                assert_that(str(e)).contains("No DNS records found")

    def test_extract_ttl_returns_none_when_no_ttl_attribute(self) -> None:
        """Test line 93: return None when ttl attribute doesn't exist"""
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverDnsRecordsUseCase(repository)

        mock_answers = MagicMock()
        del mock_answers.ttl

        ttl = use_case._extract_ttl(mock_answers)

        assert_that(ttl).is_none()

    def test_extract_target_for_cname_record(self) -> None:
        """Test line 120: _extract_target for CNAME extraction"""
        extractor = RecordValueExtractor()

        mock_rdata = MagicMock()
        mock_rdata.target = "target.example.com."

        result = extractor._extract_target(mock_rdata)

        assert_that(result).is_equal_to("target.example.com")

    def test_extract_target_strips_trailing_dot(self) -> None:
        """Test line 120: _extract_target strips trailing dot"""
        extractor = RecordValueExtractor()

        mock_rdata = MagicMock()
        mock_rdata.target = "www.example.com."

        result = extractor._extract_target(mock_rdata)

        assert_that(result).is_equal_to("www.example.com")

    def test_extract_mname_for_soa_record(self) -> None:
        """Test line 129: _extract_mname for SOA extraction"""
        extractor = RecordValueExtractor()

        mock_rdata = MagicMock()
        mock_rdata.mname = "ns1.example.com."

        result = extractor._extract_mname(mock_rdata)

        assert_that(result).is_equal_to("ns1.example.com")

    def test_extract_mname_strips_trailing_dot(self) -> None:
        """Test line 129: _extract_mname strips trailing dot"""
        extractor = RecordValueExtractor()

        mock_rdata = MagicMock()
        mock_rdata.mname = "dns.example.com."

        result = extractor._extract_mname(mock_rdata)

        assert_that(result).is_equal_to("dns.example.com")

    def test_discover_cname_records_end_to_end(self) -> None:
        """Integration test for CNAME discovery using extractor"""
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverDnsRecordsUseCase(repository)

        expected_discovery = DnsRecordDiscovery(
            domain_name="www.example.com",
            record_type=DnsRecordType.CNAME,
            values=["example.com"],
            ttl=3600,
            discovered_at=datetime.now(),
        )
        repository.create_or_update_dns_record_discovery.return_value = expected_discovery

        with patch(
            "via_node.application.use_case.discover_dns_records_use_case.dns.resolver.Resolver"
        ) as mock_resolver_class:
            mock_resolver = MagicMock()
            mock_resolver_class.return_value = mock_resolver

            mock_cname_rdata = MagicMock()
            mock_cname_rdata.target = "example.com."

            mock_answers = MagicMock()
            mock_answers.__iter__ = MagicMock(return_value=iter([mock_cname_rdata]))
            mock_answers.ttl = 3600

            mock_resolver.resolve.return_value = mock_answers

            result = use_case.execute(
                domain_name="www.example.com",
                record_types=[DnsRecordType.CNAME],
            )

            assert_that(result).is_instance_of(list)
            assert_that(result).is_length(1)

    def test_discover_soa_records_end_to_end(self) -> None:
        """Integration test for SOA discovery using extractor"""
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverDnsRecordsUseCase(repository)

        expected_discovery = DnsRecordDiscovery(
            domain_name="example.com",
            record_type=DnsRecordType.SOA,
            values=["ns1.example.com"],
            ttl=3600,
            discovered_at=datetime.now(),
        )
        repository.create_or_update_dns_record_discovery.return_value = expected_discovery

        with patch(
            "via_node.application.use_case.discover_dns_records_use_case.dns.resolver.Resolver"
        ) as mock_resolver_class:
            mock_resolver = MagicMock()
            mock_resolver_class.return_value = mock_resolver

            mock_soa_rdata = MagicMock()
            mock_soa_rdata.mname = "ns1.example.com."

            mock_answers = MagicMock()
            mock_answers.__iter__ = MagicMock(return_value=iter([mock_soa_rdata]))
            mock_answers.ttl = 3600

            mock_resolver.resolve.return_value = mock_answers

            result = use_case.execute(
                domain_name="example.com",
                record_types=[DnsRecordType.SOA],
            )

            assert_that(result).is_instance_of(list)
            assert_that(result).is_length(1)

    def test_extract_exchange_for_mx_record(self) -> None:
        """Test MX exchange extraction"""
        extractor = RecordValueExtractor()

        mock_rdata = MagicMock()
        mock_rdata.exchange = "mail.example.com."

        result = extractor._extract_exchange(mock_rdata)

        assert_that(result).is_equal_to("mail.example.com")

    def test_discover_ns_records_with_target_extraction(self) -> None:
        """Test NS record discovery"""
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = DiscoverDnsRecordsUseCase(repository)

        expected_discovery = DnsRecordDiscovery(
            domain_name="example.com",
            record_type=DnsRecordType.NS,
            values=["ns1.example.com"],
            ttl=3600,
            discovered_at=datetime.now(),
        )
        repository.create_or_update_dns_record_discovery.return_value = expected_discovery

        with patch(
            "via_node.application.use_case.discover_dns_records_use_case.dns.resolver.Resolver"
        ) as mock_resolver_class:
            mock_resolver = MagicMock()
            mock_resolver_class.return_value = mock_resolver

            mock_ns_rdata = MagicMock()
            mock_ns_rdata.target = "ns1.example.com."

            mock_answers = MagicMock()
            mock_answers.__iter__ = MagicMock(return_value=iter([mock_ns_rdata]))
            mock_answers.ttl = 3600

            mock_resolver.resolve.return_value = mock_answers

            result = use_case.execute(
                domain_name="example.com",
                record_types=[DnsRecordType.NS],
            )

            assert_that(result).is_instance_of(list)
            assert_that(result).is_length(1)
