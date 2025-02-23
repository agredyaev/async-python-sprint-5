from typing import Any

import ipaddress

from pydantic import BaseModel, field_validator


class NetworkConfig(BaseModel):
    blacklist: Any

    @field_validator("blacklist", mode="before")
    @classmethod
    def validate_networks(cls, v: list[str]) -> list[ipaddress.IPv4Network | ipaddress.IPv6Network]:
        return [ipaddress.ip_network(net, strict=False) for net in v]


class IPChecker:
    __slots__ = ("networks",)

    def __init__(self, config: NetworkConfig):
        self.networks: list[ipaddress.IPv4Network | ipaddress.IPv6Network] = config.blacklist

    def is_blocked(self, ip: str) -> bool:
        client_ip: ipaddress.IPv4Address | ipaddress.IPv6Address = ipaddress.ip_address(ip)
        return any(client_ip in net for net in self.networks)
