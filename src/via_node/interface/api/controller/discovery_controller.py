from typing import Callable, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasicCredentials
from lagom import Container

from via_node.application.use_case.discover_dns_records_use_case import DiscoverDnsRecordsUseCase
from via_node.application.use_case.discover_subdomains_use_case import DiscoverSubdomainsUseCase
from via_node.domain.model.dns_record_discovery import DnsRecordType
from via_node.interface.api.data_transfer_object.dns_discovery_dto import (
    DnsDiscoveryApiRequestDataTransferObject,
    DnsDiscoveryApiResponseDataTransferObject,
    DnsDiscoveryResultApiResponseDataTransferObject,
)
from via_node.interface.api.data_transfer_object.subdomain_discovery_dto import (
    SubdomainDiscoveryApiRequestDataTransferObject,
    SubdomainDiscoveryApiResponseDataTransferObject,
    SubdomainDiscoveryResultApiResponseDataTransferObject,
)


class DiscoveryController:
    def __init__(
        self,
        discover_dns_records_use_case: DiscoverDnsRecordsUseCase,
        discover_subdomains_use_case: DiscoverSubdomainsUseCase,
        authentication_dependency: Optional[Callable[[Optional[HTTPBasicCredentials]], None]] = None,
    ) -> None:
        self.discover_dns_records_use_case = discover_dns_records_use_case
        self.discover_subdomains_use_case = discover_subdomains_use_case
        self.authentication_dependency = authentication_dependency
        self.router = APIRouter(prefix="/api/v1", tags=["discovery"])
        self._register_routes()

    def _register_routes(self) -> None:
        dependencies = [Depends(self.authentication_dependency)] if self.authentication_dependency else []

        self.router.add_api_route(
            "/discover/dns",
            self.discover_dns,
            methods=["POST"],
            response_model=DnsDiscoveryApiResponseDataTransferObject,
            dependencies=dependencies,
        )

        self.router.add_api_route(
            "/discover/subdomains",
            self.discover_subdomains,
            methods=["POST"],
            response_model=SubdomainDiscoveryApiResponseDataTransferObject,
            dependencies=dependencies,
        )

    async def discover_dns(
        self, data_transfer_object: DnsDiscoveryApiRequestDataTransferObject
    ) -> DnsDiscoveryApiResponseDataTransferObject:
        try:
            record_types = self._parse_record_types(data_transfer_object.record_types)

            discoveries = self.discover_dns_records_use_case.execute(
                domain_name=data_transfer_object.domain_name,
                record_types=record_types,
            )

            results = [DnsDiscoveryResultApiResponseDataTransferObject.from_domain_model(d) for d in discoveries]

            return DnsDiscoveryApiResponseDataTransferObject(discoveries=results)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Validation error: {str(e)}",
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error discovering DNS records: {str(e)}",
            )

    async def discover_subdomains(
        self, data_transfer_object: SubdomainDiscoveryApiRequestDataTransferObject
    ) -> SubdomainDiscoveryApiResponseDataTransferObject:
        try:
            discoveries = self.discover_subdomains_use_case.execute(
                domain_name=data_transfer_object.domain_name,
            )

            results = [SubdomainDiscoveryResultApiResponseDataTransferObject.from_domain_model(d) for d in discoveries]

            return SubdomainDiscoveryApiResponseDataTransferObject(subdomains=results)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Validation error: {str(e)}",
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error discovering subdomains: {str(e)}",
            )

    def _parse_record_types(self, record_type_strings: Optional[List[str]]) -> Optional[List[DnsRecordType]]:
        if record_type_strings is None:
            return None

        record_types: List[DnsRecordType] = []
        for record_type_string in record_type_strings:
            try:
                record_types.append(DnsRecordType(record_type_string.strip().upper()))
            except ValueError:
                raise ValueError(f"Invalid DNS record type: {record_type_string}")
        return record_types


def create_discovery_controller(
    container: Container,
    authentication_dependency: Optional[Callable[[Optional[HTTPBasicCredentials]], None]] = None,
) -> DiscoveryController:
    discover_dns_records_use_case = container[DiscoverDnsRecordsUseCase]
    discover_subdomains_use_case = container[DiscoverSubdomainsUseCase]

    return DiscoveryController(
        discover_dns_records_use_case=discover_dns_records_use_case,
        discover_subdomains_use_case=discover_subdomains_use_case,
        authentication_dependency=authentication_dependency,
    )
