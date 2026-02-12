"""
Workflow Module for ELIXI AI
Enables multi-step automation workflows with conditional logic and error handling.
"""

import time
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class StepErrorHandling(Enum):
    """How to handle errors in workflow steps."""
    CONTINUE = "continue"  # Continue to next step
    STOP = "stop"          # Stop workflow
    ROLLBACK = "rollback"  # Undo previous steps


class WorkflowManager:
    """Manages multi-step automation workflows."""
    
    def __init__(self, db=None):
        """
        Initialize WorkflowManager.
        
        Args:
            db: MongoDB database instance
        """
        self.db = db
        self.collection_name = "workflows"
        self.history_collection_name = "workflow_history"
    
    def get_collection(self, name=None):
        """Get a collection from the database."""
        if self.db is None:
            return None
        return self.db[name or self.collection_name]
    
    def create_workflow(self, workflow_name: str, description: str, 
                       steps: List[Dict], trigger: Dict = None) -> Dict[str, Any]:
        """
        Create a new workflow.
        
        Args:
            workflow_name: Name of the workflow
            description: Description of what the workflow does
            steps: List of workflow steps (each with action, args, delay_after, on_error)
            trigger: Trigger configuration (voice, schedule, event, manual)
            
        Returns:
            Dict with success status and workflow_id
        """
        if not workflow_name or not steps:
            return {"success": False, "error": "Missing required fields"}
        
        collection = self.get_collection()
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            workflow = {
                "workflow_id": f"wf_{int(time.time() * 1000)}",
                "workflow_name": workflow_name,
                "description": description,
                "trigger": trigger or {"type": "manual"},
                "steps": self._validate_steps(steps),
                "created_date": datetime.utcnow().isoformat(),
                "last_executed": None,
                "execution_count": 0,
                "enabled": True,
                "tags": [],
            }
            
            result = collection.insert_one(workflow)
            return {
                "success": True,
                "workflow_id": workflow["workflow_id"],
                "message": f"Workflow '{workflow_name}' created successfully"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _validate_steps(self, steps: List[Dict]) -> List[Dict]:
        """
        Validate and normalize workflow steps.
        
        Args:
            steps: List of steps to validate
            
        Returns:
            Validated steps list
        """
        validated = []
        for i, step in enumerate(steps, 1):
            validated_step = {
                "step_id": i,
                "action": step.get("action", ""),
                "args": step.get("args", {}),
                "delay_after": max(0, step.get("delay_after", 0)),
                "on_error": step.get("on_error", "continue"),
                "condition": step.get("condition"),  # Optional: conditional execution
                "retry_count": step.get("retry_count", 0),
            }
            validated.append(validated_step)
        return validated
    
    def list_workflows(self, enabled_only: bool = False) -> Dict[str, Any]:
        """
        List all workflows.
        
        Args:
            enabled_only: If True, only return enabled workflows
            
        Returns:
            Dict with success status and list of workflows
        """
        collection = self.get_collection()
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            query = {"enabled": True} if enabled_only else {}
            workflows = list(collection.find(query, {"_id": 0}).sort("created_date", -1))
            return {"success": True, "workflows": workflows, "count": len(workflows)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get a specific workflow by ID.
        
        Args:
            workflow_id: The workflow ID
            
        Returns:
            Dict with workflow details or error
        """
        collection = self.get_collection()
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            workflow = collection.find_one({"workflow_id": workflow_id}, {"_id": 0})
            if not workflow:
                return {"success": False, "error": "Workflow not found"}
            return {"success": True, "workflow": workflow}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_workflow(self, workflow_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update a workflow.
        
        Args:
            workflow_id: The workflow ID
            **kwargs: Fields to update
            
        Returns:
            Dict with success status
        """
        collection = self.get_collection()
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        # Don't allow updating workflow_id or created_date
        kwargs.pop("workflow_id", None)
        kwargs.pop("created_date", None)
        
        # Validate steps if updating them
        if "steps" in kwargs:
            kwargs["steps"] = self._validate_steps(kwargs["steps"])
        
        try:
            result = collection.update_one(
                {"workflow_id": workflow_id},
                {"$set": kwargs}
            )
            
            if result.matched_count == 0:
                return {"success": False, "error": "Workflow not found"}
            
            return {"success": True, "message": "Workflow updated"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Delete a workflow.
        
        Args:
            workflow_id: The workflow ID
            
        Returns:
            Dict with success status
        """
        collection = self.get_collection()
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            result = collection.delete_one({"workflow_id": workflow_id})
            
            if result.deleted_count == 0:
                return {"success": False, "error": "Workflow not found"}
            
            return {"success": True, "message": "Workflow deleted"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def prepare_workflow_execution(self, workflow_id: str) -> Dict[str, Any]:
        """
        Prepare a workflow for execution and return its steps.
        
        Args:
            workflow_id: The workflow ID
            
        Returns:
            Dict with workflow steps and execution plan
        """
        collection = self.get_collection()
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            workflow = collection.find_one({"workflow_id": workflow_id})
            if not workflow:
                return {"success": False, "error": "Workflow not found"}
            
            if not workflow.get("enabled"):
                return {"success": False, "error": "Workflow is disabled"}
            
            # Create execution record
            execution_id = f"exec_{int(time.time() * 1000)}"
            
            return {
                "success": True,
                "execution_id": execution_id,
                "workflow_id": workflow_id,
                "workflow_name": workflow.get("workflow_name"),
                "steps": workflow.get("steps", []),
                "total_steps": len(workflow.get("steps", [])),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def record_workflow_execution(self, workflow_id: str, execution_id: str,
                                 status: str, duration_ms: int,
                                 error: str = None) -> Dict[str, Any]:
        """
        Record workflow execution in history.
        
        Args:
            workflow_id: The workflow ID
            execution_id: The execution ID
            status: Execution status (completed, failed, etc.)
            duration_ms: Execution duration in milliseconds
            error: Optional error message if failed
            
        Returns:
            Dict with success status
        """
        collection = self.get_collection()
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            # Update workflow's last execution metadata
            collection.update_one(
                {"workflow_id": workflow_id},
                {
                    "$set": {"last_executed": datetime.utcnow().isoformat()},
                    "$inc": {"execution_count": 1}
                }
            )
            
            # Record in history
            history_collection = self.get_collection(self.history_collection_name)
            history_collection.insert_one({
                "execution_id": execution_id,
                "workflow_id": workflow_id,
                "status": status,
                "duration_ms": duration_ms,
                "error": error,
                "timestamp": datetime.utcnow().isoformat(),
            })
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_workflow_history(self, workflow_id: str, limit: int = 50) -> Dict[str, Any]:
        """
        Get execution history for a workflow.
        
        Args:
            workflow_id: The workflow ID
            limit: Maximum number of records to return
            
        Returns:
            Dict with execution history
        """
        collection = self.get_collection(self.history_collection_name)
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            history = list(
                collection.find({"workflow_id": workflow_id}, {"_id": 0})
                .sort("timestamp", -1)
                .limit(limit)
            )
            return {"success": True, "history": history, "count": len(history)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def toggle_workflow(self, workflow_id: str, enabled: bool) -> Dict[str, Any]:
        """
        Enable or disable a workflow.
        
        Args:
            workflow_id: The workflow ID
            enabled: True to enable, False to disable
            
        Returns:
            Dict with success status
        """
        return self.update_workflow(workflow_id, enabled=enabled)
    
    def find_workflows_by_trigger(self, trigger_type: str) -> Dict[str, Any]:
        """
        Find workflows that use a specific trigger type.
        
        Args:
            trigger_type: The trigger type (voice, schedule, event, manual)
            
        Returns:
            Dict with matching workflows
        """
        collection = self.get_collection()
        if collection is None:
            return {"success": False, "error": "Database not configured"}
        
        try:
            workflows = list(
                collection.find(
                    {"trigger.type": trigger_type, "enabled": True},
                    {"_id": 0}
                )
            )
            return {"success": True, "workflows": workflows, "count": len(workflows)}
        except Exception as e:
            return {"success": False, "error": str(e)}


