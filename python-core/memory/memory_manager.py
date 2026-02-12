"""
Memory Manager for ELIXI AI
Handles conversation memories, context management, and memory retrieval.
Includes semantic search for intelligent memory recall.
"""

import time
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class MemoryManager:
    """Manages user memories and conversation context with semantic search."""
    
    def __init__(self, db=None):
        """
        Initialize MemoryManager.
        
        Args:
            db: MongoDB database instance
        """
        self.db = db
        self.memories_collection = "memories"
        self.context_collection = "conversation_context"
        self.vectorizer = None
        self.cached_memories = None
        self.cached_embeddings = None
    
    def get_collection(self, name):
        """Get a collection from the database."""
        if self.db is None:
            return None
        return self.db[name]
    
    def save_memory(self, memory_type: str, content: str, context: Dict = None, 
                   tags: List[str] = None, importance: str = "medium") -> Dict[str, Any]:
        """
        Save a memory entry.
        
        Args:
            memory_type: Type of memory (conversation, preference, event, fact, learning)
            content: The memory content
            context: Contextual information (conversation_id, related_memories, etc.)
            tags: Tags for categorization
            importance: Importance level (low, medium, high)
            
        Returns:
            Dict with success status and memory_id
        """
        collection = self.get_collection(self.memories_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            memory = {
                "memory_id": f"mem_{int(time.time() * 1000)}",
                "type": memory_type,
                "content": content,
                "timestamp": datetime.utcnow().isoformat(),
                "context": context or {},
                "tags": tags or [],
                "importance": importance,
                "relevance_score": 1.0,
                "expiry_date": None,
                "archived": False,
                "access_count": 0,
                "last_accessed": None,
            }
            
            collection.insert_one(memory)
            return {"success": True, "memory_id": memory["memory_id"]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_memories(self, query: str, memory_type: str = None, 
                       limit: int = 20, use_semantic: bool = True) -> Dict[str, Any]:
        """
        Search memories by content or tags with optional semantic matching.
        
        Args:
            query: Search query or tag
            memory_type: Optional filter by memory type
            limit: Maximum results to return
            use_semantic: Whether to use semantic search (default: True)
            
        Returns:
            Dict with matching memories
        """
        collection = self.get_collection(self.memories_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            # Build initial query
            search_query = {
                "archived": False,
                "$or": [
                    {"content": {"$regex": query, "$options": "i"}},
                    {"tags": query.lower()},
                ]
            }
            
            if memory_type:
                search_query["type"] = memory_type
            
            # Get memories from regex search
            regex_results = list(
                collection.find(search_query, {"_id": 0})
                .sort([("importance", -1), ("timestamp", -1)])
                .limit(limit)
            )
            
            # If semantic search is enabled and we have results, enhance with similarity scoring
            if use_semantic and len(regex_results) == 0:
                # Fallback to semantic search if regex found nothing
                semantic_results = self.semantic_search(query, memory_type, limit)
                if semantic_results.get("success"):
                    return semantic_results
            
            # Add match scores based on regex matches
            for memory in regex_results:
                match_score = 1.0
                if query.lower() in memory.get("content", "").lower():
                    match_score = 0.95
                elif any(tag == query.lower() for tag in memory.get("tags", [])):
                    match_score = 0.85
                memory["match_score"] = match_score
            
            return {"success": True, "memories": regex_results, "count": len(regex_results)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def semantic_search(self, query: str, memory_type: str = None, 
                       limit: int = 20, threshold: float = 0.3) -> Dict[str, Any]:
        """
        Perform semantic search on memories using TF-IDF similarity.
        
        Args:
            query: Search query
            memory_type: Optional filter by memory type
            limit: Maximum results to return
            threshold: Minimum similarity score (0-1)
            
        Returns:
            Dict with semantically similar memories
        """
        collection = self.get_collection(self.memories_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            # Fetch all active memories
            query_filter = {"archived": False}
            if memory_type:
                query_filter["type"] = memory_type
            
            all_memories = list(collection.find(query_filter, {"_id": 0}))
            
            if not all_memories:
                return {"success": True, "memories": [], "count": 0}
            
            # Extract content from memories
            memory_contents = [m.get("content", "") for m in all_memories]
            
            # Handle empty content
            if not any(memory_contents):
                return {"success": True, "memories": [], "count": 0}
            
            # Create TF-IDF vectorizer and fit on all memories
            vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
            try:
                # Combine all content for vocabulary
                all_text = [query] + memory_contents
                vectorizer.fit(all_text)
            except:
                # Fallback if vectorizer fails
                return {"success": True, "memories": [], "count": 0}
            
            # Transform query and memories
            query_vector = vectorizer.transform([query])
            memory_vectors = vectorizer.transform(memory_contents)
            
            # Calculate similarity scores
            similarities = cosine_similarity(query_vector, memory_vectors)[0]
            
            # Create results with similarity scores
            results = []
            for idx, memory in enumerate(all_memories):
                similarity_score = float(similarities[idx])
                if similarity_score >= threshold:
                    memory["similarity_score"] = similarity_score
                    results.append(memory)
            
            # Sort by similarity score, then by importance and timestamp
            results.sort(key=lambda m: (
                -m.get("similarity_score", 0),
                {"high": 2, "medium": 1, "low": 0}.get(m.get("importance", "low"), 0),
                m.get("timestamp", "")
            ), reverse=True)
            
            results = results[:limit]
            
            return {"success": True, "memories": results, "count": len(results)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_conversation_context(self, conversation_id: str, 
                               max_messages: int = 10) -> Dict[str, Any]:
        """
        Get context for a conversation with enhanced details.
        
        Args:
            conversation_id: The conversation ID
            max_messages: Maximum messages to retrieve
            
        Returns:
            Dict with conversation context and related memories
        """
        collection = self.get_collection(self.context_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            context = collection.find_one(
                {"conversation_id": conversation_id},
                {"_id": 0}
            )
            
            if not context:
                # Create new context
                context = {
                    "conversation_id": conversation_id,
                    "created_at": datetime.utcnow().isoformat(),
                    "messages": [],
                    "related_memories": [],
                    "topic": None,
                    "sentiment": None,
                    "message_count": 0,
                    "duration_seconds": 0,
                    "last_updated": datetime.utcnow().isoformat(),
                }
            
            # Update last accessed timestamp
            if "messages" in context and len(context["messages"]) > 0:
                last_msg = context["messages"][-1]
                if "timestamp" in last_msg:
                    context["last_message_timestamp"] = last_msg["timestamp"]
            
            # Get recent memories in conversation
            memories_collection = self.get_collection(self.memories_collection)
            related_memories = list(
                memories_collection.find(
                    {
                        "context.conversation_id": conversation_id,
                        "archived": False
                    },
                    {"_id": 0}
                ).sort("timestamp", -1).limit(max_messages)
            )
            
            context["related_memories"] = related_memories
            context["message_count"] = len(context.get("messages", []))
            
            # Calculate conversation duration if we have timestamps
            if context.get("messages") and len(context["messages"]) > 1:
                try:
                    first_msg = context["messages"][0]
                    last_msg = context["messages"][-1]
                    if "timestamp" in first_msg and "timestamp" in last_msg:
                        first_time = datetime.fromisoformat(first_msg["timestamp"])
                        last_time = datetime.fromisoformat(last_msg["timestamp"])
                        duration = (last_time - first_time).total_seconds()
                        context["duration_seconds"] = max(0, int(duration))
                except:
                    pass
            
            return {
                "success": True,
                "context": context,
                "related_memories_count": len(related_memories),
                "total_messages": context.get("message_count", 0)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def add_to_conversation(self, conversation_id: str, role: str, 
                          message: str, metadata: Dict = None) -> Dict[str, Any]:
        """
        Add a message to conversation context.
        
        Args:
            conversation_id: The conversation ID
            role: Role (user, assistant, system)
            message: The message text
            metadata: Additional metadata
            
        Returns:
            Dict with success status
        """
        collection = self.get_collection(self.context_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            msg_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "role": role,
                "message": message,
                "metadata": metadata or {},
            }
            
            # Upsert conversation context
            collection.update_one(
                {"conversation_id": conversation_id},
                {
                    "$set": {
                        "conversation_id": conversation_id,
                        "updated_at": datetime.utcnow().isoformat(),
                    },
                    "$push": {"messages": msg_entry}
                },
                upsert=True
            )
            
            # Also save as memory
            self.save_memory(
                memory_type="conversation",
                content=message,
                context={
                    "conversation_id": conversation_id,
                    "role": role
                },
                tags=["conversation", role]
            )
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_memory(self, memory_id: str) -> Dict[str, Any]:
        """
        Get a specific memory by ID.
        
        Args:
            memory_id: The memory ID
            
        Returns:
            Dict with memory details
        """
        collection = self.get_collection(self.memories_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            # Update access count
            collection.update_one(
                {"memory_id": memory_id},
                {
                    "$inc": {"access_count": 1},
                    "$set": {"last_accessed": datetime.utcnow().isoformat()}
                }
            )
            
            memory = collection.find_one({"memory_id": memory_id}, {"_id": 0})
            
            if not memory:
                return {"success": False, "error": "Memory not found"}
            
            return {"success": True, "memory": memory}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_memory(self, memory_id: str) -> Dict[str, Any]:
        """
        Delete a memory (archive rather than remove).
        
        Args:
            memory_id: The memory ID
            
        Returns:
            Dict with success status
        """
        collection = self.get_collection(self.memories_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            result = collection.update_one(
                {"memory_id": memory_id},
                {"$set": {"archived": True, "archived_at": datetime.utcnow().isoformat()}}
            )
            
            if result.matched_count == 0:
                return {"success": False, "error": "Memory not found"}
            
            return {"success": True, "message": "Memory archived"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_recent_memories(self, limit: int = 50, 
                           min_importance: str = "low") -> Dict[str, Any]:
        """
        Get recent memories, optionally filtered by importance.
        
        Args:
            limit: Maximum number of memories to return
            min_importance: Minimum importance level (low, medium, high)
            
        Returns:
            Dict with recent memories
        """
        collection = self.get_collection(self.memories_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            importance_levels = {"low": 0, "medium": 1, "high": 2}
            min_level = importance_levels.get(min_importance, 0)
            
            query = {
                "archived": False,
                "importance": {"$in": [k for k, v in importance_levels.items() if v >= min_level]}
            }
            
            memories = list(
                collection.find(query, {"_id": 0})
                .sort("timestamp", -1)
                .limit(limit)
            )
            
            return {"success": True, "memories": memories, "count": len(memories)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_memories_by_type(self, memory_type: str, 
                           limit: int = 50) -> Dict[str, Any]:
        """
        Get memories filtered by type.
        
        Args:
            memory_type: Type of memory to retrieve
            limit: Maximum number to return
            
        Returns:
            Dict with filtered memories
        """
        collection = self.get_collection(self.memories_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            memories = list(
                collection.find(
                    {"type": memory_type, "archived": False},
                    {"_id": 0}
                ).sort("timestamp", -1).limit(limit)
            )
            
            return {"success": True, "memories": memories, "count": len(memories)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_memory_relevance(self, memory_id: str, 
                               relevance_score: float) -> Dict[str, Any]:
        """
        Update memory relevance score based on usage patterns.
        
        Args:
            memory_id: The memory ID
            relevance_score: New relevance score (0-1)
            
        Returns:
            Dict with success status
        """
        collection = self.get_collection(self.memories_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            score = max(0, min(1, relevance_score))
            
            result = collection.update_one(
                {"memory_id": memory_id},
                {"$set": {"relevance_score": score}}
            )
            
            if result.matched_count == 0:
                return {"success": False, "error": "Memory not found"}
            
            return {"success": True, "relevance_score": score}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def cleanup_old_memories(self, days_to_keep: int = 90) -> Dict[str, Any]:
        """
        Archive memories older than specified days based on retention policy.
        
        Args:
            days_to_keep: Number of days to keep memories
            
        Returns:
            Dict with count of archived memories
        """
        collection = self.get_collection(self.memories_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days_to_keep)).isoformat()
            archived_count = 0
            
            # Define retention policies by memory type
            retention_policies = {
                "conversation": days_to_keep,      # Default: keep for specified days
                "preference": days_to_keep * 3,    # Keep preferences longer (3x)
                "fact": days_to_keep * 10,         # Keep facts much longer (10x)
                "learning": days_to_keep * 5,      # Keep learning memories longer (5x)
                "event": days_to_keep * 2          # Keep events longer (2x)
            }
            
            # Archive by memory type with different policies
            for memory_type, retention_days in retention_policies.items():
                type_cutoff = (datetime.utcnow() - timedelta(days=retention_days)).isoformat()
                
                # Only archive if importance is low (don't auto-delete important memories)
                result = collection.update_many(
                    {
                        "type": memory_type,
                        "timestamp": {"$lt": type_cutoff},
                        "archived": False,
                        "importance": "low"
                    },
                    {
                        "$set": {
                            "archived": True,
                            "archived_at": datetime.utcnow().isoformat()
                        }
                    }
                )
                archived_count += result.modified_count
            
            return {
                "success": True,
                "archived_count": archived_count,
                "policies": retention_policies
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def set_memory_expiry(self, memory_id: str, days_to_expiry: int) -> Dict[str, Any]:
        """
        Set an expiry date for a specific memory.
        
        Args:
            memory_id: The memory ID
            days_to_expiry: Number of days until expiry
            
        Returns:
            Dict with success status
        """
        collection = self.get_collection(self.memories_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            expiry_date = (datetime.utcnow() + timedelta(days=days_to_expiry)).isoformat()
            
            result = collection.update_one(
                {"memory_id": memory_id},
                {"$set": {"expiry_date": expiry_date}}
            )
            
            if result.matched_count == 0:
                return {"success": False, "error": "Memory not found"}
            
            return {"success": True, "expiry_date": expiry_date}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def archive_expired_memories(self) -> Dict[str, Any]:
        """
        Archive memories that have passed their expiry date.
        
        Returns:
            Dict with count of archived memories
        """
        collection = self.get_collection(self.memories_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            now = datetime.utcnow().isoformat()
            
            result = collection.update_many(
                {
                    "expiry_date": {"$ne": None, "$lt": now},
                    "archived": False
                },
                {
                    "$set": {
                        "archived": True,
                        "archived_at": now
                    }
                }
            )
            
            return {
                "success": True,
                "archived_count": result.modified_count
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about stored memories.
        
        Returns:
            Dict with memory statistics
        """
        collection = self.get_collection(self.memories_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            total = collection.count_documents({})
            active = collection.count_documents({"archived": False})
            by_type = {}
            
            # Count by type
            for memory_type in ["conversation", "preference", "event", "fact", "learning"]:
                count = collection.count_documents(
                    {"type": memory_type, "archived": False}
                )
                if count > 0:
                    by_type[memory_type] = count
            
            # Count by importance
            by_importance = {}
            for importance in ["low", "medium", "high"]:
                count = collection.count_documents(
                    {"importance": importance, "archived": False}
                )
                if count > 0:
                    by_importance[importance] = count
            
            return {
                "success": True,
                "total_memories": total,
                "active_memories": active,
                "archived_memories": total - active,
                "by_type": by_type,
                "by_importance": by_importance,
                "semantic_search_available": True
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_related_memories(self, conversation_id: str, query: str = None, 
                               limit: int = 10) -> Dict[str, Any]:
        """
        Search for memories related to a conversation, optionally filtering by query.
        
        Args:
            conversation_id: The conversation ID
            query: Optional search query
            limit: Maximum results to return
            
        Returns:
            Dict with related memories
        """
        collection = self.get_collection(self.memories_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            # First, get memories related to this conversation
            conv_query = {
                "context.conversation_id": conversation_id,
                "archived": False
            }
            
            related = list(collection.find(conv_query, {"_id": 0}))
            
            if query and len(related) > 0:
                # If there's a query, filter by semantic similarity
                memory_contents = [m.get("content", "") for m in related]
                
                if any(memory_contents):
                    try:
                        vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
                        all_text = [query] + memory_contents
                        vectorizer.fit(all_text)
                        
                        query_vector = vectorizer.transform([query])
                        memory_vectors = vectorizer.transform(memory_contents)
                        similarities = cosine_similarity(query_vector, memory_vectors)[0]
                        
                        for idx, memory in enumerate(related):
                            memory["similarity_score"] = float(similarities[idx])
                        
                        related.sort(key=lambda m: -m.get("similarity_score", 0))
                    except:
                        # Fallback to timestamp sorting if semantic search fails
                        related.sort(key=lambda m: m.get("timestamp", ""), reverse=True)
            else:
                # Sort by recency
                related.sort(key=lambda m: m.get("timestamp", ""), reverse=True)
            
            return {
                "success": True,
                "memories": related[:limit],
                "count": len(related[:limit])
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get a summary of a conversation including key topics and participants.
        
        Args:
            conversation_id: The conversation ID
            
        Returns:
            Dict with conversation summary
        """
        collection = self.get_collection(self.context_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            context = collection.find_one(
                {"conversation_id": conversation_id},
                {"_id": 0}
            )
            
            if not context:
                return {"success": False, "error": "Conversation not found"}
            
            messages = context.get("messages", [])
            
            # Analyze roles (who participated)
            roles = {}
            total_tokens = 0
            for msg in messages:
                role = msg.get("role", "unknown")
                if role not in roles:
                    roles[role] = 0
                roles[role] += len(msg.get("message", "").split())
                total_tokens += len(msg.get("message", "").split())
            
            # Extract entities/keywords from messages (simple approach)
            keywords = []
            for msg in messages:
                text = msg.get("message", "").lower()
                # Basic keyword extraction: capitalize words (simple heuristic)
                words = text.split()
                for word in words:
                    if len(word) > 5 and word.isalpha():
                        if word not in keywords:
                            keywords.append(word)
            
            return {
                "success": True,
                "summary": {
                    "conversation_id": conversation_id,
                    "message_count": len(messages),
                    "total_tokens": total_tokens,
                    "participants": list(roles.keys()),
                    "participant_distribution": roles,
                    "duration_seconds": context.get("duration_seconds", 0),
                    "created_at": context.get("created_at"),
                    "last_updated": context.get("last_updated"),
                    "topic": context.get("topic"),
                    "sentiment": context.get("sentiment"),
                    "keywords": keywords[:10]  # Top 10 keywords
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
