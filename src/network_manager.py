# src/network_manager.py
import asyncio
import aiohttp
import logging
from typing import Dict, Optional

class NetworkManager:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.logger = logging.getLogger("limoce.network")
        self.sessions: Dict[str, aiohttp.ClientSession] = {}

    async def create_session(self, device_id: str):
        """Create a new HTTP session for a device."""
        if device_id not in self.sessions:
            self.sessions[device_id] = aiohttp.ClientSession()

    async def close_session(self, device_id: str):
        """Close an HTTP session."""
        if device_id in self.sessions:
            await self.sessions[device_id].close()
            del self.sessions[device_id]

    async def send_heartbeat(self, 
                           source_id: str, 
                           target_id: str, 
                           data: Dict) -> Optional[Dict]:
        """Send heartbeat message to target device."""
        try:
            async with self.sessions[source_id].post(
                f"http://{self.host}:{self.port}/heartbeat",
                json={"source": source_id, "target": target_id, "data": data}
            ) as response:
                return await response.json()
        except Exception as e:
            self.logger.error(f"Failed to send heartbeat: {e}")
            return None

    async def transfer_checkpoint(self, 
                                source_id: str, 
                                target_id: str, 
                                checkpoint_data: Dict) -> Optional[Dict]:
        """Transfer container checkpoint to target device."""
        try:
            async with self.sessions[source_id].post(
                f"http://{self.host}:{self.port}/transfer_checkpoint",
                json={
                    "source": source_id, 
                    "target": target_id, 
                    "checkpoint": checkpoint_data
                }
            ) as response:
                return await response.json()
        except Exception as e:
            self.logger.error(f"Failed to transfer checkpoint: {e}")
            return None