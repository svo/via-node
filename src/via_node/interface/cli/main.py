from typing import List, Optional

import click

from via_node.interface.cli.container import create_container
from via_node.application.use_case.add_domain_port_edge_use_case import (
    AddDomainPortEdgeUseCase,
)
from via_node.application.use_case.add_dns_resolves_to_host_edge_use_case import (
    AddDnsResolvesToHostEdgeUseCase,
)
from via_node.application.use_case.add_host_use_case import AddHostUseCase
from via_node.application.use_case.discover_dns_records_use_case import (
    DiscoverDnsRecordsUseCase,
)
from via_node.application.use_case.discover_subdomains_use_case import (
    DiscoverSubdomainsUseCase,
)
from via_node.application.use_case.scan_ports_use_case import ScanPortsUseCase
from via_node.domain.model.dns_record_discovery import DnsRecordType
from via_node.domain.model.port_scan_result import PortScanResult


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.option("--message", default="coconuts", help="Message to print")
def run(message: str) -> None:
    print(message)


@cli.command()
@click.option("--domain", "-d", required=True, help="Domain name")
@click.option("--port", "-p", required=True, type=int, help="Port number (1-65535)")
@click.option("--protocol", default="TCP", help="Protocol (TCP/UDP)")
def add_edge(domain: str, port: int, protocol: str) -> None:
    try:
        container = create_container()
        use_case = container[AddDomainPortEdgeUseCase]

        edge = use_case.execute(domain_name=domain, port_number=port, protocol=protocol)

        click.echo(f"✓ Edge created: {edge.source_id} -> {edge.target_id}")
    except ValueError as e:
        click.echo(f"✗ Validation error: {str(e)}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)
        raise click.Abort()


@cli.command()
@click.option("--ip", "-i", required=True, help="IP address (IPv4 or IPv6)")
@click.option("--hostname", "-h", required=True, help="Hostname or FQDN")
@click.option("--os-type", "-o", required=True, help="Operating system type")
def add_host(ip: str, hostname: str, os_type: str) -> None:
    try:
        container = create_container()
        use_case = container[AddHostUseCase]

        host = use_case.execute(ip_address=ip, hostname=hostname, os_type=os_type)

        click.echo(f"✓ Host added: {host.ip_address} ({host.hostname})")
    except ValueError as e:
        click.echo(f"✗ Validation error: {str(e)}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)
        raise click.Abort()


@cli.command()
@click.option("--domain", "-d", required=True, help="Domain name")
@click.option("--ip", "-i", required=True, help="IP address")
def add_dns_resolves_to_host(domain: str, ip: str) -> None:
    try:
        container = create_container()
        use_case = container[AddDnsResolvesToHostEdgeUseCase]

        edge = use_case.execute(domain_name=domain, ip_address=ip)

        click.echo(f"✓ DNS resolves-to-host edge created: {edge.source_id} -> {edge.target_id}")
    except ValueError as e:
        click.echo(f"✗ Validation error: {str(e)}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)
        raise click.Abort()


@cli.command()
@click.option("--domain", "-d", required=True, help="Domain name to discover")
@click.option(
    "--type",
    "-t",
    multiple=True,
    type=click.Choice(["A", "AAAA", "CNAME", "MX", "NS", "SOA", "TXT"], case_sensitive=False),
    help="Record types to discover (default: A, AAAA, CNAME, MX)",
)
def discover_dns(domain: str, type: tuple) -> None:
    try:
        container = create_container()
        use_case = container[DiscoverDnsRecordsUseCase]
        record_types = _parse_record_types(type)
        discoveries = use_case.execute(domain_name=domain, record_types=record_types)
        _display_discoveries(domain, discoveries)
    except ValueError as e:
        click.echo(f"✗ Validation error: {str(e)}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)
        raise click.Abort()


def _parse_record_types(type_tuple: tuple) -> Optional[List[DnsRecordType]]:
    if not type_tuple:
        return None
    return [DnsRecordType[t.upper()] for t in type_tuple]


def _display_discoveries(domain: str, discoveries: list) -> None:
    click.echo(f"✓ Discovered {len(discoveries)} DNS record(s) for {domain}:")
    for discovery in discoveries:
        values_str = ", ".join(discovery.values)
        ttl_str = f" (TTL: {discovery.ttl})" if discovery.ttl else ""
        click.echo(f"  {discovery.record_type.value}: {values_str}{ttl_str}")


@cli.command()
@click.option("--domain", "-d", required=True, help="Domain to discover subdomains for")
@click.option(
    "--dictionary-file",
    "-f",
    type=click.Path(exists=True),
    help="Path to dictionary file with subdomains (one per line)",
)
def discover_subdomains(domain: str, dictionary_file: Optional[str]) -> None:
    try:
        container = create_container()
        use_case = _create_subdomain_use_case(container, dictionary_file)
        results = use_case.execute(domain_name=domain)
        _display_subdomain_results(domain, results)
    except ValueError as e:
        click.echo(f"✗ Validation error: {str(e)}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)
        raise click.Abort()


def _create_subdomain_use_case(
    container: object,
    dictionary_file: Optional[str],
) -> DiscoverSubdomainsUseCase:
    if not dictionary_file:
        return container[DiscoverSubdomainsUseCase]  # type: ignore

    subdomains = _load_subdomains_from_file(dictionary_file)
    if not subdomains:
        click.echo(f"✗ Dictionary file is empty: {dictionary_file}", err=True)
        raise click.Abort()

    from via_node.domain.repository.network_topology_repository import (
        NetworkTopologyRepository,
    )

    repository = container[NetworkTopologyRepository]  # type: ignore
    return DiscoverSubdomainsUseCase(repository=repository, subdomains=subdomains)


def _display_subdomain_results(domain: str, results: List) -> None:
    click.echo(f"✓ Discovered {len(results)} subdomain(s) for {domain}:")
    for result in results:
        values_str = ", ".join(result.values)
        click.echo(f"  {result.domain_name}: {values_str}")


def _load_subdomains_from_file(file_path: str) -> List[str]:
    subdomains = []
    try:
        with open(file_path, "r") as f:
            for line in f:
                subdomain = line.strip()
                if subdomain and not subdomain.startswith("#"):
                    subdomains.append(subdomain)
        return subdomains
    except IOError as e:
        raise ValueError(f"Failed to read dictionary file: {str(e)}")


def _display_scan_results(target: str, results: list) -> None:
    if results:
        click.echo(f"✓ Scanned {len(results)} port(s) on {target}:")
        for result in results:
            _display_port_result(result)
    else:
        click.echo(f"✓ Scan completed on {target}: No open ports found")


def _display_port_result(result: PortScanResult) -> None:
    state_str = result.state.value.upper()
    service_str = f" ({result.service_name})" if result.service_name else ""
    click.echo(f"  {result.protocol.upper()}/{result.port_number}: {state_str}{service_str}")


@cli.command()
@click.option("--target", "-t", required=True, help="Target IP address to scan")
@click.option("--ports", "-p", default="1-1000", help="Port range or list (e.g., 1-1000 or 22,80,443)")
def scan_ports(target: str, ports: str) -> None:
    try:
        container = create_container()
        use_case = container[ScanPortsUseCase]

        results = use_case.execute(target_ip=target, ports=ports)

        _display_scan_results(target, results)
    except ValueError as e:
        click.echo(f"✗ Validation error: {str(e)}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)
        raise click.Abort()
