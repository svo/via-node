from datetime import datetime

import pytest

from via_node.domain.model.network_topology_edge import NetworkTopologyEdge


class TestNetworkTopologyEdge:
    def test_should_create_edge_when_all_fields_are_valid(self) -> None:
        edge = NetworkTopologyEdge(
            source_id="example.com",
            target_id="443_TCP",
            edge_type="domain_to_port",
            metadata={},
            created_at=datetime.now(),
        )

        assert edge.source_id == "example.com"

    def test_should_strip_whitespace_from_source_id(self) -> None:
        edge = NetworkTopologyEdge(
            source_id="  example.com  ",
            target_id="443_TCP",
            edge_type="domain_to_port",
            metadata={},
            created_at=datetime.now(),
        )

        assert edge.source_id == "example.com"

    def test_should_strip_whitespace_from_target_id(self) -> None:
        edge = NetworkTopologyEdge(
            source_id="example.com",
            target_id="  443_TCP  ",
            edge_type="domain_to_port",
            metadata={},
            created_at=datetime.now(),
        )

        assert edge.target_id == "443_TCP"

    def test_should_raise_error_when_source_id_is_empty(self) -> None:
        with pytest.raises(ValueError, match="Source ID cannot be empty"):
            NetworkTopologyEdge(
                source_id="",
                target_id="443_TCP",
                edge_type="domain_to_port",
                metadata={},
                created_at=datetime.now(),
            )

    def test_should_raise_error_when_target_id_is_empty(self) -> None:
        with pytest.raises(ValueError, match="Target ID cannot be empty"):
            NetworkTopologyEdge(
                source_id="example.com",
                target_id="",
                edge_type="domain_to_port",
                metadata={},
                created_at=datetime.now(),
            )

    def test_should_normalize_edge_type_to_lowercase(self) -> None:
        edge = NetworkTopologyEdge(
            source_id="example.com",
            target_id="443_TCP",
            edge_type="DOMAIN_TO_PORT",
            metadata={},
            created_at=datetime.now(),
        )

        assert edge.edge_type == "domain_to_port"

    def test_should_raise_error_when_edge_type_is_invalid(self) -> None:
        with pytest.raises(ValueError, match="Edge type must be one of"):
            NetworkTopologyEdge(
                source_id="example.com",
                target_id="443_TCP",
                edge_type="invalid_type",
                metadata={},
                created_at=datetime.now(),
            )

    def test_should_store_metadata_dictionary(self) -> None:
        metadata = {"key": "value", "number": 123}
        edge = NetworkTopologyEdge(
            source_id="example.com",
            target_id="443_TCP",
            edge_type="domain_to_port",
            metadata=metadata,
            created_at=datetime.now(),
        )

        assert edge.metadata == metadata
