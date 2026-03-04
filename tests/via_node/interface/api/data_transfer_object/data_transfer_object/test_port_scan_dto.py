from datetime import datetime
from unittest.mock import MagicMock

from assertpy import assert_that

from via_node.domain.model.port_scan_result import PortState
from via_node.interface.api.data_transfer_object.port_scan_dto import (
    PortScanApiRequestDataTransferObject,
    PortScanApiResponseDataTransferObject,
    PortScanResultApiResponseDataTransferObject,
)


class TestPortScanApiRequestDataTransferObject:
    def test_creates_request_with_target(self) -> None:
        dto = PortScanApiRequestDataTransferObject(target="192.168.1.1", ports="80")

        assert_that(dto.target).is_equal_to("192.168.1.1")

    def test_creates_request_with_ports(self) -> None:
        dto = PortScanApiRequestDataTransferObject(target="192.168.1.1", ports="22,80,443")

        assert_that(dto.ports).is_equal_to("22,80,443")

    def test_creates_request_with_default_ports(self) -> None:
        dto = PortScanApiRequestDataTransferObject(target="192.168.1.1")

        assert_that(dto.ports).is_equal_to("1-1000")


class TestPortScanResultApiResponseDataTransferObject:
    def test_from_domain_model_sets_correct_target_ip(self) -> None:
        domain_model = MagicMock()
        domain_model.target_ip = "192.168.1.1"
        domain_model.port_number = 80
        domain_model.protocol = "tcp"
        domain_model.state = PortState.OPEN
        domain_model.service_name = "http"
        domain_model.service_version = "Apache 2.4"
        domain_model.scanned_at = datetime.now()

        result = PortScanResultApiResponseDataTransferObject.from_domain_model(domain_model)

        assert_that(result.target_ip).is_equal_to("192.168.1.1")

    def test_from_domain_model_sets_correct_port_number(self) -> None:
        domain_model = MagicMock()
        domain_model.target_ip = "192.168.1.1"
        domain_model.port_number = 443
        domain_model.protocol = "tcp"
        domain_model.state = PortState.OPEN
        domain_model.service_name = "https"
        domain_model.service_version = None
        domain_model.scanned_at = datetime.now()

        result = PortScanResultApiResponseDataTransferObject.from_domain_model(domain_model)

        assert_that(result.port_number).is_equal_to(443)

    def test_from_domain_model_sets_correct_state(self) -> None:
        domain_model = MagicMock()
        domain_model.target_ip = "192.168.1.1"
        domain_model.port_number = 80
        domain_model.protocol = "tcp"
        domain_model.state = PortState.FILTERED
        domain_model.service_name = None
        domain_model.service_version = None
        domain_model.scanned_at = datetime.now()

        result = PortScanResultApiResponseDataTransferObject.from_domain_model(domain_model)

        assert_that(result.state).is_equal_to("filtered")

    def test_from_domain_model_sets_correct_service_name(self) -> None:
        domain_model = MagicMock()
        domain_model.target_ip = "192.168.1.1"
        domain_model.port_number = 22
        domain_model.protocol = "tcp"
        domain_model.state = PortState.OPEN
        domain_model.service_name = "ssh"
        domain_model.service_version = "OpenSSH 8.9"
        domain_model.scanned_at = datetime.now()

        result = PortScanResultApiResponseDataTransferObject.from_domain_model(domain_model)

        assert_that(result.service_name).is_equal_to("ssh")

    def test_from_domain_model_handles_none_service_version(self) -> None:
        domain_model = MagicMock()
        domain_model.target_ip = "192.168.1.1"
        domain_model.port_number = 80
        domain_model.protocol = "tcp"
        domain_model.state = PortState.OPEN
        domain_model.service_name = "http"
        domain_model.service_version = None
        domain_model.scanned_at = datetime.now()

        result = PortScanResultApiResponseDataTransferObject.from_domain_model(domain_model)

        assert_that(result.service_version).is_none()


class TestPortScanApiResponseDataTransferObject:
    def test_creates_response_with_results(self) -> None:
        result = PortScanResultApiResponseDataTransferObject(
            target_ip="192.168.1.1",
            port_number=80,
            protocol="tcp",
            state="open",
            service_name="http",
            service_version=None,
            scanned_at=datetime.now(),
        )

        response = PortScanApiResponseDataTransferObject(results=[result])

        assert_that(response.results).is_length(1)

    def test_creates_response_with_empty_results(self) -> None:
        response = PortScanApiResponseDataTransferObject(results=[])

        assert_that(response.results).is_empty()
