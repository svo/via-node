from datetime import datetime
from typing import Any, List, Optional

import dns.resolver
from dns.exception import DNSException

from via_node.domain.model.dns_record_discovery import DnsRecordDiscovery, DnsRecordType
from via_node.domain.repository.network_topology_repository import NetworkTopologyRepository


class DiscoverDnsRecordsUseCase:
    def __init__(self, repository: NetworkTopologyRepository) -> None:
        self._repository = repository

    def execute(
        self,
        domain_name: str,
        record_types: Optional[List[DnsRecordType]] = None,
    ) -> List[DnsRecordDiscovery]:
        self._validate_domain_name(domain_name)
        domain_name = domain_name.strip().lower()

        if record_types is None:
            record_types = self._get_default_record_types()

        discoveries = self._discover_all_record_types(domain_name, record_types)

        if not discoveries:
            raise ValueError(f"No DNS records found for domain: {domain_name}")

        return discoveries

    def _validate_domain_name(self, domain_name: str) -> None:
        if not domain_name or len(domain_name.strip()) == 0:
            raise ValueError("Domain name cannot be empty")

    def _get_default_record_types(self) -> List[DnsRecordType]:
        return [
            DnsRecordType.A,
            DnsRecordType.AAAA,
            DnsRecordType.CNAME,
            DnsRecordType.MX,
        ]

    def _discover_all_record_types(
        self, domain_name: str, record_types: List[DnsRecordType]
    ) -> List[DnsRecordDiscovery]:
        discoveries: List[DnsRecordDiscovery] = []

        for record_type in record_types:
            try:
                discovery = self._discover_record_type(domain_name, record_type)
                if discovery:
                    stored = self._repository.create_or_update_dns_record_discovery(discovery)
                    discoveries.append(stored)
            except ValueError:
                pass

        return discoveries

    def _discover_record_type(self, domain_name: str, record_type: DnsRecordType) -> Optional[DnsRecordDiscovery]:
        try:
            resolver = dns.resolver.Resolver()
            answers = resolver.resolve(domain_name, record_type.value)
            values = self._extract_values(answers, record_type)

            if not values:
                return None

            ttl = self._extract_ttl(answers)

            return DnsRecordDiscovery(
                domain_name=domain_name,
                record_type=record_type,
                values=values,
                ttl=ttl,
                discovered_at=datetime.now(),
            )
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            return None
        except dns.exception.Timeout:
            raise ValueError(f"DNS timeout while querying {record_type.value} records for {domain_name}")
        except DNSException as e:
            raise ValueError(f"DNS error querying {domain_name}: {str(e)}")

    def _extract_values(self, answers: Any, record_type: DnsRecordType) -> List[str]:
        extractor = RecordValueExtractor()
        return extractor.extract(answers, record_type)

    def _extract_ttl(self, answers: Any) -> Optional[int]:
        if hasattr(answers, "ttl"):
            return int(answers.ttl)
        return None


class RecordValueExtractor:
    def __init__(self) -> None:
        self._extractors: dict = {
            DnsRecordType.CNAME: self._extract_target,
            DnsRecordType.MX: self._extract_exchange,
            DnsRecordType.NS: self._extract_target,
            DnsRecordType.TXT: self._extract_text,
            DnsRecordType.SOA: self._extract_mname,
        }

    def extract(self, answers: Any, record_type: DnsRecordType) -> List[str]:
        values: List[str] = []
        for rdata in answers:
            value = self._extract_single_value(rdata, record_type)
            if value:
                values.append(value)
        return values

    def _extract_single_value(self, rdata: Any, record_type: DnsRecordType) -> str:
        extractor = self._extractors.get(record_type, lambda r: str(r))
        result = extractor(rdata)
        return str(result)

    def _extract_target(self, rdata: Any) -> str:
        return str(rdata.target).rstrip(".")

    def _extract_exchange(self, rdata: Any) -> str:
        return str(rdata.exchange).rstrip(".")

    def _extract_text(self, rdata: Any) -> str:
        return str(rdata.strings[0], "utf-8")

    def _extract_mname(self, rdata: Any) -> str:
        return str(rdata.mname).rstrip(".")
