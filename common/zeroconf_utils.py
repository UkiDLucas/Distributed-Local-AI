""" zeroconf_utils.py
Async Zeroconf-based service registration and discovery for AIKO agents.
"""

import socket
import asyncio
from zeroconf import ServiceInfo, ServiceBrowser
from zeroconf.asyncio import AsyncZeroconf

# Global reference to AsyncZeroconf instance (optional to reuse)
async_zeroconf = AsyncZeroconf()

# Register the current agent on the LAN using Async Zeroconf
# This avoids event loop conflicts and works with modern FastAPI servers

async def register_service(agent_name: str, port: int) -> AsyncZeroconf:
    local_ip = socket.gethostbyname(socket.gethostname())
    service = ServiceInfo(
        type_="_aikoagent._tcp.local.",
        name=f"{agent_name}._aikoagent._tcp.local.",
        addresses=[socket.inet_aton(local_ip)],
        port=port,
        properties={"role": "initiator"},
        server=f"{agent_name}.local.",
    )
    await async_zeroconf.async_register_service(service)
    print(f"[{agent_name}] Registered on LAN at {local_ip}:{port}")
    return async_zeroconf


# Discover another agent on the LAN by name (e.g., PONG)
# Returns the URL for sending messages once found

async def discover_target(target_agent_name: str, timeout: int = 3) -> str:
    class Listener:
        def __init__(self):
            self.info = None

        def add_service(self, zc, type_, name):
            if target_agent_name in name:
                self.info = zc.get_service_info(type_, name)

    listener = Listener()
    ServiceBrowser(async_zeroconf.zeroconf, "_aikoagent._tcp.local.", listener)

    for _ in range(timeout * 10):
        await asyncio.sleep(0.1)
        if listener.info:
            ip = socket.inet_ntoa(listener.info.addresses[0])
            port = listener.info.port
            url = f"http://{ip}:{port}/handle"
            print(f"Discovered {target_agent_name} at {url}")
            return url

    print(f"Could not discover {target_agent_name}.")
    return None
