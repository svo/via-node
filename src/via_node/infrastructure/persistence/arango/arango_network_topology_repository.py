from datetime import datetime
from typing import List, Optional

from arango import ArangoClient
from arango.database import StandardDatabase
from arango.exceptions import DocumentInsertError, GraphCreateError

from via_node.domain.model.dns_record import DnsRecord
from via_node.domain.model.dns_record_discovery import DnsRecordDiscovery
from via_node.domain.model.host import Host
from via_node.domain.model.network_topology_edge import NetworkTopologyEdge
from via_node.domain.model.port import Port
from via_node.domain.model.port_scan_result import PortScanResult
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
        auto_create_database: bool = True,
    ) -> None:
        self._host = host
        self._port = port
        self._database_name = database
        self._username = username
        self._password = password
        self._graph_name = graph_name
        self._auto_create_database = auto_create_database

        self._dns_collection_name = "dns_records"
        self._port_collection_name = "ports"
        self._hosts_collection_name = "hosts"
        self._dns_discoveries_collection_name = "dns_discoveries"
        self._port_scan_results_collection_name = "port_scan_results"
        self._edge_collection_name = "domain_port_edges"
        self._dns_resolves_to_host_edge_collection_name = "dns_resolves_to_host_edges"

        self._client = ArangoClient(hosts=f"http://{self._host}:{self._port}")
        self._db = self._initialize_connection()
        self._initialize_graph()

    def _initialize_connection(self) -> StandardDatabase:
        db = self._client.db(self._database_name, username=self._username, password=self._password)

        if self._auto_create_database:  # pragma: no cover
            try:
                db.collections()
            except Exception as e:
                if "1228" in str(e):
                    sys_db = self._client.db("_system", username=self._username, password=self._password)
                    sys_db.create_database(self._database_name)
                    db = self._client.db(self._database_name, username=self._username, password=self._password)
                else:
                    raise

        return db

    def _initialize_graph(self) -> None:  # pragma: no cover
        if self._db.has_graph(self._graph_name):
            return

        try:
            graph = self._db.create_graph(self._graph_name)

            graph.create_vertex_collection(self._dns_collection_name)  # type: ignore[union-attr]
            graph.create_vertex_collection(self._port_collection_name)  # type: ignore[union-attr]
            graph.create_vertex_collection(self._hosts_collection_name)  # type: ignore[union-attr]
            graph.create_vertex_collection(self._dns_discoveries_collection_name)  # type: ignore[union-attr]
            graph.create_vertex_collection(self._port_scan_results_collection_name)  # type: ignore[union-attr]

            graph.create_edge_definition(  # type: ignore[union-attr]
                edge_collection=self._edge_collection_name,
                from_vertex_collections=[self._dns_collection_name],
                to_vertex_collections=[self._port_collection_name],
            )

            graph.create_edge_definition(  # type: ignore[union-attr]
                edge_collection=self._dns_resolves_to_host_edge_collection_name,
                from_vertex_collections=[self._dns_collection_name],
                to_vertex_collections=[self._hosts_collection_name],
            )
        except GraphCreateError:
            pass

    def create_or_update_dns_record(self, dns_record: DnsRecord) -> DnsRecord:  # pragma: no cover
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
        except DocumentInsertError:  # pragma: no cover
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
        except DocumentInsertError:  # pragma: no cover
            collection.replace(document)

        return port

    def create_edge(self, edge: NetworkTopologyEdge) -> NetworkTopologyEdge:  # pragma: no cover
        graph = self._db.graph(self._graph_name)

        if edge.edge_type == "dns_resolves_to_host":  # pragma: no cover
            edge_collection = graph.edge_collection(self._dns_resolves_to_host_edge_collection_name)
            from_vertex = f"{self._dns_collection_name}/{edge.source_id}"
            to_vertex = f"{self._hosts_collection_name}/{edge.target_id}"
        else:
            edge_collection = graph.edge_collection(self._edge_collection_name)
            from_vertex = f"{self._dns_collection_name}/{edge.source_id}"
            to_vertex = f"{self._port_collection_name}/{edge.target_id}"

        document = {
            "_from": from_vertex,
            "_to": to_vertex,
            "source_id": edge.source_id,
            "target_id": edge.target_id,
            "edge_type": edge.edge_type,
            "metadata": edge.metadata,
            "created_at": edge.created_at.isoformat(),
        }

        try:
            edge_collection.insert(document)
        except DocumentInsertError:  # pragma: no cover
            pass

        return edge

    def get_dns_record(self, domain_name: str) -> Optional[DnsRecord]:  # pragma: no cover
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

    def create_or_update_host(self, host: Host) -> Host:  # pragma: no cover
        graph = self._db.graph(self._graph_name)
        collection = graph.vertex_collection(self._hosts_collection_name)

        document = {
            "_key": host.ip_address,
            "ip_address": host.ip_address,
            "hostname": host.hostname,
            "os_type": host.os_type,
            "metadata": host.metadata,
            "created_at": host.created_at.isoformat(),
            "updated_at": host.updated_at.isoformat(),
        }

        try:
            collection.insert(document)
        except DocumentInsertError:  # pragma: no cover
            collection.replace(document)

        return host

    def get_host(self, ip_address: str) -> Optional[Host]:  # pragma: no cover
        graph = self._db.graph(self._graph_name)
        collection = graph.vertex_collection(self._hosts_collection_name)

        if not collection.has(ip_address):
            return None

        document = collection.get(ip_address)

        return Host(
            ip_address=document["ip_address"],  # type: ignore[index]
            hostname=document["hostname"],  # type: ignore[index]
            os_type=document["os_type"],  # type: ignore[index]
            metadata=document.get("metadata"),  # type: ignore[union-attr]
            created_at=datetime.fromisoformat(document["created_at"]),  # type: ignore[index]
            updated_at=datetime.fromisoformat(document["updated_at"]),  # type: ignore[index]
        )

    def create_or_update_dns_record_discovery(
        self, dns_record_discovery: DnsRecordDiscovery
    ) -> DnsRecordDiscovery:  # pragma: no cover
        graph = self._db.graph(self._graph_name)
        dns_collection = graph.vertex_collection(self._dns_discoveries_collection_name)

        document_key = f"{dns_record_discovery.domain_name}_{dns_record_discovery.record_type.value}"

        document = {
            "_key": document_key,
            "domain_name": dns_record_discovery.domain_name,
            "record_type": dns_record_discovery.record_type.value,
            "values": dns_record_discovery.values,
            "ttl": dns_record_discovery.ttl,
            "discovered_at": dns_record_discovery.discovered_at.isoformat(),
        }

        try:
            dns_collection.insert(document)
        except DocumentInsertError:  # pragma: no cover
            dns_collection.replace(document)

        return dns_record_discovery

    def get_dns_record_discoveries(self, domain_name: str) -> List[DnsRecordDiscovery]:  # pragma: no cover
        query = f"""
            FOR doc IN {self._dns_discoveries_collection_name}
            FILTER doc.domain_name == @domain_name
            RETURN doc
        """

        results = self._db.aql.execute(  # nosemgrep: sqlalchemy-execute-raw-query  # type: ignore[misc]
            query, bind_vars={"domain_name": domain_name}
        )

        discoveries: List[DnsRecordDiscovery] = []

        for result in results:  # type: ignore[union-attr]
            discoveries.append(
                DnsRecordDiscovery(
                    domain_name=result["domain_name"],
                    record_type=result["record_type"],
                    values=result["values"],
                    ttl=result.get("ttl"),
                    discovered_at=datetime.fromisoformat(result["discovered_at"]),
                )
            )

        return discoveries

    def create_or_update_port_scan_result(self, port_scan_result: PortScanResult) -> PortScanResult:  # pragma: no cover
        graph = self._db.graph(self._graph_name)
        scan_collection = graph.vertex_collection(self._port_scan_results_collection_name)

        document_key = f"{port_scan_result.target_ip}_{port_scan_result.protocol}_" f"{port_scan_result.port_number}"

        document = {
            "_key": document_key,
            "target_ip": port_scan_result.target_ip,
            "port_number": port_scan_result.port_number,
            "protocol": port_scan_result.protocol,
            "state": port_scan_result.state.value,
            "service_name": port_scan_result.service_name,
            "service_version": port_scan_result.service_version,
            "scanned_at": port_scan_result.scanned_at.isoformat(),
        }

        try:
            scan_collection.insert(document)
        except DocumentInsertError:  # pragma: no cover
            scan_collection.replace(document)

        return port_scan_result

    def get_port_scan_results(self, target_ip: str) -> List[PortScanResult]:  # pragma: no cover
        query = f"""
            FOR doc IN {self._port_scan_results_collection_name}
            FILTER doc.target_ip == @target_ip
            RETURN doc
        """

        results = self._db.aql.execute(  # nosemgrep: sqlalchemy-execute-raw-query  # type: ignore[misc]
            query, bind_vars={"target_ip": target_ip}
        )

        scan_results: List[PortScanResult] = []

        for result in results:  # type: ignore[union-attr]
            scan_results.append(
                PortScanResult(
                    target_ip=result["target_ip"],
                    port_number=result["port_number"],
                    protocol=result["protocol"],
                    state=result["state"],
                    service_name=result.get("service_name"),
                    service_version=result.get("service_version"),
                    scanned_at=datetime.fromisoformat(result["scanned_at"]),
                )
            )

        return scan_results
