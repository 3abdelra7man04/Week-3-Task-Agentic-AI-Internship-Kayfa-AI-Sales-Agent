# tools.py
from dataclasses import dataclass
from typing import Optional
from pymongo.database import Database
from pydantic_ai import RunContext

# 1. Define the Dependency Dataclass container
@dataclass
class DatabaseDeps:
    db: Database  # This holds the active PyMongo Database object


# 2. Refactor the Tools to consume the dependency via RunContext
def list_all_courses_summaries(ctx: RunContext[DatabaseDeps]) -> str:
    """
    Get a lightweight overview of all available courses in the database.
    Use this tool when the user asks what courses are available or wants to browse options.
    """
    # Access the database collection through the injected dependency context
    courses_collection = ctx.deps.db["courses"]
    
    projection = {"id": 1, "name": 1, "summary": 1, "_id": 0}
    courses = list(courses_collection.find({}, projection))
    
    if not courses:
        return "The course catalog is currently empty."
        
    formatted_list = []
    for c in courses:
        item = (
            f"ID: {c.get('id')}\n"
            f"Name: {c.get('name')}\n"
            f"Summary: {c.get('summary')}\n"
            "---"
        )
        formatted_list.append(item)
        
    return "\n".join(formatted_list)


def get_course_details(ctx: RunContext[DatabaseDeps], course_id: str) -> str:
    """
    Fetch the full, detailed document for a specific course using its unique ID.
    Use this tool ONLY after identifying the correct course_id from list_all_courses.

    This tool returns a structured document containing fields such as: 
    _id, id, provider, host, name, track, summary, link, duration, level, prerequisites, and roadmaps.

    Args:
        course_id: The unique string identifier of the course (e.g., 'py-101').
    """
    # Access the database collection through the injected dependency context
    courses_collection = ctx.deps.db["courses"]
    
    course_doc = courses_collection.find_one({"id": course_id}, {"_id": 0})
    
    if not course_doc:
        return f"Error: No course found with ID '{course_id}'."
        
    details = []
    for key, value in course_doc.items():
        details.append(f"{key.capitalize()}: {value}")
        
    return "\n".join(details)