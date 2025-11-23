from datetime import datetime
from unittest.mock import Mock, patch

from via_node.domain.model.dns_record import DnsRecord
from via_node.domain.model.network_topology_edge import NetworkTopologyEdge
from via_node.domain.model.port import Port
from via_node.infrastructure.persistence.arango.arango_network_topology_repository import (
    ArangoNetworkTopologyRepository,
)


class TestArangoNetworkTopologyRepository:
    @patch("via_node.infrastructure.persistence.arango.arango_network_topology_repository.ArangoClient")
    def test_should_initialize_connection_on_creation(self, mock_client_class: Mock) -> None:
        mock_db = Mock()
        mock_client_class.return_value.db.return_value = mock_db
        mock_db.has_graph.return_value = True

        ArangoNetworkTopologyRepository(
            host="localhost",
            port="8082",
            database="test_db",
            username="root",
            password="",
            graph_name="test_graph",
        )

        mock_client_class.assert_called_once()

    @patch("via_node.infrastructure.persistence.arango.arango_network_topology_repository.ArangoClient")
    def test_should_create_graph_when_it_does_not_exist(self, mock_client_class: Mock) -> None:
        mock_db = Mock()
        mock_graph = Mock()
        mock_client_class.return_value.db.return_value = mock_db
        mock_db.has_graph.return_value = False
        mock_db.create_graph.return_value = mock_graph

        ArangoNetworkTopologyRepository(
            host="localhost",
            port="8082",
            database="test_db",
            username="root",
            password="",
            graph_name="test_graph",
        )

        mock_db.create_graph.assert_called_once()

    @patch("via_node.infrastructure.persistence.arango.arango_network_topology_repository.ArangoClient")
    def test_should_not_create_graph_when_it_exists(self, mock_client_class: Mock) -> None:
        mock_db = Mock()
        mock_client_class.return_value.db.return_value = mock_db
        mock_db.has_graph.return_value = True

        ArangoNetworkTopologyRepository(
            host="localhost",
            port="8082",
            database="test_db",
            username="root",
            password="",
            graph_name="test_graph",
        )

        mock_db.create_graph.assert_not_called()

    @patch("via_node.infrastructure.persistence.arango.arango_network_topology_repository.ArangoClient")
    def test_should_insert_dns_record_with_overwrite(self, mock_client_class: Mock) -> None:
        mock_db = Mock()
        mock_graph = Mock()
        mock_collection = Mock()
        mock_client_class.return_value.db.return_value = mock_db
        mock_db.has_graph.return_value = True
        mock_db.graph.return_value = mock_graph
        mock_graph.vertex_collection.return_value = mock_collection

        repository = ArangoNetworkTopologyRepository(
            host="localhost",
            port="8082",
            database="test_db",
            username="root",
            password="",
            graph_name="test_graph",
        )

        dns_record = DnsRecord(
            domain_name="example.com",
            record_type="A",
            ip_addresses=["192.168.1.1"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        repository.create_or_update_dns_record(dns_record)

        mock_collection.insert.assert_called_once()

    @patch("via_node.infrastructure.persistence.arango.arango_network_topology_repository.ArangoClient")
    def test_should_use_domain_name_as_key_for_dns_record(self, mock_client_class: Mock) -> None:
        mock_db = Mock()
        mock_graph = Mock()
        mock_collection = Mock()
        mock_client_class.return_value.db.return_value = mock_db
        mock_db.has_graph.return_value = True
        mock_db.graph.return_value = mock_graph
        mock_graph.vertex_collection.return_value = mock_collection

        repository = ArangoNetworkTopologyRepository(
            host="localhost",
            port="8082",
            database="test_db",
            username="root",
            password="",
            graph_name="test_graph",
        )

        dns_record = DnsRecord(
            domain_name="example.com",
            record_type="A",
            ip_addresses=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        repository.create_or_update_dns_record(dns_record)

        call_args = mock_collection.insert.call_args[0][0]
        assert call_args["_key"] == "example.com"

    @patch("via_node.infrastructure.persistence.arango.arango_network_topology_repository.ArangoClient")
    def test_should_insert_port_with_overwrite(self, mock_client_class: Mock) -> None:
        mock_db = Mock()
        mock_graph = Mock()
        mock_collection = Mock()
        mock_client_class.return_value.db.return_value = mock_db
        mock_db.has_graph.return_value = True
        mock_db.graph.return_value = mock_graph
        mock_graph.vertex_collection.return_value = mock_collection

        repository = ArangoNetworkTopologyRepository(
            host="localhost",
            port="8082",
            database="test_db",
            username="root",
            password="",
            graph_name="test_graph",
        )

        port = Port(
            port_number=443,
            protocol="TCP",
            service_name="https",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        repository.create_or_update_port(port)

        mock_collection.insert.assert_called_once()

    @patch("via_node.infrastructure.persistence.arango.arango_network_topology_repository.ArangoClient")
    def test_should_use_port_number_as_string_key_for_port(self, mock_client_class: Mock) -> None:
        mock_db = Mock()
        mock_graph = Mock()
        mock_collection = Mock()
        mock_client_class.return_value.db.return_value = mock_db
        mock_db.has_graph.return_value = True
        mock_db.graph.return_value = mock_graph
        mock_graph.vertex_collection.return_value = mock_collection

        repository = ArangoNetworkTopologyRepository(
            host="localhost",
            port="8082",
            database="test_db",
            username="root",
            password="",
            graph_name="test_graph",
        )

        port = Port(
            port_number=443,
            protocol="TCP",
            service_name=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        repository.create_or_update_port(port)

        call_args = mock_collection.insert.call_args[0][0]
        assert call_args["_key"] == "443_TCP"

    @patch("via_node.infrastructure.persistence.arango.arango_network_topology_repository.ArangoClient")
    def test_should_create_edge_with_correct_from_and_to(self, mock_client_class: Mock) -> None:
        mock_db = Mock()
        mock_graph = Mock()
        mock_edge_collection = Mock()
        mock_client_class.return_value.db.return_value = mock_db
        mock_db.has_graph.return_value = True
        mock_db.graph.return_value = mock_graph
        mock_graph.edge_collection.return_value = mock_edge_collection

        repository = ArangoNetworkTopologyRepository(
            host="localhost",
            port="8082",
            database="test_db",
            username="root",
            password="",
            graph_name="test_graph",
        )

        edge = NetworkTopologyEdge(
            source_id="example.com",
            target_id="443_TCP",
            edge_type="domain_to_port",
            metadata={},
            created_at=datetime.now(),
        )

        repository.create_edge(edge)

        call_args = mock_edge_collection.insert.call_args[0][0]
        assert call_args["_from"] == "dns_records/example.com"

    @patch("via_node.infrastructure.persistence.arango.arango_network_topology_repository.ArangoClient")
    def test_should_return_none_when_dns_record_does_not_exist(self, mock_client_class: Mock) -> None:
        mock_db = Mock()
        mock_graph = Mock()
        mock_collection = Mock()
        mock_client_class.return_value.db.return_value = mock_db
        mock_db.has_graph.return_value = True
        mock_db.graph.return_value = mock_graph
        mock_graph.vertex_collection.return_value = mock_collection
        mock_collection.has.return_value = False

        repository = ArangoNetworkTopologyRepository(
            host="localhost",
            port="8082",
            database="test_db",
            username="root",
            password="",
            graph_name="test_graph",
        )

        result = repository.get_dns_record("nonexistent.com")

        assert result is None

    @patch("via_node.infrastructure.persistence.arango.arango_network_topology_repository.ArangoClient")
    def test_should_return_dns_record_when_it_exists(self, mock_client_class: Mock) -> None:
        mock_db = Mock()
        mock_graph = Mock()
        mock_collection = Mock()
        mock_client_class.return_value.db.return_value = mock_db
        mock_db.has_graph.return_value = True
        mock_db.graph.return_value = mock_graph
        mock_graph.vertex_collection.return_value = mock_collection
        mock_collection.has.return_value = True
        mock_collection.get.return_value = {
            "domain_name": "example.com",
            "record_type": "A",
            "ip_addresses": ["192.168.1.1"],
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }

        repository = ArangoNetworkTopologyRepository(
            host="localhost",
            port="8082",
            database="test_db",
            username="root",
            password="",
            graph_name="test_graph",
        )

        result = repository.get_dns_record("example.com")

        assert result is not None

    @patch("via_node.infrastructure.persistence.arango.arango_network_topology_repository.ArangoClient")
    def test_should_return_none_when_port_does_not_exist(self, mock_client_class: Mock) -> None:
        mock_db = Mock()
        mock_graph = Mock()
        mock_collection = Mock()
        mock_client_class.return_value.db.return_value = mock_db
        mock_db.has_graph.return_value = True
        mock_db.graph.return_value = mock_graph
        mock_graph.vertex_collection.return_value = mock_collection
        mock_collection.has.return_value = False

        repository = ArangoNetworkTopologyRepository(
            host="localhost",
            port="8082",
            database="test_db",
            username="root",
            password="",
            graph_name="test_graph",
        )

        result = repository.get_port(9999, "TCP")

        assert result is None

    @patch("via_node.infrastructure.persistence.arango.arango_network_topology_repository.ArangoClient")
    def test_should_return_port_when_it_exists(self, mock_client_class: Mock) -> None:
        mock_db = Mock()
        mock_graph = Mock()
        mock_collection = Mock()
        mock_client_class.return_value.db.return_value = mock_db
        mock_db.has_graph.return_value = True
        mock_db.graph.return_value = mock_graph
        mock_graph.vertex_collection.return_value = mock_collection
        mock_collection.has.return_value = True
        mock_collection.get.return_value = {
            "port_number": 443,
            "protocol": "TCP",
            "service_name": "https",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }

        repository = ArangoNetworkTopologyRepository(
            host="localhost",
            port="8082",
            database="test_db",
            username="root",
            password="",
            graph_name="test_graph",
        )

        result = repository.get_port(443, "TCP")

        assert result is not None

    @patch("via_node.infrastructure.persistence.arango.arango_network_topology_repository.ArangoClient")
    def test_should_replace_dns_record_when_insert_fails(self, mock_client_class: Mock) -> None:
        from unittest.mock import MagicMock

        from arango.exceptions import DocumentInsertError

        mock_db = Mock()
        mock_graph = Mock()
        mock_collection = Mock()
        mock_client_class.return_value.db.return_value = mock_db
        mock_db.has_graph.return_value = True
        mock_db.graph.return_value = mock_graph
        mock_graph.vertex_collection.return_value = mock_collection

        mock_response = MagicMock()
        mock_response.is_success = False
        mock_response.error_code = 1210
        mock_response.error_message = "unique constraint violated"
        mock_request = MagicMock()

        mock_collection.insert.side_effect = DocumentInsertError(mock_response, mock_request)

        repository = ArangoNetworkTopologyRepository(
            host="localhost",
            port="8082",
            database="test_db",
            username="root",
            password="",
            graph_name="test_graph",
        )

        dns_record = DnsRecord(
            domain_name="example.com",
            record_type="A",
            ip_addresses=["192.168.1.1"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        repository.create_or_update_dns_record(dns_record)

        mock_collection.replace.assert_called_once()

    @patch("via_node.infrastructure.persistence.arango.arango_network_topology_repository.ArangoClient")
    def test_should_replace_port_when_insert_fails(self, mock_client_class: Mock) -> None:
        from unittest.mock import MagicMock

        from arango.exceptions import DocumentInsertError

        mock_db = Mock()
        mock_graph = Mock()
        mock_collection = Mock()
        mock_client_class.return_value.db.return_value = mock_db
        mock_db.has_graph.return_value = True
        mock_db.graph.return_value = mock_graph
        mock_graph.vertex_collection.return_value = mock_collection

        mock_response = MagicMock()
        mock_response.is_success = False
        mock_response.error_code = 1210
        mock_response.error_message = "unique constraint violated"
        mock_request = MagicMock()

        mock_collection.insert.side_effect = DocumentInsertError(mock_response, mock_request)

        repository = ArangoNetworkTopologyRepository(
            host="localhost",
            port="8082",
            database="test_db",
            username="root",
            password="",
            graph_name="test_graph",
        )

        port = Port(
            port_number=443,
            protocol="TCP",
            service_name="https",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        repository.create_or_update_port(port)

        mock_collection.replace.assert_called_once()

    @patch("via_node.infrastructure.persistence.arango.arango_network_topology_repository.ArangoClient")
    def test_should_handle_graph_create_error_gracefully(self, mock_client_class: Mock) -> None:
        from unittest.mock import MagicMock

        from arango.exceptions import GraphCreateError

        mock_db = Mock()
        mock_client_class.return_value.db.return_value = mock_db
        mock_db.has_graph.return_value = False

        mock_response = MagicMock()
        mock_response.is_success = False
        mock_response.error_code = 1925
        mock_response.error_message = "graph already exists"
        mock_request = MagicMock()

        mock_db.create_graph.side_effect = GraphCreateError(mock_response, mock_request)

        repository = ArangoNetworkTopologyRepository(
            host="localhost",
            port="8082",
            database="test_db",
            username="root",
            password="",
            graph_name="test_graph",
        )

        assert repository is not None

    @patch("via_node.infrastructure.persistence.arango.arango_network_topology_repository.ArangoClient")
    def test_should_handle_duplicate_edge_insert_gracefully(self, mock_client_class: Mock) -> None:
        from unittest.mock import MagicMock

        from arango.exceptions import DocumentInsertError

        mock_db = Mock()
        mock_graph = Mock()
        mock_edge_collection = Mock()
        mock_client_class.return_value.db.return_value = mock_db
        mock_db.has_graph.return_value = True
        mock_db.graph.return_value = mock_graph
        mock_graph.edge_collection.return_value = mock_edge_collection

        mock_response = MagicMock()
        mock_response.is_success = False
        mock_response.error_code = 1210
        mock_response.error_message = "unique constraint violated"
        mock_request = MagicMock()

        mock_edge_collection.insert.side_effect = DocumentInsertError(mock_response, mock_request)

        repository = ArangoNetworkTopologyRepository(
            host="localhost",
            port="8082",
            database="test_db",
            username="root",
            password="",
            graph_name="test_graph",
        )

        edge = NetworkTopologyEdge(
            source_id="example.com",
            target_id="443_TCP",
            edge_type="domain_to_port",
            metadata={},
            created_at=datetime.now(),
        )

        result = repository.create_edge(edge)

        assert result == edge
