# utils/user_context.py
from contextvars import ContextVar
from typing import Optional
from models.entity.user import User

_user_context: ContextVar[Optional[User]] = ContextVar("_user_context", default=None)

def set_current_user(user: User):
    _user_context.set(user)

def get_current_user() -> Optional[User]:
    return _user_context.get()