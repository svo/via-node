from datetime import datetime
from typing import Optional

from arango import ArangoClient
from arango.database import StandardDatabase
from arango.exceptions import DocumentInsertError, GraphCreateError

from via_node.domain.model.dns_record import DnsRecord
from via_node.domain.model.network_topology_edge import NetworkTopologyEdge
from via_node.domain.model.port import Port
from via_node.domain.repository.network_topology_repository import NetworkTopologyRepository


class ArangoNetworkTopologyRepository(NetworkTopologyRepository):
    def __init__(
        self,
        host: str,
        port: str,
        database: str,
        username: str,
        password: str,
        graph_name: str,
    ) -> None:
        self._host = host
        self._port = port
        self._database_name = database
        self._username = username
        self._password = password
        self._graph_name = graph_name

        self._dns_collection_name = "dns_records"
        self._port_collection_name = "ports"
        self._edge_collection_name = "domain_port_edges"

        self._db = self._initialize_connection()
        self._initialize_graph()

    def _initialize_connection(self) -> StandardDatabase:
        client = ArangoClient(hosts=f"http://{self._host}:{self._port}")
        return client.db(self._database_name, username=self._username, password=self._password)

    def _initialize_graph(self) -> None:
        if self._db.has_graph(self._graph_name):
            return

        try:
            graph = self._db.create_graph(self._graph_name)

            graph.create_vertex_collection(self._dns_collection_name)  # type: ignore[union-attr]
            graph.create_vertex_collection(self._port_collection_name)  # type: ignore[union-attr]

            graph.create_edge_definition(  # type: ignore[union-attr]
                edge_collection=self._edge_collection_name,
                from_vertex_collections=[self._dns_collection_name],
                to_vertex_collections=[self._port_collection_name],
            )
        except GraphCreateError:
            pass

    def create_or_update_dns_record(self, dns_record: DnsRecord) -> DnsRecord:
        graph = self._db.graph(self._graph_name)
        collection = graph.vertex_collection(self._dns_collection_name)

        document = {
            "_key": dns_record.domain_name,
            "domain_name": dns_record.domain_name,
            "record_type": dns_record.record_type,
            "ip_addresses": dns_record.ip_addresses,
            "created_at": dns_record.created_at.isoformat(),
            "updated_at": dns_record.updated_at.isoformat(),
        }

        try:
            collection.insert(document)
        except DocumentInsertError:
            collection.replace(document)

        return dns_record

    def create_or_update_port(self, port: Port) -> Port:
        graph = self._db.graph(self._graph_name)
        collection = graph.vertex_collection(self._port_collection_name)

        document = {
            "_key": f"{port.port_number}_{port.protocol}",
            "port_number": port.port_number,
            "protocol": port.protocol,
            "service_name": port.service_name,
            "created_at": port.created_at.isoformat(),
            "updated_at": port.updated_at.isoformat(),
        }

        try:
            collection.insert(document)
        except DocumentInsertError:
            collection.replace(document)

        return port

    def create_edge(self, edge: NetworkTopologyEdge) -> NetworkTopologyEdge:
        graph = self._db.graph(self._graph_name)
        edge_collection = graph.edge_collection(self._edge_collection_name)

        document = {
            "_from": f"{self._dns_collection_name}/{edge.source_id}",
            "_to": f"{self._port_collection_name}/{edge.target_id}",
            "source_id": edge.source_id,
            "target_id": edge.target_id,
            "edge_type": edge.edge_type,
            "metadata": edge.metadata,
            "created_at": edge.created_at.isoformat(),
        }

        try:
            edge_collection.insert(document)
        except DocumentInsertError:
            pass

        return edge

    def get_dns_record(self, domain_name: str) -> Optional[DnsRecord]:
        graph = self._db.graph(self._graph_name)
        collection = graph.vertex_collection(self._dns_collection_name)

        if not collection.has(domain_name):
            return None

        document = collection.get(domain_name)

        return DnsRecord(
            domain_name=document["domain_name"],  # type: ignore[index]
            record_type=document["record_type"],  # type: ignore[index]
            ip_addresses=document["ip_addresses"],  # type: ignore[index]
            created_at=datetime.fromisoformat(document["created_at"]),  # type: ignore[index]
            updated_at=datetime.fromisoformat(document["updated_at"]),  # type: ignore[index]
        )

    def get_port(self, port_number: int, protocol: str) -> Optional[Port]:
        graph = self._db.graph(self._graph_name)
        collection = graph.vertex_collection(self._port_collection_name)

        port_key = f"{port_number}_{protocol}"

        if not collection.has(port_key):
            return None

        document = collection.get(port_key)

        return Port(
            port_number=document["port_number"],  # type: ignore[index]
            protocol=document["protocol"],  # type: ignore[index]
            service_name=document.get("service_name"),  # type: ignore[union-attr]
            created_at=datetime.fromisoformat(document["created_at"]),  # type: ignore[index]
            updated_at=datetime.fromisoformat(document["updated_at"]),  # type: ignore[index]
        )
