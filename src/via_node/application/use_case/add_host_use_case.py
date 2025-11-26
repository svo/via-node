from datetime import datetime
from typing import Any, Dict, Optional

from via_node.domain.model.host import Host
from via_node.domain.repository.network_topology_repository import NetworkTopologyRepository


class AddHostUseCase:
    def __init__(self, repository: NetworkTopologyRepository) -> None:
        self._repository = repository

    def execute(
        self,
        ip_address: str,
        hostname: str,
        os_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Host:
        now = datetime.now()

        host = Host(
            ip_address=ip_address,
            hostname=hostname,
            os_type=os_type,
            metadata=metadata or {},
            created_at=now,
            updated_at=now,
        )

        return self._repository.create_or_update_host(host)
