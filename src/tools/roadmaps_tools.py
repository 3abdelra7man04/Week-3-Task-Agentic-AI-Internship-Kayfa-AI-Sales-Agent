# tools.py
from dataclasses import dataclass
from typing import Optional
from pymongo.database import Database
from pydantic_ai import RunContext

@dataclass
class DatabaseDeps:
    db: Database  # Shared database dependency container


# ==========================================
# --- ROADMAPS COLLECTION TOOLS ---
# ==========================================

def list_all_roadmaps(ctx: RunContext[DatabaseDeps]) -> str:
    """
    Get a lightweight overview of all career paths, study tracks, and learning roadmaps available.
    Use this tool when a user asks for guidance on how to learn a skill, career paths, or what roadmaps exist.
    """
    roadmaps_collection = ctx.deps.db["roadmaps"]
    
    # Projection: Only grab basic identifier tracking fields to preserve token limits
    projection = {"id": 1, "name": 1, "summary": 1, "_id": 0}
    roadmaps = list(roadmaps_collection.find({}, projection))
    
    if not roadmaps:
        return "There are currently no learning roadmaps available in the collection."
        
    formatted_list = []
    for r in roadmaps:
        item = (
            f"ID: {r.get('id')}\n"
            f"Name: {r.get('name')}\n"
            f"Summary: {r.get('summary')}\n"
            "---"
        )
        formatted_list.append(item)
        
    return "\n".join(formatted_list)


def get_roadmap_details(ctx: RunContext[DatabaseDeps], roadmap_id: str) -> str:
    """
    Fetch the complete step-by-step roadmap structure, milestones, and details using its unique ID.
    Use this tool ONLY after finding the valid roadmap_id via list_all_roadmaps.
    
    Args:
        roadmap_id: The unique string identifier of the roadmap (e.g., 'backend-eng', 'ai-ml').
    """
    roadmaps_collection = ctx.deps.db["roadmaps"]
    roadmap_doc = roadmaps_collection.find_one({"id": roadmap_id}, {"_id": 0})
    
    if not roadmap_doc:
        return f"Error: No roadmap sequence found matching ID '{roadmap_id}'."
        
    # Standard format conversion for the agent context loop
    details = []
    for key, value in roadmap_doc.items():
        # Clean up nested fields if they are arrays/lists of milestones
        if isinstance(value, list):
            details.append(f"{key.capitalize()}:")
            for item in value:
                details.append(f"  - {item}")
        else:
            details.append(f"{key.capitalize()}: {value}")
            
    return "\n".join(details)