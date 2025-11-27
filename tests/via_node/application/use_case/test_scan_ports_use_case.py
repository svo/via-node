from unittest.mock import MagicMock

import pytest
from assertpy import assert_that

from via_node.application.use_case.scan_ports_use_case import ScanPortsUseCase
from via_node.domain.model.port_scan_result import PortState
from via_node.domain.repository.network_topology_repository import NetworkTopologyRepository


class TestScanPortsUseCaseValidation:
    def test_validate_target_ip_rejects_empty_string(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = ScanPortsUseCase(repository)

        with pytest.raises(ValueError):
            use_case.execute(target_ip="")

    def test_validate_target_ip_rejects_whitespace_only(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = ScanPortsUseCase(repository)

        with pytest.raises(ValueError):
            use_case.execute(target_ip="   ")

    def test_init_creates_use_case(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = ScanPortsUseCase(repository)

        assert_that(use_case._repository).is_equal_to(repository)


class TestScanPortsUseCasePortStateMapping:
    def test_map_open_state(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = ScanPortsUseCase(repository)

        state = use_case._map_port_state("open")
        assert_that(state).is_equal_to(PortState.OPEN)

    def test_map_closed_state(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = ScanPortsUseCase(repository)

        state = use_case._map_port_state("closed")
        assert_that(state).is_equal_to(PortState.CLOSED)

    def test_map_filtered_state(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = ScanPortsUseCase(repository)

        state = use_case._map_port_state("filtered")
        assert_that(state).is_equal_to(PortState.FILTERED)

    def test_map_unfiltered_state(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = ScanPortsUseCase(repository)

        state = use_case._map_port_state("unfiltered")
        assert_that(state).is_equal_to(PortState.UNFILTERED)

    def test_map_unknown_state_defaults_to_filtered(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = ScanPortsUseCase(repository)

        state = use_case._map_port_state("unknown")
        assert_that(state).is_equal_to(PortState.FILTERED)

    def test_map_empty_state_defaults_to_filtered(self) -> None:
        repository = MagicMock(spec=NetworkTopologyRepository)
        use_case = ScanPortsUseCase(repository)

        state = use_case._map_port_state("")
        assert_that(state).is_equal_to(PortState.FILTERED)
