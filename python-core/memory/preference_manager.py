"""
Preference Manager for ELIXI AI
Manages user preferences and learned behaviors.
Stage 4 Phase 3: Enhanced with behavioral learning and pattern detection.
"""

import time
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from collections import Counter, defaultdict


class PreferenceManager:
    """Manages user preferences and learned settings."""
    
    def __init__(self, db=None):
        """
        Initialize PreferenceManager.
        
        Args:
            db: MongoDB database instance
        """
        self.db = db
        self.preferences_collection = "user_preferences"
        self.preference_history_collection = "preference_history"
    
    def get_collection(self, name):
        """Get a collection from the database."""
        if self.db is None:
            return None
        return self.db[name]
    
    def set_preference(self, category: str, key: str, value: Any,
                      source: str = "manual", confidence: float = 1.0) -> Dict[str, Any]:
        """
        Set a user preference.
        
        Args:
            category: Category (voice, display, automation, behavior, system)
            key: Preference key
            value: Preference value
            source: Source of preference (manual, auto, inferred)
            confidence: Confidence score (0-1) for learned preferences
            
        Returns:
            Dict with success status
        """
        collection = self.get_collection(self.preferences_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            preference = {
                "preference_id": f"pref_{int(time.time() * 1000)}",
                "category": category,
                "key": key,
                "value": value,
                "set_date": datetime.utcnow().isoformat(),
                "modified_date": datetime.utcnow().isoformat(),
                "source": source,
                "confidence": max(0, min(1, confidence)),
                "version": 1,
            }
            
            # Upsert: update if exists, insert if not
            result = collection.update_one(
                {"category": category, "key": key},
                {"$set": preference},
                upsert=True
            )
            
            # Log to history
            self._log_preference_change(category, key, value, source)
            
            return {"success": True, "preference_id": preference.get("preference_id")}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_preference(self, category: str, key: str) -> Dict[str, Any]:
        """
        Get a specific preference.
        
        Args:
            category: Preference category
            key: Preference key
            
        Returns:
            Dict with preference value or error
        """
        collection = self.get_collection(self.preferences_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            preference = collection.find_one(
                {"category": category, "key": key},
                {"_id": 0}
            )
            
            if not preference:
                return {"success": False, "error": "Preference not found"}
            
            return {
                "success": True,
                "value": preference.get("value"),
                "source": preference.get("source"),
                "confidence": preference.get("confidence")
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_all_preferences(self, category: str = None) -> Dict[str, Any]:
        """
        Get all preferences, optionally filtered by category.
        
        Args:
            category: Optional category filter
            
        Returns:
            Dict with all preferences
        """
        collection = self.get_collection(self.preferences_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            query = {"category": category} if category else {}
            
            preferences = list(
                collection.find(query, {"_id": 0})
                .sort("category", 1)
            )
            
            # Group by category
            grouped = {}
            for pref in preferences:
                cat = pref.get("category", "unknown")
                if cat not in grouped:
                    grouped[cat] = []
                grouped[cat].append(pref)
            
            return {
                "success": True,
                "preferences": preferences,
                "grouped": grouped,
                "count": len(preferences)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_preference(self, category: str, key: str) -> Dict[str, Any]:
        """
        Delete a preference.
        
        Args:
            category: Preference category
            key: Preference key
            
        Returns:
            Dict with success status
        """
        collection = self.get_collection(self.preferences_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            result = collection.delete_one({"category": category, "key": key})
            
            if result.deleted_count == 0:
                return {"success": False, "error": "Preference not found"}
            
            return {"success": True, "message": "Preference deleted"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _log_preference_change(self, category: str, key: str, 
                              value: Any, source: str) -> None:
        """Log preference change to history."""
        try:
            collection = self.get_collection(self.preference_history_collection)
            if collection is None:
                return
            
            collection.insert_one({
                "timestamp": datetime.utcnow().isoformat(),
                "category": category,
                "key": key,
                "value": value,
                "source": source,
            })
        except Exception:
            pass  # Silently fail on history logging
    
    def learn_preference(self, category: str, key: str, value: Any,
                        confidence: float) -> Dict[str, Any]:
        """
        Learn a preference from user behavior.
        
        Args:
            category: Preference category
            key: Preference key
            value: Inferred value
            confidence: Confidence score (0-1)
            
        Returns:
            Dict with success status
        """
        if confidence < 0.3:
            return {"success": False, "error": "Confidence too low"}
        
        return self.set_preference(category, key, value, source="inferred", confidence=confidence)
    
    def get_preference_recommendations(self, category: str = None) -> Dict[str, Any]:
        """
        Get preferences that could be learned/recommended.
        
        Args:
            category: Optional category filter
            
        Returns:
            Dict with recommendations
        """
        collection = self.get_collection(self.preferences_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            query = {
                "source": {"$in": ["inferred", "auto"]},
                "confidence": {"$gte": 0.7}
            }
            
            if category:
                query["category"] = category
            
            recommendations = list(
                collection.find(query, {"_id": 0})
                .sort("confidence", -1)
                .limit(20)
            )
            
            return {
                "success": True,
                "recommendations": recommendations,
                "count": len(recommendations)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def apply_preference(self, category: str, key: str) -> Dict[str, Any]:
        """
        Apply a learned preference (promote from inferred to manual).
        
        Args:
            category: Preference category
            key: Preference key
            
        Returns:
            Dict with success status
        """
        collection = self.get_collection(self.preferences_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            result = collection.update_one(
                {"category": category, "key": key},
                {
                    "$set": {
                        "source": "manual",
                        "modified_date": datetime.utcnow().isoformat(),
                        "confidence": 1.0
                    }
                }
            )
            
            if result.matched_count == 0:
                return {"success": False, "error": "Preference not found"}
            
            return {"success": True, "message": "Preference applied"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def reject_preference(self, category: str, key: str) -> Dict[str, Any]:
        """
        Reject a learned preference (remove it).
        
        Args:
            category: Preference category
            key: Preference key
            
        Returns:
            Dict with success status
        """
        return self.delete_preference(category, key)
    
    def get_preference_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about preferences.
        
        Returns:
            Dict with preference statistics
        """
        collection = self.get_collection(self.preferences_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            total = collection.count_documents({})
            by_source = {}
            by_category = {}
            
            # Count by source
            for source in ["manual", "inferred", "auto"]:
                count = collection.count_documents({"source": source})
                if count > 0:
                    by_source[source] = count
            
            # Count by category
            categories = collection.distinct("category")
            for cat in categories:
                count = collection.count_documents({"category": cat})
                by_category[cat] = count
            
            # Average confidence
            preferences = list(collection.find({}, {"confidence": 1, "_id": 0}))
            avg_confidence = (
                sum(p.get("confidence", 1) for p in preferences) / len(preferences)
                if preferences else 0
            )
            
            return {
                "success": True,
                "total_preferences": total,
                "by_source": by_source,
                "by_category": by_category,
                "average_confidence": round(avg_confidence, 2),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_preference_history(self, category: str = None, key: str = None, 
                              limit: int = 50) -> Dict[str, Any]:
        """
        Get history of preference changes.
        
        Args:
            category: Optional category filter
            key: Optional key filter
            limit: Maximum records to return
            
        Returns:
            Dict with preference history
        """
        collection = self.get_collection(self.preference_history_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            query = {}
            if category:
                query["category"] = category
            if key:
                query["key"] = key
            
            history = list(
                collection.find(query, {"_id": 0})
                .sort("timestamp", -1)
                .limit(limit)
            )
            
            return {
                "success": True,
                "history": history,
                "count": len(history)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== PHASE 3: BEHAVIORAL LEARNING ====================
    
    def analyze_behavior_for_preferences(self, days: int = 14) -> Dict[str, Any]:
        """
        Analyze user behavior patterns to infer preferences.
        Examines events, habits, and interaction patterns.
        
        Args:
            days: Number of days of history to analyze
            
        Returns:
            Dict with detected preference patterns
        """
        if self.db is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            patterns = []
            
            # Analyze application usage patterns
            app_preferences = self._analyze_app_preferences(cutoff_date)
            patterns.extend(app_preferences)
            
            # Analyze time-based preferences
            time_preferences = self._analyze_time_preferences(cutoff_date)
            patterns.extend(time_preferences)
            
            # Analyze interaction style preferences
            interaction_preferences = self._analyze_interaction_preferences(cutoff_date)
            patterns.extend(interaction_preferences)
            
            # Analyze command usage preferences
            command_preferences = self._analyze_command_preferences(cutoff_date)
            patterns.extend(command_preferences)
            
            # Store high-confidence patterns as inferred preferences
            stored_count = 0
            for pattern in patterns:
                if pattern.get("confidence", 0) >= 0.6:
                    result = self.learn_preference(
                        pattern["category"],
                        pattern["key"],
                        pattern["value"],
                        pattern["confidence"]
                    )
                    if result.get("success"):
                        stored_count += 1
            
            return {
                "success": True,
                "patterns_detected": len(patterns),
                "preferences_learned": stored_count,
                "patterns": patterns
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _analyze_app_preferences(self, cutoff_date: str) -> List[Dict[str, Any]]:
        """Analyze application usage to detect preferred apps."""
        patterns = []
        
        try:
            events_collection = self.db["events"] if self.db is not None else None
            if events_collection is None:
                return patterns
            
            # Get app open events
            app_events = list(events_collection.find({
                "timestamp": {"$gte": cutoff_date},
                "event_type": {"$in": ["app_opened", "app_launched"]}
            }))
            
            if not app_events:
                return patterns
            
            # Count app usage
            app_counter = Counter()
            for event in app_events:
                app_name = event.get("event_data", {}).get("app_name")
                if app_name:
                    app_counter[app_name] += 1
            
            # Detect preferred apps (used significantly more than others)
            if app_counter:
                total = sum(app_counter.values())
                most_common = app_counter.most_common(3)
                
                for app_name, count in most_common:
                    usage_ratio = count / total
                    if usage_ratio > 0.3:  # App used in 30%+ of sessions
                        patterns.append({
                            "category": "behavior",
                            "key": "preferred_app",
                            "value": app_name,
                            "confidence": min(0.95, 0.5 + usage_ratio),
                            "evidence": f"Used {count} times ({usage_ratio:.1%} of sessions)",
                            "source": "app_usage_analysis"
                        })
        except Exception as e:
            print(f"Error analyzing app preferences: {e}")
        
        return patterns
    
    def _analyze_time_preferences(self, cutoff_date: str) -> List[Dict[str, Any]]:
        """Analyze time-based activity patterns."""
        patterns = []
        
        try:
            events_collection = self.db["events"] if self.db is not None else None
            if events_collection is None:
                return patterns
            
            # Get all events with time_of_day
            events = list(events_collection.find({
                "timestamp": {"$gte": cutoff_date},
                "time_of_day": {"$exists": True}
            }))
            
            if not events:
                return patterns
            
            # Count activity by time period
            time_counter = Counter(e.get("time_of_day") for e in events)
            total = sum(time_counter.values())
            
            # Detect peak activity time
            if time_counter:
                most_active_time, count = time_counter.most_common(1)[0]
                activity_ratio = count / total
                
                if activity_ratio > 0.35:  # 35%+ of activity in this period
                    patterns.append({
                        "category": "behavior",
                        "key": "peak_activity_time",
                        "value": most_active_time,
                        "confidence": min(0.9, 0.4 + activity_ratio),
                        "evidence": f"{count} events ({activity_ratio:.1%} of activity)",
                        "source": "time_analysis"
                    })
        except Exception as e:
            print(f"Error analyzing time preferences: {e}")
        
        return patterns
    
    def _analyze_interaction_preferences(self, cutoff_date: str) -> List[Dict[str, Any]]:
        """Analyze interaction style from chat history."""
        patterns = []
        
        try:
            memories_collection = self.db["memories"] if self.db is not None else None
            if memories_collection is None:
                return patterns
            
            # Get conversation memories
            conversations = list(memories_collection.find({
                "timestamp": {"$gte": cutoff_date},
                "memory_type": "conversation"
            }))
            
            if len(conversations) < 5:  # Need sufficient data
                return patterns
            
            # Analyze response length preference
            response_lengths = []
            for conv in conversations:
                content = conv.get("content", "")
                if content:
                    response_lengths.append(len(content))
            
            if response_lengths:
                avg_length = sum(response_lengths) / len(response_lengths)
                
                # Categorize preference
                if avg_length < 100:
                    style = "brief"
                    confidence = 0.75
                elif avg_length < 300:
                    style = "moderate"
                    confidence = 0.70
                else:
                    style = "detailed"
                    confidence = 0.75
                
                patterns.append({
                    "category": "interaction",
                    "key": "response_style",
                    "value": style,
                    "confidence": confidence,
                    "evidence": f"Average response: {avg_length:.0f} characters",
                    "source": "conversation_analysis"
                })
        except Exception as e:
            print(f"Error analyzing interaction preferences: {e}")
        
        return patterns
    
    def _analyze_command_preferences(self, cutoff_date: str) -> List[Dict[str, Any]]:
        """Analyze command execution patterns."""
        patterns = []
        
        try:
            events_collection = self.db["events"] if self.db is not None else None
            if events_collection is None:
                return patterns
            
            # Get command execution events
            command_events = list(events_collection.find({
                "timestamp": {"$gte": cutoff_date},
                "event_type": "command_executed"
            }))
            
            if not command_events:
                return patterns
            
            # Count command types
            command_counter = Counter()
            for event in command_events:
                cmd_type = event.get("event_data", {}).get("command_type")
                if cmd_type:
                    command_counter[cmd_type] += 1
            
            # Detect command preferences
            if command_counter:
                total = sum(command_counter.values())
                most_common = command_counter.most_common(2)
                
                for cmd_type, count in most_common:
                    usage_ratio = count / total
                    if usage_ratio > 0.25:  # Used 25%+ of the time
                        patterns.append({
                            "category": "automation",
                            "key": "preferred_command_type",
                            "value": cmd_type,
                            "confidence": min(0.85, 0.5 + usage_ratio),
                            "evidence": f"Used {count} times ({usage_ratio:.1%})",
                            "source": "command_usage_analysis"
                        })
        except Exception as e:
            print(f"Error analyzing command preferences: {e}")
        
        return patterns
    
    def detect_preference_patterns(self) -> Dict[str, Any]:
        """
        Detect patterns in existing preferences.
        Identifies trends and relationships between preferences.
        
        Returns:
            Dict with detected patterns
        """
        collection = self.get_collection(self.preferences_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            all_preferences = list(collection.find({}, {"_id": 0}))
            
            if not all_preferences:
                return {
                    "success": True,
                    "patterns": [],
                    "message": "No preferences to analyze"
                }
            
            patterns = []
            
            # Group by category
            by_category = defaultdict(list)
            for pref in all_preferences:
                by_category[pref.get("category", "unknown")].append(pref)
            
            # Detect category-level patterns
            for category, prefs in by_category.items():
                if len(prefs) >= 3:
                    # Check if user has strong preferences in this category
                    high_confidence = [p for p in prefs if p.get("confidence", 0) > 0.8]
                    if len(high_confidence) >= 2:
                        patterns.append({
                            "pattern_type": "category_preference",
                            "category": category,
                            "description": f"Strong preferences in {category} category",
                            "evidence": f"{len(high_confidence)} high-confidence preferences",
                            "confidence": 0.8
                        })
            
            # Detect source distribution patterns
            source_counts = Counter(p.get("source") for p in all_preferences)
            inferred_count = source_counts.get("inferred", 0)
            manual_count = source_counts.get("manual", 0)
            total = len(all_preferences)
            
            if inferred_count / total > 0.6:
                patterns.append({
                    "pattern_type": "learning_active",
                    "description": "System is actively learning preferences",
                    "evidence": f"{inferred_count}/{total} preferences inferred",
                    "confidence": 0.9
                })
            
            if manual_count / total > 0.7:
                patterns.append({
                    "pattern_type": "manual_preference",
                    "description": "User prefers explicit control",
                    "evidence": f"{manual_count}/{total} preferences manual",
                    "confidence": 0.85
                })
            
            return {
                "success": True,
                "patterns": patterns,
                "total_preferences": len(all_preferences),
                "analysis_date": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def auto_learn_from_usage(self, enabled: bool = True) -> Dict[str, Any]:
        """
        Enable or disable automatic preference learning.
        
        Args:
            enabled: Whether to enable auto-learning
            
        Returns:
            Dict with success status
        """
        collection = self.get_collection("system_settings")
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            collection.update_one(
                {"setting_key": "auto_learn_preferences"},
                {
                    "$set": {
                        "value": enabled,
                        "updated_at": datetime.utcnow().isoformat()
                    }
                },
                upsert=True
            )
            
            return {
                "success": True,
                "auto_learning": enabled,
                "message": f"Auto-learning {'enabled' if enabled else 'disabled'}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def suggest_preferences_from_habits(self, habit_ids: List[str] = None) -> Dict[str, Any]:
        """
        Generate preference suggestions based on detected habits.
        
        Args:
            habit_ids: Optional list of specific habit IDs to analyze
            
        Returns:
            Dict with preference suggestions
        """
        if self.db is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            habits_collection = self.db["detected_habits"] if self.db is not None else None
            if habits_collection is None:
                return {"success": False, "error": "Habits collection not found"}
            
            # Build query
            query = {}
            if habit_ids:
                query["habit_id"] = {"$in": habit_ids}
            else:
                # Only analyze recent, high-confidence habits
                query = {
                    "confidence_score": {"$gte": 0.7},
                    "user_feedback": {"$ne": "rejected"}
                }
            
            habits = list(habits_collection.find(query, {"_id": 0}).limit(20))
            
            if not habits:
                return {
                    "success": True,
                    "suggestions": [],
                    "message": "No habits found to analyze"
                }
            
            suggestions = []
            
            for habit in habits:
                pattern_type = habit.get("pattern_type")
                pattern_desc = habit.get("pattern_description", "")
                confidence = habit.get("confidence_score", 0)
                
                # Sequential patterns suggest workflow preferences
                if pattern_type == "sequential":
                    suggestions.append({
                        "category": "automation",
                        "key": "workflow_automation_enabled",
                        "value": True,
                        "confidence": min(0.9, confidence + 0.1),
                        "reason": f"Detected habit: {pattern_desc}",
                        "habit_id": habit.get("habit_id")
                    })
                
                # Time-based patterns suggest schedule preferences
                elif pattern_type == "time_based":
                    time_period = self._extract_time_from_description(pattern_desc)
                    if time_period:
                        suggestions.append({
                            "category": "behavior",
                            "key": "preferred_work_time",
                            "value": time_period,
                            "confidence": min(0.85, confidence),
                            "reason": f"Active during {time_period}",
                            "habit_id": habit.get("habit_id")
                        })
                
                # Frequency patterns suggest usage preferences
                elif pattern_type == "frequency":
                    occurrences = habit.get("occurrences", 0)
                    if occurrences >= 10:
                        suggestions.append({
                            "category": "automation",
                            "key": "automation_suggestions_enabled",
                            "value": True,
                            "confidence": 0.8,
                            "reason": f"High frequency activity ({occurrences} times)",
                            "habit_id": habit.get("habit_id")
                        })
            
            return {
                "success": True,
                "suggestions": suggestions,
                "habits_analyzed": len(habits),
                "suggestions_count": len(suggestions)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _extract_time_from_description(self, description: str) -> Optional[str]:
        """Extract time period from habit description."""
        description_lower = description.lower()
        for period in ["morning", "afternoon", "evening", "night"]:
            if period in description_lower:
                return period
        return None
    
    def get_learning_analytics(self) -> Dict[str, Any]:
        """
        Get analytics about preference learning performance.
        
        Returns:
            Dict with learning analytics
        """
        collection = self.get_collection(self.preferences_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            # Get all preferences
            all_prefs = list(collection.find({}, {"_id": 0}))
            
            if not all_prefs:
                return {
                    "success": True,
                    "message": "No preferences yet",
                    "learning_enabled": False
                }
            
            # Calculate metrics
            total = len(all_prefs)
            inferred = len([p for p in all_prefs if p.get("source") == "inferred"])
            manual = len([p for p in all_prefs if p.get("source") == "manual"])
            auto = len([p for p in all_prefs if p.get("source") == "auto"])
            
            # Apply rate (inferred preferences that were accepted)
            accepted = len([p for p in all_prefs 
                          if p.get("source") == "manual" and 
                          p.get("version", 1) > 1])  # Version > 1 means it was updated from inferred
            
            # Average confidence by source
            avg_confidence = {}
            for source in ["manual", "inferred", "auto"]:
                source_prefs = [p for p in all_prefs if p.get("source") == source]
                if source_prefs:
                    avg_confidence[source] = sum(p.get("confidence", 1) for p in source_prefs) / len(source_prefs)
            
            # Learning effectiveness score
            learning_score = 0
            if inferred + auto > 0:
                learning_score = min(1.0, (inferred + auto) / total) * 100
            
            return {
                "success": True,
                "total_preferences": total,
                "by_source": {
                    "manual": manual,
                    "inferred": inferred,
                    "auto": auto
                },
                "learning_metrics": {
                    "learning_score": round(learning_score, 1),
                    "accepted_suggestions": accepted,
                    "avg_confidence": {k: round(v, 2) for k, v in avg_confidence.items()}
                },
                "analysis_date": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
