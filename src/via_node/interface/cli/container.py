from lagom import Container

from via_node.application.use_case.add_domain_port_edge_use_case import AddDomainPortEdgeUseCase
from via_node.domain.repository.network_topology_repository import NetworkTopologyRepository
from via_node.infrastructure.persistence.arango.arango_network_topology_repository import (
    ArangoNetworkTopologyRepository,
)
from via_node.shared.configuration import ApplicationSettings


def create_container() -> Container:
    container = Container()

    settings = ApplicationSettings()

    repository = ArangoNetworkTopologyRepository(
        host=settings.arango_host,
        port=settings.arango_port,
        database=settings.arango_database,
        username=settings.arango_username,
        password=settings.arango_password,
        graph_name=settings.arango_graph_name,
    )

    container[NetworkTopologyRepository] = lambda: repository  # type: ignore[type-abstract]
    container[AddDomainPortEdgeUseCase] = AddDomainPortEdgeUseCase

    return container
