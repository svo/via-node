import uuid

from via_node.domain.model.coconut import Coconut
from via_node.domain.repository.coconut_repository import CoconutQueryRepository
from via_node.infrastructure.persistence.in_memory.shared_storage import SharedStorage


class InMemoryCoconutQueryRepository(CoconutQueryRepository):
    def __init__(self) -> None:
        self._storage = SharedStorage()

    def read(self, id: uuid.UUID) -> Coconut:
        if not isinstance(id, uuid.UUID):
            raise ValueError("Invalid UUID")

        coconut = self._storage.get_coconut(id)

        if coconut is None:
            raise Exception("Coconut not found")

        return coconut

    def add_to_storage(self, coconut: Coconut) -> None:
        if coconut.id is None:
            raise ValueError("Coconut ID cannot be None")

        self._storage.add_coconut(coconut)
