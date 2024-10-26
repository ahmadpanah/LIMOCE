# src/migration_coordinator.py
from dataclasses import dataclass
from datetime import datetime
import asyncio
from typing import Dict, Optional
import logging

@dataclass
class MigrationState:
    source_id: str
    target_id: str
    container_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "pending"
    error: Optional[str] = None

class MigrationCoordinator:
    def __init__(self, container_manager, network_manager):
        self.container_manager = container_manager
        self.network_manager = network_manager
        self.migrations: Dict[str, MigrationState] = {}
        self.logger = logging.getLogger("limoce.migration")

    async def start_migration(self, 
                            source_id: str, 
                            target_id: str, 
                            container_id: str) -> str:
        """Start container migration process."""
        migration_id = f"migration_{int(datetime.now().timestamp())}"
        
        self.migrations[migration_id] = MigrationState(
            source_id=source_id,
            target_id=target_id,
            container_id=container_id,
            start_time=datetime.now()
        )

        try:
            # Create checkpoint
            checkpoint_success = await self.create_checkpoint(migration_id)
            if not checkpoint_success:
                raise Exception("Checkpoint creation failed")

            # Transfer checkpoint
            transfer_success = await self.transfer_checkpoint(migration_id)
            if not transfer_success:
                raise Exception("Checkpoint transfer failed")

            # Restore container
            restore_success = await self.restore_container(migration_id)
            if not restore_success:
                raise Exception("Container restore failed")

            # Verify migration
            verify_success = await self.verify_migration(migration_id)
            if not verify_success:
                raise Exception("Migration verification failed")

            # Update migration state
            self.migrations[migration_id].status = "completed"
            self.migrations[migration_id].end_time = datetime.now()
            
            # Update metrics
            duration = (self.migrations[migration_id].end_time - 
                       self.migrations[migration_id].start_time).total_seconds()
            self.container_manager.migration_duration.set(duration)
            self.container_manager.migration_counter.inc()

            return migration_id

        except Exception as e:
            self.logger.error(f"Migration failed: {e}")
            self.migrations[migration_id].status = "failed"
            self.migrations[migration_id].error = str(e)
            self.migrations[migration_id].end_time = datetime.now()
            return migration_id

    async def create_checkpoint(self, migration_id: str) -> bool:
        """Create container checkpoint."""
        migration = self.migrations[migration_id]
        return await asyncio.get_event_loop().run_in_executor(
            None,
            self.container_manager.checkpoint_container,
            migration.container_id,
            f"/tmp/checkpoints/{migration_id}"
        )

    async def transfer_checkpoint(self, migration_id: str) -> bool:
        """Transfer checkpoint to target device."""
        migration = self.migrations[migration_id]
        checkpoint_data = {
            "migration_id": migration_id,
            "container_id": migration.container_id,
            "checkpoint_path": f"/tmp/checkpoints/{migration_id}"
        }
        
        result = await self.network_manager.transfer_checkpoint(
            migration.source_id,
            migration.target_id,
            checkpoint_data
        )
        return result is not None

    async def restore_container(self, migration_id: str) -> bool:
        """Restore container on target device."""
        migration = self.migrations[migration_id]
        return await asyncio.get_event_loop().run_in_executor(
            None,
            self.container_manager.restore_container,
            migration.container_id,
            f"/tmp/checkpoints/{migration_id}"
        )

    async def verify_migration(self, migration_id: str) -> bool:
        """Verify migration success."""
        migration = self.migrations[migration_id]
        
        # Get container stats from target device
        stats = await asyncio.get_event_loop().run_in_executor(
            None,
            self.container_manager.get_container_stats,
            migration.container_id
        )
        
        return bool(stats)