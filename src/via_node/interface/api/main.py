import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Optional

import uvicorn
from fastapi import FastAPI
from lagom import Container

from via_node.application.use_case.add_dns_resolves_to_host_edge_use_case import (
    AddDnsResolvesToHostEdgeUseCase,
)
from via_node.application.use_case.add_domain_port_edge_use_case import AddDomainPortEdgeUseCase
from via_node.application.use_case.add_host_use_case import AddHostUseCase
from via_node.application.use_case.coconut_use_case import CreateCoconutUseCase, GetCoconutUseCase
from via_node.application.use_case.discover_dns_records_use_case import DiscoverDnsRecordsUseCase
from via_node.application.use_case.discover_subdomains_use_case import DiscoverSubdomainsUseCase
from via_node.application.use_case.health_use_case import HealthUseCase
from via_node.application.use_case.scan_ports_use_case import ScanPortsUseCase
from via_node.domain.health.health_checker import HealthChecker
from via_node.domain.repository.coconut_repository import CoconutCommandRepository, CoconutQueryRepository
from via_node.domain.repository.network_topology_repository import NetworkTopologyRepository
from via_node.infrastructure.persistence.arango.arango_network_topology_repository import (
    ArangoNetworkTopologyRepository,
)
from via_node.infrastructure.persistence.in_memory.in_memory_coconut_command_repository import (
    InMemoryCoconutCommandRepository,
)
from via_node.infrastructure.persistence.in_memory.in_memory_coconut_query_repository import (
    InMemoryCoconutQueryRepository,
)
from via_node.infrastructure.security.basic_authentication import (
    BasicAuthenticator,
    SecurityDependency,
    get_basic_authenticator,
)
from via_node.infrastructure.system.health_factory import create_health_checker
from via_node.interface.api.controller.coconut_controller import (
    create_coconut_controller,
)
from via_node.interface.api.controller.discovery_controller import create_discovery_controller
from via_node.interface.api.controller.health_controller import create_health_controller
from via_node.interface.api.controller.scanning_controller import create_scanning_controller
from via_node.interface.api.controller.topology_controller import create_topology_controller
from via_node.shared.configuration import ApplicationSettings, get_application_setting_provider


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    initialize_app()
    yield


app = FastAPI(title="Via Node API", version="1.0.0", lifespan=lifespan)


def get_container() -> Container:
    container = Container()

    settings = ApplicationSettings()

    query_repo = InMemoryCoconutQueryRepository()
    command_repo = InMemoryCoconutCommandRepository(query_repo)

    container[CoconutQueryRepository] = lambda: query_repo  # type: ignore
    container[CoconutCommandRepository] = lambda: command_repo  # type: ignore

    container[GetCoconutUseCase] = GetCoconutUseCase
    container[CreateCoconutUseCase] = CreateCoconutUseCase

    network_topology_repository = ArangoNetworkTopologyRepository(
        host=settings.arango_host,
        port=settings.arango_port,
        database=settings.arango_database,
        username=settings.arango_username,
        password=settings.arango_password,
        graph_name=settings.arango_graph_name,
        auto_create_database=settings.arango_auto_create_database,
    )

    container[NetworkTopologyRepository] = lambda: network_topology_repository  # type: ignore[type-abstract]
    container[AddHostUseCase] = AddHostUseCase
    container[AddDomainPortEdgeUseCase] = AddDomainPortEdgeUseCase
    container[AddDnsResolvesToHostEdgeUseCase] = AddDnsResolvesToHostEdgeUseCase
    container[DiscoverDnsRecordsUseCase] = DiscoverDnsRecordsUseCase
    container[DiscoverSubdomainsUseCase] = DiscoverSubdomainsUseCase
    container[ScanPortsUseCase] = ScanPortsUseCase

    authenticator = get_basic_authenticator()
    security_dependency = SecurityDependency(authenticator)
    container[BasicAuthenticator] = lambda: authenticator
    container[SecurityDependency] = lambda: security_dependency

    health_checker = create_health_checker()

    container[HealthChecker] = lambda: health_checker  # type: ignore
    container[HealthUseCase] = HealthUseCase

    return container


global_container: Optional[Container] = None


def get_global_container() -> Optional[Container]:
    return global_container


def initialize_app() -> None:
    global global_container
    if global_container is not None:
        return
    global_container = get_container()

    security_dependency = global_container[SecurityDependency]
    authentication_dependency = security_dependency.authentication_dependency()

    coconut_controller = create_coconut_controller(global_container, authentication_dependency)
    app.include_router(coconut_controller.router)

    topology_controller = create_topology_controller(global_container, authentication_dependency)
    app.include_router(topology_controller.router)

    discovery_controller = create_discovery_controller(global_container, authentication_dependency)
    app.include_router(discovery_controller.router)

    scanning_controller = create_scanning_controller(global_container, authentication_dependency)
    app.include_router(scanning_controller.router)

    health_use_case = global_container[HealthUseCase]
    health_controller = create_health_controller(health_use_case)
    app.include_router(health_controller)


def main(args: list) -> None:
    settings_provider = get_application_setting_provider()
    reload_setting = settings_provider.get("reload")
    host_setting = settings_provider.get("host")

    uvicorn.run(
        "via_node.interface.api.main:app",
        reload=reload_setting,
        host=host_setting,
    )


def run() -> None:
    main(sys.argv[1:])
