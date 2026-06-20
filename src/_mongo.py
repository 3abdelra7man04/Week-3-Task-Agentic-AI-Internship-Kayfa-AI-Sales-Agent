"""
_mongo.py — MongoDB helpers for CRM ticket persistence.
Falls back gracefully if MongoDB is unreachable.
"""

import os
import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

# ─── Connection ──────────────────────────────────────────────────────────────

_client = None
_db = None
_collection = None

MONGO_URL = os.getenv("MONGODB_URL", "mongodb+srv://kayfa:ahm2004514@cluster0.riomgta.mongodb.net/")
MONGO_DB   = os.getenv("MONGODB_DATABASE", "Kayfa_Sales_Agent")
COLLECTION = "crm_tickets"


def _get_collection():
    global _client, _db, _collection
    if _collection is not None:
        return _collection
    try:
        from pymongo import MongoClient
        from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

        _client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=3000)
        # Ping to confirm connection
        _client.admin.command("ping")
        _db = _client[MONGO_DB]
        _collection = _db[COLLECTION]
        logger.info("MongoDB connected: %s / %s", MONGO_DB, COLLECTION)
        return _collection
    except Exception as exc:
        logger.warning("MongoDB unavailable: %s", exc)
        return None


# ─── Public API ──────────────────────────────────────────────────────────────

def save_ticket(ticket: dict) -> tuple[bool, str]:
    """
    Save a CRM ticket to MongoDB.
    Returns (success: bool, message: str).
    """
    col = _get_collection()
    if col is None:
        return False, "MongoDB غير متاح حالياً — لم يتم حفظ التذكرة"

    try:
        ticket["created_at"] = ticket.get("created_at", datetime.now())
        result = col.insert_one(ticket)
        return True, str(result.inserted_id)
    except Exception as exc:
        logger.error("save_ticket error: %s", exc)
        return False, str(exc)


def get_tickets(
    status: str | None = None,
    course_keyword: str | None = None,
    limit: int = 100,
) -> list[dict]:
    """
    Fetch CRM tickets from MongoDB with optional filters.
    Returns a list of ticket dicts, or empty list on error.
    """
    col = _get_collection()
    if col is None:
        return []

    try:
        query: dict[str, Any] = {}
        if status and status != "all":
            query["status"] = status
        if course_keyword:
            query["interested_courses"] = {"$regex": course_keyword, "$options": "i"}

        cursor = col.find(query).sort("created_at", -1).limit(limit)
        tickets = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            tickets.append(doc)
        return tickets
    except Exception as exc:
        logger.error("get_tickets error: %s", exc)
        return []


def is_connected() -> bool:
    """Quick connectivity check."""
    return _get_collection() is not None
