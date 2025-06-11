# managers/cached_data_manager.py
import json
import os
from typing import List, Optional
from models.common.cached_data import CachedData


class CachedDataManager:
    _instance = None
    _data_file_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "data", "cached_data.json"
    )

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CachedDataManager, cls).__new__(cls)
        return cls._instance

    def _load_cache(self) -> List[CachedData]:
        try:
            with open(self._data_file_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                return [CachedData(**item) for item in raw_data]
        except FileNotFoundError:
            return []

    def _save_cache(self, items: List[CachedData]):
        with open(self._data_file_path, "w", encoding="utf-8") as f:
            json.dump(
                [item.model_dump() for item in items],
                f,
                indent=4,
                ensure_ascii=False,
                default=str
            )

    def list_cache(self, include_expired: bool = False) -> List[CachedData]:
        cache_list = self._load_cache()
        if include_expired:
            return cache_list
        return [item for item in cache_list if not item.is_expired()]
    
    def set_cache(self, data: CachedData):
        cache_list = self._load_cache()
        for i, item in enumerate(cache_list):
            if item.cache_key == data.cache_key:
                cache_list[i] = data
                break
        else:
            cache_list.append(data)
        self._save_cache(cache_list)

    def get_cache(self, cache_key: str) -> Optional[CachedData]:
        cache_list = self._load_cache()
        for item in cache_list:
            if item.cache_key == cache_key:
                if not item.is_expired():
                    item.access()
                    self._save_cache(cache_list)
                    return item
        return None

    def delete_cache(self, cache_key: str):
        cache_list = self._load_cache()
        new_list = [item for item in cache_list if item.cache_key != cache_key]
        self._save_cache(new_list)