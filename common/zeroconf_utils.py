""" zeroconf_utils.py
Async Zeroconf-based service registration and discovery for AIKO agents.
"""

import socket
import asyncio
from zeroconf import ServiceInfo, ServiceBrowser, InterfaceChoice
from zeroconf.asyncio import AsyncZeroconf

# Create a separate AsyncZeroconf instance per agent

def get_async_zeroconf():
    return AsyncZeroconf(interfaces=InterfaceChoice.Default)

# Register the current agent on the LAN using Async Zeroconf
async def register_service(agent_name: str, port: int) -> AsyncZeroconf:
    local_ip = socket.gethostbyname(socket.gethostname())
    hostname = socket.gethostname()
    async_zeroconf = get_async_zeroconf()
    service = ServiceInfo(
        type_="_aikoagent._tcp.local.",
        name=f"{agent_name}_{hostname}._aikoagent._tcp.local.",
        addresses=[socket.inet_aton(local_ip)],
        port=port,
        properties={"role": "initiator"},
        server=f"{agent_name}.local.",
    )
    await async_zeroconf.async_register_service(service, allow_name_change=True)
    print(f"[{agent_name}] Registered on LAN at {local_ip}:{port}")
    return async_zeroconf

# Discover another agent on the LAN by name (e.g., PONG)
async def discover_target(target_agent_name: str, timeout: int = 3) -> str:
    async_zeroconf = get_async_zeroconf()

    class Listener:
        def __init__(self):
            self.info = None

        def add_service(self, zc, type_, name):
            if target_agent_name.lower() in name.lower():
                self.info = zc.get_service_info(type_, name)

        def update_service(self, zc, type_, name):
            pass  # Avoid FutureWarning about missing method

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

    print(f"[WARNING]: Could not discover {target_agent_name}.")
    return None
