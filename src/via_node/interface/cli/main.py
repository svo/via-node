import click

from via_node.interface.cli.container import create_container
from via_node.application.use_case.add_domain_port_edge_use_case import AddDomainPortEdgeUseCase


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
