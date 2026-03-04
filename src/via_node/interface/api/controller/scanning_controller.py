from typing import Callable, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasicCredentials
from lagom import Container

from via_node.application.use_case.scan_ports_use_case import ScanPortsUseCase
from via_node.interface.api.data_transfer_object.port_scan_dto import (
    PortScanApiRequestDataTransferObject,
    PortScanApiResponseDataTransferObject,
    PortScanResultApiResponseDataTransferObject,
)


class ScanningController:
    def __init__(
        self,
        scan_ports_use_case: ScanPortsUseCase,
        authentication_dependency: Optional[Callable[[Optional[HTTPBasicCredentials]], None]] = None,
    ) -> None:
        self.scan_ports_use_case = scan_ports_use_case
        self.authentication_dependency = authentication_dependency
        self.router = APIRouter(prefix="/api/v1", tags=["scanning"])
        self._register_routes()

    def _register_routes(self) -> None:
        dependencies = [Depends(self.authentication_dependency)] if self.authentication_dependency else []

        self.router.add_api_route(
            "/scan/ports",
            self.scan_ports,
            methods=["POST"],
            response_model=PortScanApiResponseDataTransferObject,
            dependencies=dependencies,
        )

    async def scan_ports(
        self, data_transfer_object: PortScanApiRequestDataTransferObject
    ) -> PortScanApiResponseDataTransferObject:
        try:
            results = self.scan_ports_use_case.execute(
                target_ip=data_transfer_object.target,
                ports=data_transfer_object.ports,
            )

            scan_results = [PortScanResultApiResponseDataTransferObject.from_domain_model(r) for r in results]

            return PortScanApiResponseDataTransferObject(results=scan_results)
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
                detail=f"Error scanning ports: {str(e)}",
            )


def create_scanning_controller(
    container: Container,
    authentication_dependency: Optional[Callable[[Optional[HTTPBasicCredentials]], None]] = None,
) -> ScanningController:
    scan_ports_use_case = container[ScanPortsUseCase]

    return ScanningController(
        scan_ports_use_case=scan_ports_use_case,
        authentication_dependency=authentication_dependency,
    )
