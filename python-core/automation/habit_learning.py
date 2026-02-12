"""
Habit Learning System for ELIXI AI
Analyzes user behavior patterns and suggests automations.
"""

import time
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import math


class HabitLearningEngine:
    """Analyzes user behavior and learns habits."""
    
    def __init__(self, db=None):
        """
        Initialize HabitLearningEngine.
        
        Args:
            db: MongoDB database instance
        """
        self.db = db
        self.events_collection = "events"  # Existing events collection
        self.habits_collection = "detected_habits"
        self.patterns_collection = "user_patterns"
    
    def get_collection(self, name):
        """Get a collection from the database."""
        if self.db is None:
            return None
        return self.db[name]
    
    def record_event(self, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Record a user event for habit analysis.
        
        Args:
            event_type: Type of event (app_opened, app_closed, command_executed, etc.)
            event_data: Event-specific data
            
        Returns:
            Dict with success status and event_id
        """
        collection = self.get_collection(self.events_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            now = datetime.utcnow()
            event = {
                "event_id": f"evt_{int(time.time() * 1000)}",
                "event_type": event_type,
                "event_data": event_data,
                "timestamp": now.isoformat(),
                "time_of_day": self._get_time_period(now),
                "day_of_week": now.strftime("%A"),
                "analyzed": False,  # Flag for batch processing
            }
            
            collection.insert_one(event)
            return {"success": True, "event_id": event["event_id"]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_time_period(self, dt: datetime) -> str:
        """Get time period of day (morning, afternoon, evening, night)."""
        hour = dt.hour
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
    
    def analyze_recent_events(self, days: int = 7) -> Dict[str, Any]:
        """
        Analyze recent events to detect patterns.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict with detected patterns and habits
        """
        collection = self.get_collection(self.events_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            # Get recent events
            events = list(
                collection.find(
                    {"timestamp": {"$gte": cutoff_date}},
                    {"_id": 0}
                ).sort("timestamp", 1)
            )
            
            if not events:
                return {
                    "success": True, 
                    "patterns": [],
                    "habits": [],
                    "message": "No events in the specified time period"
                }
            
            # Analyze patterns
            patterns = self._detect_patterns(events)
            habits = self._generate_habit_suggestions(patterns, events)
            
            # Store detected patterns
            self._store_patterns(patterns)
            
            return {
                "success": True,
                "patterns": patterns,
                "habits": habits,
                "analysis_period_days": days,
                "events_analyzed": len(events)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _detect_patterns(self, events: List[Dict]) -> List[Dict[str, Any]]:
        """
        Detect patterns from a list of events.
        
        Args:
            events: List of events to analyze
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        # Sequential patterns (what apps are opened in sequence)
        app_sequences = self._detect_sequential_patterns(events)
        for seq_pattern in app_sequences:
            if seq_pattern["confidence"] > 0.7:
                patterns.append(seq_pattern)
        
        # Time-based patterns (what happens at specific times)
        time_patterns = self._detect_time_patterns(events)
        for time_pattern in time_patterns:
            if time_pattern["confidence"] > 0.6:
                patterns.append(time_pattern)
        
        # Frequency patterns (repeated actions)
        frequency_patterns = self._detect_frequency_patterns(events)
        for freq_pattern in frequency_patterns:
            if freq_pattern["confidence"] > 0.6:
                patterns.append(freq_pattern)
        
        return patterns
    
    def _detect_sequential_patterns(self, events: List[Dict]) -> List[Dict]:
        """Detect sequential action patterns."""
        patterns = []
        
        # Extract app opening events
        app_events = [e for e in events if e.get("event_type") == "app_opened"]
        
        if len(app_events) < 2:
            return patterns
        
        # Build sequences
        sequences = defaultdict(int)
        for i in range(len(app_events) - 1):
            app1 = app_events[i].get("event_data", {}).get("app_name", "")
            app2 = app_events[i + 1].get("event_data", {}).get("app_name", "")
            
            # Only count if within 5 min
            time1 = app_events[i].get("timestamp")
            time2 = app_events[i + 1].get("timestamp")
            
            if app1 and app2:
                if self._time_diff_minutes(time1, time2) <= 5:
                    sequences[f"{app1} → {app2}"] += 1
        
        # Convert to patterns with confidence
        for sequence, count in sequences.items():
            if count >= 2:  # At least 2 occurrences
                patterns.append({
                    "pattern_type": "sequential",
                    "description": sequence,
                    "occurrences": count,
                    "confidence_score": min(0.95, 0.7 + (count * 0.05)),
                })
        
        return patterns
    
    def _detect_time_patterns(self, events: List[Dict]) -> List[Dict]:
        """Detect time-based patterns."""
        patterns = []
        
        time_events = defaultdict(list)
        for event in events:
            time_period = event.get("time_of_day", "")
            event_type = event.get("event_type", "")
            if time_period and event_type:
                time_events[time_period].append(event_type)
        
        # Analyze each time period
        for time_period, event_types in time_events.items():
            if event_types:
                most_common = Counter(event_types).most_common(3)
                total = len(event_types)
                
                for event_type, count in most_common:
                    confidence = count / total
                    if confidence > 0.4:
                        patterns.append({
                            "pattern_type": "time_based",
                            "description": f"At {time_period}: {event_type}",
                            "time_period": time_period,
                            "occurrences": count,
                            "confidence_score": confidence,
                        })
        
        return patterns
    
    def _detect_frequency_patterns(self, events: List[Dict]) -> List[Dict]:
        """Detect frequency-based patterns."""
        patterns = []
        
        # Count event types
        event_counts = Counter(e.get("event_type", "") for e in events)
        total_events = len(events)
        
        for event_type, count in event_counts.items():
            if event_type and count >= 3:
                frequency = count / total_events
                patterns.append({
                    "pattern_type": "frequency",
                    "description": f"Frequently: {event_type}",
                    "occurrences": count,
                    "confidence_score": min(0.95, frequency),
                })
        
        return patterns
    
    def _time_diff_minutes(self, time1: str, time2: str) -> float:
        """Calculate time difference in minutes between two ISO format timestamps."""
        try:
            dt1 = datetime.fromisoformat(time1)
            dt2 = datetime.fromisoformat(time2)
            return abs((dt2 - dt1).total_seconds() / 60)
        except:
            return float('inf')
    
    def _generate_habit_suggestions(self, patterns: List[Dict], 
                                  events: List[Dict]) -> List[Dict]:
        """Transform patterns into habit suggestions."""
        suggestions = []
        
        for pattern in patterns:
            if pattern["confidence_score"] < 0.6:
                continue
            
            pattern_type = pattern.get("pattern_type")
            
            if pattern_type == "sequential":
                suggestion = {
                    "habit_id": f"hab_{int(time.time() * 1000)}",
                    "type": "automation",
                    "title": f"Automate: {pattern['description']}",
                    "description": f"I noticed you open {pattern['description'].split(' → ')[0]} "
                                   f"followed by {pattern['description'].split(' → ')[1]} "
                                   f"{pattern['occurrences']} times.",
                    "confidence_score": pattern["confidence_score"],
                    "pattern": pattern,
                    "suggested_action": "create_workflow",
                    "status": "pending",
                }
                suggestions.append(suggestion)
            
            elif pattern_type == "time_based":
                suggestion = {
                    "habit_id": f"hab_{int(time.time() * 1000)}",
                    "type": "scheduling",
                    "title": f"Schedule routine for {pattern.get('time_period')}?",
                    "description": f"You frequently {pattern['description'].lower()}",
                    "confidence_score": pattern["confidence_score"],
                    "pattern": pattern,
                    "suggested_action": "create_schedule",
                    "status": "pending",
                }
                suggestions.append(suggestion)
        
        return suggestions
    
    def _store_patterns(self, patterns: List[Dict]) -> None:
        """Store patterns in the database."""
        collection = self.get_collection(self.patterns_collection)
        if collection is None:
            return
        
        try:
            for pattern in patterns:
                pattern["detected_at"] = datetime.utcnow().isoformat()
                collection.insert_one(pattern)
        except Exception as e:
            print(f"Error storing patterns: {e}")
    
    def get_detected_habits(self) -> Dict[str, Any]:
        """
        Get all detected habits.
        
        Returns:
            Dict with list of habits
        """
        collection = self.get_collection(self.patterns_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            habits = list(
                collection.find({}, {"_id": 0})
                .sort("detected_at", -1)
                .limit(50)
            )
            return {"success": True, "habits": habits, "count": len(habits)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def provide_habit_feedback(self, pattern_id: str, feedback: str) -> Dict[str, Any]:
        """
        Record user feedback on a habit suggestion.
        
        Args:
            pattern_id: The pattern/habit ID
            feedback: User feedback (helpful, not_helpful, skip)
            
        Returns:
            Dict with success status
        """
        collection = self.get_collection(self.patterns_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            collection.update_one(
                {"habit_id": pattern_id},
                {"$set": {"user_feedback": feedback, "feedback_date": datetime.utcnow().isoformat()}}
            )
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_habit_analytics(self) -> Dict[str, Any]:
        """
        Get analytics on detected habits and user feedback.
        
        Returns:
            Dict with habit analytics
        """
        collection = self.get_collection(self.patterns_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            habits = list(collection.find({}, {"_id": 0}))
            
            feedback_counts = Counter(h.get("user_feedback", "pending") for h in habits)
            pattern_types = Counter(h.get("pattern_type", "unknown") for h in habits)
            
            avg_confidence = sum(h.get("confidence_score", 0) for h in habits) / len(habits) if habits else 0
            
            return {
                "success": True,
                "total_habits": len(habits),
                "feedback": dict(feedback_counts),
                "pattern_types": dict(pattern_types),
                "average_confidence": round(avg_confidence, 2),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


