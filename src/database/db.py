import asyncio
from prisma import Prisma
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.client: Optional[Prisma] = None
        self._connected = False

    async def connect(self):
        if not self._connected:
            try:
                self.client = Prisma()
                await self.client.connect()
                self._connected = True
                logger.info("Database connected successfully")
            except Exception as e:
                logger.error(f"Failed to connect to database: {e}")
                raise

    async def disconnect(self):
        if self._connected and self.client:
            try:
                await self.client.disconnect()
                self._connected = False
                logger.info("Database disconnected")
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")

    def get_client(self) -> Prisma:
        if not self._connected or not self.client:
            raise RuntimeError("Database not connected.")
        return self.client
    
db_manager = DatabaseManager()