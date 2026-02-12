"""
Suggestion Engine for ELIXI AI
Provides intelligent, personalized suggestions based on user behavior and context.
"""

import time
from typing import Optional, List, Dict, Any
from datetime import datetime
import random


class SuggestionEngine:
    """Generates intelligent suggestions for users."""
    
    def __init__(self, db=None):
        """
        Initialize SuggestionEngine.
        
        Args:
            db: MongoDB database instance
        """
        self.db = db
        self.suggestions_collection = "suggestions"
        self.preferences_collection = "user_preferences"
    
    def get_collection(self, name):
        """Get a collection from the database."""
        if self.db is None:
            return None
        return self.db[name]
    
    def create_suggestion(self, suggestion_type: str, title: str, 
                         description: str, confidence_score: float,
                         suggested_action: Dict = None) -> Dict[str, Any]:
        """
        Create a new suggestion.
        
        Args:
            suggestion_type: Type of suggestion (automation, preference, optimization, learning)
            title: Short title of the suggestion
            description: Detailed description
            confidence_score: Score 0-1 indicating confidence in this suggestion
            suggested_action: The action to take if user accepts
            
        Returns:
            Dict with success status and suggestion_id
        """
        collection = self.get_collection(self.suggestions_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            suggestion = {
                "suggestion_id": f"sugg_{int(time.time() * 1000)}",
                "type": suggestion_type,
                "title": title,
                "description": description,
                "confidence_score": max(0, min(1, confidence_score)),
                "suggested_action": suggested_action or {},
                "status": "pending",
                "created_date": datetime.utcnow().isoformat(),
                "shown_date": None,
                "response_date": None,
                "user_response": None,  # accepted, rejected, later, ignored
                "helpful": None,  # True, False, None
            }
            
            result = collection.insert_one(suggestion)
            return {
                "success": True,
                "suggestion_id": suggestion["suggestion_id"],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_active_suggestions(self, limit: int = 5) -> Dict[str, Any]:
        """
        Get pending suggestions to show user.
        
        Args:
            limit: Maximum number of suggestions to return
            
        Returns:
            Dict with suggestions ranked by relevance
        """
        collection = self.get_collection(self.suggestions_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            # Get pending suggestions, sorted by confidence and recency
            suggestions = list(
                collection.find(
                    {"status": "pending"},
                    {"_id": 0}
                ).sort([("confidence_score", -1), ("created_date", -1)])
                .limit(limit)
            )
            
            return {"success": True, "suggestions": suggestions, "count": len(suggestions)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_suggestions_for_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get suggestions relevant to current context.
        
        Args:
            context: Contextual information (time_of_day, active_apps, etc.)
            
        Returns:
            Dict with relevant suggestions
        """
        collection = self.get_collection(self.suggestions_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            # Get pending suggestions
            suggestions = list(
                collection.find({"status": "pending"}, {"_id": 0})
            )
            
            # Score suggestions based on context match
            scored = []
            for sugg in suggestions:
                score = self._calculate_context_score(sugg, context)
                if score > 0:
                    scored.append((sugg, score))
            
            # Sort by score
            scored.sort(key=lambda x: x[1], reverse=True)
            
            results = [s[0] for s in scored[:3]]
            
            return {"success": True, "suggestions": results, "count": len(results)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _calculate_context_score(self, suggestion: Dict, context: Dict) -> float:
        """
        Calculate how relevant a suggestion is to the current context.
        
        Args:
            suggestion: The suggestion to score
            context: Current context
            
        Returns:
            Score 0-1 indicating relevance
        """
        score = suggestion.get("confidence_score", 0.5)
        
        # Boost score based on context matches
        sugg_type = suggestion.get("type", "")
        
        # Time-based boost
        if context.get("time_of_day") == "morning" and "routine" in suggestion.get("description", "").lower():
            score += 0.1
        
        # Activity-based boost
        active_apps = context.get("active_apps", [])
        if active_apps and any(app.lower() in suggestion.get("description", "").lower() for app in active_apps):
            score += 0.15
        
        # Recency boost - newer suggestions are more relevant
        created = suggestion.get("created_date")
        if created:
            # Penalize old suggestions slightly
            age_hours = self._get_hours_since(created)
            if age_hours > 24:
                score *= 0.8
        
        return min(1.0, score)
    
    def _get_hours_since(self, iso_date: str) -> float:
        """Get hours since an ISO format date."""
        try:
            target_date = datetime.fromisoformat(iso_date)
            delta = datetime.utcnow() - target_date
            return delta.total_seconds() / 3600
        except:
            return 0
    
    def respond_to_suggestion(self, suggestion_id: str, response: str,
                            helpful: bool = None) -> Dict[str, Any]:
        """
        Record user response to a suggestion.
        
        Args:
            suggestion_id: The suggestion ID
            response: User response (accepted, rejected, later, ignored)
            helpful: Whether user found the suggestion helpful
            
        Returns:
            Dict with success status
        """
        collection = self.get_collection(self.suggestions_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            update_data = {
                "status": "responded",
                "user_response": response,
                "response_date": datetime.utcnow().isoformat(),
            }
            
            if helpful is not None:
                update_data["helpful"] = helpful
            
            collection.update_one(
                {"suggestion_id": suggestion_id},
                {"$set": update_data}
            )
            
            return {"success": True, "message": f"Response recorded: {response}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_suggestion_analytics(self) -> Dict[str, Any]:
        """
        Get analytics on suggestion performance.
        
        Returns:
            Dict with suggestion statistics
        """
        collection = self.get_collection(self.suggestions_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            all_suggestions = list(collection.find({}, {"_id": 0}))
            
            if not all_suggestions:
                return {
                    "success": True,
                    "total_suggestions": 0,
                    "acceptance_rate": 0,
                    "helpfulness_rate": 0,
                }
            
            responded = [s for s in all_suggestions if s.get("status") == "responded"]
            accepted = [s for s in responded if s.get("user_response") == "accepted"]
            helpful = [s for s in responded if s.get("helpful") == True]
            
            acceptance_rate = (len(accepted) / len(responded) * 100) if responded else 0
            helpfulness_rate = (len(helpful) / len(responded) * 100) if responded else 0
            
            by_type = {}
            for sugg in all_suggestions:
                sugg_type = sugg.get("type", "unknown")
                if sugg_type not in by_type:
                    by_type[sugg_type] = {"total": 0, "accepted": 0}
                by_type[sugg_type]["total"] += 1
                if sugg.get("user_response") == "accepted":
                    by_type[sugg_type]["accepted"] += 1
            
            return {
                "success": True,
                "total_suggestions": len(all_suggestions),
                "pending": len([s for s in all_suggestions if s.get("status") == "pending"]),
                "responded_to": len(responded),
                "acceptance_rate": round(acceptance_rate, 1),
                "helpfulness_rate": round(helpfulness_rate, 1),
                "by_type": by_type,
                "average_confidence": round(sum(s.get("confidence_score", 0) for s in all_suggestions) / len(all_suggestions), 2),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def generate_learning_suggestion(self, preference_key: str, 
                                    inferred_value: Any,
                                    confidence: float) -> Dict[str, Any]:
        """
        Generate a suggestion to learn a user preference.
        
        Args:
            preference_key: The preference being learned (e.g., "preferred_browser")
            inferred_value: The inferred value
            confidence: Confidence in the inference
            
        Returns:
            Result of creating the suggestion
        """
        return self.create_suggestion(
            suggestion_type="learning",
            title=f"Learn: {preference_key}?",
            description=f"I've noticed you seem to prefer '{inferred_value}'. Should I remember this?",
            confidence_score=confidence,
            suggested_action={
                "type": "set_preference",
                "key": preference_key,
                "value": inferred_value,
            }
        )
    
    def generate_optimization_suggestion(self, current_action: str,
                                        optimized_action: str,
                                        benefit: str,
                                        confidence: float) -> Dict[str, Any]:
        """
        Generate a suggestion for process optimization.
        
        Args:
            current_action: Current way user does something
            optimized_action: Suggested improved way
            benefit: Description of the benefit
            confidence: Confidence in the optimization
            
        Returns:
            Result of creating the suggestion
        """
        return self.create_suggestion(
            suggestion_type="optimization",
            title=f"Faster way to {current_action}?",
            description=f"Instead of {current_action}, you could {optimized_action}. This would {benefit}.",
            confidence_score=confidence,
            suggested_action={
                "type": "create_optimization",
                "current": current_action,
                "optimized": optimized_action,
            }
        )
    
    def dismiss_suggestion_type(self, suggestion_type: str) -> Dict[str, Any]:
        """
        Dismiss all pending suggestions of a certain type.
        
        Args:
            suggestion_type: Type to dismiss
            
        Returns:
            Dict with success status
        """
        collection = self.get_collection(self.suggestions_collection)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            result = collection.update_many(
                {"type": suggestion_type, "status": "pending"},
                {"$set": {"status": "dismissed", "response_date": datetime.utcnow().isoformat()}}
            )
            
            return {
                "success": True,
                "dismissed_count": result.modified_count
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


