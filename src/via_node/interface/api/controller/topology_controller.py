from typing import Callable, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPBasicCredentials
from lagom import Container

from via_node.application.use_case.add_dns_resolves_to_host_edge_use_case import (
    AddDnsResolvesToHostEdgeUseCase,
)
from via_node.application.use_case.add_domain_port_edge_use_case import (
    AddDomainPortEdgeUseCase,
)
from via_node.application.use_case.add_host_use_case import AddHostUseCase
from via_node.domain.repository.network_topology_repository import NetworkTopologyRepository
from via_node.interface.api.data_transfer_object.dns_record_dto import (
    DnsRecordApiResponseDataTransferObject,
)
from via_node.interface.api.data_transfer_object.edge_dto import (
    DnsResolvesToHostEdgeApiRequestDataTransferObject,
    DomainPortEdgeApiRequestDataTransferObject,
)
from via_node.interface.api.data_transfer_object.host_dto import (
    HostApiRequestDataTransferObject,
    HostApiResponseDataTransferObject,
)
from via_node.interface.api.data_transfer_object.port_dto import (
    PortApiResponseDataTransferObject,
)


class TopologyController:
    def __init__(
        self,
        add_host_use_case: AddHostUseCase,
        add_domain_port_edge_use_case: AddDomainPortEdgeUseCase,
        add_dns_resolves_to_host_edge_use_case: AddDnsResolvesToHostEdgeUseCase,
        network_topology_repository: NetworkTopologyRepository,
        authentication_dependency: Optional[Callable[[Optional[HTTPBasicCredentials]], None]] = None,
    ) -> None:
        self.add_host_use_case = add_host_use_case
        self.add_domain_port_edge_use_case = add_domain_port_edge_use_case
        self.add_dns_resolves_to_host_edge_use_case = add_dns_resolves_to_host_edge_use_case
        self.network_topology_repository = network_topology_repository
        self.authentication_dependency = authentication_dependency
        self.router = APIRouter(prefix="/api/v1", tags=["topology"])
        self._register_routes()

    def _register_routes(self) -> None:
        dependencies = [Depends(self.authentication_dependency)] if self.authentication_dependency else []

        self.router.add_api_route(
            "/hosts",
            self.create_host,
            methods=["POST"],
            status_code=status.HTTP_201_CREATED,
            response_class=Response,
            dependencies=dependencies,
        )

        self.router.add_api_route(
            "/hosts/{ip_address}",
            self.get_host,
            methods=["GET"],
            response_model=HostApiResponseDataTransferObject,
            dependencies=dependencies,
        )

        self.router.add_api_route(
            "/edges/domain-port",
            self.create_domain_port_edge,
            methods=["POST"],
            status_code=status.HTTP_201_CREATED,
            response_class=Response,
            dependencies=dependencies,
        )

        self.router.add_api_route(
            "/edges/dns-resolves-to-host",
            self.create_dns_resolves_to_host_edge,
            methods=["POST"],
            status_code=status.HTTP_201_CREATED,
            response_class=Response,
            dependencies=dependencies,
        )

        self.router.add_api_route(
            "/ports/{port_number}/{protocol}",
            self.get_port,
            methods=["GET"],
            response_model=PortApiResponseDataTransferObject,
            dependencies=dependencies,
        )

        self.router.add_api_route(
            "/dns-records/{domain_name}",
            self.get_dns_record,
            methods=["GET"],
            response_model=DnsRecordApiResponseDataTransferObject,
            dependencies=dependencies,
        )

    async def create_host(self, data_transfer_object: HostApiRequestDataTransferObject) -> Response:
        try:
            host = self.add_host_use_case.execute(
                ip_address=data_transfer_object.ip_address,
                hostname=data_transfer_object.hostname,
                os_type=data_transfer_object.os_type,
                metadata=data_transfer_object.metadata,
            )

            response = Response(status_code=status.HTTP_201_CREATED)
            response.headers["Location"] = f"/api/v1/hosts/{host.ip_address}"

            return response
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Validation error: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating host: {str(e)}",
            )

    async def get_host(self, ip_address: str) -> HostApiResponseDataTransferObject:
        try:
            host = self.network_topology_repository.get_host(ip_address)
            if not host:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Host with IP {ip_address} not found",
                )
            return HostApiResponseDataTransferObject.from_domain_model(host)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving host: {str(e)}",
            )

    async def create_domain_port_edge(
        self, data_transfer_object: DomainPortEdgeApiRequestDataTransferObject
    ) -> Response:
        try:
            edge = self.add_domain_port_edge_use_case.execute(
                domain_name=data_transfer_object.domain_name,
                port_number=data_transfer_object.port_number,
                protocol=data_transfer_object.protocol,
            )

            response = Response(status_code=status.HTTP_201_CREATED)
            response.headers["Location"] = f"/api/v1/edges/domain-port/{edge.source_id}/{edge.target_id}"

            return response
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Validation error: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating domain-port edge: {str(e)}",
            )

    async def create_dns_resolves_to_host_edge(
        self, data_transfer_object: DnsResolvesToHostEdgeApiRequestDataTransferObject
    ) -> Response:
        try:
            edge = self.add_dns_resolves_to_host_edge_use_case.execute(
                domain_name=data_transfer_object.domain_name,
                ip_address=data_transfer_object.ip_address,
            )

            response = Response(status_code=status.HTTP_201_CREATED)
            response.headers["Location"] = f"/api/v1/edges/dns-resolves-to-host/{edge.source_id}/{edge.target_id}"

            return response
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Validation error: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating DNS-resolves-to-host edge: {str(e)}",
            )

    async def get_port(self, port_number: int, protocol: str) -> PortApiResponseDataTransferObject:
        try:
            port = self.network_topology_repository.get_port(port_number, protocol)
            if not port:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Port {port_number}/{protocol} not found",
                )
            return PortApiResponseDataTransferObject.from_domain_model(port)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving port: {str(e)}",
            )

    async def get_dns_record(self, domain_name: str) -> DnsRecordApiResponseDataTransferObject:
        try:
            dns_record = self.network_topology_repository.get_dns_record(domain_name)
            if not dns_record:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"DNS record for domain {domain_name} not found",
                )
            return DnsRecordApiResponseDataTransferObject.from_domain_model(dns_record)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving DNS record: {str(e)}",
            )


def create_topology_controller(
    container: Container,
    authentication_dependency: Optional[Callable[[Optional[HTTPBasicCredentials]], None]] = None,
) -> TopologyController:
    add_host_use_case = container[AddHostUseCase]
    add_domain_port_edge_use_case = container[AddDomainPortEdgeUseCase]
    add_dns_resolves_to_host_edge_use_case = container[AddDnsResolvesToHostEdgeUseCase]
    network_topology_repository = container[NetworkTopologyRepository]  # type: ignore[type-abstract]

    return TopologyController(
        add_host_use_case=add_host_use_case,
        add_domain_port_edge_use_case=add_domain_port_edge_use_case,
        add_dns_resolves_to_host_edge_use_case=add_dns_resolves_to_host_edge_use_case,
        network_topology_repository=network_topology_repository,
        authentication_dependency=authentication_dependency,
    )
