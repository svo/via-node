from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class Port(BaseModel):
    port_number: int
    protocol: str
    service_name: Optional[str]
    created_at: datetime
    updated_at: datetime

    @field_validator("port_number")
    @classmethod
    def validate_port_number(cls, port_number: int) -> int:
        if not (1 <= port_number <= 65535):
            raise ValueError("Port number must be between 1 and 65535")

        return port_number

    @field_validator("protocol")
    @classmethod
    def validate_protocol(cls, protocol: str) -> str:
        valid_protocols = {"TCP", "UDP"}
        protocol_upper = protocol.upper()

        if protocol_upper not in valid_protocols:
            raise ValueError(f"Protocol must be one of {valid_protocols}")

        return protocol_upper
