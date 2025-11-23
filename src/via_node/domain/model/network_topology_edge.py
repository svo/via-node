from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, field_validator


class NetworkTopologyEdge(BaseModel):
    source_id: str
    target_id: str
    edge_type: str
    metadata: Dict[str, Any]
    created_at: datetime

    @field_validator("source_id")
    @classmethod
    def validate_source_id(cls, source_id: str) -> str:
        if not source_id or len(source_id.strip()) == 0:
            raise ValueError("Source ID cannot be empty")

        return source_id.strip()

    @field_validator("target_id")
    @classmethod
    def validate_target_id(cls, target_id: str) -> str:
        if not target_id or len(target_id.strip()) == 0:
            raise ValueError("Target ID cannot be empty")

        return target_id.strip()

    @field_validator("edge_type")
    @classmethod
    def validate_edge_type(cls, edge_type: str) -> str:
        valid_types = {"domain_to_port"}
        edge_type_lower = edge_type.lower()

        if edge_type_lower not in valid_types:
            raise ValueError(f"Edge type must be one of {valid_types}")

        return edge_type_lower
