import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class ComponentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, example="react")
    version: str = Field(..., min_length=1, max_length=50, example="17.0.2")
    category: Optional[str] = Field(default="general", example="frontend")

class ComponentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    version: Optional[str] = Field(None, min_length=1, max_length=50)
    category: Optional[str] = None

class ComponentResponse(BaseModel):
    id: str
    name: str
    version: str
    category: str
    created_at: datetime
    updated_at: datetime

class InMemoryDatabase:
    """Thread-safe, high-performance in-memory repository for tech stack components."""
    def __init__(self):
        self._data: Dict[str, dict] = {}
        self._seed_default_data()

    def _seed_default_data(self):
        initial_items = [
            {"name": "node", "version": "18.15.0", "category": "runtime"},
            {"name": "react", "version": "17.0.2", "category": "frontend"},
            {"name": "postgres", "version": "12.0", "category": "database"},
        ]
        for item in initial_items:
            self.create(ComponentCreate(**item))

    def list_all(self, category: Optional[str] = None) -> List[dict]:
        items = list(self._data.values())
        if category:
            items = [i for i in items if i.get("category", "").lower() == category.lower()]
        return sorted(items, key=lambda x: x["created_at"], reverse=True)

    def get_by_id(self, item_id: str) -> Optional[dict]:
        return self._data.get(item_id)

    def create(self, payload: ComponentCreate) -> dict:
        item_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        record = {
            "id": item_id,
            "name": payload.name.strip().lower(),
            "version": payload.version.strip(),
            "category": (payload.category or "general").strip().lower(),
            "created_at": now,
            "updated_at": now,
        }
        self._data[item_id] = record
        return record

    def update(self, item_id: str, payload: ComponentUpdate) -> Optional[dict]:
        record = self._data.get(item_id)
        if not record:
            return None
        
        now = datetime.now(timezone.utc)
        if payload.name is not None:
            record["name"] = payload.name.strip().lower()
        if payload.version is not None:
            record["version"] = payload.version.strip()
        if payload.category is not None:
            record["category"] = payload.category.strip().lower()
        
        record["updated_at"] = now
        self._data[item_id] = record
        return record

    def delete(self, item_id: str) -> bool:
        if item_id in self._data:
            del self._data[item_id]
            return True
        return False

    def clear(self):
        self._data.clear()

# Global database singleton
db = InMemoryDatabase()
