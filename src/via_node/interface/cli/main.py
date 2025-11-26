import click

from via_node.interface.cli.container import create_container
from via_node.application.use_case.add_domain_port_edge_use_case import AddDomainPortEdgeUseCase
from via_node.application.use_case.add_host_use_case import AddHostUseCase
from via_node.application.use_case.add_dns_resolves_to_host_edge_use_case import AddDnsResolvesToHostEdgeUseCase


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
