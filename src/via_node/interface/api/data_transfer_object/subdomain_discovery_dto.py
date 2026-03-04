from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class SubdomainDiscoveryApiRequestDataTransferObject(BaseModel):
    domain_name: str = Field(..., description="Domain name to discover subdomains for")
    dictionary: Optional[List[str]] = Field(None, description="Optional list of subdomain prefixes to test")


class SubdomainDiscoveryResultApiResponseDataTransferObject(BaseModel):
    domain_name: str = Field(..., description="Full subdomain name discovered")
    record_type: str = Field(..., description="DNS record type")
    values: List[str] = Field(..., description="Resolved IP addresses")
    ttl: Optional[int] = Field(None, description="Time to live in seconds")
    discovered_at: datetime = Field(..., description="Discovery timestamp")

    @classmethod
    def from_domain_model(cls, domain_model: Any) -> SubdomainDiscoveryResultApiResponseDataTransferObject:
        return cls(
            domain_name=domain_model.domain_name,
            record_type=domain_model.record_type.value,
            values=domain_model.values,
            ttl=domain_model.ttl,
            discovered_at=domain_model.discovered_at,
        )


class SubdomainDiscoveryApiResponseDataTransferObject(BaseModel):
    subdomains: List[SubdomainDiscoveryResultApiResponseDataTransferObject] = Field(
        ..., description="List of discovered subdomains"
    )
