from datetime import datetime
from typing import List

from pydantic import BaseModel, field_validator


class DnsRecord(BaseModel):
    domain_name: str
    record_type: str
    ip_addresses: List[str]
    created_at: datetime
    updated_at: datetime

    @field_validator("domain_name")
    @classmethod
    def validate_domain_name(cls, domain_name: str) -> str:
        if not domain_name or len(domain_name.strip()) == 0:
            raise ValueError("Domain name cannot be empty")

        if len(domain_name) > 253:
            raise ValueError("Domain name cannot exceed 253 characters")

        return domain_name.strip().lower()

    @field_validator("record_type")
    @classmethod
    def validate_record_type(cls, record_type: str) -> str:
        valid_types = {"A", "AAAA", "CNAME", "MX", "NS", "TXT", "SOA", "PTR"}
        record_type_upper = record_type.upper()

        if record_type_upper not in valid_types:
            raise ValueError(f"Record type must be one of {valid_types}")

        return record_type_upper

    @field_validator("ip_addresses")
    @classmethod
    def validate_ip_addresses(cls, ip_addresses: List[str]) -> List[str]:
        if not ip_addresses:
            return ip_addresses

        return [ip.strip() for ip in ip_addresses]
