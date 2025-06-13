import json
import os
from typing import List, Optional
from datetime import datetime
from models.entity.user import User


class UserDataManager:
    _instance = None
    _data_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "user_data.json")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserDataManager, cls).__new__(cls)
        return cls._instance

    def _load_users(self) -> List[User]:
        try:
            with open(self._data_file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                return [User(**user) for user in data]
        except FileNotFoundError:
            return []

    def _save_users(self, users: List[User]):
        with open(self._data_file_path, "w", encoding="utf-8") as file:
            json.dump([user.model_dump() for user in users], file, indent=4, default=str, ensure_ascii=False)

    def create_user(self, user_data: dict):
        users = self._load_users()
        max_id = max((user.id for user in users), default=0)
        user_data["id"] = max_id + 1
        user_data["avatar"] = "https://cdn.quasar.dev/img/boy-avatar.png"   # 默认头像
        user_data["created_at"] = datetime.now().isoformat()
        user_data["status"] = user_data.get("status", "ENABLED")  # 如果没传，则默认状态为ENABLED
        new_user = User(**user_data)
        users.append(new_user)
        self._save_users(users)

    def get_user(self, user_id: int) -> Optional[User]:
        users = self._load_users()
        return next((user for user in users if user.id == user_id), None)

    def get_user_by_username(self, username: str) -> Optional[User]:
        users = self._load_users()
        return next((user for user in users if user.username == username), None)

    def update_user(self, user_id: int, updated_data: dict):
        users = self._load_users()
        for user in users:
            if user.id == user_id:
                for key, value in updated_data.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                user.updated_at = datetime.now().isoformat()
                self._save_users(users)
                return
        raise ValueError(f"User with ID {user_id} not found.")

    def delete_user(self, user_id: int):
        users = self._load_users()
        users = [user for user in users if user.id != user_id]
        self._save_users(users)

    def list_users(self) -> List[User]:
        return self._load_users()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance