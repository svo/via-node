from datetime import datetime
from unittest.mock import MagicMock

import pytest
from assertpy import assert_that
from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient
from lagom import Container

from via_node.application.use_case.scan_ports_use_case import ScanPortsUseCase
from via_node.domain.model.port_scan_result import PortScanResult, PortState
from via_node.interface.api.controller.scanning_controller import (
    ScanningController,
    create_scanning_controller,
)


@pytest.fixture
def mock_scan_ports_use_case() -> MagicMock:
    return MagicMock(spec=ScanPortsUseCase)


@pytest.fixture
def scanning_controller(
    mock_scan_ports_use_case: MagicMock,
) -> ScanningController:
    return ScanningController(
        scan_ports_use_case=mock_scan_ports_use_case,
        authentication_dependency=None,
    )


@pytest.fixture
def test_client(scanning_controller: ScanningController) -> TestClient:
    app = FastAPI()
    app.include_router(scanning_controller.router)
    return TestClient(app)


class TestScanPorts:
    def test_scan_ports_returns_200_with_results(
        self,
        test_client: TestClient,
        mock_scan_ports_use_case: MagicMock,
    ) -> None:
        sample_result = PortScanResult(
            target_ip="192.168.1.1",
            port_number=80,
            protocol="tcp",
            state=PortState.OPEN,
            service_name="http",
            service_version="Apache 2.4",
            scanned_at=datetime.now(),
        )
        mock_scan_ports_use_case.execute.return_value = [sample_result]

        response = test_client.post(
            "/api/v1/scan/ports",
            json={"target": "192.168.1.1", "ports": "80"},
        )

        assert_that(response.status_code).is_equal_to(status.HTTP_200_OK)

    def test_scan_ports_returns_correct_target_ip(
        self,
        test_client: TestClient,
        mock_scan_ports_use_case: MagicMock,
    ) -> None:
        sample_result = PortScanResult(
            target_ip="192.168.1.1",
            port_number=80,
            protocol="tcp",
            state=PortState.OPEN,
            service_name="http",
            scanned_at=datetime.now(),
        )
        mock_scan_ports_use_case.execute.return_value = [sample_result]

        response = test_client.post(
            "/api/v1/scan/ports",
            json={"target": "192.168.1.1", "ports": "80"},
        )

        data = response.json()
        assert_that(data["results"][0]["target_ip"]).is_equal_to("192.168.1.1")

    def test_scan_ports_returns_correct_port_state(
        self,
        test_client: TestClient,
        mock_scan_ports_use_case: MagicMock,
    ) -> None:
        sample_result = PortScanResult(
            target_ip="192.168.1.1",
            port_number=80,
            protocol="tcp",
            state=PortState.OPEN,
            service_name="http",
            scanned_at=datetime.now(),
        )
        mock_scan_ports_use_case.execute.return_value = [sample_result]

        response = test_client.post(
            "/api/v1/scan/ports",
            json={"target": "192.168.1.1", "ports": "80"},
        )

        data = response.json()
        assert_that(data["results"][0]["state"]).is_equal_to("open")

    def test_scan_ports_calls_use_case_with_correct_parameters(
        self,
        test_client: TestClient,
        mock_scan_ports_use_case: MagicMock,
    ) -> None:
        mock_scan_ports_use_case.execute.return_value = []

        test_client.post(
            "/api/v1/scan/ports",
            json={"target": "192.168.1.1", "ports": "22,80,443"},
        )

        mock_scan_ports_use_case.execute.assert_called_once_with(
            target_ip="192.168.1.1",
            ports="22,80,443",
        )

    def test_scan_ports_uses_default_ports_when_not_specified(
        self,
        test_client: TestClient,
        mock_scan_ports_use_case: MagicMock,
    ) -> None:
        mock_scan_ports_use_case.execute.return_value = []

        test_client.post(
            "/api/v1/scan/ports",
            json={"target": "192.168.1.1"},
        )

        mock_scan_ports_use_case.execute.assert_called_once_with(
            target_ip="192.168.1.1",
            ports="1-1000",
        )

    def test_scan_ports_returns_400_on_validation_error(
        self,
        test_client: TestClient,
        mock_scan_ports_use_case: MagicMock,
    ) -> None:
        mock_scan_ports_use_case.execute.side_effect = ValueError("Target IP cannot be empty")

        response = test_client.post(
            "/api/v1/scan/ports",
            json={"target": "", "ports": "80"},
        )

        assert_that(response.status_code).is_equal_to(status.HTTP_400_BAD_REQUEST)
        assert_that(response.json()["detail"]).contains("Target IP cannot be empty")

    def test_scan_ports_returns_500_on_unexpected_error(
        self,
        test_client: TestClient,
        mock_scan_ports_use_case: MagicMock,
    ) -> None:
        mock_scan_ports_use_case.execute.side_effect = Exception("Scanner error")

        response = test_client.post(
            "/api/v1/scan/ports",
            json={"target": "192.168.1.1", "ports": "80"},
        )

        assert_that(response.status_code).is_equal_to(status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_scan_ports_returns_empty_list_when_no_ports_found(
        self,
        test_client: TestClient,
        mock_scan_ports_use_case: MagicMock,
    ) -> None:
        mock_scan_ports_use_case.execute.return_value = []

        response = test_client.post(
            "/api/v1/scan/ports",
            json={"target": "192.168.1.1", "ports": "80"},
        )

        assert_that(response.status_code).is_equal_to(status.HTTP_200_OK)
        assert_that(response.json()["results"]).is_empty()

    def test_scan_ports_returns_multiple_results(
        self,
        test_client: TestClient,
        mock_scan_ports_use_case: MagicMock,
    ) -> None:
        results = [
            PortScanResult(
                target_ip="192.168.1.1",
                port_number=22,
                protocol="tcp",
                state=PortState.OPEN,
                service_name="ssh",
                scanned_at=datetime.now(),
            ),
            PortScanResult(
                target_ip="192.168.1.1",
                port_number=80,
                protocol="tcp",
                state=PortState.OPEN,
                service_name="http",
                scanned_at=datetime.now(),
            ),
        ]
        mock_scan_ports_use_case.execute.return_value = results

        response = test_client.post(
            "/api/v1/scan/ports",
            json={"target": "192.168.1.1", "ports": "22,80"},
        )

        assert_that(response.json()["results"]).is_length(2)


class TestScanPortsHttpExceptionPassthrough:
    def test_scan_ports_passes_through_http_exception(
        self,
        test_client: TestClient,
        mock_scan_ports_use_case: MagicMock,
    ) -> None:
        mock_scan_ports_use_case.execute.side_effect = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

        response = test_client.post(
            "/api/v1/scan/ports",
            json={"target": "192.168.1.1", "ports": "80"},
        )

        assert_that(response.status_code).is_equal_to(status.HTTP_403_FORBIDDEN)


class TestCreateScanningController:
    def test_create_scanning_controller_returns_controller_instance(self) -> None:
        container = Container()
        mock_scan_ports = MagicMock(spec=ScanPortsUseCase)

        container[ScanPortsUseCase] = lambda: mock_scan_ports

        controller = create_scanning_controller(container)

        assert_that(controller).is_instance_of(ScanningController)

    def test_create_scanning_controller_sets_correct_use_case(self) -> None:
        container = Container()
        mock_scan_ports = MagicMock(spec=ScanPortsUseCase)

        container[ScanPortsUseCase] = lambda: mock_scan_ports

        controller = create_scanning_controller(container)

        assert_that(controller.scan_ports_use_case).is_equal_to(mock_scan_ports)
