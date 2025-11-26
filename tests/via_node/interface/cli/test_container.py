from unittest.mock import patch

from lagom import Container

from via_node.interface.cli.container import create_container


class TestContainer:
    @patch("via_node.interface.cli.container.ApplicationSettings")
    @patch("via_node.interface.cli.container.ArangoNetworkTopologyRepository")
    def test_should_create_container(self, mock_arango_repo: type, mock_settings: type) -> None:
        container = create_container()

        assert isinstance(container, Container)

    @patch("via_node.interface.cli.container.ApplicationSettings")
    @patch("via_node.interface.cli.container.ArangoNetworkTopologyRepository")
    def test_should_call_application_settings(self, mock_arango_repo: type, mock_settings: type) -> None:
        create_container()

        mock_settings.assert_called_once()

    @patch("via_node.interface.cli.container.ApplicationSettings")
    @patch("via_node.interface.cli.container.ArangoNetworkTopologyRepository")
    def test_should_configure_arango_repository_with_settings(
        self, mock_arango_repo: type, mock_settings: type
    ) -> None:
        mock_settings_instance = mock_settings.return_value
        mock_settings_instance.arango_host = "testhost"
        mock_settings_instance.arango_port = "9999"
        mock_settings_instance.arango_database = "testdb"
        mock_settings_instance.arango_username = "testuser"
        mock_settings_instance.arango_password = "testpass"
        mock_settings_instance.arango_graph_name = "testgraph"
        mock_settings_instance.arango_auto_create_database = True

        create_container()

        assert mock_settings.called

    @patch("via_node.interface.cli.container.ApplicationSettings")
    @patch("via_node.interface.cli.container.ArangoNetworkTopologyRepository")
    def test_should_create_arango_repository_when_repository_is_resolved(
        self, mock_arango_repo: type, mock_settings: type
    ) -> None:
        from via_node.domain.repository.network_topology_repository import NetworkTopologyRepository

        mock_settings_instance = mock_settings.return_value
        mock_settings_instance.arango_host = "testhost"
        mock_settings_instance.arango_port = "9999"
        mock_settings_instance.arango_database = "testdb"
        mock_settings_instance.arango_username = "testuser"
        mock_settings_instance.arango_password = "testpass"
        mock_settings_instance.arango_graph_name = "testgraph"
        mock_settings_instance.arango_auto_create_database = True

        container = create_container()
        container[NetworkTopologyRepository]

        mock_arango_repo.assert_called_once_with(
            host="testhost",
            port="9999",
            database="testdb",
            username="testuser",
            password="testpass",
            graph_name="testgraph",
            auto_create_database=True,
        )
