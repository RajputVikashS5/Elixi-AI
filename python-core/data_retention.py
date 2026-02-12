#!/usr/bin/env python3
"""
Data Retention & Lifecycle Management Module for ELIXI AI
Handles automatic cleanup, archival, and retention policies.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pymongo import MongoClient

logger = logging.getLogger(__name__)


class DataRetentionManager:
    """Manages data retention policies and lifecycle management."""
    
    # Default retention policies (in days)
    DEFAULT_POLICIES = {
        "short_term": {
            "retention_days": 30,
            "action": "delete",
            "description": "Short-term memories, removed after 30 days"
        },
        "conversations": {
            "retention_days": 90,
            "action": "archive",
            "archive_collection": "archived_conversations",
            "description": "Conversation history, archived after 90 days"
        },
        "important": {
            "retention_days": 365,
            "action": "archive",
            "archive_collection": "archived_memories",
            "description": "Important memories, archived after 1 year"
        },
        "events": {
            "retention_days": 60,
            "action": "aggregate",
            "aggregation_window": "weekly",
            "description": "Events aggregated monthly, kept for 60 days"
        },
        "habits": {
            "retention_days": 180,
            "action": "keep",
            "description": "Habits data, kept for 180 days"
        },
        "preferences": {
            "retention_days": None,
            "action": "keep",
            "description": "User preferences, kept indefinitely"
        },
        "commands": {
            "retention_days": None,
            "action": "keep",
            "description": "Custom commands, kept indefinitely"
        },
        "workflows": {
            "retention_days": None,
            "action": "keep",
            "description": "Workflows, kept indefinitely"
        }
    }
    
    def __init__(self, db, archive_db=None):
        """
        Initialize the data retention manager.
        
        Args:
            db: Main MongoDB database instance
            archive_db: Optional separate database for archives
        """
        self.db = db
        self.archive_db = archive_db or db  # Use same DB if not specified
        self.policies = self.DEFAULT_POLICIES.copy()
        self.retention_log = []
    
    def set_retention_policy(self, memory_type: str, retention_days: Optional[int], 
                           action: str = "delete", **kwargs) -> Dict:
        """
        Set or update retention policy for a memory type.
        
        Args:
            memory_type: Type of memory (e.g., 'short_term', 'conversations')
            retention_days: Days to retain (None = indefinite)
            action: Action to take ('delete', 'archive', 'aggregate', 'keep')
            **kwargs: Additional policy parameters
            
        Returns:
            Dict with policy confirmation
        """
        try:
            policy = {
                "retention_days": retention_days,
                "action": action,
                "updated_at": datetime.utcnow(),
                **kwargs
            }
            
            self.policies[memory_type] = policy
            logger.info(f"✓ Set retention policy for '{memory_type}': {retention_days} days, action: {action}")
            
            return {
                "status": "success",
                "memory_type": memory_type,
                "policy": policy
            }
            
        except Exception as e:
            logger.error(f"✗ Error setting retention policy: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_retention_policy(self, memory_type: str) -> Dict:
        """
        Retrieve retention policy for a memory type.
        
        Args:
            memory_type: Type of memory
            
        Returns:
            Dict with policy details
        """
        if memory_type not in self.policies:
            return {"error": f"No policy found for '{memory_type}'"}
        
        return self.policies[memory_type]
    
    def cleanup_expired_data(self, memory_type: Optional[str] = None) -> Dict:
        """
        Execute cleanup based on retention policies.
        
        Args:
            memory_type: Specific type to clean (None = all types)
            
        Returns:
            Dict with cleanup results
        """
        logger.info(f"Starting data cleanup (type: {memory_type or 'all'})...")
        cleanup_results = {}
        
        try:
            types_to_clean = [memory_type] if memory_type else list(self.policies.keys())
            
            for mem_type in types_to_clean:
                policy = self.policies.get(mem_type)
                if not policy:
                    continue
                
                action = policy.get("action", "keep")
                
                if action == "delete":
                    cleanup_results[mem_type] = self._delete_expired(mem_type, policy)
                elif action == "archive":
                    cleanup_results[mem_type] = self._archive_expired(mem_type, policy)
                elif action == "aggregate":
                    cleanup_results[mem_type] = self._aggregate_expired(mem_type, policy)
                elif action == "keep":
                    cleanup_results[mem_type] = {"status": "skipped", "reason": "retention policy is 'keep'"}
            
            logger.info(f"✓ Cleanup completed: {cleanup_results}")
            return cleanup_results
            
        except Exception as e:
            logger.error(f"✗ Error during cleanup: {e}")
            return {"status": "error", "error": str(e)}
    
    def _delete_expired(self, memory_type: str, policy: Dict) -> Dict:
        """Delete expired records."""
        try:
            retention_days = policy.get("retention_days")
            if retention_days is None:
                return {"status": "skipped", "reason": "no retention limit"}
            
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            # Determine collection based on memory type
            if memory_type == "short_term":
                collection = self.db.memories
                query = {"memory_type": "short_term", "timestamp": {"$lt": cutoff_date}}
            elif memory_type == "events":
                collection = self.db.events
                query = {"timestamp": {"$lt": cutoff_date}}
            else:
                return {"status": "skipped", "reason": "no matching collection"}
            
            result = collection.delete_many(query)
            
            logger.info(f"✓ Deleted {result.deleted_count} expired '{memory_type}' records")
            return {
                "status": "success",
                "action": "delete",
                "records_deleted": result.deleted_count,
                "cutoff_date": cutoff_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"✗ Error deleting expired data: {e}")
            return {"status": "error", "error": str(e)}
    
    def _archive_expired(self, memory_type: str, policy: Dict) -> Dict:
        """Archive expired records."""
        try:
            retention_days = policy.get("retention_days")
            if retention_days is None:
                return {"status": "skipped", "reason": "no retention limit"}
            
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            archive_collection = policy.get("archive_collection", f"archived_{memory_type}")
            
            # Determine source collection and query
            if memory_type == "conversations":
                source_collection = self.db.conversations
                query = {"timestamp": {"$lt": cutoff_date}}
            elif memory_type == "important":
                source_collection = self.db.memories
                query = {"memory_type": "important", "timestamp": {"$lt": cutoff_date}}
            else:
                return {"status": "skipped", "reason": "no matching collection"}
            
            # Move documents to archive
            expired_records = list(source_collection.find(query))
            
            if expired_records:
                # Insert to archive collection
                archive_coll = self.archive_db[archive_collection]
                archive_coll.insert_many(expired_records)
                
                # Remove from source collection
                result = source_collection.delete_many(query)
                
                logger.info(f"✓ Archived {len(expired_records)} '{memory_type}' records to '{archive_collection}'")
                return {
                    "status": "success",
                    "action": "archive",
                    "records_archived": len(expired_records),
                    "archive_collection": archive_collection,
                    "cutoff_date": cutoff_date.isoformat()
                }
            else:
                return {
                    "status": "success",
                    "action": "archive",
                    "records_archived": 0,
                    "message": "No expired records to archive"
                }
            
        except Exception as e:
            logger.error(f"✗ Error archiving data: {e}")
            return {"status": "error", "error": str(e)}
    
    def _aggregate_expired(self, memory_type: str, policy: Dict) -> Dict:
        """Aggregate expired records."""
        try:
            retention_days = policy.get("retention_days")
            if retention_days is None:
                return {"status": "skipped", "reason": "no retention limit"}
            
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            aggregation_window = policy.get("aggregation_window", "weekly")
            
            if memory_type == "events":
                collection = self.db.events
                query = {"timestamp": {"$lt": cutoff_date}}
                
                # Create aggregation by type
                aggregation = list(collection.aggregate([
                    {"$match": query},
                    {"$group": {
                        "_id": "$event_type",
                        "count": {"$sum": 1},
                        "first_occurrence": {"$min": "$timestamp"},
                        "last_occurrence": {"$max": "$timestamp"}
                    }}
                ]))
                
                # Store aggregation summary
                summary_collection = self.db.event_aggregates
                for agg in aggregation:
                    summary_collection.update_one(
                        {"_id": agg["_id"]},
                        {
                            "$set": agg,
                            "$inc": {"total_events": agg["count"]}
                        },
                        upsert=True
                    )
                
                # Delete old records
                result = collection.delete_many(query)
                
                logger.info(f"✓ Aggregated {result.deleted_count} '{memory_type}' records")
                return {
                    "status": "success",
                    "action": "aggregate",
                    "records_aggregated": result.deleted_count,
                    "aggregation_window": aggregation_window,
                    "cutoff_date": cutoff_date.isoformat()
                }
            else:
                return {"status": "skipped", "reason": "aggregation not supported for this type"}
            
        except Exception as e:
            logger.error(f"✗ Error aggregating data: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_retention_stats(self) -> Dict:
        """
        Get statistics on data retention and cleanup.
        
        Returns:
            Dict with retention statistics
        """
        try:
            stats = {
                "policies_configured": len(self.policies),
                "retention_summary": {},
                "collection_sizes": {}
            }
            
            # Get policy summary
            for mem_type, policy in self.policies.items():
                retention_days = policy.get("retention_days")
                stats["retention_summary"][mem_type] = {
                    "retention_days": retention_days if retention_days else "indefinite",
                    "action": policy.get("action"),
                    "description": policy.get("description", "")
                }
            
            # Get collection sizes
            try:
                collections_to_check = ['memories', 'events', 'conversations', 'custom_commands', 'workflows']
                for coll_name in collections_to_check:
                    if coll_name in self.db.list_collection_names():
                        count = self.db[coll_name].count_documents({})
                        stats["collection_sizes"][coll_name] = count
            except:
                pass  # Collection might not exist
            
            logger.info(f"Retention statistics: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting retention stats: {e}")
            return {"status": "error", "error": str(e)}
    
    def restore_from_archive(self, memory_type: str, archive_collection: str) -> Dict:
        """
        Restore records from archive back to main collection.
        
        Args:
            memory_type: Type of memory to restore
            archive_collection: Name of archive collection to restore from
            
        Returns:
            Dict with restoration results
        """
        try:
            archive_coll = self.archive_db[archive_collection]
            
            # Determine target collection
            if memory_type == "conversations":
                target_collection = self.db.conversations
            elif memory_type == "important":
                target_collection = self.db.memories
            else:
                return {"status": "error", "error": f"Unknown memory type: {memory_type}"}
            
            # Get all records from archive
            archived_records = list(archive_coll.find({}))
            
            if archived_records:
                # Insert back to main collection
                target_collection.insert_many(archived_records)
                
                # Delete from archive
                archive_coll.delete_many({})
                
                logger.info(f"✓ Restored {len(archived_records)} records from '{archive_collection}'")
                return {
                    "status": "success",
                    "records_restored": len(archived_records),
                    "target_collection": target_collection.name
                }
            else:
                return {
                    "status": "success",
                    "message": "No records in archive to restore"
                }
            
        except Exception as e:
            logger.error(f"✗ Error restoring from archive: {e}")
            return {"status": "error", "error": str(e)}
    
    def list_policies(self) -> Dict:
        """
        List all configured retention policies.
        
        Returns:
            Dict with all policies
        """
        return {
            "total_policies": len(self.policies),
            "policies": self.policies
        }


def get_retention_manager(db, archive_db=None):
    """Factory function to get a DataRetentionManager instance."""
    return DataRetentionManager(db, archive_db)
