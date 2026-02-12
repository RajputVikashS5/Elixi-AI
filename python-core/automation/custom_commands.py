"""
Custom Commands Module for ELIXI AI
Allows users to create, manage, and execute custom voice commands.
"""

import time
from typing import Optional, List, Dict, Any
from datetime import datetime


class CustomCommandManager:
    """Manages custom voice commands and their execution."""
    
    def __init__(self, db=None):
        """
        Initialize CustomCommandManager.
        
        Args:
            db: MongoDB database instance
        """
        self.db = db
        self.collection_name = "custom_commands"
    
    def get_collection(self):
        """Get the custom commands collection."""
        if self.db is None:
            return None
        return self.db[self.collection_name]
    
    def create_command(self, command_name: str, trigger_words: List[str], 
                      actions: List[Dict], description: str = "") -> Dict[str, Any]:
        """
        Create a new custom command.
        
        Args:
            command_name: Name of the command
            trigger_words: List of voice phrases that trigger this command
            actions: List of actions to execute (each with action type and args)
            description: Optional description of the command
            
        Returns:
            Dict with success status and command_id
        """
        if not command_name or not trigger_words or not actions:
            return {"success": False, "error": "Missing required fields"}
        
        collection = self.get_collection()
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            command = {
                "command_id": f"cmd_{int(time.time() * 1000)}",
                "command_name": command_name,
                "trigger_words": [w.lower() for w in trigger_words],
                "description": description,
                "actions": actions,
                "created_date": datetime.utcnow().isoformat(),
                "last_used": None,
                "usage_count": 0,
                "enabled": True,
            }
            
            result = collection.insert_one(command)
            return {
                "success": True,
                "command_id": command["command_id"],
                "message": f"Command '{command_name}' created successfully"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_commands(self, enabled_only: bool = False) -> Dict[str, Any]:
        """
        List all custom commands.
        
        Args:
            enabled_only: If True, only return enabled commands
            
        Returns:
            Dict with success status and list of commands
        """
        collection = self.get_collection()
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            query = {"enabled": True} if enabled_only else {}
            commands = list(collection.find(query, {"_id": 0}).sort("created_date", -1))
            return {"success": True, "commands": commands, "count": len(commands)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_command(self, command_id: str) -> Dict[str, Any]:
        """
        Get a specific command by ID.
        
        Args:
            command_id: The command ID
            
        Returns:
            Dict with command details or error
        """
        collection = self.get_collection()
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            command = collection.find_one({"command_id": command_id}, {"_id": 0})
            if not command:
                return {"success": False, "error": "Command not found"}
            return {"success": True, "command": command}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_command(self, command_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update a custom command.
        
        Args:
            command_id: The command ID
            **kwargs: Fields to update
            
        Returns:
            Dict with success status
        """
        collection = self.get_collection()
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        # Don't allow updating command_id or created_date
        kwargs.pop("command_id", None)
        kwargs.pop("created_date", None)
        
        try:
            result = collection.update_one(
                {"command_id": command_id},
                {"$set": kwargs}
            )
            
            if result.matched_count == 0:
                return {"success": False, "error": "Command not found"}
            
            return {"success": True, "message": "Command updated"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_command(self, command_id: str) -> Dict[str, Any]:
        """
        Delete a custom command.
        
        Args:
            command_id: The command ID
            
        Returns:
            Dict with success status
        """
        collection = self.get_collection()
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            result = collection.delete_one({"command_id": command_id})
            
            if result.deleted_count == 0:
                return {"success": False, "error": "Command not found"}
            
            return {"success": True, "message": "Command deleted"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def find_matching_command(self, user_input: str) -> Optional[Dict[str, Any]]:
        """
        Find a custom command that matches the user input.
        
        Args:
            user_input: User's voice input or text command
            
        Returns:
            The matching command or None
        """
        collection = self.get_collection()
        if collection is None:
            return None
        
        user_input_lower = user_input.lower()
        
        try:
            # Find enabled commands with matching trigger words
            commands = list(collection.find({"enabled": True}, {"_id": 0}))
            
            # Sort by exact matches and partial matches
            best_match = None
            best_score = 0
            
            for command in commands:
                for trigger in command.get("trigger_words", []):
                    if trigger == user_input_lower:
                        # Exact match - highest priority
                        return command
                    elif trigger in user_input_lower:
                        # Partial match
                        match_score = len(trigger) / len(user_input_lower)
                        if match_score > best_score:
                            best_score = match_score
                            best_match = command
            
            return best_match
        except Exception as e:
            print(f"Error finding matching command: {e}")
            return None
    
    def execute_command(self, command_id: str) -> Dict[str, Any]:
        """
        Execute a custom command and update its metadata.
        
        Args:
            command_id: The command ID to execute
            
        Returns:
            Dict with execution results and detected actions
        """
        collection = self.get_collection()
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            # Get the command
            command = collection.find_one({"command_id": command_id})
            if not command:
                return {"success": False, "error": "Command not found"}
            
            # Update usage tracking
            collection.update_one(
                {"command_id": command_id},
                {
                    "$set": {"last_used": datetime.utcnow().isoformat()},
                    "$inc": {"usage_count": 1}
                }
            )
            
            # Return the actions to be executed by the main handler
            return {
                "success": True,
                "command_name": command.get("command_name"),
                "actions": command.get("actions", []),
                "message": f"Executing command: {command.get('command_name')}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_top_commands(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get the most frequently used commands.
        
        Args:
            limit: Maximum number of commands to return
            
        Returns:
            List of top commands sorted by usage
        """
        collection = self.get_collection()
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            commands = list(
                collection.find({}, {"_id": 0})
                .sort("usage_count", -1)
                .limit(limit)
            )
            return {"success": True, "commands": commands}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def toggle_command(self, command_id: str, enabled: bool) -> Dict[str, Any]:
        """
        Enable or disable a command.
        
        Args:
            command_id: The command ID
            enabled: True to enable, False to disable
            
        Returns:
            Dict with success status
        """
        return self.update_command(command_id, enabled=enabled)


