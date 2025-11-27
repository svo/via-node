from datetime import datetime
from typing import Any, List, Optional

import dns.resolver
from dns.exception import DNSException

from via_node.domain.model.dns_record_discovery import DnsRecordDiscovery, DnsRecordType
from via_node.domain.repository.network_topology_repository import NetworkTopologyRepository


class DiscoverSubdomainsUseCase:
    def __init__(self, repository: NetworkTopologyRepository) -> None:
        self._repository = repository
        self._common_subdomains = [
            "www",
            "mail",
            "ftp",
            "localhost",
            "webmail",
            "smtp",
            "pop",
            "ns",
            "webdisk",
            "ns1",
            "cpanel",
            "whm",
            "autodiscover",
            "autoconfig",
            "m",
            "imap",
            "test",
            "portal",
            "api",
            "admin",
            "dev",
            "staging",
            "beta",
            "stage",
            "app",
            "cdn",
            "git",
            "github",
            "ssh",
            "vpn",
            "dns",
            "lb",
            "cache",
            "db",
            "backup",
            "secure",
            "secure-login",
            "login",
            "panel",
            "billing",
            "support",
            "shop",
            "blog",
            "news",
            "download",
            "upload",
            "files",
            "assets",
            "static",
            "images",
            "video",
            "docs",
            "documentation",
            "help",
            "status",
            "monitoring",
            "analytics",
            "dashboard",
            "graph",
            "stats",
            "maps",
            "photos",
            "mail2",
            "mailserver",
            "calendar",
            "contacts",
            "notes",
            "tasks",
            "wiki",
            "forum",
            "community",
            "chat",
            "slack",
            "teams",
            "zoom",
            "meet",
            "confluence",
            "jira",
            "jenkins",
            "docker",
            "kubernetes",
            "prometheus",
            "grafana",
            "elasticsearch",
            "kibana",
            "logstash",
            "splunk",
            "datadog",
            "newrelic",
            "sentry",
            "rollbar",
            "bugsnag",
            "amplitude",
            "mixpanel",
            "segment",
            "google",
            "facebook",
            "twitter",
            "linkedin",
            "instagram",
            "youtube",
            "pinterest",
            "reddit",
            "tiktok",
            "snapchat",
            "whatsapp",
            "telegram",
            "discord",
        ]

    def execute(self, domain_name: str) -> List[DnsRecordDiscovery]:
        self._validate_domain_name(domain_name)
        domain_name = domain_name.strip().lower()

        subdomains_found: List[DnsRecordDiscovery] = []

        for subdomain in self._common_subdomains:
            full_domain = f"{subdomain}.{domain_name}"
            try:
                discovery = self._discover_subdomain(full_domain)
                if discovery:
                    stored = self._repository.create_or_update_dns_record_discovery(discovery)
                    subdomains_found.append(stored)
            except ValueError:
                pass

        if not subdomains_found:
            raise ValueError(f"No subdomains found for domain: {domain_name}")

        return subdomains_found

    def _validate_domain_name(self, domain_name: str) -> None:
        if not domain_name or len(domain_name.strip()) == 0:
            raise ValueError("Domain name cannot be empty")

    def _discover_subdomain(self, domain_name: str) -> Optional[DnsRecordDiscovery]:
        try:
            resolver = dns.resolver.Resolver()
            answers = resolver.resolve(domain_name, DnsRecordType.A.value)
            return self._build_discovery(domain_name, answers)
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            return None
        except dns.exception.Timeout:
            raise ValueError(f"DNS timeout while querying subdomain: {domain_name}")
        except DNSException as e:
            raise ValueError(f"DNS error querying subdomain {domain_name}: {str(e)}")

    def _build_discovery(self, domain_name: str, answers: Any) -> Optional[DnsRecordDiscovery]:
        values = [str(answer) for answer in answers]

        if not values:
            return None

        ttl = int(answers.ttl) if hasattr(answers, "ttl") else None

        return DnsRecordDiscovery(
            domain_name=domain_name,
            record_type=DnsRecordType.A,
            values=values,
            ttl=ttl,
            discovered_at=datetime.now(),
        )
