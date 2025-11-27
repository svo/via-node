from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, field_validator


class DnsRecordType(Enum):
    A = "A"
    AAAA = "AAAA"
    CNAME = "CNAME"
    MX = "MX"
    SOA = "SOA"
    NS = "NS"
    TXT = "TXT"


class DnsRecordDiscovery(BaseModel):
    domain_name: str
    record_type: DnsRecordType
    values: List[str]
    ttl: Optional[int] = None
    discovered_at: datetime

    @field_validator("domain_name")
    @classmethod
    def validate_domain_name(cls, domain_name: str) -> str:
        if not domain_name or len(domain_name.strip()) == 0:
            raise ValueError("Domain name cannot be empty")
        return domain_name.strip().lower()

    @field_validator("values")
    @classmethod
    def validate_values(cls, values: List[str]) -> List[str]:
        if not values or len(values) == 0:
            raise ValueError("Values list cannot be empty")
        return [v.strip() for v in values if v.strip()]

    @field_validator("ttl")
    @classmethod
    def validate_ttl(cls, ttl: Optional[int]) -> Optional[int]:
        if ttl is not None and ttl < 0:
            raise ValueError("TTL cannot be negative")
        return ttl
