from datetime import datetime

import pytest
from assertpy import assert_that

from via_node.domain.model.port_scan_result import PortScanResult, PortState


class TestPortScanResultCreation:
    def test_create_port_scan_result_with_valid_data(self) -> None:
        result = PortScanResult(
            target_ip="192.168.1.1",
            port_number=80,
            protocol="tcp",
            state=PortState.OPEN,
            service_name="http",
            service_version="1.0",
            scanned_at=datetime.now(),
        )

        assert_that(result.target_ip).is_equal_to("192.168.1.1")

    def test_create_port_scan_result_with_open_port(self) -> None:
        result = PortScanResult(
            target_ip="192.168.1.1",
            port_number=443,
            protocol="tcp",
            state=PortState.OPEN,
            scanned_at=datetime.now(),
        )

        assert_that(result.state).is_equal_to(PortState.OPEN)

    def test_create_port_scan_result_with_closed_port(self) -> None:
        result = PortScanResult(
            target_ip="192.168.1.1",
            port_number=9999,
            protocol="tcp",
            state=PortState.CLOSED,
            scanned_at=datetime.now(),
        )

        assert_that(result.state).is_equal_to(PortState.CLOSED)

    def test_create_port_scan_result_with_filtered_port(self) -> None:
        result = PortScanResult(
            target_ip="192.168.1.1",
            port_number=22,
            protocol="tcp",
            state=PortState.FILTERED,
            scanned_at=datetime.now(),
        )

        assert_that(result.state).is_equal_to(PortState.FILTERED)

    def test_create_port_scan_result_with_udp_protocol(self) -> None:
        result = PortScanResult(
            target_ip="192.168.1.1",
            port_number=53,
            protocol="udp",
            state=PortState.OPEN,
            scanned_at=datetime.now(),
        )

        assert_that(result.protocol).is_equal_to("udp")

    def test_create_port_scan_result_without_service_info(self) -> None:
        result = PortScanResult(
            target_ip="192.168.1.1",
            port_number=80,
            protocol="tcp",
            state=PortState.OPEN,
            scanned_at=datetime.now(),
        )

        assert_that(result.service_name).is_none()


class TestPortScanResultTargetIpValidation:
    def test_target_ip_cannot_be_empty(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            PortScanResult(
                target_ip="",
                port_number=80,
                protocol="tcp",
                state=PortState.OPEN,
                scanned_at=datetime.now(),
            )

        assert_that(str(exc_info.value)).contains("Target IP cannot be empty")

    def test_target_ip_whitespace_is_stripped(self) -> None:
        result = PortScanResult(
            target_ip="  192.168.1.1  ",
            port_number=80,
            protocol="tcp",
            state=PortState.OPEN,
            scanned_at=datetime.now(),
        )

        assert_that(result.target_ip).is_equal_to("192.168.1.1")


class TestPortScanResultPortNumberValidation:
    def test_port_number_cannot_be_zero(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            PortScanResult(
                target_ip="192.168.1.1",
                port_number=0,
                protocol="tcp",
                state=PortState.OPEN,
                scanned_at=datetime.now(),
            )

        assert_that(str(exc_info.value)).contains("Port number must be between 1 and 65535")

    def test_port_number_cannot_exceed_65535(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            PortScanResult(
                target_ip="192.168.1.1",
                port_number=65536,
                protocol="tcp",
                state=PortState.OPEN,
                scanned_at=datetime.now(),
            )

        assert_that(str(exc_info.value)).contains("Port number must be between 1 and 65535")

    def test_port_number_1_is_valid(self) -> None:
        result = PortScanResult(
            target_ip="192.168.1.1",
            port_number=1,
            protocol="tcp",
            state=PortState.OPEN,
            scanned_at=datetime.now(),
        )

        assert_that(result.port_number).is_equal_to(1)

    def test_port_number_65535_is_valid(self) -> None:
        result = PortScanResult(
            target_ip="192.168.1.1",
            port_number=65535,
            protocol="tcp",
            state=PortState.OPEN,
            scanned_at=datetime.now(),
        )

        assert_that(result.port_number).is_equal_to(65535)


class TestPortScanResultProtocolValidation:
    def test_protocol_cannot_be_invalid(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            PortScanResult(
                target_ip="192.168.1.1",
                port_number=80,
                protocol="http",
                state=PortState.OPEN,
                scanned_at=datetime.now(),
            )

        assert_that(str(exc_info.value)).contains("Protocol must be 'tcp' or 'udp'")

    def test_protocol_lowercase_tcp_is_valid(self) -> None:
        result = PortScanResult(
            target_ip="192.168.1.1",
            port_number=80,
            protocol="tcp",
            state=PortState.OPEN,
            scanned_at=datetime.now(),
        )

        assert_that(result.protocol).is_equal_to("tcp")

    def test_protocol_uppercase_tcp_is_normalized(self) -> None:
        result = PortScanResult(
            target_ip="192.168.1.1",
            port_number=80,
            protocol="TCP",
            state=PortState.OPEN,
            scanned_at=datetime.now(),
        )

        assert_that(result.protocol).is_equal_to("tcp")

    def test_protocol_lowercase_udp_is_valid(self) -> None:
        result = PortScanResult(
            target_ip="192.168.1.1",
            port_number=53,
            protocol="udp",
            state=PortState.OPEN,
            scanned_at=datetime.now(),
        )

        assert_that(result.protocol).is_equal_to("udp")


class TestPortStateEnum:
    def test_port_state_open(self) -> None:
        assert_that(PortState.OPEN.value).is_equal_to("open")

    def test_port_state_closed(self) -> None:
        assert_that(PortState.CLOSED.value).is_equal_to("closed")

    def test_port_state_filtered(self) -> None:
        assert_that(PortState.FILTERED.value).is_equal_to("filtered")

    def test_port_state_unfiltered(self) -> None:
        assert_that(PortState.UNFILTERED.value).is_equal_to("unfiltered")
