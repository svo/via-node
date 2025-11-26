from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, field_validator


class Host(BaseModel):
    ip_address: str
    hostname: str
    os_type: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    @field_validator("ip_address")
    @classmethod
    def validate_ip_address(cls, ip_address: str) -> str:
        ip = ip_address.strip()
        if not ip:
            raise ValueError("IP address cannot be empty")

        if ":" in ip:
            cls._validate_ipv6(ip)
        else:
            cls._validate_ipv4(ip)

        return ip

    @staticmethod
    def _validate_ipv6(ip: str) -> None:
        if not all(c in "0123456789abcdefABCDEF::" for c in ip):
            raise ValueError("Invalid IPv6 address format")

    @staticmethod
    def _validate_ipv4(ip: str) -> None:
        parts = ip.split(".")
        if len(parts) != 4:
            raise ValueError("Invalid IPv4 address format")

        for part in parts:
            Host._validate_ipv4_octet(part)

    @staticmethod
    def _validate_ipv4_octet(part: str) -> None:
        try:
            num = int(part)
        except ValueError:
            raise ValueError("IPv4 address must contain numeric octets")

        if not (0 <= num <= 255):
            raise ValueError("IPv4 octets must be between 0 and 255")

    @field_validator("hostname")
    @classmethod
    def validate_hostname(cls, hostname: str) -> str:
        if not hostname or len(hostname.strip()) == 0:
            raise ValueError("Hostname cannot be empty")

        if len(hostname) > 253:
            raise ValueError("Hostname cannot exceed 253 characters")

        return hostname.strip().lower()

    @field_validator("os_type")
    @classmethod
    def validate_os_type(cls, os_type: str) -> str:
        if not os_type or len(os_type.strip()) == 0:
            raise ValueError("OS type cannot be empty")

        return os_type.strip()

    @field_validator("metadata", mode="before")
    @classmethod
    def validate_metadata(cls, metadata: Any) -> Optional[Dict[str, Any]]:
        if metadata is None:
            return None
        if isinstance(metadata, dict):
            return metadata
        raise ValueError("Metadata must be a dictionary")
