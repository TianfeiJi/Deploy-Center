# models/entity/cached_data.py
from pydantic import BaseModel
from typing import Optional, Union, List
from datetime import datetime, timedelta


class CachedData(BaseModel):
    cache_key: str
    cache_value: Union[str, int, float, bool, dict, list, None]
    data_type: str = "unknown"
    ttl: Optional[int] = None
    expire_at: Optional[datetime] = None
    hit_count: int = 0
    source: str = "runtime"
    tags: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def is_expired(self) -> bool:
        now = datetime.now().isoformat()
        if self.expire_at:
            return now >= self.expire_at
        if self.ttl:
            return now >= self.created_at + timedelta(seconds=self.ttl)
        return False

    def access(self):
        self.hit_count += 1
        self.updated_at = datetime.now().isoformat()

    def touch(self, ttl: Optional[int] = None):
        self.updated_at = datetime.now().isoformat()
        if ttl:
            self.ttl = ttl
            self.expire_at = self.updated_at + timedelta(seconds=ttl)
